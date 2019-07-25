from hamcrest import assert_that, equal_to, is_not
from ui_automation_core.utilities.string_util import *


def test_generate_random_string_default_length():
    expected_length = 8

    result1 = generate_random_string()
    result2 = generate_random_string()
    results = result1 + result2

    assert_that(len(result1), equal_to(expected_length), "Incorrect length of the first random string")
    assert_that(len(result2), equal_to(expected_length), "Incorrect length of the second random string")
    assert_that(result1, is_not(equal_to(result2)), "Different strings should be generated each time")
    assert_that("_" not in results and "," not in results and "'" not in results, "Invalid characters in random string")


def test_generate_random_string_increased_length():
    expected_length = 1500

    result1 = generate_random_string(expected_length)
    result2 = generate_random_string(expected_length)
    results = result1 + result2

    assert_that(len(result1), equal_to(expected_length), "Incorrect length of the first random string")
    assert_that(len(result2), equal_to(expected_length), "Incorrect length of the second random string")
    assert_that(result1, is_not(equal_to(result2)), "Different strings should be generated each time")
    assert_that("_" not in results and "," not in results and "'" not in results, "Invalid characters in random string")


def test_remove_invalid_characters():
    input = "test, 'string'\n"

    result = remove_invalid_characters(input)

    assert_that(result, equal_to("test_string"), "All invalid characters should be removed")


def test_remove_invalid_characters_does_not_change_valid_string():
    input = "test_string"

    result = remove_invalid_characters(input)

    assert_that(result, equal_to(input), "A string with only valid characters should not be changed")
