"""
Create any custom assertion in here
"""

from hamcrest import assert_that, is_


def assert_that_result_description_is_empty(result_description):
    """
        asserting the value passed is empty
    :param result_description:
    :return:
    """
    assert_that(result_description, is_(""), result_description)
