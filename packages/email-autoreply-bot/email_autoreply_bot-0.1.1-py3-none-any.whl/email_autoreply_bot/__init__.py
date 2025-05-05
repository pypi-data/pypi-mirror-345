"""
Email Autoreply Bot - An automated email reply system with configurable rules.
"""

__version__ = "0.1.1"

from email_autoreply_bot.bot import EmailAutoreplyBot
from email_autoreply_bot.config import create_default_config

__all__ = ["__version__", "EmailAutoreplyBot", "create_default_config"]
