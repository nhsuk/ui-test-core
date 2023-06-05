from hamcrest import assert_that, calling, raises, is_not
from uitestcore.custom_assertion import assert_no_failures


def test_assert_no_failures_succeeds_when_passed_empty_string():
    assert_that(calling(assert_no_failures).with_args(""), is_not(raises(AssertionError)),
                "The assertion should pass when there is no failure description")


def test_assert_no_failures_fails_when_passed_non_empty_string():
    assert_that(calling(assert_no_failures).with_args("test failed"), raises(AssertionError),
                "The assertion should fail when there is a failure description")


def test_assert_no_failures_reports_failure_description():
    try:
        assert_no_failures("test failed")
    except AssertionError as e:
        assert_that(str(e).startswith("test failed"), "Failure description not reported correctly")
