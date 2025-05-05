"""Command-line interface for Email Autoreply Bot."""

import argparse
import sys
import os
import logging
from email_autoreply_bot.bot import EmailAutoreplyBot
from email_autoreply_bot.config import create_default_config

logger = logging.getLogger("email_autoreply_bot")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Email Autoreply Bot - Automatically reply to incoming emails based on rules",
    )

    parser.add_argument(
        "-c",
        "--config",
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)",
    )

    parser.add_argument(
        "--create-config",
        action="store_true",
        help="Create a default configuration file",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing configuration file when using --create-config",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )

    return parser.parse_args()


def setup_logging(verbose=False):
    """Configure logging based on verbosity level."""
    log_level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


def main():
    """Main entry point for the command-line interface."""
    args = parse_args()
    setup_logging(args.verbose)

    if args.create_config:
        success = create_default_config(args.config, args.overwrite)
        if success:
            print(f"Default configuration created at: {args.config}")
            print(
                "Please edit this file with your email settings before running the bot."
            )
        else:
            print("Failed to create configuration file. See log for details.")
            if not args.overwrite and os.path.exists(args.config):
                print("File already exists. Use --overwrite to replace it.")
        return 0 if success else 1

    if not os.path.exists(args.config):
        print(f"Configuration file not found: {args.config}")
        print("Use --create-config to generate a default configuration file.")
        return 1

    try:
        bot = EmailAutoreplyBot(args.config)
        bot.run()
    except KeyboardInterrupt:
        print("\nBot stopped by user.")
        return 0
    except Exception as e:
        logger.error(f"Error running bot: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
