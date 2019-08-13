"""
This module handles attaching screenshots to test result records on Azure DevOps
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

AZURE_API_VERSION_GET = "5.0"
AZURE_API_VERSION_POST = "5.0-preview.1"


def parse_parameters(args):
    """
    Parse the release ID and auth token from the provided arguments
    :param args: sys.argv which should contain the release ID and auth token
    :return: tuple containing the two parameters or None if there was an error
    """
    try:
        params = args[1], args[2]

    except IndexError:
        print("Error: Unable to parse required parameters - ensure they are passed correctly. "
              "Expected release ID and auth token.")
        return None

    else:
        print(f"The release ID is: {params[0]}")
        return params


def get_run_ids(release_id, request_url, auth_token):
    """
    Get the test run IDs for the given release ID - each feature will have a unique run ID
    :param release_id: the release ID from Azure DevOps
    :param request_url: the URL for the Microsoft API
    :param auth_token: the ID number of the release from Azure DevOps
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
        auth=("", auth_token)
    )

    print(f"Get run IDs for release {release_id} - response {response.status_code}")

    if not response.status_code == 200:
        print(f"Could not get run IDs for release {release_id}")
        print_response_info(response)
        return []

    response_json = response.json()
    run_ids = []

    for item in response_json["value"]:
        run_ids.append(item["id"])

    return run_ids


def print_response_info(response):
    """
    Prints additional infomration from the title of the response e.g. to show when the token has expired
    :param response: the response object returned by the request
    """
    info = fromstring(response.content).findtext('.//title')
    if info:
        print(info)


def get_failed_tests(run_ids, request_url, auth_token):
    """
    Get the required details of the failed tests from the given runs
    :param run_ids: list of run IDs to query
    :param request_url: the URL for the Microsoft API
    :param auth_token: the ID number of the release from Azure DevOps
    :return: list of test details in the format: (run ID, test ID, test name)
    """
    failed_tests = []

    for run_id in run_ids:
        response = requests.get(
            request_url + f"/{run_id}/results",
            params={"api-version": AZURE_API_VERSION_GET},
            auth=("", auth_token)
        )

        print(f"Get failed tests for run ID {run_id} - response {response.status_code}")

        if not response.status_code == 200:
            print(f"Could not get failed test IDs for run {run_id}")
            continue

        response_json = response.json()

        for test_result in response_json["value"]:
            if test_result["outcome"] == "Failed":
                failed_tests.append((run_id, test_result["id"], test_result["testCase"]["name"]))

    if not failed_tests:
        print("No failed tests were found. If this is because all of the tests passed, this task should be configured "
              "to be skipped by setting the 'Run this task' option to 'Only when a previous task has failed'")

    return failed_tests


def get_image_base64(file_path):
    """
    Get the Base64 encoded string for a given screenshot file
    :param file_path: the file path to a screenshot
    :return: the Base64 string
    """
    with open(file_path, "rb") as image_file:
        base64_string = base64.b64encode(image_file.read())

    return base64_string


def attach_screenshots(project, args):
    """
    Get the details of the failed tests from a given release and attach the screenshots using Microsoft API calls
    :param project: the Azure project name e.g. "nhsuk.contact-us"
    :param args: sys.argv which should contain the release ID and auth token
    :return: integer: 1 if there were errors, otherwise 0
    """
    # Get the release ID and auth token from the passed arguments
    params = parse_parameters(args)
    if not params:
        return 1
    release_id = params[0]
    auth_token = params[1]

    # Set the URL for the required API
    request_url = f"https://dev.azure.com/nhsuk/{project}/_apis/test/runs"

    # Get the run IDs for the given release
    run_ids = get_run_ids(release_id, request_url, auth_token)

    if not run_ids:
        print(f"No test runs found for release {release_id}")
        return 1

    print(f"Run IDs found for release {release_id}: {run_ids}")

    # Get the list of failed tests
    failed_tests = get_failed_tests(run_ids, request_url, auth_token)

    if not failed_tests:
        return 1

    print(f"Failed tests found: {failed_tests}")

    # Attach the relevant screenshots
    for failed_test in failed_tests:
        # Get all of the file names of screenshots for this test
        screenshots_path = "screenshots/" + remove_invalid_characters(failed_test[2])
        file_names = listdir(screenshots_path)

        if not file_names:
            print(f"Could not find any screenshot files in folder: {screenshots_path}")
            continue

        # Attach any screenshots found for this test
        for file_name in file_names:
            image_b64 = get_image_base64(f"{screenshots_path}/{file_name}")

            if not image_b64:
                print(f"Could not convert file to Base64: {screenshots_path}/{file_name}")
                continue

            run_id = failed_test[0]
            test_case_result_id = failed_test[1]

            response = requests.post(
                f"{request_url}/{run_id}/Results/{test_case_result_id}/attachments",
                params={"api-version": AZURE_API_VERSION_POST},
                auth=("", auth_token),
                headers={"Content-Type": "application/json"},
                data=json.dumps({
                    "attachmentType": "GeneralAttachment",
                    "comment": "Example screenshot",
                    "fileName": file_name,
                    "stream": image_b64.decode("utf-8")
                })
            )

            print(f"Attach screenshot {file_name} - response {response.status_code}")

    return 0
