import logging
import sys
import os


def setup_logger(name=__name__):
    # 1. Create a custom logger
    logger = logging.getLogger(name)

    # Check if handlers are already set to prevent duplicate logs on reload
    if not logger.handlers:
        # 2. Set the global log level (from env or default to INFO)
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        logger.setLevel(log_level)

        # 3. Create handlers
        c_handler = logging.StreamHandler(sys.stdout)  # Console output

        # Ensure logs directory exists at the project root
        os.makedirs('logs', exist_ok=True)
        f_handler = logging.FileHandler('logs/app.log')    # File output

        # 4. Create formatters and add it to handlers
        # Format: Time - Logger Name - Level - Message
        c_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        f_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)

        # 5. Add handlers to the logger
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)

    return logger
