from unittest import mock
from hamcrest import assert_that, calling, raises, is_not
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from tests.unit.unit_test_utils import check_mocked_functions_called
from ui_automation_core.page_element import PageElement
from ui_automation_core.waiter import Waiter


class MockElementHasAttribute:
    def __init__(self, finder, page_element, attribute_name, expected_attribute_value):
        self.find = finder
        self.page_element = page_element
        self.attribute_name = attribute_name
        self.expected_attribute_value = expected_attribute_value

    def __call__(self, *args):
        if self.expected_attribute_value is "test_value_exists":
            return True
        return False


@mock.patch("ui_automation_core.waiter.ElementHasAttribute", side_effect=MockElementHasAttribute)
def test_for_element_to_have_attribute_exists(mock_element_has_attribute):
    test_waiter = Waiter("driver", "logger", "finder", 0)

    assert_that(calling(test_waiter.for_element_to_have_attribute).with_args(
        PageElement(By.ID, "id_exists"), "test_attribute", "test_value_exists"), is_not(raises(TimeoutException)),
        "Checking for an element with an non-existent attribute should raise an exception")

    check_mocked_functions_called(mock_element_has_attribute)


@mock.patch("ui_automation_core.waiter.ElementHasAttribute", side_effect=MockElementHasAttribute)
def test_for_element_to_have_attribute_not_exists(mock_element_has_attribute):
    test_waiter = Waiter("driver", "logger", "finder", 0)

    assert_that(calling(test_waiter.for_element_to_have_attribute).with_args(
        PageElement(By.ID, "id_exists"), "test_attribute", "test_not_exists"), raises(TimeoutException),
        "Checking for an element with an non-existent attribute should raise an exception")

    check_mocked_functions_called(mock_element_has_attribute)
