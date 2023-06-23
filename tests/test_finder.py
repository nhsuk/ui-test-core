from unittest.mock import MagicMock
from hamcrest import assert_that, equal_to
from selenium.webdriver.common.by import By
from uitestcore.page_element import PageElement
from uitestcore.finder import Finder


class MockDriver:
    def __init__(self, elements_to_return=None):
        self.elements_to_return = elements_to_return

    def find_elements(self, by, value):
        if self.elements_to_return:
            return self.elements_to_return

        elif value:
            return [MockElement(f"elements found by '{by}' using value '{value}'")]

        else:
            return []


class MockElement:
    def __init__(self, info="", is_displayed_flag=True, aria_hidden="false"):
        self.info = info
        self.is_displayed_flag = is_displayed_flag
        self.aria_hidden = aria_hidden

    def is_displayed(self):
        return self.is_displayed_flag

    def get_attribute(self, _attr):
        return self.aria_hidden


def test_elements():
    driver = MockDriver()
    find = Finder(driver, None)

    elements = find.elements(PageElement(By.ID, "test-id"))

    assert_that(elements[0].info, equal_to("elements found by 'id' using value 'test-id'"),
                "An element list should be found")


def test_elements_logs_out_info():
    driver = MockDriver()
    logger = MagicMock()
    find = Finder(driver, logger)

    find.elements(PageElement(By.ID, "test-id"))

    assert_that(logger.info.call_count, equal_to(2), "Two messages should have been logged")
    logger.info.assert_any_call("Looking for elements matching PageElement id='test-id'")
    logger.info.assert_any_call("Found 1 element(s)")


def test_element():
    driver = MockDriver()
    find = Finder(driver, None)

    element = find.element(PageElement(By.CLASS_NAME, "test-class"))

    assert_that(element.info, equal_to("elements found by 'class name' using value 'test-class'"),
                "An element should be found")


def test_element_handles_index_error():
    driver = MockDriver()
    find = Finder(driver, None)

    element = find.element(PageElement(By.CLASS_NAME, ""))

    assert_that(element, equal_to(None), "None should be returned when no elements can be found")


def test_visible_elements_returns_correct_elements():
    elements_to_return = [
        MockElement("", True, "false"),
        MockElement("", False, "false"),
        MockElement("", True, "true"),
        MockElement("", False, "true")
    ]

    driver = MockDriver(elements_to_return)
    find = Finder(driver, None)

    visible_elements = find.visible_elements(PageElement(By.CLASS_NAME, "test-class"))

    assert_that(len(visible_elements), equal_to(1), "Incorrect number of elements returned")


def test_number_of_elements():
    elements_to_return = [MockElement(), MockElement(), MockElement()]
    driver = MockDriver(elements_to_return)
    find = Finder(driver, None)

    num_elements = find.number_of_elements(PageElement(By.CLASS_NAME, ""))

    assert_that(num_elements, equal_to(3), "Incorrect number of elements returned")
