"""
You can create your own logger and pass it into the uitestcore
However if you don't want to, and just want something simple, you might find this useful
"""
import logging
import logging.config
import os
import string
import time

from uitestcore.utilities.string_util import generate_random_string


def init_unique_log_file_logger(file_path=os.path.abspath('logs'),
                                level=logging.INFO,
                                log_format='%(asctime)s - %(levelname)s - %(name)s: %(message)s'):
    """
    Setting up the basic config for the logging module. Creates a log file in the specified location.
    File name will be time.strftime('%Y%m%d-%H%M%S') + '.log'
    You can specify a logging level and the format of the log messages

    :param file_path: default os.path.abspath('logs')
    :param level: default logging.INFO
    :param log_format: default '%(asctime)s - %(levelname)s - %(name)s: %(message)s'
    """
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    file_name = os.path.join(file_path, time.strftime('%Y%m%d-%H%M%S') + '.log')
    logging.basicConfig(filename=file_name, filemode='w', level=level, format=log_format)
    logging.debug("initialised logger to write to file %s with level %s and format %s",
                  file_name, level, log_format)


def auto_log(logger_name):
    """
    A decorator that wraps the passed in function, logs entering and exiting the function,
    and logs exceptions should one occur. Exceptions are reraised.
    Tag each method or function with @auto_log(__name__) to automatically log calls.
    Logs these calls at DEBUG level.

    :param logger_name: The class or module name of the calling method. Use __name__
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(logger_name)
            log_identifier = generate_random_string(6, chars=string.digits)
            try:
                entry_message = "Entering function %s (Function call ID %s) " \
                    "with args %s and kwargs %s"
                logger.debug(entry_message, func.__name__, log_identifier, args, kwargs)
                return_value = func(*args, **kwargs)
                exit_message = "Exited function %s (Function call ID %s) " \
                    "with return value %s"
                logger.debug(exit_message, func.__name__, log_identifier, return_value)
                return return_value
            except Exception as e:
                # log the exception
                err = "There was an exception thrown in function %s (Function call ID %s)"
                logger.exception(err, func.__name__, log_identifier)

                # re-raise the exception
                raise e

        return wrapper
    return decorator
