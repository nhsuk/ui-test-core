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
    :param context:
    :param scenario:
    :return:
    """
    if(context.url in [context.live_url, context.beta_url] or
            context.browser.current_url in [context.live_url, context.beta_url]):
        scenario.skip("Skipped run against Live when tagged with @fixture.NoRunInLive")
