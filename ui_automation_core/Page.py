from ui_automation_core.Finder import Finder
from ui_automation_core.Interactor import Interactor
from ui_automation_core.Interrogator import Interrogator
from ui_automation_core.Waiter import Waiter


class BasePage(object):
    """
    This is the base page class from which common functionality can be inherited
    """
    def __init__(self, driver, logger, wait_time=10):
        """
        Default constructor which passes the control of webDriver to the current page
        :param driver: the Selenium web driver
        :param logger: logger object used to save information to a log file
        :param wait_time: number of seconds as an Integer, defaults to 10
        """
        self.driver = driver
        self.logger = logger
        self.implicit_wait = wait_time
        self.find = Finder(driver, logger)
        self.wait = Waiter(driver, logger, wait_time)
        self.interrogate = Interrogator(driver, logger, self.find)
        self.interact = Interactor(driver, logger, self.find, self.interrogate, self.wait)
