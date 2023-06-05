from unittest import mock
from hamcrest import equal_to, starts_with, calling, is_not, raises
from tests.unit_test_utils import *
from uitestcore.utilities.attachments_api import *


class MockResponse:
    def __init__(self, content, status_code=0, mode=""):
        self.content = content
        self.status_code = status_code
        self.mode = mode

    def json(self):
        if self.mode == "get_run_ids_from_response":
            return {
                "value": [
                    {"id": 1},
                    {"id": 2},
                    {"id": 3}
                ]
            }

        elif self.mode == "get_failed_tests":
            return {
                "value": [
                    {"id": 1, "outcome": "Failed", "testCase": {"name": "test1"}},
                    {"id": 2, "outcome": "Passed", "testCase": {"name": "test2"}},
                    {"id": 3, "outcome": "Failed", "testCase": {"name": "test3"}}
                ]
            }

        else:
            return {}


class MockBuiltIn:

    def __init__(self, *args):
        pass

    def __enter__(self, *args):
        return self

    def __exit__(self, *args):
        pass

    @staticmethod
    def read():
        return "test data".encode()


def mock_list_dir(file_path):
    if file_path == "test/folder":
        return ["file1.png", "file2.png", "file2.png"]
    elif file_path == "test/folder_with_no_files":
        return []
    raise FileNotFoundError


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


@mock.patch("builtins.print")
@mock.patch("requests.get", side_effect=lambda *args, **kwargs: MockResponse("", 200, "get_run_ids_from_response"))
def test_get_run_ids_by_release_performs_the_correct_request(mock_get, _mock_print):
    get_run_ids_by_release(100, "test-url", "test-token")

    check_mocked_functions_called(mock_get)
    request_args = mock_get.call_args

    assert_that(request_args[0][0], equal_to("test-url"), "request_url incorrect")
    assert_that(request_args[1]["params"]["releaseIds"], equal_to(100), "releaseIds incorrect")
    assert_that(request_args[1]["params"]["api-version"], equal_to("6.0"), "api-version for GET incorrect")
    assert_that(request_args[1]["auth"][1], equal_to("test-token"), "Auth token incorrect")


@mock.patch("builtins.print")
@mock.patch("requests.get", side_effect=lambda *args, **kwargs: MockResponse("", 200, "get_run_ids_from_response"))
def test_get_run_ids_by_build_performs_the_correct_request(mock_get, _mock_print):
    get_run_ids_by_build(100, "test-url", "test-token")

    check_mocked_functions_called(mock_get)
    request_args = mock_get.call_args

    assert_that(request_args[0][0], equal_to("test-url"), "request_url incorrect")
    assert_that(request_args[1]["params"]["buildIds"], equal_to(100), "buildIds incorrect")
    assert_that(request_args[1]["params"]["api-version"], equal_to("6.0"), "api-version for GET incorrect")
    assert_that(request_args[1]["auth"][1], equal_to("test-token"), "Auth token incorrect")


@mock.patch("builtins.print")
@mock.patch("requests.get", side_effect=lambda *args, **kwargs: MockResponse("", 200, "get_run_ids_from_response"))
def test_get_run_ids_by_release_returns_ids_when_request_succeeds(mock_get, _mock_print):
    run_ids = get_run_ids_by_release(100, "test-url", "test-token")

    check_mocked_functions_called(mock_get)
    assert_that(run_ids, equal_to([1, 2, 3]), "Incorrect run IDs returned")


@mock.patch("requests.get", side_effect=lambda *args, **kwargs: MockResponse("", 400, "get_run_ids_from_response"))
@mock.patch("builtins.print")
def test_get_run_ids_by_release_returns_no_ids_when_request_fails(mock_print, mock_get):
    run_ids = get_run_ids_by_release(100, "test-url", "test-token")

    check_mocked_functions_called(mock_get, mock_print)
    assert_that(run_ids, equal_to([]), "Run IDs should not be returned when the request failed")
    mock_print.assert_called_with("##vso[task.logissue type=error]Could not get run IDs for release/build 100")


@mock.patch("requests.get", side_effect=lambda *args, **kwargs: MockResponse("", 400, "get_failed_tests"))
@mock.patch("builtins.print")
def test_get_failed_tests_returns_no_failed_tests_when_request_fails(mock_print, mock_get):
    failed_tests = get_failed_tests([100, 101, 102], "test-url", "test-token")

    check_mocked_functions_called(mock_get, mock_print)
    assert_that(failed_tests, equal_to([]), "Failed tests should not be returned when the request failed")
    request_failed_message = mock_print.call_args[0][0]
    assert_that(request_failed_message, starts_with("##vso[task.logissue type=warning]No failed tests were found"))


@mock.patch("builtins.print")
@mock.patch("requests.get", side_effect=lambda *args, **kwargs: MockResponse("", 200, "get_failed_tests"))
def test_get_failed_tests_returns_failed_tests_when_request_succeeds(mock_get, _mock_print):
    failed_tests = get_failed_tests([100], "test-url", "test-token")

    check_mocked_functions_called(mock_get)
    assert_that(failed_tests, equal_to([(100, 1, "test1"), (100, 3, "test3")]),
                "Incorrect info regarding failed UI tests returned")


@mock.patch("builtins.print")
@mock.patch("requests.get", side_effect=lambda *args, **kwargs: MockResponse("", 200, "get_failed_tests"))
def test_get_failed_tests_performs_the_correct_request(mock_get, _mock_print):
    get_failed_tests([100], "test-url", "test-token")

    check_mocked_functions_called(mock_get)
    request_args = mock_get.call_args

    assert_that(request_args[0][0], equal_to("test-url/100/results"), "request_url incorrect")
    assert_that(request_args[1]["params"]["api-version"], equal_to("6.0"), "api-version for GET incorrect")
    assert_that(request_args[1]["auth"][1], equal_to("test-token"), "Auth token incorrect")


@mock.patch("builtins.open", side_effect=MockBuiltIn)
def test_get_file_base64(mock_open):
    image_b64 = get_file_base64("test/file")

    check_mocked_functions_called(mock_open)
    assert_that(image_b64, equal_to(b"dGVzdCBkYXRh"), "Incorrect base 64 string")


@mock.patch("builtins.print")
def test_attach_files_fails_when_passed_no_parameters(_mock_print):
    result = attach_files("test-org", "test-project", "screenshots", [])

    assert_that(result, equal_to(1), "Result should be a failure when no parameters passed")


@mock.patch("builtins.print")
@mock.patch("uitestcore.utilities.attachments_api.get_run_ids_from_response", side_effect=lambda *args: None)
def test_attach_files_release_fails_when_there_are_no_run_ids(mock_get_run_ids_from_response, _mock_print):
    result = attach_files_release("test-org", "test-project", "screenshots", "100", "test-token")

    check_mocked_functions_called(mock_get_run_ids_from_response)
    assert_that(result, equal_to(1), "Result should be a failure when there are no run IDs")


@mock.patch("builtins.print")
@mock.patch("uitestcore.utilities.attachments_api.get_run_ids_from_response", side_effect=lambda *args: None)
def test_attach_files_build_fails_when_there_are_no_run_ids(mock_get_run_ids_from_response, _mock_print):
    result = attach_files_build("test-org", "test-project", "screenshots", "100", "test-token")

    check_mocked_functions_called(mock_get_run_ids_from_response)
    assert_that(result, equal_to(1), "Result should be a failure when there are no run IDs")


@mock.patch("builtins.print")
@mock.patch("uitestcore.utilities.attachments_api.get_run_ids_from_response", side_effect=lambda *args: [10, 11])
@mock.patch("uitestcore.utilities.attachments_api.get_failed_tests", side_effect=lambda *args: None)
def test_attach_files_fails_when_there_are_no_failed_tests(mock_get_failed_tests, mock_get_run_ids_from_response, _mock_print):
    result = attach_files_release("test-org", "test-project", "screenshots", "100", "test-token")

    check_mocked_functions_called(mock_get_failed_tests, mock_get_run_ids_from_response)
    assert_that(result, equal_to(1), "Result should be a failure when there are no failed tests")


@mock.patch("builtins.print")
@mock.patch("uitestcore.utilities.attachments_api.get_run_ids_from_response", side_effect=lambda *args: [10, 11])
@mock.patch("uitestcore.utilities.attachments_api.listdir", side_effect=lambda *args: None)
@mock.patch("uitestcore.utilities.attachments_api.get_failed_tests", side_effect=lambda *args: [[10, 100, "test1"],
                                                                                                [11, 101, "test2"]])
def test_attach_files_fails_when_there_are_no_files(mock_get_failed_tests, mock_listdir, mock_get_run_ids_from_response, _mock_print):
    result = attach_files_release("test-org", "test-project", "screenshots", "100", "test-token")

    check_mocked_functions_called(mock_listdir, mock_get_failed_tests, mock_get_run_ids_from_response)
    assert_that(result, equal_to(1), "Result should be a failure when there are no files")


@mock.patch("builtins.print")
@mock.patch("uitestcore.utilities.attachments_api.get_run_ids_from_response", side_effect=lambda *args: [10, 11])
@mock.patch("uitestcore.utilities.attachments_api.listdir", side_effect=lambda *args: ["test1", "test2"])
@mock.patch("uitestcore.utilities.attachments_api.get_file_base64", side_effect=lambda *args: None)
@mock.patch("uitestcore.utilities.attachments_api.get_failed_tests", side_effect=lambda *args: [[10, 100, "test1"],
                                                                                                [11, 101, "test2"]])
def test_attach_files_fails_when_there_base64_conversion_fails(mock_get_failed_tests, mock_get_file_base64,
                                                               mock_listdir, mock_get_run_ids_from_response, _mock_print):
    result = attach_files_release("test-org", "test-project", "screenshots", "100", "test-token")

    check_mocked_functions_called(mock_get_failed_tests, mock_get_file_base64, mock_listdir, mock_get_run_ids_from_response)
    assert_that(result, equal_to(1), "Result should be a failure when base64 conversion fails")


@mock.patch("builtins.print")
@mock.patch("uitestcore.utilities.attachments_api.get_run_ids_from_response", side_effect=lambda *args: [10, 11])
@mock.patch("uitestcore.utilities.attachments_api.listdir", side_effect=lambda *args: ["file1"])
@mock.patch("uitestcore.utilities.attachments_api.get_file_base64", side_effect=lambda *args: None)
@mock.patch("uitestcore.utilities.attachments_api.get_failed_tests", side_effect=lambda *args: [[10, 100, "test1"]])
def test_attach_files_gets_the_base64_of_the_correct_file(mock_get_failed_tests, mock_get_file_base64,
                                                          mock_listdir, mock_get_run_ids_from_response, _mock_print):
    attach_files_release("test-org", "test-project", "screenshots", "100", "test-token")

    check_mocked_functions_called(mock_get_failed_tests, mock_listdir, mock_get_run_ids_from_response)
    mock_get_file_base64.assert_called_with("screenshots/test1/file1")


@mock.patch("builtins.print")
@mock.patch("uitestcore.utilities.attachments_api.get_run_ids_from_response", side_effect=lambda *args: [10, 11])
@mock.patch("uitestcore.utilities.attachments_api.listdir", side_effect=lambda *args: ["test1", "test2"])
@mock.patch("uitestcore.utilities.attachments_api.get_file_base64", side_effect=lambda *args: b"test-base64-string")
@mock.patch("requests.post", side_effect=lambda *args, **kwargs: MockResponse("", 400))
@mock.patch("uitestcore.utilities.attachments_api.get_failed_tests", side_effect=lambda *args: [[10, 100, "test1"],
                                                                                                [11, 101, "test2"]])
def test_attach_files_fails_when_the_request_fails(mock_get_failed_tests, mock_post, mock_get_file_base64,
                                                   mock_listdir, mock_get_run_ids_from_response, _mock_print):
    result = attach_files_release("test-org", "test-project", "screenshots", "100", "test-token")

    check_mocked_functions_called(mock_get_failed_tests, mock_post, mock_get_file_base64,
                                  mock_listdir, mock_get_run_ids_from_response)
    assert_that(result, equal_to(1), "Result should be a failure when the request fails")


@mock.patch("builtins.print")
@mock.patch("uitestcore.utilities.attachments_api.get_run_ids_from_response", side_effect=lambda *args: [10, 11])
@mock.patch("uitestcore.utilities.attachments_api.listdir", side_effect=lambda *args: ["test1", "test2"])
@mock.patch("uitestcore.utilities.attachments_api.get_file_base64", side_effect=lambda *args: b"test-base64-string")
@mock.patch("requests.post", side_effect=lambda *args, **kwargs: MockResponse("", 200))
@mock.patch("uitestcore.utilities.attachments_api.get_failed_tests", side_effect=lambda *args: [[10, 100, "test1"],
                                                                                                [11, 101, "test2"]])
def test_attach_files_release_succeeds(mock_get_failed_tests, mock_post, mock_get_file_base64,
                               mock_listdir, mock_get_run_ids_from_response, _mock_print):
    result = attach_files_release("test-org", "test-project", "screenshots", "100", "test-token")

    check_mocked_functions_called(mock_get_failed_tests, mock_post, mock_get_file_base64,
                                  mock_listdir, mock_get_run_ids_from_response)
    assert_that(result, equal_to(0), "Result should be a success when everything works")


@mock.patch("builtins.print")
@mock.patch("uitestcore.utilities.attachments_api.get_run_ids_from_response", side_effect=lambda *args: [10, 11])
@mock.patch("uitestcore.utilities.attachments_api.listdir", side_effect=lambda *args: ["test1", "test2"])
@mock.patch("uitestcore.utilities.attachments_api.get_file_base64", side_effect=lambda *args: b"test-base64-string")
@mock.patch("requests.post", side_effect=lambda *args, **kwargs: MockResponse("", 200))
@mock.patch("uitestcore.utilities.attachments_api.get_failed_tests", side_effect=lambda *args: [[10, 100, "test1"],
                                                                                                [11, 101, "test2"]])
def test_attach_files_build_succeeds(mock_get_failed_tests, mock_post, mock_get_file_base64,
                               mock_listdir, mock_get_run_ids_from_response, _mock_print):
    result = attach_files_build("test-org", "test-project", "screenshots", "100", "test-token")

    check_mocked_functions_called(mock_get_failed_tests, mock_post, mock_get_file_base64,
                                  mock_listdir, mock_get_run_ids_from_response)
    assert_that(result, equal_to(0), "Result should be a success when everything works")


@mock.patch("builtins.print")
@mock.patch("uitestcore.utilities.attachments_api.get_run_ids_from_response", side_effect=lambda *args: [10, 11])
@mock.patch("uitestcore.utilities.attachments_api.listdir", side_effect=lambda *args: ["test1", "test2"])
@mock.patch("uitestcore.utilities.attachments_api.get_file_base64", side_effect=lambda *args: b"test-base64-string")
@mock.patch("requests.post", side_effect=lambda *args, **kwargs: MockResponse("", 200))
@mock.patch("uitestcore.utilities.attachments_api.get_failed_tests", side_effect=lambda *args: [[10, 100, "test1"],
                                                                                                [11, 101, "test2"]])
def test_attach_files_performs_the_correct_request(mock_get_failed_tests, mock_post, mock_get_file_base64,
                                                   mock_listdir, mock_get_run_ids_from_response, _mock_print):
    attach_files_release("test-org", "test-project", "screenshots", "100", "test-token")

    check_mocked_functions_called(mock_get_failed_tests, mock_post, mock_get_file_base64,
                                  mock_listdir, mock_get_run_ids_from_response)
    request_args = mock_post.call_args

    assert_that(request_args[0][0], equal_to("https://dev.azure.com/test-org/test-project/_apis/"
                                             "test/runs/11/Results/101/attachments"), "request_url incorrect")
    assert_that(request_args[1]["params"]["api-version"], equal_to("5.0-preview.1"), "api-version for POST incorrect")
    assert_that(request_args[1]["auth"][1], equal_to("test-token"), "Auth token incorrect")
    assert_that(request_args[1]["headers"]["Content-Type"], equal_to("application/json"), "Incorrect request header")
    assert_that(request_args[1]["data"], equal_to("{\"attachmentType\": \"GeneralAttachment\", \"comment\": "
                                                  "\"Attached by UiTestCore\", \"fileName\": \"test2\", \"stream\": "
                                                  "\"test-base64-string\"}"), "Incorrect request body")


@mock.patch("uitestcore.utilities.attachments_api.listdir", side_effect=mock_list_dir)
def test_append_file_names(mock_listdir):
    file_names = []
    result = append_file_names(file_names, "test/folder")

    assert_that(result, equal_to(0), "Result should be success when files found")
    assert_that(file_names, equal_to(["file1.png", "file2.png", "file2.png"]), "File names list incorrect")
    mock_listdir.assert_called_once_with("test/folder")


@mock.patch("builtins.print")
def test_append_file_names_handles_folder_not_found(_mock_print):
    file_names = []
    assert_that(calling(append_file_names).with_args(file_names, "test/folder_not_exists"),
                is_not(raises(FileNotFoundError)),
                "Errors should be handled when the folder is not found")


@mock.patch("builtins.print")
def test_append_file_names_outputs_a_warning_message_and_does_not_fail_when_folder_not_found(mock_print):
    file_names = []
    result = append_file_names(file_names, "test/folder_not_exists")

    expected_message = "##vso[task.logissue type=warning]Folder not found: test/folder_not_exists - " \
                       "this could have happened due to failed tests in a previous deployment attempt"
    assert_that(result, equal_to(0), "Result should be success when there is only a warning")
    mock_print.assert_called_once_with(expected_message)


@mock.patch("builtins.print")
@mock.patch("uitestcore.utilities.attachments_api.listdir", side_effect=mock_list_dir)
def test_append_file_names_outputs_an_error_message_and_fails_when_files_not_found_in_folder(mock_listdir, mock_print):
    file_names = []
    result = append_file_names(file_names, "test/folder_with_no_files")

    assert_that(result, equal_to(1), "Result should be failure when there is an error")
    assert_that(file_names, equal_to([]), "File names list should be empty when there was an error")
    mock_print.assert_called_once_with("##vso[task.logissue type=error]Could not find any files in folder: "
                                       "test/folder_with_no_files")
    mock_listdir.assert_called_once_with("test/folder_with_no_files")


@mock.patch("builtins.print")
def test_print_azure_error(mock_print):
    print_azure_error("test-error")

    mock_print.assert_called_once_with("##vso[task.logissue type=error]test-error")


@mock.patch("builtins.print")
def test_print_azure_warning(mock_print):
    print_azure_warning("test-warning")

    mock_print.assert_called_once_with("##vso[task.logissue type=warning]test-warning")
