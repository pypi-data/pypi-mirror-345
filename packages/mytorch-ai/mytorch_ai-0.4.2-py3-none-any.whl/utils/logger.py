###############################################################################
# Copyright (c) 2024 MyTorch Systems Inc. All rights reserved.
###############################################################################

import logging


# Map string representations to logging level constants
level_map = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARN': logging.WARNING,
    'ERROR': logging.ERROR
}

MIN_LOG_LEVEL = logging.INFO

class Logger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            logger = logging.getLogger()
            logger.setLevel(MIN_LOG_LEVEL)
            cls._instance.logger = logger

            # Define formats
            debug_format = logging.Formatter('%(message)s')
            general_format = logging.Formatter('%(levelname)s - %(message)s')

            # Stream handler for debug level
            debug_handler = logging.StreamHandler()
            debug_handler.setLevel(logging.DEBUG)
            debug_handler.setFormatter(debug_format)
            debug_handler.addFilter(logging.Filter())  # Allow only DEBUG
            debug_handler.addFilter(lambda record: record.levelno == logging.DEBUG)

            # Stream handler for all levels, but configured to handle INFO and above
            general_handler = logging.StreamHandler()
            general_handler.setLevel(logging.INFO)  # Changed to INFO
            general_handler.setFormatter(general_format)

            # Add handlers to the logger
            logger.addHandler(debug_handler)
            logger.addHandler(general_handler)

        return cls._instance

    @staticmethod
    def get_logger():
        return Logger()._instance.logger
