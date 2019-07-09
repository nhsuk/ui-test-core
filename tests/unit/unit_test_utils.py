from hamcrest import assert_that


def check_mocked_function_called(mocked_function):
    """
    Asserts that a MagicMock object has been called - this should be done for every mocked function
    :param mocked_function: MagicMock instance which is created by mock.patch
    """
    assert_that(mocked_function.called, f"The mocked function was not called - {mocked_function}")
