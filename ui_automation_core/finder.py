class Finder:
    """
    Selenium based find methods
    Use this class to first find an element(s) before interacting with it
    """

    def __init__(self, driver, logger):
        """
        Default constructor which passes the control of webDriver to the current page
        :param driver: the Selenium web driver
        :param logger: logger object used to save information to a log file
        """
        self.driver = driver
        self.logger = logger

    def elements(self, page_element):
        """
        Find the elements matching the given page element object
        :param page_element: PageElement instance representing the element
        :return: list of matching WebElements
        """
        return self.driver.find_elements(page_element.locator_type, page_element.locator_value)

    def visible_elements(self, page_element):
        """
        Find the elements matching the given page element object, only returning the visible ones
        :param page_element: PageElement instance representing the element
        :return: list of matching WebElements which are visible
        """
        elements = self.driver.find_elements(page_element.locator_type, page_element.locator_value)
        visible_elements = []

        for element in elements:
            if element.is_displayed() and not element.get_attribute("aria-hidden") == "true":
                visible_elements.append(element)

        return visible_elements

    def element(self, page_element):
        """
        Find a single element matching the given page element object
        If no element found, will return None
        :param page_element: PageElement instance representing the element
        :return: single WebElement or None
        """
        try:
            return self.elements(page_element)[0]
        except IndexError:
            return None

    def number_of_elements(self, page_element):
        """
        Count the number of matching elements on the page
        :param page_element: PageElement instance representing the element
        :return: the number of elements found
        """
        elements = self.elements(page_element)
        return len(elements)
