"""
This represents an element on the page with information which can be used to locate it
"""
from enum import Enum


class PageElement:

    def __init__(self, locator_type, locator_value, element_type=""):
        """
        Default constructor to create a PageElement
        :param locator_type: the type of Selenium locator e.g. By.ID
        :param locator_value: the locator string e.g. the ID of the element
        :param element_type: additional information about an element e.g. "text" represents a text field
        """
        self.locator_type = locator_type
        self.locator_value = locator_value
        self.field_type = element_type


class FieldTypes(Enum):
    text_box = "text"
    radio_button = "radio"
    check_box = "check"
