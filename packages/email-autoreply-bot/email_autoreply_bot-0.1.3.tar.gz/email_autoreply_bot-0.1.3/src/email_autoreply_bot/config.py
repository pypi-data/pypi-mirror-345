"""Configuration utilities for Email Autoreply Bot."""

import os
import yaml
import logging
import importlib.resources as resources
import shutil

from datetime import datetime, timedelta

logger = logging.getLogger("email_autoreply_bot")


def create_default_config(file_path='config.yaml', overwrite=False):
    """
    Create a default configuration file at the specified path.
    
    Args:
        file_path (str): Path where the config file should be created
        overwrite (bool): Whether to overwrite an existing file
        
    Returns:
        bool: True if file was created, False otherwise
    """
    if os.path.exists(file_path) and not overwrite:
        logger.warning(f"Configuration file already exists at {file_path}. Use overwrite=True to replace it.")
        return False
    
    try:        
        # Read the template content
        template_content = resources.read_text('email_autoreply_bot.templates', 'default_config.yaml')
        
        # Write the template to the destination
        with open(file_path, 'w') as file:
            file.write(template_content)
        
        logger.info(f"Default configuration file created at {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating configuration file: {e}")
        return False