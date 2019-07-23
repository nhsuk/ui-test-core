import pytest
from hamcrest import assert_that, equal_to
from ui_automation_core.custom_fixtures import skip_execution_if_running_against_live_environment


class MockBrowser:
    def __init__(self):
        self.current_url = "test_current_url"


class MockContext:
    def __init__(self):
        self.url = "test_url"
        self.browser = MockBrowser()


class MockScenario:
    def __init__(self):
        self.events = []

    def skip(self, data):
        self.events.append(data)


def test_skip_execution_if_running_against_live_environment_handles_missing_urls():
    context = MockContext()
    scenario = MockScenario()

    try:
        skip_execution_if_running_against_live_environment(context, scenario)
    except Exception as e:
        pytest.fail(f"An exception occurred: {e}")

    assert_that(len(scenario.events), equal_to(0), "No scenario events should have been triggered")


def test_skip_execution_if_running_against_live_environment_skip_context_url():
    context = MockContext()
    scenario = MockScenario()

    context.live_url = "test_url"

    skip_execution_if_running_against_live_environment(context, scenario)

    assert_that(len(scenario.events), equal_to(1), "Only one scenario event should have been triggered")
    assert_that(scenario.events[0], equal_to("Skipped run against Live when tagged with @fixture.NoRunInLive"))


def test_skip_execution_if_running_against_live_environment_skip_current_url():
    context = MockContext()
    scenario = MockScenario()

    context.beta_url = "test_current_url"

    skip_execution_if_running_against_live_environment(context, scenario)

    assert_that(len(scenario.events), equal_to(1), "Only one scenario event should have been triggered")
    assert_that(scenario.events[0], equal_to("Skipped run against Live when tagged with @fixture.NoRunInLive"))
