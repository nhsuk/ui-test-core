import logging

import requests
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from uitestcore.utilities.logger_handler import auto_log


class Interrogator:
    """
    Interrogate an element and return a value
    Such as is_visible -> True/False
    And get_attribute -> String
    """

    def __init__(self, driver, finder, existing_logger=None):
        """
        Default constructor which passes the control of webDriver to the current page
        :param driver: the Selenium web driver
        :param finder: Finder used to find elements before interrogating
        :param existing_logger: logger object used to save information to a log file

        """
        self.driver = driver
        self.find = finder
        self.logger = existing_logger or logging.getLogger(__name__)

    @auto_log(__name__)
    def table_is_not_empty(self, page_element, min_list_length=5):
        """
        check if a table is empty using by counting the rows as found in get_table_row_count(page_element)
        :param page_element: PageElement instance representing the element
        :param min_list_length: some tables have a number of default rows that act as headers
            specify the number of rows to ignore in the count. Defaults to 5
        :return: bool whether table is empty
        """
        table_body = self.find.element(page_element)

        if table_body is None:
            return False

        if self.get_table_row_count(table_body) < min_list_length:
            return False

        return True

    @auto_log(__name__)
    def list_is_not_empty(self, page_element, min_list_length=1):
        """
        check if a list is empty by counting the number of li tags
        :param page_element: PageElement instance representing the element
        :param min_list_length: Some lists might have a default number of rows so it could be 'empty' but have some
            li tags. Defaults to 1
        :return: bool if number of li tags is less than expected
        """
        list_unsorted_tag_result = (self.find.element(page_element)).find_elements_by_tag_name('li')
        if (len(list_unsorted_tag_result)) > min_list_length:
            return True
        return False

    @auto_log(__name__)
    def is_image_visible_by_checking_src(self, page_element):
        """
        Scrape the src attribute from the element
        Perform GET request on src
        If request returns 200 then image is visible and valid
        If request returns other code then image must be broken

        If image doesnt have a src, returns True

        If element src is relative i.e. uses /some/path/to/image.png
        Uses window.location.origin to get host to prefix to src

        :param page_element: PageElement instance representing the element
        :return: bool
        """
        src_url = self.get_attribute(page_element, "src")
        if src_url is None:
            return True

        if src_url[0] == "/":
            src_url = self.driver.execute_script("return window.location.origin") + src_url

        status_code = requests.get(src_url).status_code
        return status_code == 200

    @auto_log(__name__)
    def is_image_visible_by_javascript(self, page_element):
        """
        This method is used to verify if an image content is displayed
        rather than just the image element.
        There is a special case for SVGs, ideally don't test SVGs
        :param page_element: PageElement instance representing the element
        :return: boolean ( true= found, false=not found)
        """
        # SVGs are special, when SVGs don't have a src they are using embedded details which cannot be tested
        # So simply check the element as a whole is displayed
        element = self.find.element(page_element)
        element_tag = element.tag_name
        element_image_src = element.get_attribute("src")
        if element_tag == 'svg' and element_image_src is None:
            return element.is_displayed()

        script = "return (" \
            "(arguments[0].complete)" \
            "||" \
            "(arguments[0].naturalWidth !='undefined' && arguments[0].naturalWidth > 0)" \
            ")"

        return self.driver.execute_script(script, element)

    @auto_log(__name__)
    def is_element_visible(self, page_element, wait=None):
        """
        Check that an element is visible
        using find_elements so there is no exception here
        :param page_element: PageElement instance representing the element
        :param wait: optional Waiter object used to wait before interrogating
        :return: bool
        """
        if wait:
            try:
                wait.for_element_to_be_visible(page_element)
            except TimeoutException:
                pass

        elements = self.find.elements(page_element)
        return len(elements) > 0 and elements[0].is_displayed()

    @auto_log(__name__)
    def are_elements_visible(self, page_element):
        """
        Finds a list of elements using the page_element passed in, and iterates over them to check they are all visible
        If one element is not visible, return false
        if no elements are found, return false
        :param page_element
        :return: bool
        """
        elements = self.find.elements(page_element)

        if not elements:
            return False

        for element in elements:
            if not element.is_displayed() or element.get_attribute("aria-hidden") == "true":
                return False

        return True

    @auto_log(__name__)
    def is_radio_button_visible(self, page_element):
        """
        Check that a radio button is visible - also need to check visibility of parent element for these
        :param page_element: PageElement instance representing the element
        :return: boolean representing whether the element was visible
        """
        return self.is_element_or_parent_visible(page_element)

    @auto_log(__name__)
    def is_checkbox_visible(self, page_element):
        """
        Check that a checkbox is visible - also need to check visibility of parent element for these
        :param page_element: PageElement instance representing the element
        :return: boolean representing whether the element was visible
        """
        return self.is_element_or_parent_visible(page_element)

    @auto_log(__name__)
    def is_checkbox_selected(self, page_element):
        """
        Check that a checkbox element is selected (ticked)
        :param page_element: PageElement instance representing the element
        :return: boolean representing whether the element is selected
        """
        return self.find.element(page_element).is_selected()

    @auto_log(__name__)
    def is_element_or_parent_visible(self, page_element):
        """
        Check if an element or its parent is visible - sometimes the visibility is only set on the parent e.g. checkbox
        :param page_element: PageElement instance representing the element
        :return: boolean representing whether the element was visible
        """
        # Check for element using find_elements so there is no exception here
        elements = self.find.elements(page_element)
        return len(elements) > 0 and (elements[0].is_displayed() or
                                      elements[0].find_element(By.XPATH, "./..").is_displayed())

    @auto_log(__name__)
    def is_element_selected(self, page_element):
        """
        Check if an element such as a radio button is selected
        :param page_element: PageElement instance representing the element
        :return: boolean representing whether the element was selected
        """
        elements = self.find.elements(page_element)
        return len(elements) > 0 and elements[0].is_selected()

    @auto_log(__name__)
    def is_element_enabled(self, page_element):
        """
        Check if an element is enabled using the given Selenium locator
        :param page_element: PageElement instance representing the element
        :return: boolean representing whether the element is enabled
        """
        # Check for element using find_elements so there is no exception here
        elements = self.find.elements(page_element)
        return len(elements) > 0 and elements[0].is_enabled()

    @auto_log(__name__)
    def is_element_visible_and_contains_text(self, page_element, expected_text):
        """
        Check that an element is visible on the page and contains the expected text
        :param page_element: PageElement instance representing the element
        :param expected_text: the text to check against the element contents
        :return: boolean representing whether the element with expected text was found
        """
        visible_elements = self.find.visible_elements(page_element)

        for element in visible_elements:
            if expected_text in element.text:
                return True
        return False

    @auto_log(__name__)
    def get_number_of_elements(self, page_element):
        """
        Count the number of matching elements on the page
        :param page_element: PageElement instance representing the element
        :return: the number of elements found
        """
        elements = self.find.elements(page_element)
        return len(elements)

    @auto_log(__name__)
    def get_number_of_elements_with_background_url(self, page_element):
        """
        Count number of elements with CSS background e.g. check that a required image is displayed
        :param page_element: PageElement instance representing the element
        :return: the number of elements found with a background
        """
        element_counter = 0
        elements = self.find.elements(page_element)

        for element in elements:
            background_value = element.value_of_css_property("background")
            if "url" in background_value:
                element_counter += 1

        return element_counter

    @auto_log(__name__)
    def get_current_url(self):
        """
        :return: the url of the current page
        """
        return self.driver.current_url

    @auto_log(__name__)
    def get_table_row_count(self, page_element):
        """
        Finds the page element, and then finds the number of tr tags
        :param page_element: PageElement instance representing the element
        :return: int
        """
        return len(self.find.element(page_element).find_elements_by_tag_name('tr'))

    @auto_log(__name__)
    def get_attribute(self, page_element, attribute):
        """
         Get any attribute on an element
        :param page_element: PageElement instance representing the element
        :param attribute: the name of the attribute whose value you want e.g. 'type'
        :return: attribute as string
        """
        elements = self.find.elements(page_element)
        if not elements:
            return ""
        return elements[0].get_attribute(attribute)

    @auto_log(__name__)
    def get_text(self, page_element):
        """
        Return the text value of an element
        :param page_element: PageElement instance representing the element
        :return: String or None
        """
        return self.find.element(page_element).text

    @auto_log(__name__)
    def element_has_class(self, page_element, expected_class):
        """
        Find an element and check it has the correct class
        :param page_element: PageElement instance representing the element
        :param expected_class: the class to look for on the element - it can be one of several classes
        :return: boolean representing whether the class was found on the element
        """
        elements = self.find.elements(page_element)
        return len(elements) > 0 and elements[0].is_displayed() and expected_class in elements[0].get_attribute("class")

    @auto_log(__name__)
    def element_parent_has_class(self, page_element, expected_class):
        """
        Find an element and check its parent has the correct class
        :param page_element: PageElement instance representing the element
        :param expected_class: the class to look for on the parent - it can be one of several classes
        :return: boolean representing whether the class was found on the parent
        """
        elements = self.find.elements(page_element)
        if elements:
            parent = elements[0].find_element(By.XPATH, "./..")
            return parent.is_displayed() and expected_class in parent.get_attribute("class")
        return False

    @auto_log(__name__)
    def element_sibling_has_class(self, page_element, expected_class):
        """
        Find an element and check that any of its sibling elements has the correct class
        :param page_element: PageElement instance representing the element
        :param expected_class: the class to look for on the sibling - it can be one of several classes
        :return: boolean representing whether the class was found on the sibling
        """
        elements = self.find.elements(page_element)
        if elements:
            siblings_with_class = elements[0].find_elements(By.XPATH,
                                                            "./../*[contains(@class,'" + expected_class + "')]")
            number_of_siblings_with_class = len(siblings_with_class)
            return number_of_siblings_with_class > 0 and siblings_with_class[0].is_displayed()
        return False

    @auto_log(__name__)
    def element_contains_link(self, page_element, expected_url):
        """
        Check if an element contains a link to the given URL
        :param page_element: PageElement instance representing the element
        :param expected_url: the URL expected for the link
        :return: boolean representing whether the link was valid
        """
        elements = self.find.elements(page_element)
        if elements:
            return elements[0].is_displayed() and expected_url in elements[0].get_attribute("href")
        return False

    @auto_log(__name__)
    def get_all_cookies(self):
        """
        Gets all of the cookies from the current page
        :return: list of dictionaries corresponding to cookies visible in the current session
        """
        return self.driver.get_cookies()

    @auto_log(__name__)
    def get_value_from_cookie(self, name_to_find):
        """
        Return the value of a named cookie. The name of the cookie must be supplied and matched
        :param name_to_find: The name of the cookie to search for and return
        :return: The value of the named cookie or an empty string
        """
        all_cookies = self.get_all_cookies()

        for cookie in all_cookies:
            if cookie['name'] == name_to_find:
                return cookie['value']
        return ""
