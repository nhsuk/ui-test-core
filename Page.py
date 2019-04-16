from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
import string
import random


# This is the base page class which defines the generic attributes and methods that all other pages will share
class BasePage(object):

    def __init__(self, driver, logger):
        """
        Default constructor which passes the control of webDriver to the current page
        :param driver: the Selenium web driver
        :param logger: logger object used to save information to a log file
        """
        self.driver = driver
        self.logger = logger

    def find_elements(self, page_element):
        """
        Find the elements matching the given page element object
        :param page_element: common.PageElement
        :return: list of matching WebElements
        """
        return self.driver.find_elements(page_element.locator_type, page_element.locator_value)

    def get_attribute(self, page_element, attribute):
        """
        Get any attribute on an element
        :param page_element: common.PageElement
        :param attribute: the name of the attribute whose value you want e.g. 'type'
        :return: the string value of the attribute, empty if the element was not found
        """
        elements = self.find_elements(page_element)
        if not elements:
            return ""
        return elements[0].get_attribute(attribute)

    def get_current_url(self):
        """
        :return: the url of the current page
        """
        return self.driver.current_url

    @staticmethod
    def __is_element_visible(element):
        """
        Check that a specific element is visible, also looking for an aria-hidden attribute to validate accessibility
        :param element: the Selenium element object - find the correct element before calling this function
        :return: boolean representing whether the element is visible
        """
        return element.is_displayed() and not element.get_attribute("aria-hidden") == "true"

    def element_visible(self, page_element):
        """
        Check if an element is visible using the given Selenium locator
        :param page_element: common.PageElement
        :return: boolean representing whether the element is visible
        """
        # Check for element using find_elements so there is no exception here
        elements = self.find_elements(page_element)
        return elements and self.__is_element_visible(elements[0])

    def element_enabled(self, page_element):
        """
        Check if an element is enabled using the given Selenium locator
        :param page_element: common.PageElement
        :return: boolean representing whether the element is enabled
        """
        # Check for element using find_elements so there is no exception here
        elements = self.find_elements(page_element)
        return elements and elements[0].is_enabled()

    def element_visible_and_contains_text(self, page_element, expected_text):
        """
        Check that an element is visible on the page and contains the expected text
        :param page_element: common.PageElement
        :param expected_text: the text to check against the element contents
        :return: boolean representing whether the element with expected text was found
        """
        elements = self.find_elements(page_element)

        # Check each element found with the expected text
        for element in elements:
            if self.__is_element_visible(element) and expected_text in element.text:
                return True
        return False

    def number_of_elements(self, page_element):
        """
        Count the number of matching elements on the page
        :param page_element: common.PageElement
        :return: the number of elements found
        """
        elements = self.find_elements(page_element)
        return len(elements)

    def number_of_elements_with_background_url(self, page_element):
        """
        Count number of elements with CSS background e.g. check that a required image is displayed
        :param page_element: common.PageElement
        :return: the number of elements found with a background
        """
        element_counter = 0
        elements = self.find_elements(page_element)

        for element in elements:
            background_value = element.value_of_css_property("background")
            if "url" in background_value:
                element_counter += 1

        return element_counter

    def radio_button_visible(self, page_element):
        """
        Check that a radio button is visible - also need to check visibility of parent element for these
        :param page_element: common.PageElement
        :return: boolean representing whether the element was visible
        """
        return self.element_or_parent_visible(page_element)

    def checkbox_visible(self, page_element):
        """
        Check that a checkbox is visible - also need to check visibility of parent element for these
        :param page_element: common.PageElement
        :return: boolean representing whether the element was visible
        """
        return self.element_or_parent_visible(page_element)

    def element_or_parent_visible(self, page_element):
        """
        Check if an element or its parent is visible - sometimes the visibility is only set on the parent e.g. checkbox
        :param page_element: common.PageElement
        :return: boolean representing whether the element was visible
        """
        # Check for element using find_elements so there is no exception here
        elements = self.find_elements(page_element)
        return elements and (elements[0].is_displayed() or elements[0].find_element(By.XPATH, "./..").is_displayed())

    def element_has_class(self, page_element, expected_class):
        """
        Find an element and check it has the correct class
        :param page_element: common.PageElement
        :param expected_class: the class to look for on the element - it can be one of several classes
        :return: boolean representing whether the class was found on the element
        """
        elements = self.find_elements(page_element)
        return elements and elements[0].is_displayed() and expected_class in elements[0].get_attribute("class")

    def parent_of_element_has_class(self, page_element, expected_class):
        """
        Find an element and check its parent has the correct class
        :param page_element: common.PageElement
        :param expected_class: the class to look for on the parent - it can be one of several classes
        :return: boolean representing whether the class was found on the parent
        """
        elements = self.find_elements(page_element)
        if elements:
            parent = elements[0].find_element(By.XPATH, "./..")
            return parent.is_displayed() and expected_class in parent.get_attribute("class")
        return False

    def sibling_of_element_has_class(self, page_element, expected_class):
        """
        Find an element and check that any of its sibling elements has the correct class
        :param page_element: common.PageElement
        :param expected_class: the class to look for on the sibling - it can be one of several classes
        :return: boolean representing whether the class was found on the sibling
        """
        elements = self.find_elements(page_element)
        if elements:
            siblings_with_class = elements[0].find_elements(By.XPATH,
                                                            "./../*[contains(@class,'" + expected_class + "')]")
            return siblings_with_class and siblings_with_class[0].is_displayed()
        return False

    def element_contains_link(self, page_element, expected_url):
        """
        Check if an element contains a link to the given URL
        :param page_element: common.PageElement
        :param expected_url: the URL expected for the link
        :return: boolean representing whether the link was valid
        """
        elements = self.find_elements(page_element)
        if elements:
            return elements[0].is_displayed() and expected_url in elements[0].get_attribute("href")
        return False

    def click_element(self, page_element):
        """
        Finds and clicks on an element on the page
        :param page_element: common.PageElement
        """
        self.driver.find_element(page_element.locator_type, page_element.locator_value).click()

    def edit_element(self, page_element, field_input, clear_first=True):
        """
        Writes the given text to an element on the page - only to be used with editable text fields
        :param page_element: common.PageElement
        :param field_input: the text to write to the element
        :param clear_first: boolean representing whether or not to clear the field before editing (default True)
        """
        element = self.driver.find_element(page_element.locator_type, page_element.locator_value)
        if clear_first:
            element.clear()
        element.send_keys(field_input)

    def append_url(self, additional_url):
        """
        Adds additional data to URL e.g. query string
        :param additional_url: the string to append the URL
        """
        url = self.get_current_url()
        url += additional_url
        self.open_url(url)

    def element_selected(self, page_element):
        """
        Check if an element such as a radio button is selected
        :param page_element: common.PageElement
        :return: boolean representing whether the element was selected
        """
        elements = self.find_elements(page_element)
        return elements and elements[0].is_selected()

    @staticmethod
    def generate_random_string(size=8, chars=string.ascii_letters + string.digits + " "):
        """
        Generate a random string with specified length and character set
        :param size: The length required for the string
        :param chars: The character set to generate the string from - by default this is letters, numbers and spaces
        :return: The generated string
        """
        return "".join(random.choice(chars) for _ in range(size))

    # Definition to open any given url
    def open_url(self, url):
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.XPATH, "//h1")))
        self.logger.log(20, "PASS: Successfully opened the URL - " + url)

    # Switch the control to a new page that opens up
    def switch_window(self):
        window_02 = self.driver.window_handles[1]
        self.logger.log(20, "Switching to new window")
        self.driver.switch_to_window(window_02)
