from hamcrest import assert_that, equal_to
from ui_automation_core.custom_expected_conditions import ElementHasAttribute


class MockFinder:
    @staticmethod
    def elements(page_element):
        if page_element:
            return [MockElement("valid_attribute")]
        return None


class MockElement:
    def __init__(self, attribute):
        self.attribute = attribute

    def get_attribute(self, *_args):
        return self.attribute


def test_element_has_attribute():
    inst = ElementHasAttribute(MockFinder(), "page_element", "test_name", "valid_attribute")

    result = inst("driver")

    assert_that(result, equal_to(True), "The attribute should have been found")


def test_element_has_attribute_no_element():
    inst = ElementHasAttribute(MockFinder(), None, "test_name", "valid_attribute")

    result = inst("driver")

    assert_that(result, equal_to(False), "The attribute should not have been found")


def test_element_has_attribute_not_matching():
    inst = ElementHasAttribute(MockFinder(), "page_element", "test_name", "invalid_attribute")

    result = inst("driver")

    assert_that(result, equal_to(False), "The attribute should not have been found")
