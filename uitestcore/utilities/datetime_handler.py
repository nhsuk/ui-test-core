"""
A useful collection of date and time utility methods
"""
import datetime
from dateutil.relativedelta import relativedelta


def get_current_date():
    """
    Uses the standard datetime lib to return date.today()
    :return: Date in YYY-MM-DD format
    """
    return datetime.date.today()


def get_current_datetime():
    """
    Uses the standard datetime lib to return date.now()
    :return: Date in YYY-MM-DD-HH-MM-SS format
    """
    return datetime.datetime.now()


def get_date_altered_by_days(day_difference, current_date=datetime.date.today()):
    """
    Generates a date offset by a number of days
    Can be a date in the future or in past, by passing in a positive or negative day_difference
    :param day_difference: int number of days to offset from current date
    :param current_date: optional. can be used to set a different starting date to offset from. Used for unit tests
    :return: Date in YYY-MM-DD format
    """
    return current_date + relativedelta(days=day_difference)


def get_date_altered_by_months(month_difference, current_date=datetime.date.today()):
    """
    Generates a date offset by a number of days
    Can be a date in the future or in past, by passing in a positive or negative month_difference
    :param month_difference: int number of months to offset from current date
    :param current_date: optional. can be used to set a different starting date to offset from. Used for unit tests
    :return: Date in YYY-MM-DD format
    """
    return current_date + relativedelta(months=month_difference)
