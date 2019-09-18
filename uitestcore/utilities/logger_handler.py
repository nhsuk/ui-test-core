import logging
import logging.config
import os
import time


def init_unique_log_file_logger(file_path=os.path.abspath('logs'), level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s: %(message)s'):
    """
    Setting up the basic config for the logging module. Creates a log file in the specified location.
    File name will be time.strftime('%Y%m%d-%H%M%S') + '.log'
    You can specify a logging level and the format of the log messages

    :param file_path: default os.path.abspath('logs')
    :param level: default logging.INFO
    :param format: default '%(asctime)s - %(levelname)s - %(name)s: %(message)s'
    """
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    file_name = os.path.join(file_path, time.strftime('%Y%m%d-%H%M%S') + '.log')
    logging.basicConfig(filename=file_name, filemode='w', level=level, format=format)
    logging.debug(f"initialised logger to write to file {file_name} with level {level} and format {format}")
