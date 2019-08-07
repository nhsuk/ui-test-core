"""
Create any custom assertion in here
"""
from hamcrest import assert_that, is_


def assert_no_failures(failure_description):
    """
    Assert that the string passed is empty representing no failures - to be used in test steps
    :param failure_description: a string describing failures in a test step, or empty if no failures
    """
    assert_that(failure_description, is_(""), failure_description)
