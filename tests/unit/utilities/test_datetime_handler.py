from datetime import timedelta
from hamcrest import assert_that, equal_to, less_than
from uitestcore.utilities.datetime_handler import *


def test_get_current_date():
    expected_date = datetime.date.today()

    actual_date = get_current_date()

    assert_that(actual_date, equal_to(expected_date), "Date should have been today")


def test_get_current_datetime():
    expected_date_time = datetime.datetime.now()

    actual_date_time = get_current_datetime()
    time_difference = (actual_date_time - expected_date_time).microseconds

    assert_that(time_difference, less_than(1000), "Current date time incorrect")


def test_get_date_altered_by_days_from_today():
    expected_date_time = datetime.date.today() + timedelta(days=2)

    actual_date_time = get_date_altered_by_days(2)

    assert_that(actual_date_time, equal_to(expected_date_time), "Incorrect date")


def test_get_date_altered_by_days_from_tomorrow():
    expected_date_time = datetime.date.today() + timedelta(days=6)

    actual_date_time = get_date_altered_by_days(5, datetime.date.today() + timedelta(days=1))

    assert_that(actual_date_time, equal_to(expected_date_time), "Incorrect date")


def test_get_date_altered_by_months():
    expected_date_time = datetime.date.today() + relativedelta(months=4)

    actual_date_time = get_date_altered_by_months(4)

    assert_that(actual_date_time, equal_to(expected_date_time), "Incorrect date")


def test_get_date_altered_by_months_from_difference_month():
    example_date = datetime.datetime.strptime("2020-02-29_08.00.00.000000", "%Y-%m-%d_%H.%M.%S.%f")
    expected_date_time = datetime.datetime.strptime("2021-02-28_08.00.00.000000", "%Y-%m-%d_%H.%M.%S.%f")

    actual_date_time = get_date_altered_by_months(12, example_date)

    assert_that(actual_date_time, equal_to(expected_date_time), "Incorrect date")
