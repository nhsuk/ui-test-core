import logging
import os
import time

"""
Logging Helper:         This class contains the functions of interactions when reading a file
Created by:             Raj Singh
Reviewed and Edited by:
Date Created:           05/07/2018
"""


class Logger(object):

    @staticmethod
    def start():
        print("Starting Test")

    @staticmethod
    def init_logger():
        # Create logger with some name
        logger = logging.getLogger('base_logger')
        logger.setLevel(logging.DEBUG)

        return logger

    @staticmethod
    def create_log_file():
        logger = Logger.init_logger()
        file_path = os.path.abspath('logs')

        # Create file handler which logs messages
        if not os.path.exists(file_path):
            os.makedirs(file_path)

        file_handler = logging.FileHandler(os.path.join(file_path, time.strftime('%Y%m%d-%H%M%S') + '.log'))
        file_handler.setLevel(logging.DEBUG)

        # Create console handler for higher log level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)

        # Create formatter and add it to handlers
        formatter = logging.Formatter('%(asctime)s: %(name)s: %(levelname)s:: %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        logger.debug('Created the file to write to')
        return logger

    @staticmethod
    def log(log_level, message):
        logging.log(log_level, message)
