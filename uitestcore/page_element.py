from enum import Enum


class PageElement:
    """
    This represents an element on the page with information which can be used to locate it
    """

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

    def __add__(self, value):
        """
        Overrides the "+" operator for this class to allow appending of locator value
        :param value: the string to append to the locator value
        :return: a new PageElement instance with the altered locator value
        """
        return PageElement(self.locator_type, self.locator_value + value)

    def __str__(self):
        """
        Provides a string representation of the PageElement
        :return: String
        """
        return f"PageElement {self.locator_type}='{self.locator_value}'"


class FieldTypes(Enum):
    text_box = "text"
    radio_button = "radio"
    check_box = "check"
