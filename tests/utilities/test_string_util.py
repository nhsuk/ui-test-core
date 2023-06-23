from json import JSONDecodeError

from hamcrest import assert_that, equal_to, is_not, raises, calling
from uitestcore.utilities.string_util import *


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
    test_input_string = "https://test, 'string'\n"

    result = remove_invalid_characters(test_input_string)

    assert_that(result, equal_to("https__test_string"), "All invalid characters should be removed")


def test_remove_invalid_characters_does_not_change_valid_string():
    test_input_string = "test_string"

    result = remove_invalid_characters(test_input_string)

    assert_that(result, equal_to(test_input_string), "A string with only valid characters should not be changed")


def test_decode_url_string_with_empty_input():
    empty_url_string = ""
    assert_that(calling(decode_url_string).with_args(empty_url_string), raises(JSONDecodeError),
                "A JSONDecodeError should occur when decoding an empty string")


def test_decode_url_string_with_none_input():
    none_url_string = None
    assert_that(calling(decode_url_string).with_args(none_url_string), raises(TypeError),
                "A JSONDecodeError should occur with a None value")


def test_decode_url_string_with_invalid_input():
    invalid_url_string = "necessary%22%3Atrue%2C%22preferences%22%3Atrue%2C%22statistics%22%3Atrue" \
                         "%2C%22marketing%22%3Afalse%2C%22consented%22%3Afalse%2C%22version1"
    assert_that(calling(decode_url_string).with_args(invalid_url_string), raises(JSONDecodeError),
                "A JSONDecodeError should occur when decoding an invalid input string")


def test_decode_url_string_with_valid_input():
    valid_url_string = "%7B%22necessary%22%3Atrue%2C%22preferences%22%3Atrue%2C%22statistics%22%3Atrue" \
                       "%2C%22marketing%22%3Afalse%2C%22consented%22%3Afalse%2C%22version%22%3A1%7D"
    assert_that(calling(decode_url_string).with_args(valid_url_string), is_not(raises(JSONDecodeError)),
                "A JSONDecodeError should not occur when decoding a valid input string")


def test_replace_null_with_empty_string():
    text = "null"

    result = replace_null_with_empty_string(text)

    assert_that(result, equal_to(""), "Expected empty string")


def test_replace_null_with_empty_string_text_not_null():
    text = "sample"

    result = replace_null_with_empty_string(text)

    assert_that(result, is_not(""), "Expected text to not be empty string")
