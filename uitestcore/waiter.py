"""
Created by Tony Lawson
"""
import logging
import time
from selenium.webdriver.support import wait
from selenium.webdriver.support.expected_conditions import presence_of_element_located, alert_is_present
from selenium.webdriver.support.expected_conditions import visibility_of_element_located
from selenium.webdriver.support.wait import WebDriverWait
from uitestcore import custom_expected_conditions
from uitestcore.custom_expected_conditions import ElementHasAttribute


class Waiter:
    """
    Selenium based wait methods
    Uses both standard and custom expected conditions
    """

    def __init__(self, driver, finder, wait_time=10, logger=None):
        """
        Default constructor which passes the control of webDriver to the current page
        :param driver: the Selenium web driver
        :param finder: Finder used to find elements before waiting for them
        :param wait_time: number of seconds as an Integer, defaults to 10
        :param logger: logger object used to save information to a log file
        """
        self.driver = driver
        self.find = finder
        self.wait_time = wait_time
        self.logger = logger or logging.getLogger(__name__)

    def for_page_to_load(self):
        """
        Wait for browser to load using custom expected condition BrowserIsReady
        """
        self.logger.info("Waiting for browser")

        # Initial sleep before the first check - some tests can fail without this
        time.sleep(wait.POLL_FREQUENCY)

        WebDriverWait(self.driver, self.wait_time).until(custom_expected_conditions.BrowserIsReady())
        self.logger.info("Finished waiting for browser")

    def for_element_to_be_visible(self, page_element):
        """
        Wait for element to be visible, using selenium expected condition class
        :param page_element: PageElement instance representing the element
        :return:
        """
        self.logger.info("Waiting for element to be visible")
        WebDriverWait(self.driver, self.wait_time).until(visibility_of_element_located(
            (page_element.locator_type, page_element.locator_value)))
        self.logger.info("found element")

    def for_element_to_be_present(self, page_element):
        """
        Wait for element to be present, using selenium expected condition class
        :param page_element: PageElement instance representing the element
        """
        self.logger.info("Waiting for element to be present")
        WebDriverWait(self.driver, self.wait_time).until(presence_of_element_located(
            (page_element.locator_type, page_element.locator_value)))
        self.logger.info("found element")

    def for_element_to_have_attribute(self, page_element, attribute_name, expected_attribute_value):
        """
        Wait for an element to have a specific attribute value e.g. to check if an animation has finished
        :param page_element: PageElement instance representing the element
        :param attribute_name: the name of the attribute whose value you want e.g. 'type'
        :param expected_attribute_value: the string value which is expected for the attribute
        """
        WebDriverWait(self.driver, self.wait_time).until(ElementHasAttribute(self.find, page_element,
                                                                             attribute_name, expected_attribute_value))

    def for_alert_to_be_present(self):
        """
        Wait for alert to be present, using selenium expected condition class
        """
        self.logger.info("Waiting for alert to be present")
        WebDriverWait(self.driver, self.wait_time).until(alert_is_present())
        self.logger.info("switched to alert")
