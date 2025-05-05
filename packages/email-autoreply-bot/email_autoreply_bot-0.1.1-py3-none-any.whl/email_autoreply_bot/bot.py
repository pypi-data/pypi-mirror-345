#!/usr/bin/env python3
import imaplib
import email
import smtplib
import time
import re
import yaml
import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from email.utils import parseaddr
from dateutil import parser as date_parser
import pytz
from tzlocal import get_localzone

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("email_autoreply_bot")


class EmailAutoreplyBot:
    def __init__(self, config_path="config.yaml"):
        """Initialize the bot with configuration from a YAML file."""
        self.config = self._load_config(config_path)
        self.replied_to = set()  # Store email IDs we've already replied to
        self.last_uid = 0  # Store the highest UID we've seen

        # Track when we last replied to each sender (for rate limiting)
        self.last_reply_date = {}  # sender_email -> datetime

        # Set up timezone
        self.timezone = self._setup_timezone()
        logger.info(f"Using timezone: {self.timezone}")

        # Get backfill period from config (default to 24 hours if not specified)
        self.backfill_hours = self.config.get("backfill_hours", 24)
        logger.info(
            f"Will check emails from the past {self.backfill_hours} hours on first run"
        )

        # Get date format configuration
        self.date_format = self.config.get("date_format", "%A, %B %d, %Y")
        logger.info(f"Using date format: {self.date_format} ({datetime.now().strftime(self.date_format)})")

        # Parse date range for auto-reply if configured
        self.start_date = None
        self.end_date = None

        if "date_range" in self.config:
            # Handle start date with optional time
            if "start" in self.config["date_range"]:
                start_str = self.config["date_range"]["start"]
                self.start_date = self._parse_date_with_optional_time(
                    start_str, is_start=True
                )
                logger.info(
                    f"Auto-reply will start at: {self.start_date.strftime('%Y-%m-%d %H:%M:%S %Z')}"
                )

            # Handle end date with optional time
            if "end" in self.config["date_range"]:
                end_str = self.config["date_range"]["end"]
                self.end_date = self._parse_date_with_optional_time(
                    end_str, is_start=False
                )
                logger.info(
                    f"Auto-reply will end at: {self.end_date.strftime('%Y-%m-%d %H:%M:%S %Z')}"
                )

        # Log rate limit configuration
        rate_limit_hours = self.config.get("rate_limit_hours", 24)
        if rate_limit_hours <= 0:
            logger.info("Rate limiting is disabled")
        else:
            logger.info(
                f"Rate limiting set to {rate_limit_hours} hours between replies to the same sender"
            )

    def _load_config(self, config_path):
        """Load configuration from YAML file."""
        try:
            with open(config_path, "r") as file:
                config = yaml.safe_load(file)
                logger.info(f"Configuration loaded from {config_path}")
                return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise

    def _setup_timezone(self):
        """Set up the timezone for date/time operations."""
        # Get timezone from config, default to system timezone
        timezone_name = self.config.get("timezone", None)

        if not timezone_name:
            # Use system timezone if not specified
            return get_localzone()

        try:
            # Try to get the timezone by name
            return pytz.timezone(timezone_name)
        except pytz.exceptions.UnknownTimeZoneError:
            logger.warning(f"Unknown timezone: {timezone_name}, falling back to UTC")
            return pytz.UTC

    def _parse_date_with_optional_time(self, date_str, is_start=True):
        """
        Parse a date string that may or may not include a time component.
        Applies the configured timezone to the result.

        Args:
            date_str (str): The date string to parse
            is_start (bool): Whether this is a start date (True) or end date (False)

        Returns:
            datetime: The parsed datetime object with appropriate time and timezone
        """
        try:
            # Check if the string contains time information
            has_time = len(date_str.split()) > 1 or "T" in date_str or ":" in date_str

            if has_time:
                # If time is included, parse as is
                dt = date_parser.parse(date_str)

                # If the parsed datetime doesn't have a timezone, apply our timezone
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=self.timezone)

                return dt
            else:
                # Parse just the date part
                date_obj = date_parser.parse(date_str).date()

                # For start dates, use beginning of day (00:00:00)
                if is_start:
                    return datetime.combine(
                        date_obj, datetime.min.time(), tzinfo=self.timezone
                    )
                # For end dates, use end of day (23:59:59)
                else:
                    return datetime.combine(
                        date_obj,
                        datetime.max.time().replace(microsecond=0),
                        tzinfo=self.timezone,
                    )
        except Exception as e:
            logger.error(f"Error parsing date '{date_str}': {e}")
            # Return current date as fallback
            return datetime.now(self.timezone)

    def connect_to_mailbox(self):
        """Connect to the IMAP server and login."""
        try:
            # Get IMAP configuration
            imap_config = self.config["imap"]
            server = imap_config["server"]
            port = imap_config.get("port", 993)  # Default to 993 for SSL
            username = imap_config["username"]
            password = imap_config["password"]
            use_ssl = imap_config.get("ssl", True)
            ssl_context = imap_config.get("ssl_context")
            verify_ssl = imap_config.get("verify_ssl", True)

            # Configure SSL context if needed
            context = None
            if ssl_context:
                import ssl

                if ssl_context == "default":
                    context = ssl.create_default_context()
                elif ssl_context == "trusted":
                    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                elif os.path.exists(ssl_context):
                    context = ssl.create_default_context(cafile=ssl_context)

                # Handle certificate verification
                if not verify_ssl and context:
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE

            # Connect to the server
            if use_ssl:
                self.mail = imaplib.IMAP4_SSL(server, port, ssl_context=context)
            else:
                self.mail = imaplib.IMAP4(server, port)

                # Use STARTTLS if available
                if hasattr(self.mail, "starttls"):
                    self.mail.starttls(ssl_context=context)

            # Login and select inbox
            self.mail.login(username, password)
            self.mail.select("inbox")

            logger.info(f"Connected to {server}:{port} as {username}")
            return True
        except Exception as e:
            logger.error(f"Error connecting to mailbox: {e}")
            return False

    def is_autoreply_active(self):
        """Check if auto-reply is currently active based on date range configuration."""
        now = datetime.now(self.timezone)

        # If no date range is configured, auto-reply is always active
        if not self.start_date and not self.end_date:
            return True

        # Check if current time is within the configured range
        if self.start_date and now < self.start_date:
            logger.info(
                f"Auto-reply not active yet. Current time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}, Start time: {self.start_date.strftime('%Y-%m-%d %H:%M:%S %Z')}"
            )
            return False

        if self.end_date and now > self.end_date:
            logger.info(
                f"Auto-reply period has ended. Current time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}, End time: {self.end_date.strftime('%Y-%m-%d %H:%M:%S %Z')}"
            )
            return False

        return True

    def check_for_new_emails(self):
        """Check for new emails and process them."""
        # First check if auto-reply is active
        if not self.is_autoreply_active():
            logger.info("Auto-reply is not active at this time. Skipping email check.")
            return

        try:
            # Different approach for first run vs. subsequent runs
            if not self.last_uid:
                # On first run, use date-based search with backfill
                self._check_emails_by_date()
            else:
                # On subsequent runs, use UID-based search
                self._check_emails_by_uid()

        except Exception as e:
            logger.error(f"Error checking for new emails: {e}")

    def _check_emails_by_date(self):
        """Check for new emails using date-based search (for first run)."""
        # Calculate the backfill date
        backfill_date = datetime.now(self.timezone) - timedelta(
            hours=self.backfill_hours
        )

        # If we have a start date and it's after the backfill date, use the start date
        if self.start_date and self.start_date > backfill_date:
            search_date = self.start_date
            logger.info(
                f"Using start date for initial search: {search_date.strftime('%Y-%m-%d %H:%M:%S %Z')}"
            )
        else:
            search_date = backfill_date
            logger.info(
                f"Using backfill date for initial search: {search_date.strftime('%Y-%m-%d %H:%M:%S %Z')}"
            )

        # Format date for IMAP search
        date_str = search_date.strftime("%d-%b-%Y")

        # Search for all unseen emails since the search date
        search_criteria = f"(UNSEEN SINCE {date_str})"
        result, data = self.mail.search(None, search_criteria)

        if result != "OK":
            logger.warning(f"Search failed with result: {result}")
            return

        email_ids = data[0].split()
        logger.info(f"Found {len(email_ids)} unseen emails on first run")

        # Process emails and track the highest UID
        processed_count = 0
        skipped_count = 0

        for email_id in email_ids:
            # Get the UID for this message
            result, uid_data = self.mail.fetch(email_id, "(UID)")
            if result == "OK" and uid_data[0]:
                # Extract UID from response like b'42 (UID 12345)'
                uid_str = uid_data[0].decode("utf-8")
                uid_match = re.search(r"UID (\d+)", uid_str)
                if uid_match:
                    uid = int(uid_match.group(1))
                    self.last_uid = max(self.last_uid, uid)

            # Process the email
            if self._process_email(email_id):
                processed_count += 1
            else:
                skipped_count += 1

        logger.info(
            f"First run: Processed {processed_count} emails, skipped {skipped_count} emails"
        )
        logger.info(f"Highest UID seen: {self.last_uid}")

    def _check_emails_by_uid(self):
        """Check for new emails using UID-based search (for subsequent runs)."""
        try:
            # Enable UID command mode
            self.mail.select("inbox")

            # Search for UIDs greater than the last one we processed
            search_criteria = f"(UID {self.last_uid+1}:* UNSEEN)"
            result, data = self.mail.uid("search", None, search_criteria)

            if result != "OK":
                logger.warning(f"UID search failed with result: {result}")
                return

            email_uids = data[0].split()
            logger.info(
                f"Found {len(email_uids)} new unseen emails with UID > {self.last_uid}"
            )

            processed_count = 0
            skipped_count = 0

            for uid in email_uids:
                uid_int = int(uid.decode("utf-8"))

                # Fetch the email by UID
                result, data = self.mail.uid("fetch", uid, "(RFC822)")

                if result != "OK":
                    logger.warning(
                        f"UID fetch failed for UID {uid} with result: {result}"
                    )
                    continue

                # Process the email directly from the fetched data
                if self._process_email_from_data(data):
                    processed_count += 1
                else:
                    skipped_count += 1

                # Update the highest UID we've seen
                self.last_uid = max(self.last_uid, uid_int)

            logger.info(
                f"Subsequent run: Processed {processed_count} emails, skipped {skipped_count} emails"
            )
            logger.info(f"Highest UID seen: {self.last_uid}")

        except Exception as e:
            logger.error(f"Error in UID-based email check: {e}")

    def _process_email(self, email_id):
        """
        Process a single email by ID and send autoreply if needed.

        Returns:
            bool: True if email was processed and replied to, False if skipped
        """
        try:
            result, data = self.mail.fetch(email_id, "(RFC822)")
            if result != "OK":
                logger.warning(
                    f"Fetch failed for email {email_id} with result: {result}"
                )
                return False

            return self._process_email_from_data(data)
        except Exception as e:
            logger.error(f"Error processing email {email_id}: {e}")
            return False

    def _check_rate_limit(self, sender_email):
        """
        Check if we should send a reply based on rate limiting.
        Returns True if we should send a reply, False if rate limited.
        """
        # Get rate limit configuration (default to 1 per day)
        rate_limit_hours = self.config.get("rate_limit_hours", 24)

        # If rate limit is disabled (0 or negative), always allow replies
        if rate_limit_hours <= 0:
            return True

        # If sender is not in our tracking dict, we've never replied to them
        if sender_email not in self.last_reply_date:
            return True

        # Get the last reply time for this sender
        last_reply = self.last_reply_date[sender_email]

        # Get current time
        current_time = datetime.now(self.timezone)

        # Calculate time difference
        time_diff = current_time - last_reply
        hours_diff = time_diff.total_seconds() / 3600

        # Only send another reply if enough time has passed
        return hours_diff >= rate_limit_hours

    def _update_rate_limit(self, sender_email):
        """Update the rate limit tracking after sending a reply."""
        self.last_reply_date[sender_email] = datetime.now(self.timezone)

    def _process_email_from_data(self, data):
        """
        Process an email from fetched data and send autoreply if needed.

        Returns:
            bool: True if email was processed and replied to, False if skipped
        """
        try:
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Extract the received date from the email
            # The first 'Received' header is typically the one added by the recipient's server
            received_headers = msg.get_all("Received")
            email_date = None

            if received_headers and len(received_headers) > 0:
                # Parse the date from the first Received header
                try:
                    # The date is typically at the end of the header after ';'
                    received_header = received_headers[0]
                    date_part = received_header.split(";")[-1].strip()
                    email_date = email.utils.parsedate_to_datetime(date_part)

                    # Ensure the email date has a timezone
                    if email_date.tzinfo is None:
                        email_date = email_date.replace(tzinfo=pytz.UTC)

                    # Skip emails received before the start date
                    if self.start_date and email_date < self.start_date:
                        logger.debug(
                            f"Skipping email received on {email_date.strftime('%Y-%m-%d %H:%M:%S %Z')}, before start date {self.start_date.strftime('%Y-%m-%d %H:%M:%S %Z')}"
                        )
                        return False

                    # Skip emails received after the end date
                    if self.end_date and email_date > self.end_date:
                        logger.debug(
                            f"Skipping email received on {email_date.strftime('%Y-%m-%d %H:%M:%S %Z')}, after end date {self.end_date.strftime('%Y-%m-%d %H:%M:%S %Z')}"
                        )
                        return False
                except Exception as e:
                    logger.warning(f"Could not parse received date from header: {e}")
                    # Continue processing if we can't parse the date

            # Extract sender information
            from_header = msg["From"]
            sender_name, sender_email = parseaddr(from_header)

            # Check if we should reply to this sender
            if not self._should_reply_to(sender_email):
                logger.info(
                    f"Skipping reply to {sender_email} based on configuration rules"
                )
                return False

            # Check rate limit - only reply if we haven't exceeded the rate limit
            if not self._check_rate_limit(sender_email):
                logger.info(
                    f"Skipping reply to {sender_email} due to rate limit (already replied within the rate limit period)"
                )
                return False

            # Check if we've already replied to this conversation
            message_id = msg.get("Message-ID", "")
            in_reply_to = msg.get("In-Reply-To", "")
            references = msg.get("References", "")

            # Create conversation identifiers
            conversation_ids = []

            if message_id:
                conversation_ids.append(message_id)
            if in_reply_to:
                conversation_ids.append(in_reply_to)
            if references:
                conversation_ids.extend(references.split())

            # Check if we've already replied to this conversation
            have_replied = any(cid in self.replied_to for cid in conversation_ids)

            # Add the current IDs to the replied set
            for cid in conversation_ids:
                self.replied_to.add(cid)

            # Skip if we've already replied to this conversation
            if have_replied:
                logger.info(
                    f"Already replied to conversation {conversation_ids}, skipping"
                )
                return False

            # Extract information for placeholders
            subject = msg.get("Subject", "")

            # Format current date according to configuration
            current_date = datetime.now(self.timezone).strftime(self.date_format)

            # Get message body
            message_body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    # Skip attachments
                    if "attachment" in content_disposition:
                        continue

                    # Get the body text
                    if content_type == "text/plain":
                        message_body = part.get_payload(decode=True).decode()
                        break
            else:
                message_body = msg.get_payload(decode=True).decode()

            # Extract first line or snippet of the message
            message_snippet = (
                message_body.strip().split("\n")[0][:50] + "..." if message_body else ""
            )

            # Create placeholder dictionary
            placeholders = {
                "sender_name": sender_name or sender_email.split("@")[0],
                "sender_email": sender_email,
                "original_subject": subject,
                "date": current_date,
                "message_snippet": message_snippet,
                "original_message": message_body,
                "current_date": current_date,
            }

            # Add date range information to placeholders if configured
            if self.start_date:
                placeholders["start_date"] = self.start_date.strftime(self.date_format)
            if self.end_date:
                placeholders["end_date"] = self.end_date.strftime(self.date_format)

            # Add return date if end date is configured
            if self.end_date:
                # Add one day to end date for return date
                return_date = self.end_date + timedelta(days=1)
                placeholders["return_date"] = return_date.strftime(self.date_format)

            # Extract CC recipients if needed
            cc_recipients = []

            # Get original To recipients if configured
            if self.config.get("autoreply", {}).get("cc_include_to", False):
                to_headers = msg.get_all("To", [])
                for to_header in to_headers:
                    for name, email_addr in email.utils.getaddresses([to_header]):
                        # Don't CC the sender or ourselves
                        if (
                            email_addr
                            and email_addr != sender_email
                            and email_addr != self.config["smtp"]["username"]
                        ):
                            cc_recipients.append(email_addr)

            # Get original CC recipients if configured
            if self.config.get("autoreply", {}).get("cc_include_cc", False):
                cc_headers = msg.get_all("Cc", [])
                for cc_header in cc_headers:
                    for name, email_addr in email.utils.getaddresses([cc_header]):
                        # Don't CC the sender or ourselves
                        if (
                            email_addr
                            and email_addr != sender_email
                            and email_addr != self.config["smtp"]["username"]
                        ):
                            cc_recipients.append(email_addr)

            # Send the autoreply with placeholders
            if self._send_autoreply(
                sender_email, subject, conversation_ids[0], placeholders, cc_recipients
            ):
                # Mark as replied to
                self.replied_to.add(conversation_ids[0])

                # Update rate limit tracking
                self._update_rate_limit(sender_email)

                logger.info(
                    f"Processed email from {sender_email} with subject: {subject}"
                )
                return True
            else:
                logger.warning(f"Failed to send autoreply to {sender_email}")
                return False

        except Exception as e:
            logger.error(f"Error processing email from data: {e}")
            return False

    def _should_reply_to(self, sender_email):
        """Determine if we should reply to this sender based on config rules."""
        rules = self.config.get("rules", {})

        # Check allowlist (if specified)
        if "allowlist" in rules:
            for pattern in rules["allowlist"]:
                if re.search(pattern, sender_email, re.IGNORECASE):
                    return True
            return False  # If allowlist exists and no match, don't reply

        # Check denylist
        if "denylist" in rules:
            for pattern in rules["denylist"]:
                if re.search(pattern, sender_email, re.IGNORECASE):
                    return False

        # Default to replying if no rules matched
        return True

    def _replace_placeholders(self, text, placeholders):
        """Replace placeholders in text with actual values."""
        for key, value in placeholders.items():
            placeholder = f"{{{key}}}"
            text = text.replace(placeholder, str(value))
        return text

    def _send_autoreply(
        self, recipient, original_subject, in_reply_to, placeholders, cc_recipients=None
    ):
        """Send an autoreply email with placeholders."""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.config["smtp"]["username"]
            msg["To"] = recipient

            # Add CC if specified
            if cc_recipients and len(cc_recipients) > 0:
                msg["Cc"] = ", ".join(cc_recipients)
                logger.info(
                    f"Adding {len(cc_recipients)} recipients to CC: {', '.join(cc_recipients)}"
                )

            # Use the configured subject with placeholders or create a reply subject
            if "subject" in self.config["autoreply"]:
                subject_template = self.config["autoreply"]["subject"]
                subject = self._replace_placeholders(subject_template, placeholders)
                msg["Subject"] = subject
            else:
                # Add Re: if not already there
                if original_subject.lower().startswith("re:"):
                    msg["Subject"] = original_subject
                else:
                    msg["Subject"] = f"Re: {original_subject}"

            # Set In-Reply-To header for proper threading
            if in_reply_to:
                msg["In-Reply-To"] = in_reply_to
                msg["References"] = in_reply_to

            # Add message body with placeholders replaced
            message_template = self.config["autoreply"]["message"]
            message = self._replace_placeholders(message_template, placeholders)
            msg.attach(MIMEText(message, "plain"))

            # Get SMTP configuration
            smtp_config = self.config["smtp"]
            server = smtp_config["server"]
            port = smtp_config.get("port", 465)  # Default to 465 for SSL
            username = smtp_config["username"]
            password = smtp_config["password"]
            use_ssl = smtp_config.get("use_ssl", True)
            use_tls = smtp_config.get("use_tls", False)
            ssl_context = smtp_config.get("ssl_context")
            verify_ssl = smtp_config.get("verify_ssl", True)
            timeout = smtp_config.get("timeout", 30)

            # Configure SSL context if needed
            context = None
            if ssl_context:
                import ssl

                if ssl_context == "default":
                    context = ssl.create_default_context()
                elif ssl_context == "trusted":
                    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                elif os.path.exists(ssl_context):
                    context = ssl.create_default_context(cafile=ssl_context)

                # Handle certificate verification
                if not verify_ssl and context:
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE

            # Connect to the SMTP server with appropriate security
            if use_ssl:
                server_connection = smtplib.SMTP_SSL(
                    server, port, context=context, timeout=timeout
                )
            else:
                server_connection = smtplib.SMTP(server, port, timeout=timeout)

                # Use STARTTLS if requested
                if use_tls:
                    server_connection.starttls(context=context)

            # Login and send the message
            with server_connection as smtp:
                smtp.login(username, password)

                # Get all recipients (To + CC)
                all_recipients = [recipient]
                if cc_recipients:
                    all_recipients.extend(cc_recipients)

                smtp.send_message(msg)

            cc_info = (
                f" with {len(cc_recipients)} CC recipients" if cc_recipients else ""
            )
            logger.info(f"Sent autoreply to {recipient}{cc_info}")
            return True
        except Exception as e:
            logger.error(f"Error sending autoreply to {recipient}: {e}")
            return False

    def run(self):
        """Run the bot in a loop, checking for new emails periodically."""
        logger.info("Starting Email Autoreply Bot")

        while True:
            if self.connect_to_mailbox():
                self.check_for_new_emails()
                self.mail.logout()

            # Wait for the configured interval before checking again
            interval = self.config.get("check_interval", 300)  # Default 5 minutes
            logger.info(f"Sleeping for {interval} seconds")
            time.sleep(interval)
