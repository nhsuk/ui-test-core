from unittest import mock
from unittest.mock import MagicMock
from hamcrest import calling, raises, is_not
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from tests.unit_test_utils import *
from uitestcore.page_element import PageElement
from uitestcore.waiter import Waiter


class MockBrowserIsReady:
    def __call__(self, *args):
        return True


class MockBrowserIsNotReady:
    def __call__(self, *args):
        return False


class MockVisibilityOfElementLocated:
    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        if self.locator[1] == "visible_element":
            return True
        return False


class MockPresenceOfElementLocated(object):
    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        if self.locator[1] == "element_present":
            return True
        return False


class MockElementHasAttribute:
    def __init__(self, finder, page_element, attribute_name, expected_attribute_value):
        self.find = finder
        self.page_element = page_element
        self.attribute_name = attribute_name
        self.expected_attribute_value = expected_attribute_value

    def __call__(self, *args):
        if self.expected_attribute_value == "test_value_exists":
            return True
        return False


class MockAlertIsPresent:
    def __call__(self, driver):
        return True


class MockAlertIsNotPresent:
    def __call__(self, driver):
        return False


@mock.patch("time.sleep")
@mock.patch("uitestcore.custom_expected_conditions.BrowserIsReady", side_effect=MockBrowserIsReady)
def test_for_page_to_load_ready(mock_browser_is_ready, mock_sleep):
    wait = Waiter("driver", "finder", 0, MagicMock(name="logger"))

    assert_that(calling(wait.for_page_to_load), is_not(raises(TimeoutException)),
                "Waiting for the page to load when the browser is ready should not raise an exception")

    check_mocked_functions_called(mock_sleep, mock_browser_is_ready)


@mock.patch("time.sleep")
@mock.patch("uitestcore.custom_expected_conditions.BrowserIsReady", side_effect=MockBrowserIsNotReady)
def test_for_page_to_load_not_ready(mock_browser_is_ready, mock_sleep):
    wait = Waiter("driver", "finder", 0, MagicMock(name="logger"))

    assert_that(calling(wait.for_page_to_load), raises(TimeoutException),
                "Waiting for the page to load when the browser is not ready should raise an exception")

    check_mocked_functions_called(mock_sleep, mock_browser_is_ready)


@mock.patch("uitestcore.waiter.visibility_of_element_located", side_effect=MockVisibilityOfElementLocated)
def test_for_element_to_be_visible_is_visible(mock_visibility_of_element_located):
    wait = Waiter("driver", "finder", 0, MagicMock(name="logger"))
    page_element = PageElement(By.ID, "visible_element")

    assert_that(calling(wait.for_element_to_be_visible).with_args(page_element), is_not(raises(TimeoutException)),
                "Waiting for an element to be visible when the element is displayed should not raise an exception")

    check_mocked_functions_called(mock_visibility_of_element_located)


@mock.patch("time.sleep")
@mock.patch("uitestcore.waiter.visibility_of_element_located", side_effect=MockVisibilityOfElementLocated)
def test_for_element_to_be_visible_is_not_visible(mock_visibility_of_element_located, mock_sleep):
    wait = Waiter("driver", "finder", 0, MagicMock(name="logger"))
    page_element = PageElement(By.ID, "not_visible_element")

    assert_that(calling(wait.for_element_to_be_visible).with_args(page_element), raises(TimeoutException),
                "Waiting for an element to be visible when the element is not displayed should raise an exception")

    check_mocked_functions_called(mock_sleep, mock_visibility_of_element_located)


@mock.patch("uitestcore.waiter.presence_of_element_located", side_effect=MockPresenceOfElementLocated)
def test_for_element_to_be_present_is_present(mock_presence_of_element_located):
    wait = Waiter("driver", "finder", 0, MagicMock(name="logger"))
    page_element = PageElement(By.ID, "element_present")

    assert_that(calling(wait.for_element_to_be_present).with_args(page_element), is_not(raises(TimeoutException)),
                "Waiting for an element to be present when the element is present should not raise an exception")

    check_mocked_functions_called(mock_presence_of_element_located)


@mock.patch("time.sleep")
@mock.patch("uitestcore.waiter.presence_of_element_located", side_effect=MockPresenceOfElementLocated)
def test_for_element_to_be_present_is_not_present(mock_presence_of_element_located, mock_sleep):
    wait = Waiter("driver", "finder", 0, MagicMock(name="logger"))
    page_element = PageElement(By.ID, "element_not_present")

    assert_that(calling(wait.for_element_to_be_present).with_args(page_element), raises(TimeoutException),
                "Waiting for an element to be present when the element is not present should raise an exception")

    check_mocked_functions_called(mock_sleep, mock_presence_of_element_located)


@mock.patch("uitestcore.waiter.ElementHasAttribute", side_effect=MockElementHasAttribute)
def test_for_element_to_have_attribute_exists(mock_element_has_attribute):
    test_waiter = Waiter("driver", "finder", 0, MagicMock(name="logger"))
    page_element = PageElement(By.ID, "id_exists")

    assert_that(calling(test_waiter.for_element_to_have_attribute).with_args(
        page_element, "test_attribute", "test_value_exists"), is_not(raises(TimeoutException)),
        "Checking for an element with an existing attribute should not raise an exception")

    check_mocked_functions_called(mock_element_has_attribute)


@mock.patch("time.sleep")
@mock.patch("uitestcore.waiter.ElementHasAttribute", side_effect=MockElementHasAttribute)
def test_for_element_to_have_attribute_not_exists(mock_element_has_attribute, mock_sleep):
    test_waiter = Waiter("driver", "finder", 0, MagicMock(name="logger"))
    page_element = PageElement(By.ID, "id_exists")

    assert_that(calling(test_waiter.for_element_to_have_attribute).with_args(
        page_element, "test_attribute", "test_not_exists"), raises(TimeoutException),
        "Checking for an element with an non-existent attribute should raise an exception")

    check_mocked_functions_called(mock_sleep, mock_element_has_attribute)


@mock.patch("uitestcore.waiter.alert_is_present", side_effect=MockAlertIsPresent)
def test_for_alert_to_be_present_is_present(mock_alert_is_present):
    wait = Waiter("driver", "finder", 0, MagicMock(name="logger"))

    assert_that(calling(wait.for_alert_to_be_present), is_not(raises(TimeoutException)),
                "Waiting for an alert to be present when the alert is present should not raise an exception")

    check_mocked_functions_called(mock_alert_is_present)


@mock.patch("time.sleep")
@mock.patch("uitestcore.waiter.alert_is_present", side_effect=MockAlertIsNotPresent)
def test_for_alert_to_be_present_is_not_present(mock_alert_is_present, mock_sleep):
    wait = Waiter("driver", "finder", 0, MagicMock(name="logger"))

    assert_that(calling(wait.for_alert_to_be_present), raises(TimeoutException),
                "Waiting for an alert to be present when the alert is not present should raise an exception")

    check_mocked_functions_called(mock_sleep, mock_alert_is_present)
