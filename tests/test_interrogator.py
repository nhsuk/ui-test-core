from unittest import mock
from unittest.mock import MagicMock
import requests
from hamcrest import assert_that, equal_to, is_
from selenium.webdriver.common.by import By
from tests.unit_test_utils import check_mocked_functions_called
from uitestcore.finder import Finder
from uitestcore.interrogator import Interrogator
from uitestcore.page_element import PageElement

default_page_element = PageElement(By.ID, "test-id")


class MockDriver(object):

    @staticmethod
    def get_cookies():
        mock_cookies = [{"name": "cookie-consent", "value": "%7B%22preferences%22%3Atrue%7D"},
                        {"name": "s_getNewRepeat", "value": "1564127000350-Repeat"}]
        return mock_cookies


class MockFinder(object):
    def __init__(self, list_of_elements_to_return=None):
        self.list_of_elements_to_return = list_of_elements_to_return

    def elements(self, _page_element):
        return self.list_of_elements_to_return


class MockElement(object):
    def __init__(self, visibility, aria_hidden=False, parent_visible=False):
        self.visibility = visibility
        self.is_displayed_called = 0
        self.aria_hidden = aria_hidden
        self.parent_visible = parent_visible

    def is_displayed(self):
        self.is_displayed_called += 1
        return self.visibility

    def get_attribute(self, attr):
        if attr == "aria-hidden":
            if self.aria_hidden:
                return "true"
            return "false"

        if attr == "class":
            return "test_class"

        if attr == "href":
            return "test_url"

        return None

    def find_element(self, by, value):
        if by == By.XPATH and value == "./..":
            return MockElement(self.parent_visible)
        return None

    def find_elements(self, by, value):
        if by == By.XPATH and value == "./../*[contains(@class,'test_class')]":
            return [MockElement(self.visibility)]
        return []


class MockWaiter(object):
    def __init__(self):
        self.for_element_to_be_visible_called = 0

    def for_element_to_be_visible(self, _page_element):
        self.for_element_to_be_visible_called += 1


@mock.patch("uitestcore.interrogator.Interrogator.get_table_row_count", side_effect=lambda *args: len(args[0]))
def test_table_is_not_empty(mock_get_table_row_count):
    mock_finder = MagicMock()
    mock_finder.element.return_value = ["element_1", "element_2", "element_3", "element_4", "element_5"]
    interrogate = Interrogator(None, mock_finder, MagicMock(name="logger"))

    result = interrogate.table_is_not_empty(default_page_element)

    check_mocked_functions_called(mock_get_table_row_count)
    assert_that(result, equal_to(True), "Empty table should have been handled")


def test_table_is_not_empty_handles_table_body_not_found():
    mock_finder = MagicMock()
    mock_finder.element.return_value = None
    interrogate = Interrogator(None, mock_finder, MagicMock(name="logger"))

    result = interrogate.table_is_not_empty(default_page_element)

    assert_that(result, equal_to(False), "Empty table body should have been handled")


@mock.patch("uitestcore.interrogator.Interrogator.get_table_row_count", side_effect=lambda *args: len(args[0]))
def test_table_is_not_empty_handles_row_count_below_min_length(mock_get_table_row_count):
    mock_finder = MagicMock()
    mock_finder.element.return_value = ["element_1", "element_2", "element_3"]
    interrogate = Interrogator(None, mock_finder, MagicMock(name="logger"))

    result = interrogate.table_is_not_empty(default_page_element)

    check_mocked_functions_called(mock_get_table_row_count)
    assert_that(result, equal_to(False), "Row count below min value should have been handled")


def test_list_is_not_empty():
    mock_finder = MagicMock()

    mock_element = MagicMock()
    mock_element.find_elements.return_value = ["element_1", "element_2"]
    mock_finder.element.return_value = mock_element

    interrogate = Interrogator(None, mock_finder, MagicMock(name="logger"))

    result = interrogate.list_is_not_empty(default_page_element)

    mock_element.find_elements.assert_called_once_with(By.TAG_NAME, 'li')
    assert_that(result, equal_to(True), "List should not be empty")


def test_list_is_not_empty_min_value():
    mock_finder = MagicMock()

    mock_element = MagicMock()
    mock_element.find_elements.return_value = ["element_1"]
    mock_finder.element.return_value = mock_element

    interrogate = Interrogator(None, mock_finder, MagicMock(name="logger"))

    result = interrogate.list_is_not_empty(default_page_element)

    mock_element.find_elements.assert_called_once_with(By.TAG_NAME, 'li')
    assert_that(result, equal_to(False), "List should be considered empty below minimum length")


def test_list_is_not_empty_with_empty_list():
    mock_finder = MagicMock()

    mock_element = MagicMock()
    mock_element.find_elements.return_value = []
    mock_finder.element.return_value = mock_element

    interrogate = Interrogator(None, mock_finder, MagicMock(name="logger"))

    result = interrogate.list_is_not_empty(default_page_element)

    mock_element.find_elements.assert_called_once_with(By.TAG_NAME, 'li')
    assert_that(result, equal_to(False), "List is empty")


def test_is_image_visible_by_checking_src_success():
    mock_driver = MagicMock()
    mock_driver.execute_script.return_value = "test/url"
    interrogate = Interrogator(mock_driver, None, None)

    mock_get_attribute = MagicMock(return_value="/source")
    interrogate.get_attribute = mock_get_attribute

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_get = MagicMock(return_value=mock_response)
    requests.get = mock_get

    result = interrogate.is_image_visible_by_checking_src(default_page_element)

    mock_get_attribute.assert_called_once_with(default_page_element, "src")
    mock_get.assert_called_once_with("test/url/source")
    mock_driver.execute_script.assert_called_once_with("return window.location.origin")
    assert_that(result, equal_to(True), "The image should have been found")


def test_is_image_visible_by_checking_src_failure():
    mock_driver = MagicMock()
    mock_driver.execute_script.return_value = "test/url"
    interrogate = Interrogator(mock_driver, None, None)

    mock_get_attribute = MagicMock(return_value="/source")
    interrogate.get_attribute = mock_get_attribute

    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_get = MagicMock(return_value=mock_response)
    requests.get = mock_get

    result = interrogate.is_image_visible_by_checking_src(default_page_element)

    mock_get_attribute.assert_called_once_with(default_page_element, "src")
    mock_get.assert_called_once_with("test/url/source")
    mock_driver.execute_script.assert_called_once_with("return window.location.origin")
    assert_that(result, equal_to(False), "The image should not have been found")


def test_is_image_visible_by_checking_src_no_src_url():
    interrogate = Interrogator(None, None, None)
    mock_get_attribute = MagicMock(return_value=None)
    interrogate.get_attribute = mock_get_attribute

    result = interrogate.is_image_visible_by_checking_src(default_page_element)

    mock_get_attribute.assert_called_once_with(default_page_element, "src")
    assert_that(result, equal_to(True), "The image should be considered visible if it has no source URL")


def test_is_image_visible_by_javascript():
    mock_element = MagicMock()
    mock_element.tag_name = "svg"
    mock_element.get_attribute.return_value = "test-image"
    mock_finder = MagicMock()
    mock_finder.element.return_value = mock_element
    mock_driver = MagicMock()
    mock_driver.execute_script.return_value = "result of execute_script"
    interrogate = Interrogator(mock_driver, mock_finder, None)

    result = interrogate.is_image_visible_by_javascript(default_page_element)

    expected_script = "return ((arguments[0].complete)||(arguments[0].naturalWidth !='undefined' && " \
                      "arguments[0].naturalWidth > 0))"
    mock_driver.execute_script.assert_called_once_with(expected_script, mock_element)
    assert_that(result, equal_to("result of execute_script"), "Element should have been checked with JavaScript")


def test_is_image_visible_by_javascript_svg_no_src():
    mock_element = MagicMock()
    mock_element.tag_name = "svg"
    mock_element.get_attribute.return_value = None
    mock_element.is_displayed.return_value = "result of is_displayed"
    mock_finder = MagicMock()
    mock_finder.element.return_value = mock_element
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.is_image_visible_by_javascript(default_page_element)
    mock_element.is_displayed.assert_called_once()
    assert_that(result, equal_to("result of is_displayed"), "Element should have been checked with is_displayed")


def test_is_element_visible():
    mock_driver = MagicMock()
    elements = [
        MockElement("true")
    ]
    finder = MockFinder(list_of_elements_to_return=elements)
    wait_time = 10
    test_interrogator = Interrogator(mock_driver, finder, wait_time, "logger")

    test_interrogator.is_element_visible(PageElement(By.ID, "some_id"))
    assert_that(mock_driver.implicitly_wait.call_count, equal_to(2), "Expected two calls to implicitly_wait")
    assert_that(elements[0].is_displayed_called, is_(1), "is_displayed was not called the expected amount of times")


def test_is_element_visible_with_wait():
    mock_driver = MagicMock()
    elements = [
        MockElement("true")
    ]
    finder = MockFinder(list_of_elements_to_return=elements)
    wait_time = 10
    test_interrogator = Interrogator(mock_driver, finder, wait_time, "logger")
    wait = MockWaiter()

    test_interrogator.is_element_visible(PageElement(By.ID, "some_id"), wait)
    assert_that(mock_driver.implicitly_wait.call_count, equal_to(0), "Expected zero calls to implicitly_wait")
    assert_that(wait.for_element_to_be_visible_called, is_(1),
                "for_element_to_be_visible was not called the expected amount of times")
    assert_that(elements[0].is_displayed_called, is_(1), "is_displayed was not called the expected amount of times")


def test_are_elements_visible_none_found():
    mock_finder = MagicMock()
    mock_finder.elements.return_value = []
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.are_elements_visible(default_page_element)

    assert_that(result, equal_to(False), "No elements should have been found")


def test_are_elements_visible_all_displayed():
    elements = [MockElement(True, False), MockElement(True, False), MockElement(True, False)]
    mock_finder = MagicMock()
    mock_finder.elements.return_value = elements
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.are_elements_visible(default_page_element)

    assert_that(result, equal_to(True), "All elements should be visible")


def test_are_elements_visible_one_not_displayed():
    elements = [MockElement(True, False), MockElement(True, False), MockElement(False, False)]
    mock_finder = MagicMock()
    mock_finder.elements.return_value = elements
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.are_elements_visible(default_page_element)

    assert_that(result, equal_to(False), "One element should not be visible")


def test_are_elements_visible_one_aria_hidden():
    elements = [MockElement(True, False), MockElement(True, False), MockElement(True, True)]
    mock_finder = MagicMock()
    mock_finder.elements.return_value = elements
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.are_elements_visible(default_page_element)

    assert_that(result, equal_to(False), "One element should be aria hidden")


def test_is_radio_button_visible():
    mock_is_element_or_parent_visible = MagicMock(return_value="result of is_displayed")
    interrogate = Interrogator(None, None, None)
    interrogate.is_element_or_parent_visible = mock_is_element_or_parent_visible

    result = interrogate.is_radio_button_visible(default_page_element)

    mock_is_element_or_parent_visible.assert_called_once_with(default_page_element)
    assert_that(result, equal_to("result of is_displayed"), "Result not returned correctly")


def test_is_checkbox_visible():
    mock_is_element_or_parent_visible = MagicMock(return_value="result of is_displayed")
    interrogate = Interrogator(None, None, None)
    interrogate.is_element_or_parent_visible = mock_is_element_or_parent_visible

    result = interrogate.is_checkbox_visible(default_page_element)

    mock_is_element_or_parent_visible.assert_called_once_with(default_page_element)
    assert_that(result, equal_to("result of is_displayed"), "Result not returned correctly")


def test_is_checkbox_selected():
    mock_element = MagicMock()
    mock_element.is_selected.return_value = "result of is_selected"
    mock_finder = MagicMock()
    mock_finder.element.return_value = mock_element
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.is_checkbox_selected(default_page_element)

    assert_that(result, equal_to("result of is_selected"), "Selection of checkbox should be inspected")


def test_is_element_or_parent_visible_element_visible():
    mock_finder = MagicMock()
    mock_finder.elements.return_value = [MockElement(True)]
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.is_element_or_parent_visible(default_page_element)

    assert_that(result, equal_to(True), "Element should be visible")


def test_is_element_or_parent_visible_element_not_visible():
    mock_finder = MagicMock()
    mock_finder.elements.return_value = [MockElement(False, False, False)]
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.is_element_or_parent_visible(default_page_element)

    assert_that(result, equal_to(False), "Element should not be visible")


def test_is_element_or_parent_visible_parent_visible():
    mock_finder = MagicMock()
    mock_finder.elements.return_value = [MockElement(False, False, True)]
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.is_element_or_parent_visible(default_page_element)

    assert_that(result, equal_to(True), "Element's parent should be visible")


def test_is_element_or_parent_visible_no_elements_found():
    mock_finder = MagicMock()
    mock_finder.elements.return_value = []
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.is_element_or_parent_visible(default_page_element)

    assert_that(result, equal_to(False), "No elements should have been found")


def test_is_element_selected():
    mock_element = MagicMock()
    mock_element.is_selected.return_value = True
    mock_finder = MagicMock()
    mock_finder.elements.return_value = [mock_element]
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.is_element_selected(default_page_element)

    assert_that(result, equal_to(True), "Element should be selected")


def test_is_element_selected_no_element_found():
    mock_finder = MagicMock()
    mock_finder.elements.return_value = []
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.is_element_selected(default_page_element)

    assert_that(result, equal_to(False), "Element should not be found")


def test_is_element_selected_element_not_selected():
    mock_element = MagicMock()
    mock_element.is_selected.return_value = False
    mock_finder = MagicMock()
    mock_finder.elements.return_value = [mock_element]
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.is_element_selected(default_page_element)

    assert_that(result, equal_to(False), "Element should not be selected")


def test_is_element_enabled():
    mock_element = MagicMock()
    mock_element.is_enabled.return_value = True
    mock_finder = MagicMock()
    mock_finder.elements.return_value = [mock_element]
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.is_element_enabled(default_page_element)

    assert_that(result, equal_to(True), "Element should not be enabled")


def test_is_element_enabled_no_element_found():
    mock_finder = MagicMock()
    mock_finder.elements.return_value = []
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.is_element_enabled(default_page_element)

    assert_that(result, equal_to(False), "Element should not be found")


def test_is_element_enabled_element_not_enabled():
    mock_element = MagicMock()
    mock_element.is_enabled.return_value = False
    mock_finder = MagicMock()
    mock_finder.elements.return_value = [mock_element]
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.is_element_enabled(default_page_element)

    assert_that(result, equal_to(False), "Element should not be enabled")


def test_is_element_visible_and_contains_text():
    mock_element_1 = MagicMock()
    mock_element_2 = MagicMock()
    mock_element_1.text = "1234"
    mock_element_2.text = "abcd"
    mock_finder = MagicMock()
    mock_finder.visible_elements.return_value = [mock_element_1, mock_element_2]
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.is_element_visible_and_contains_text(default_page_element, "abcd")

    assert_that(result, equal_to(True), "Expected text found")


def test_is_element_visible_and_contains_text_no_elements_found():
    mock_finder = MagicMock()
    mock_finder.visible_elements.return_value = []
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.is_element_visible_and_contains_text(default_page_element, "test-text")

    assert_that(result, equal_to(False), "No elements should be found")


def test_is_element_visible_and_contains_text_expected_text_not_found():
    mock_element_1 = MagicMock()
    mock_element_2 = MagicMock()
    mock_element_1.text = "1234"
    mock_element_2.text = "abcd"
    mock_finder = MagicMock()
    mock_finder.visible_elements.return_value = [mock_element_1, mock_element_2]
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.is_element_visible_and_contains_text(default_page_element, "test-text")

    assert_that(result, equal_to(False), "Expected text should not be found")


def test_get_number_of_elements():
    mock_finder = MagicMock()
    mock_finder.elements.return_value = ["element_1", "element_2", "element_3"]
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.get_number_of_elements(default_page_element)

    assert_that(result, equal_to(3), "Incorrect number of elements found")


def test_get_number_of_elements_with_background_url():
    mock_element_1 = MagicMock()
    mock_element_2 = MagicMock()
    mock_element_1.value_of_css_property.return_value = "1234"
    mock_element_2.value_of_css_property.return_value = "test-url"
    mock_finder = MagicMock()
    mock_finder.elements.return_value = [mock_element_1, mock_element_2]
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.get_number_of_elements_with_background_url(default_page_element)

    assert_that(result, equal_to(1), "One element with a background should have been found")


def test_get_number_of_elements_with_background_url_no_elements_found():
    mock_finder = MagicMock()
    mock_finder.elements.return_value = []
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.get_number_of_elements_with_background_url(default_page_element)

    assert_that(result, equal_to(0), "No elements should have been found")


def test_get_number_of_elements_with_background_url_no_backgrounds():
    mock_element_1 = MagicMock()
    mock_element_2 = MagicMock()
    mock_element_1.value_of_css_property.return_value = "1234"
    mock_element_2.value_of_css_property.return_value = "abcd"
    mock_finder = MagicMock()
    mock_finder.elements.return_value = [mock_element_1, mock_element_2]
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.get_number_of_elements_with_background_url(default_page_element)

    assert_that(result, equal_to(0), "No elements should have been found")


def test_get_current_url():
    mock_driver = MagicMock()
    mock_driver.current_url = "test/url"
    interrogate = Interrogator(mock_driver, None, None)

    result = interrogate.get_current_url()

    assert_that(result, equal_to("test/url"), "The correct URL was not found")


def test_get_table_row_count():
    mock_element = MagicMock()
    mock_element.find_elements.return_value = ["element_1", "element_2"]
    mock_finder = MagicMock()
    mock_finder.element.return_value = mock_element
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.get_table_row_count(default_page_element)

    mock_element.find_elements.assert_called_once_with(By.TAG_NAME, 'tr')
    assert_that(result, equal_to(2), "Incorrect number of rows found")


def test_get_attribute():
    mock_element = MagicMock()
    mock_element.get_attribute.return_value = "test_attr_val"
    mock_finder = MagicMock()
    mock_finder.elements.return_value = [mock_element]
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.get_attribute(default_page_element, "test_attr")

    assert_that(result, equal_to("test_attr_val"), "Element attribute not returned correctly")


def test_get_attribute_no_element_found():
    mock_finder = MagicMock()
    mock_finder.elements.return_value = []
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.get_attribute(default_page_element, "test_attr")

    assert_that(result, equal_to(""), "No elements should have been found")


def test_get_list_of_attributes():
    mock_element_1 = MagicMock()
    mock_element_2 = MagicMock()
    mock_element_1.get_attribute.return_value = "test_attr_val1"
    mock_element_2.get_attribute.return_value = "test_attr_val2"
    mock_finder = MagicMock()
    mock_finder.elements.return_value = [mock_element_1, mock_element_2]
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.get_list_of_attributes(default_page_element, "test_attr")

    assert_that(result, equal_to(["test_attr_val1", "test_attr_val2"]), "Unexpected list of attributes returned")
    assert_that(len(result), equal_to(2), "Unexpected number of attributes in list")


def test_get_list_of_attributes_single_element():
    mock_element_1 = MagicMock()
    mock_element_1.get_attribute.return_value = "test_attr_val"
    mock_finder = MagicMock()
    mock_finder.elements.return_value = [mock_element_1]
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.get_list_of_attributes(default_page_element, "test_attr")

    assert_that(result, equal_to(["test_attr_val"]), "Unexpected list of attributes returned")
    assert_that(len(result), equal_to(1), "Unexpected number of attributes in list")


def test_get_list_of_attributes_no_element_found():
    mock_finder = MagicMock()
    mock_finder.elements.return_value = []
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.get_list_of_attributes(default_page_element, "test_attr")

    assert_that(result, equal_to([]), "No elements should have been found")


def test_get_text():
    mock_element = MagicMock()
    mock_element.text = "text_content"
    mock_finder = MagicMock()
    mock_finder.element.return_value = mock_element
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.get_text(default_page_element)

    assert_that(result, equal_to("text_content"), "Text not found correctly")


def test_get_list_of_texts():
    mock_element_1 = MagicMock()
    mock_element_2 = MagicMock()
    mock_element_3 = MagicMock()
    mock_element_1.text = "element_text_1"
    mock_element_2.text = "element_text_2"
    mock_element_3.text = "element_text_3"
    mock_finder = MagicMock()
    mock_finder.elements.return_value = [mock_element_1, mock_element_2, mock_element_3]
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.get_list_of_texts(default_page_element)

    assert_that(result, equal_to(["element_text_1", "element_text_2", "element_text_3"]), "Unexpected list returned")
    assert_that(len(result), equal_to(3), "Unexpected number of Strings in list")


def test_get_list_of_texts_single_element():
    mock_element_1 = MagicMock()
    mock_element_1.text = "element_text_1"
    mock_finder = MagicMock()
    mock_finder.elements.return_value = [mock_element_1]
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.get_list_of_texts(default_page_element)

    assert_that(result, equal_to(["element_text_1"]), "Unexpected list returned")
    assert_that(len(result), equal_to(1), "Unexpected number of Strings in list")


def test_get_list_of_texts_no_element_found():
    mock_finder = MagicMock()
    mock_finder.elements.return_value = []
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.get_list_of_texts(default_page_element)

    assert_that(result, equal_to([]), "No elements should have been found")


def test_element_has_class():
    mock_element = MagicMock()
    mock_element.is_displayed.return_value = True
    mock_element.get_attribute.return_value = "class1 class2 test_class"
    mock_finder = MagicMock()
    mock_finder.elements.return_value = [mock_element]
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.element_has_class(default_page_element, "test_class")

    assert_that(result, equal_to(True), "The class should match")


def test_element_has_class_no_elements_found():
    mock_finder = MagicMock()
    mock_finder.elements.return_value = []
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.element_has_class(default_page_element, "test_class")

    assert_that(result, equal_to(False), "No elements should have been found")


def test_element_has_class_incorrect_class():
    mock_element = MagicMock()
    mock_element.is_displayed.return_value = True
    mock_element.get_attribute.return_value = "class1 class2"
    mock_finder = MagicMock()
    mock_finder.elements.return_value = [mock_element]
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.element_has_class(default_page_element, "test_class")

    assert_that(result, equal_to(False), "The class should not match")


def test_element_parent_has_class():
    mock_finder = MagicMock()
    mock_finder.elements.return_value = [MockElement(True, False, True)]
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.element_parent_has_class(default_page_element, "test_class")

    assert_that(result, equal_to(True), "Parent should have been found with the expected class")


def test_element_parent_has_class_incorrect_class():
    mock_finder = MagicMock()
    mock_finder.elements.return_value = [MockElement(True, False, True)]
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.element_parent_has_class(default_page_element, "test_class_2")

    assert_that(result, equal_to(False), "Parent should not have been found with the incorrect class")


def test_element_parent_has_class_no_elements_found():
    mock_finder = MagicMock()
    mock_finder.elements.return_value = []
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.element_parent_has_class(default_page_element, "test_class")

    assert_that(result, equal_to(False), "No elements should have been found")


def test_element_sibling_has_class():
    mock_finder = MagicMock()
    mock_finder.elements.return_value = [MockElement(True)]
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.element_sibling_has_class(default_page_element, "test_class")

    assert_that(result, equal_to(True), "Sibling should have been found with the expected class")


def test_element_sibling_has_class_incorrect_class():
    mock_finder = MagicMock()
    mock_finder.elements.return_value = [MockElement(True)]
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.element_sibling_has_class(default_page_element, "test_class_2")

    assert_that(result, equal_to(False), "Sibling should not have been found with the incorrect class")


def test_element_sibling_has_class_no_elements_found():
    mock_finder = MagicMock()
    mock_finder.elements.return_value = []
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.element_sibling_has_class(default_page_element, "test_class")

    assert_that(result, equal_to(False), "No elements should have been found")


def test_element_contains_link():
    mock_finder = MagicMock()
    mock_finder.elements.return_value = [MockElement(True)]
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.element_contains_link(default_page_element, "test_url")

    assert_that(result, equal_to(True), "Element should have been found with the expected link")


def test_element_contains_link_incorrect_link():
    mock_finder = MagicMock()
    mock_finder.elements.return_value = [MockElement(True)]
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.element_contains_link(default_page_element, "test_url_2")

    assert_that(result, equal_to(False), "Element should not have been found with the incorrect link")


def test_element_contains_link_no_elements_found():
    mock_finder = MagicMock()
    mock_finder.elements.return_value = []
    interrogate = Interrogator(None, mock_finder, None)

    result = interrogate.element_contains_link(default_page_element, "test_url")

    assert_that(result, equal_to(False), "No elements should have been found")


def test_get_value_from_cookie_with_empty_string():
    finder = Finder("driver", "logger")
    test_interrogator = Interrogator(MockDriver(), finder, "logger")
    name = ""
    result = test_interrogator.get_value_from_cookie(name)
    assert_that(result, equal_to(""), f"Incorrect cookie value when searching for name: '{name}'")


def test_get_value_from_cookie_with_none_value():
    finder = Finder("driver", "logger")
    test_interrogator = Interrogator(MockDriver(), finder, "logger")
    name = None
    result = test_interrogator.get_value_from_cookie(name)
    assert_that(result, equal_to(""), f"Incorrect cookie value when searching for name: '{name}'")


def test_get_value_from_cookie_with_correct_value():
    finder = Finder("driver", "logger")
    test_interrogator = Interrogator(MockDriver(), finder, "logger")
    name = "cookie-consent"
    result = test_interrogator.get_value_from_cookie(name)
    assert_that(result, equal_to("%7B%22preferences%22%3Atrue%7D"),
                f"Incorrect cookie value when searching for name: '{name}'")


def test_get_value_from_cookie_with_wrong_key_value():
    finder = Finder("driver", "logger")
    test_interrogator = Interrogator(MockDriver(), finder, "logger")
    name = "consent"
    result = test_interrogator.get_value_from_cookie(name)
    assert_that(result, equal_to(""), f"Incorrect cookie value when searching for name: '{name}'")


def test_get_all_cookies():
    driver = MagicMock()
    driver.get_cookies.return_value = "test_cookie"

    interrogate = Interrogator(driver, None, None)

    cookies = interrogate.get_all_cookies()

    driver.get_cookies.assert_called_once()
    assert_that(cookies, equal_to("test_cookie"), "Cookies not returned correctly")
