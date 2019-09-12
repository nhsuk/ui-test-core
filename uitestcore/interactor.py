from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select


class Interactor:
    """
    Interact with elements without returning a value, such as clicking, sending keys, or performing Actions
    If you're expecting a return value, such as the Element or True/False look in the Finder or Interrogator
    """

    def __init__(self, driver, logger, finder, interrogator, waiter):
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

    def select_by_visible_text(self, page_element, visible_text_to_select):
        """
        Select all options that display text matching the visible_text_to_select argument.
        :param page_element: the element to select
        :param visible_text_to_select: The visible text to select in the drop down
        """
        element: WebElement = self.find.element(page_element)
        Select(element).select_by_visible_text(visible_text_to_select)

    def select_by_value(self, page_element, value):
        """
        Select all options that have a value matching the argument
        :param page_element: the element to select
        :param value:The value to match against
        """
        element: WebElement = self.find.element(page_element)
        Select(element).select_by_value(value)

    def select_by_index(self, page_element, index):
        """
        Select the option at the given index. This is done by examining the "index" attribute of an
        element
        :param page_element:the element to select
        :param index:The option at this index will be selected
        """
        element: WebElement = self.find.element(page_element)
        Select(element).select_by_index(index)

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

    def open_url(self, url):
        """
        open any given url
        :param url:
        :return: None
        """
        self.driver.get(url)
        self.wait.for_page_to_load()
        self.logger.log(20, f"Navigated to the URL - {url}")

    def append_and_open_url(self, additional_url):
        """
        Adds additional data to URL e.g. query string
        :param additional_url: the string to append the URL
        """
        url = self.interrogate.get_current_url()
        url += additional_url
        self.open_url(url)

    def close_current_window(self):
        """
        Close the current window/tab
        Then will switch to a remaining window if available
        :return: None
        """
        self.driver.close()
        if len(self.driver.window_handles) > 1:
            self.driver.switch_to_window(self.driver.window_handles[len(self.driver.window_handles) - 1])

    def scroll_into_view(self, page_element):
        """
        scroll an element into view using javascript
        :param page_element:
        :return:
        """
        self.logger.log(20, f"Scrolling to {page_element.locator_value}")
        element: WebElement = self.find.element(page_element)
        self.driver.execute_script("arguments[0].scrollIntoView();", element)

    def switch_to_next_window(self):
        """
        Switch the control to a new page that opens up
        :return: None
        """
        new_window = self.driver.window_handles[len(self.driver.window_handles) - 1]
        self.logger.log(20, "Switching to next window")
        self.driver.switch_to_window(new_window)
        self.logger.log(20, "Switched to next window")

    def switch_to_original_window(self):
        """
        Switch the control to the original window with a window_handle index of 0
        :return:None
        """
        old_window = self.driver.window_handles[0]
        self.driver.switch_to_window(old_window)

    def switch_to_frame(self, page_element):
        """
        Switch the control into an iframe
        :param page_element: iframe
        :return: None
        """
        self.driver.switch_to.frame(self.find.element(page_element))

    def accept_alert(self):
        """
        Accept an alert using built in selenium
        :return:
        """
        self.driver.switch_to.alert.accept()

    def dismiss_alert(self):
        """
        Dismisses an alert using built in selenium
        :return: None
        """
        self.driver.switch_to.alert.dismiss()

    def enter_text_into_alert(self, text):
        """
        Sends keys to the alert using Selenium
        :param text:
        :return: None
        """
        self.driver.switch_to.alert.send_keys(text)

    def switch_to_default_content(self):
        """
        Switch focus to the default frame
        """
        self.driver.switch_to.default_content()

    def clear_cookie_and_refresh_page(self, cookie_name):
        """
        Delete a single cookie and refresh the related page. The name of the cookie must be supplied and matched.
        :param cookie_name: The name of the cookie to search for and to delete
        """
        self.driver.delete_cookie(cookie_name)
        self.driver.refresh()
