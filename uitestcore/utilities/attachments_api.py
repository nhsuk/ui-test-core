"""
This module handles attaching files to test result records on Azure DevOps
Uses Azure DevOps Services REST API:
https://docs.microsoft.com/en-us/rest/api/azure/devops/test/attachments?view=azure-devops-rest-5.0
"""

import base64
import datetime
import json
from os import listdir
from xml.etree.ElementTree import fromstring
import requests
from uitestcore.utilities.string_util import remove_invalid_characters

AZURE_API_VERSION_GET = "6.0"
AZURE_API_VERSION_POST = "5.0-preview.1"


def attach_files_release(organisation, project, attachments_path, release_id, access_token):
    """
    The organisation and project names can be found in the project URL e.g. dev.azure.com/organisation/project
    :param organisation: the Azure organisation name
    :param project: the Azure project name
    :param attachments_path: the file path to the directory containing the files to attach
    :param release_id: the release id to search for test runs in
    :param access_token: access token to authenticate with the azure api
    :return: integer: a return value of 0 indicates success, 1 means that any file could not be attached
    """

    # Set the URL for the required API
    request_url = f"https://dev.azure.com/{organisation}/{project}/_apis/test/runs"

    # Get the run IDs for the given release
    run_ids = get_run_ids_by_release(release_id, request_url, access_token)
    if not run_ids:
        print_azure_error(f"No test runs found for release {release_id}")
        return 1
    print(f"Run IDs found for release {release_id}: {run_ids}")

    return attach_files(run_ids, request_url, access_token, attachments_path)


def attach_files_build(organisation, project, attachments_path, build_id, access_token):
    """
    The organisation and project names can be found in the project URL e.g. dev.azure.com/organisation/project
    :param organisation: the Azure organisation name
    :param project: the Azure project name
    :param attachments_path: the file path to the directory containing the files to attach
    :param build_id: the build id to search for test runs in
    :param access_token: access token to authenticate with the azure api
    :return: integer: a return value of 0 indicates success, 1 means that any file could not be attached
    """

    # Set the URL for the required API
    request_url = f"https://dev.azure.com/{organisation}/{project}/_apis/test/runs"

    # Get the run IDs for the given build
    run_ids = get_run_ids_by_build(build_id, request_url, access_token)
    if not run_ids:
        print_azure_error(f"No test runs found for build {build_id}")
        return 1
    print(f"Run IDs found for build {build_id}: {run_ids}")

    return attach_files(run_ids, request_url, access_token, attachments_path)


def attach_files(run_ids, request_url, access_token, attachment_file_path):
    """
    Get the details of the failed tests from a given set of run ids and attach the files using Microsoft Azure API calls
    :param run_ids: list of run ids to search for failed tests within and attach files to
    :param request_url: the url for the azure api
    :param access_token: access token to authenticate with the azure api
    :param attachment_file_path: the file path to the directory containing the files to attach
    :return: integer: a return value of 0 indicates success, 1 means that any file could not be attached
    """

    # Get the list of failed tests
    failed_tests = get_failed_tests(run_ids, request_url, access_token)

    if not failed_tests:
        return 1

    print(f"Failed tests found (run ID, test case result ID, test name): {failed_tests}")

    # A return value of 0 indicates success, 1 means that any file could not be attached
    return_value = 0

    # Ensure that the file path ends with a "/"
    if not attachment_file_path.endswith("/"):
        attachment_file_path += "/"

    # Attach the relevant files
    for failed_test in failed_tests:
        # Get all of the file names to attach for this test
        file_path = attachment_file_path + remove_invalid_characters(failed_test[2])
        file_names = []

        if append_file_names(file_names, file_path) == 1:
            return_value = 1

        if not file_names:
            continue

        # Attach any files found for this test
        for file_name in file_names:
            file_b64 = get_file_base64(f"{file_path}/{file_name}")

            if not file_b64:
                print_azure_error(f"Could not convert file to Base64: {file_path}/{file_name}")
                return_value = 1
                continue

            run_id = failed_test[0]
            test_case_result_id = failed_test[1]

            response = requests.post(
                f"{request_url}/{run_id}/Results/{test_case_result_id}/attachments",
                params={"api-version": AZURE_API_VERSION_POST},
                auth=("", access_token),
                headers={"Content-Type": "application/json"},
                data=json.dumps({
                    "attachmentType": "GeneralAttachment",
                    "comment": "Attached by UiTestCore",
                    "fileName": file_name,
                    "stream": file_b64.decode("utf-8")
                })
            )

            print(f"Attach file {file_name} - response {response.status_code}")

            if not response.status_code == 200:
                return_value = 1

    return return_value


def get_run_ids_by_release(release_id, request_url, access_token):
    """
    Get the test run IDs for the given release ID - each feature will have a unique run ID
    :param release_id: the release ID from Azure DevOps
    :param request_url: the url for the azure api
    :param access_token: access token to authenticate with the azure api
    :return: list of run IDs which were found
    """
    max_last_updated_date = datetime.datetime.now()
    min_last_updated_date = max_last_updated_date - datetime.timedelta(days=1)

    response = requests.get(
        request_url,
        params={"minLastUpdatedDate": min_last_updated_date,
                "maxLastUpdatedDate": max_last_updated_date,
                "releaseIds": release_id,
                "api-version": AZURE_API_VERSION_GET
                },
        auth=("", access_token)
    )
    return get_run_ids_from_response(release_id, response)


def get_run_ids_by_build(build_id, request_url, access_token):
    """
    Get the test run IDs for the given build ID - each feature will have a unique run ID
    :param build_id: the build ID from Azure DevOps
    :param request_url: the url for the azure api
    :param access_token: access token to authenticate with the azure api
    :return: list of run IDs which were found
    """
    max_last_updated_date = datetime.datetime.now()
    min_last_updated_date = max_last_updated_date - datetime.timedelta(days=1)

    response = requests.get(
        request_url,
        params={"minLastUpdatedDate": min_last_updated_date,
                "maxLastUpdatedDate": max_last_updated_date,
                "buildIds": build_id,
                "api-version": AZURE_API_VERSION_GET
                },
        auth=("", access_token)
    )
    return get_run_ids_from_response(build_id, response)


def get_run_ids_from_response(query_id, response):
    """
    Get the run ids from response body of queried api
    :param query_id: the release/build ID from Azure DevOps
    :param response: the response of the queried api to extract run ids from
    :return: list of run IDs which were found
    """
    print(f"Get run IDs - response {response.status_code}")

    if not response.status_code == 200:
        print_azure_error(f"Could not get run IDs for release/build {query_id}")
        print_response_info(response)
        return []

    response_json = response.json()
    run_ids = []

    for item in response_json["value"]:
        run_ids.append(item["id"])

    return run_ids


def print_response_info(response):
    """
    Prints additional information from the title of the response e.g. to show when the token has expired
    :param response: the response object returned by the request
    """
    if response.content:
        info = fromstring(response.content).findtext('.//title')
        if info:
            print(info)


def get_failed_tests(run_ids, request_url, access_token):
    """
    Get the required details of the failed tests from the given runs
    :param run_ids: list of run IDs to query
    :param request_url: the url for the azure api
    :param access_token: access token to authenticate with the azure api
    :return: list of test details in the format: (run ID, test ID, test name)
    """
    failed_tests = []

    for run_id in run_ids:
        response = requests.get(
            request_url + f"/{run_id}/results",
            params={"api-version": AZURE_API_VERSION_GET},
            auth=("", access_token)
        )

        print(f"Get failed tests for run ID {run_id} - response {response.status_code}")

        if not response.status_code == 200:
            print_azure_error(f"Could not get failed test IDs for run {run_id}")
            continue

        response_json = response.json()

        for test_result in response_json["value"]:
            if test_result["outcome"] == "Failed":
                failed_tests.append((run_id, test_result["id"], test_result["testCase"]["name"]))

    if not failed_tests:
        print_azure_warning("No failed tests were found. If this is because all of the tests passed, "
                            "this task should be configured to be skipped by setting the 'Run this task' option to "
                            "'Only when a previous task has failed'")

    return failed_tests


def get_file_base64(file_path):
    """
    Get the Base64 encoded string for a given file
    :param file_path: the file path to a file to be attached
    :return: the Base64 string
    """
    with open(file_path, "rb") as the_file:
        base64_string = base64.b64encode(the_file.read())

    return base64_string


def append_file_names(file_names, folder_path):
    """
    Get a list of file names inside a folder with the given path
    :param file_names: the list of file names to append to
    :param folder_path: the path to the folder to look in
    :return: 0: success (or only a warning), 1: failure
    """
    try:
        files_in_folder = listdir(folder_path)

    except FileNotFoundError:
        # The folder might not be found due to the API returning a test which didn't fail in the current deployment,
        # so this is only considered a warning
        print_azure_warning(f"Folder not found: {folder_path} - "
                            f"this could have happened due to failed tests in a previous deployment attempt")
        return 0

    if not files_in_folder:
        print_azure_error("Could not find any files in folder: " + folder_path)
        return 1

    for file in files_in_folder:
        file_names.append(file)

    return 0


def print_azure_error(error_message):
    print("##vso[task.logissue type=error]" + error_message)


def print_azure_warning(warning_message):
    print("##vso[task.logissue type=warning]" + warning_message)
