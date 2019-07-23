"""
Create any custom fixtures in here
Use them by adding the tags to the feature files
docs: https://behave.readthedocs.io/en/latest/fixtures.html
"""
from behave import fixture


@fixture
def skip_execution_if_running_against_live_environment(context, scenario):
    """
    Skip the current scenario if we are running against the Live URL
    https://stackoverflow.com/a/42721605
    :param context: the test context instance
    :param scenario: the Behave scenario instance
    """
    # Get the live and beta URLs, ensuring there are no errors if these don't exist on the context
    live_url = getattr(context, "live_url", "")
    beta_url = getattr(context, "beta_url", "")

    if context.url in [live_url, beta_url] or context.browser.current_url in [live_url, beta_url]:
        scenario.skip("Skipped run against Live when tagged with @fixture.NoRunInLive")
