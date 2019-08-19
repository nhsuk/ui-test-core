from unittest import mock
from unittest.mock import MagicMock

from selenium.webdriver.common.by import By

from uitestcore.finder import Finder
from uitestcore.interactor import Interactor
from uitestcore.interrogator import Interrogator
from uitestcore.page_element import PageElement
from uitestcore.waiter import Waiter


@mock.patch("selenium.webdriver")
def test_switch_to_frame(mock_driver):
    finder = Finder(mock_driver, "logger")
    interrogator = Interrogator(mock_driver, "logger", finder)
    waiter = Waiter(mock_driver, "logger", finder)
    test_interactor = Interactor(mock_driver, "logger", finder, interrogator, waiter)
    frame_to_find = PageElement(By.ID, "frame_id")
    mock_driver.switch_to.frame = MagicMock(name="frame")

    test_interactor.switch_to_frame(frame_to_find)

    mock_driver.switch_to.frame.assert_called_once_with(frame_to_find)


@mock.patch("selenium.webdriver")
def test_accept_alert(mock_driver):
    finder = Finder(mock_driver, "logger")
    interrogator = Interrogator(mock_driver, "logger", finder)
    waiter = Waiter(mock_driver, "logger", finder)
    test_interactor = Interactor(mock_driver, "logger", finder, interrogator, waiter)
    mock_driver.switch_to.alert.accept = MagicMock(name="accept")

    test_interactor.accept_alert()

    mock_driver.switch_to.alert.accept.assert_called_once()


@mock.patch("selenium.webdriver")
def test_dismiss_alert(mock_driver):
    finder = Finder(mock_driver, "logger")
    interrogator = Interrogator(mock_driver, "logger", finder)
    waiter = Waiter(mock_driver, "logger", finder)
    test_interactor = Interactor(mock_driver, "logger", finder, interrogator, waiter)
    mock_driver.switch_to.alert.dismiss = MagicMock(name="dismiss")

    test_interactor.dismiss_alert()

    mock_driver.switch_to.alert.dismiss.assert_called_once()


@mock.patch("selenium.webdriver")
def test_enter_text_into_alert(mock_driver):
    finder = Finder(mock_driver, "logger")
    interrogator = Interrogator(mock_driver, "logger", finder)
    waiter = Waiter(mock_driver, "logger", finder)
    test_interactor = Interactor(mock_driver, "logger", finder, interrogator, waiter)
    mock_driver.switch_to.alert.send_keys = MagicMock(name="send_keys")
    text = "my text value"

    test_interactor.enter_text_into_alert(text)

    mock_driver.switch_to.alert.send_keys.assert_called_once_with(text)


@mock.patch("selenium.webdriver")
def test_switch_to_original_window(mock_driver):
    finder = Finder(mock_driver, "logger")
    interrogator = Interrogator(mock_driver, "logger", finder)
    waiter = Waiter(mock_driver, "logger", finder)
    test_interactor = Interactor(mock_driver, "logger", finder, interrogator, waiter)
    mock_driver.window_handles = ["window_0", "window_1"]

    test_interactor.switch_to_original_window()

    mock_driver.switch_to_window_with("window_0")


@mock.patch("selenium.webdriver")
def test_switch_to_new_window(mock_driver):
    finder = Finder(mock_driver, "logger")
    interrogator = Interrogator(mock_driver, "logger", finder)
    waiter = Waiter(mock_driver, "logger", finder)
    test_interactor = Interactor(mock_driver, MagicMock(name="logger"), finder, interrogator, waiter)

    test_interactor.switch_to_new_window()

    mock_driver.switch_to_window.assert_called_once()


@mock.patch("selenium.webdriver")
def test_close_current_window_with_2_windows(mock_driver):
    finder = Finder(mock_driver, "logger")
    interrogator = Interrogator(mock_driver, "logger", finder)
    waiter = Waiter(mock_driver, "logger", finder)
    test_interactor = Interactor(mock_driver, MagicMock(name="logger"), finder, interrogator, waiter)
    mock_driver.window_handles.len = 2

    test_interactor.close_current_window()

    mock_driver.close.assert_called_once()
    mock_driver.switch_to_window.assert_called_once()


@mock.patch("selenium.webdriver")
def test_close_current_window_with_1_window(mock_driver):
    finder = Finder(mock_driver, "logger")
    interrogator = Interrogator(mock_driver, "logger", finder)
    waiter = Waiter(mock_driver, "logger", finder)
    test_interactor = Interactor(mock_driver, MagicMock(name="logger"), finder, interrogator, waiter)
    mock_driver.window_handles.len = 1

    test_interactor.close_current_window()

    mock_driver.close.assert_called_once()
    mock_driver.switch_to_window.assert_not_called()
