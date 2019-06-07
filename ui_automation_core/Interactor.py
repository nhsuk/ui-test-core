from selenium.webdriver.remote.webelement import WebElement

from ui_automation_core.Finder import Finder
from ui_automation_core.Interrogator import Interrogator
from ui_automation_core.Waiter import Waiter


class Interactor(object):
    """
    Interact with elements without returning a value, such as clicking, sending keys, or performing Actions
    If you're expecting a return value, such as the Element or True/False look in the Finder or Interrogator
    """

    def __init__(self, driver, logger, finder: Finder, interrogator: Interrogator, waiter: Waiter):
        """
        Default constructor which passes the control of webDriver to the current page
        :param driver: the Selenium web driver
        :param logger: logger object used to save information to a log file
        :param finder: Finder
        :param interrogator: Interrogator
        :param waiter: Waiter
        """
        self.driver = driver
        self.logger = logger
        self.find = finder
        self.interrogate = interrogator
        self.wait = waiter

    def click_element(self, page_element):
        """
        Finds and clicks on an element on the page
        :param page_element: PageElement instance representing the element
        """
        self.find.element(page_element).click()

    def execute_click_with_java_script(self, page_element):
        """
        execute the click on the element using javascript.
        :param page_element: the element to click
        :return: element clicked
        """
        element: WebElement = self.find.element(page_element)
        return self.driver.execute_script("arguments[0].click();", element)

    def enter_text(self, page_element, field_input, clear_first=True):
        """
        Writes the given text to an element on the page - only to be used with editable text fields
        :param page_element: PageElement instance representing the element
        :param field_input: the text to write to the element
        :param clear_first: boolean representing whether or not to clear the field before editing (default True)
        """
        element: WebElement = self.find.element(page_element)
        if clear_first:
            element.clear()
        element.send_keys(field_input)

    def send_keys(self, page_element, key):
        """
        Send a Key action to an element
        :param page_element: PageElement instance representing the element
        :param key: the key to press e.g. Keys.ARROW_DOWN
        """
        self.enter_text(page_element, key, False)

    def append_and_open_url(self, additional_url):
        """
        Adds additional data to URL e.g. query string
        :param additional_url: the string to append the URL
        """
        url = self.interrogate.get_current_url()
        url += additional_url
        self.open_url(url)

    def open_url(self, url):
        """
        open any given url
        :param url:
        :return: None
        """

        self.driver.get(url)
        self.wait.for_page_to_load()
        self.logger.log(20, f"PASS: Navigated to the URL - {url}")

    def scroll_into_view(self, page_element):
        """
        scroll an element into view using javascript
        :param page_element:
        :return:
        """
        self.logger.log(20, f"Scrolling to {page_element.locator_value}")
        element: WebElement = self.find.element(page_element)
        self.driver.execute_script("arguments[0].scrollIntoView();", element)

    def switch_window(self):
        """
        Switch the control to a new page that opens up
        :return:
        """
        new_window = self.driver.window_handles[1]
        self.logger.log(20, "Switching to new window")
        self.driver.switch_to_window(new_window)
        self.logger.log(20, "Switched to new window")
