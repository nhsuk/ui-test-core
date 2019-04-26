"""
Created by Tony Lawson
"""
from selenium.webdriver.support.expected_conditions import visibility_of_element_located
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.wait import WebDriverWait

from ui_automation_core import custom_expected_conditions


class Waiter(object):
    """
    Selenium based wait methods
    Uses both standard and custom expected conditions
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
        self.wait_time = wait_time

    def for_page_to_load(self):
        """
        Wait for browser to load using custom expected condition BrowserIsReady
        :return:
        """
        self.logger.log(20, "Waiting for browser")
        WebDriverWait(self.driver, self.wait_time).until(custom_expected_conditions.BrowserIsReady())
        self.logger.log(20, "Finished waiting for browser")

    def for_element_to_be_visible(self, page_element):
        """
        Wait for element to be visible, using selenium expected condition class
        :param page_element: common.PageElement
        :return:
        """
        self.logger.log(20, "Waiting for element to be visible")
        WebDriverWait(self.driver, self.wait_time).until(visibility_of_element_located(
            (page_element.locator_type, page_element.locator_value)))
        self.logger.log(20, "found element")

    def for_element_to_be_present(self, page_element):
        """
        Wait for element to be present, using selenium expected condition class
        :param page_element:
        :return:
        """
        self.logger.log(20, "Waiting for element to be present")
        WebDriverWait(self.driver, self.wait_time).until(presence_of_element_located(
            (page_element.locator_type, page_element.locator_value)))
        self.logger.log(20, "found element")
