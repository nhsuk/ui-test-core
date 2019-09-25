import logging

from uitestcore.finder import Finder
from uitestcore.interactor import Interactor
from uitestcore.interrogator import Interrogator
from uitestcore.waiter import Waiter


class BasePage:
    """
    This is the base page class from which common functionality can be inherited
    """
    def __init__(self, driver, existing_logger=None, wait_time=10):
        """
        Default constructor which passes the control of webDriver to the current page
        :param driver: the Selenium web driver
        :param existing_logger: logger object used to save information to a log file, None by default
        :param wait_time: number of seconds as an Integer, defaults to 10
        """
        self.driver = driver
        self.logger = existing_logger or logging.getLogger(__name__)
        self.implicit_wait = wait_time
        self.find = Finder(driver, existing_logger)
        self.wait = Waiter(driver, self.find, wait_time, existing_logger)
        self.interrogate = Interrogator(driver, self.find, existing_logger)
        self.interact = Interactor(driver, self.find, self.interrogate, self.wait, existing_logger)
