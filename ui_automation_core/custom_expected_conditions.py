"""
Create custom expected conditions in here
See these links for more details:
    https://selenium-python.readthedocs.io/api.html#module-selenium.webdriver.support.expected_conditions
    http://www.teachmeselenium.com/2018/04/07/python-selenium-waits-writing-own-custom-wait-conditions/
"""


class BrowserIsReady:
    """
    This condition uses JavaScript to check the documents ready state is 'complete'
    Has an initial wait to avoid false positive, gives browser a chance to refresh
    """

    def __init__(self):
        pass

    def __call__(self, driver):
        return driver.execute_script("return document.readyState") == "complete"


class ElementHasAttribute:
    """
    This condition checks if an element has a specific attribute e.g. to check if an animation has finished
    """
    def __init__(self, finder, page_element, attribute_name, expected_attribute_value):
        self.find = finder
        self.page_element = page_element
        self.attribute_name = attribute_name
        self.expected_attribute_value = expected_attribute_value

    def __call__(self, driver):
        elements = self.find.elements(self.page_element)
        if elements:
            attribute_value = elements[0].get_attribute(self.attribute_name)
            return attribute_value == self.expected_attribute_value
        return False
