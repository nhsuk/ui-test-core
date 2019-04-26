"""
Utility functions to create data to be used by tests e.g. strings
"""
import random
import string


def generate_random_string(size=8, chars=string.ascii_letters + string.digits + " "):
    """
    Generate a random string with specified length and character set
    :param size: The length required for the string
    :param chars: The character set to generate the string from - by default this is letters, numbers and spaces
    :return: The generated string
    """
    return "".join(random.choice(chars) for _ in range(size))
