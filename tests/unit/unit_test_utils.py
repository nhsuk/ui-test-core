from hamcrest import assert_that


def check_mocked_functions_called(*mocked_functions):
    """
    Asserts that some MagicMock objects have been called - this should be done for every mocked function
    :param mocked_functions: Any number of MagicMock instances which are created by mock.patch
    """
    for mocked_function in mocked_functions:
        assert_that(mocked_function.called, f"The function was not called - {mocked_function}")


def check_mocked_functions_not_called(*mocked_functions):
    """
    Asserts that some MagicMock objects have not been called
    :param mocked_functions: Any number of MagicMock instances which are created by mock.patch
    """
    for mocked_function in mocked_functions:
        assert_that(not mocked_function.called, f"The function should not have been called - {mocked_function}")
