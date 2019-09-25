"""
Utility functions to create data to be used by tests e.g. strings
"""
import json
import random
import string
import urllib.parse


def generate_random_string(size=8, chars=string.ascii_letters + string.digits + " "):
    """
    Generate a random string with specified length and character set
    :param size: The length required for the string
    :param chars: The character set to generate the string from - by default this is letters, numbers and spaces
    :return: The generated string
    """
    return "".join(random.choice(chars) for _ in range(size))


def remove_invalid_characters(input_string):
    """
    Edit a string by replacing underscores with spaces and removing commas, single quotes and new line characters
    :param input_string: the string which needs to be altered
    :return: edited string
    """
    return input_string.replace(" ", "_").replace(",", "").replace("'", "")\
                       .replace("\n", "").replace("/", "_").replace(":", "")


def decode_url_string(input_string):
    """
    Decode a string which is URL encoded
    :param input_string: the string which needs to be decoded
    :return: json dictionary
    """
    return json.loads(urllib.parse.unquote(input_string))
