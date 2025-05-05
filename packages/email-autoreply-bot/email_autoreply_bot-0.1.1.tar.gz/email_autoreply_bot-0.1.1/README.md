# Email Autoreply Bot

An automated email reply system with configurable rules and templates.

## Features

- Connects to an IMAP mailbox to check for new emails
- Sends automatic replies with customizable subject and message
- Supports placeholders for personalized replies
- Configurable rules for who should receive autoreplies
- Date range settings to automatically activate and deactivate
- Customizable date formats
- Configurable backfill period for catching up on emails
- Comprehensive SSL/TLS security settings
- Option to CC original recipients on auto-replies

## Installation

```bash
pip install email-autoreply-bot
```

## Quick Start

1. Create a default configuration file:

```bash
email-autoreply-bot --create-config
```

2. Edit the generated `config.yaml` file with your email settings and preferences.

3. Run the bot:

```bash
email-autoreply-bot
```

## Configuration

The bot is configured using a YAML file. Here's an overview of the configuration options:

### Email Settings

```yaml
imap:
  server: imap.example.com
  port: 993
  username: your_email@example.com
  password: your_password
  ssl: true

smtp:
  server: smtp.example.com
  port: 465
  username: your_email@example.com
  password: your_password
  use_ssl: true
```

### Date and Time Settings

```yaml
# Format for dates in messages
date_format: "%A, %B %d, %Y"

# When the auto-reply should be active
date_range:
  start: "2023-12-24"
  end: "2024-01-02"

# How many hours of past emails to check on startup
backfill_hours: 24

# How often to check for new emails (in seconds)
check_interval: 300
```

### Auto-reply Message

```yaml
autoreply:
  subject: "Re: {original_subject} - Out of Office"
  message: |
    Hello {sender_name},

    Thank you for your email regarding "{original_subject}".

    I am currently out of the office from {start_date} until {end_date}.
    I will respond to your message when I return on {return_date}.

    For urgent matters, please contact support@example.com.

    Best regards,
    Your Name

  # CC settings
  cc_include_to: false # Include original To recipients in CC
  cc_include_cc: false # Include original CC recipients in CC
```

### Reply Rules

```yaml
rules:
  # If specified, ONLY these patterns will receive replies
  allowlist:
    - "@company\\.com$"
    - "@client\\.org$"

  # These patterns will never receive autoreplies
  denylist:
    - "noreply@"
    - "donotreply@"
    - "automated@"
```

## Date Range Configuration

The bot can be configured to only send auto-replies during a specific date range. This is useful for vacation periods, holidays, or other out-of-office scenarios.

### Basic Configuration

```yaml
date_range:
  start: "2024-12-24" # Start date (beginning of day)
  end: "2025-01-02" # End date (end of day)
```

### Date Format Options

You can specify dates in several formats:

1. **Date only** (recommended for simplicity):

   ```yaml
   start: "2024-12-24" # December 24, 2024 at 00:00:00
   end: "2025-01-02" # January 2, 2025 at 23:59:59
   ```

2. **Date with time**:

   ```yaml
   start: "2024-12-24 17:00:00" # December 24, 2024 at 5:00 PM
   end: "2025-01-02 09:00:00" # January 2, 2025 at 9:00 AM
   ```

3. **ISO 8601 format**:
   ```yaml
   start: "2024-12-24T17:00:00" # December 24, 2024 at 5:00 PM
   end: "2025-01-02T09:00:00" # January 2, 2025 at 9:00 AM
   ```

### Time Handling

- For **start dates** without a specified time, the bot uses **00:00:00** (beginning of the day)
- For **end dates** without a specified time, the bot uses **23:59:59** (end of the day)
- The bot will use the time zone of the machine it's running on.

## CC Options

You can configure the bot to CC other recipients of the original email on your auto-reply:

```yaml
autoreply:
  # Other autoreply settings...

  # CC settings
  cc_include_to: false # Include original To recipients in CC
  cc_include_cc: false # Include original CC recipients in CC
```

If both settings are `false`, the bot will only reply to the original sender.

## Security Settings

### IMAP Security Options

```yaml
imap:
  server: imap.example.com
  port: 993 # Standard SSL port for IMAP
  username: your_email@example.com
  password: your_password
  ssl: true # Use SSL/TLS for connection
  ssl_context: null # Options: null (default), "default", "trusted", or path to cert file
  verify_ssl: true # Verify SSL certificates
```

- `ssl`: Whether to use SSL/TLS for the connection (recommended)
- `ssl_context`: SSL context configuration:
  - `null`: Use system default SSL context
  - `"default"`: Create a default SSL context
  - `"trusted"`: Create a context for trusted clients
  - `/path/to/cert.pem`: Path to a custom certificate file
- `verify_ssl`: Whether to verify SSL certificates (recommended for security)

### SMTP Security Options

```yaml
smtp:
  server: smtp.example.com
  port: 465 # SSL port for SMTP
  username: your_email@example.com
  password: your_password
  use_ssl: true # Use SSL for connection (port 465)
  use_tls: false # Use STARTTLS (usually with port 587)
  ssl_context: null # Options: null (default), "default", "trusted", or path to cert file
  verify_ssl: true # Verify SSL certificates
  timeout: 30 # Connection timeout in seconds
```

- `use_ssl`: Use SSL/TLS from the start of the connection (typically port 465)
- `use_tls`: Use STARTTLS to upgrade an unencrypted connection (typically port 587)
- `ssl_context`: SSL context configuration (same options as IMAP)
- `verify_ssl`: Whether to verify SSL certificates
- `timeout`: Connection timeout in seconds

## Available Placeholders

The following placeholders can be used in the subject and message templates:

- `{sender_name}` - The name of the sender
- `{sender_email}` - The email address of the sender
- `{original_subject}` - The subject of the original email
- `{date}` - The current date
- `{current_date}` - The current date (same as {date})
- `{message_snippet}` - A snippet of the original message
- `{original_message}` - The full body of the original message
- `{start_date}` - The start date of your out-of-office period
- `{end_date}` - The end date of your out-of-office period
- `{return_date}` - The date you'll return (day after end_date)

## Command-line Options

```
usage: email-autoreply-bot [-h] [-c CONFIG] [--create-config] [--overwrite] [-v]

Email Autoreply Bot - Automatically reply to incoming emails based on rules

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to configuration file (default: config.yaml)
  --create-config       Create a default configuration file
  --overwrite           Overwrite existing configuration file when using --create-config
  -v, --verbose         Enable verbose logging
```

## Using as a Library

You can theoretically also use the Email Autoreply Bot as a library in your own Python code:

```python
from email_autoreply_bot import EmailAutoreplyBot, create_default_config

# Create a default config file if needed
create_default_config('my_config.yaml')

# Initialize and run the bot
bot = EmailAutoreplyBot('my_config.yaml')
bot.run()
```

## Security Considerations

- The configuration file contains sensitive information (email passwords)
- Set appropriate file permissions (e.g., `chmod 600 config.yaml`)

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file
