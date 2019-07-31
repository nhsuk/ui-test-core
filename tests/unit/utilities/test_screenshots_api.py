from unittest import mock
from tests.unit.unit_test_utils import *
from ui_automation_core.utilities.screenshots_api import print_response_info


class MockResponse:
    def __init__(self, content):
        self.content = content


@mock.patch("builtins.print")
def test_print_response_info_prints_response_title(mock_print):
    response = MockResponse("<body><title>Access Denied: The Personal Access Token used has expired.</title></body>")

    print_response_info(response)

    mock_print.assert_called_with("Access Denied: The Personal Access Token used has expired.")


@mock.patch("builtins.print")
def test_print_response_info_does_not_print_when_response_has_no_title(mock_print):
    response = MockResponse("<body>This is some body text</body>")

    print_response_info(response)

    check_mocked_functions_not_called(mock_print)
