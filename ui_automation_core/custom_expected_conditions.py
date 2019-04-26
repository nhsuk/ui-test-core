"""
Create custom expected conditions in here
See these links for more details:
    https://selenium-python.readthedocs.io/api.html#module-selenium.webdriver.support.expected_conditions
    http://www.teachmeselenium.com/2018/04/07/python-selenium-waits-writing-own-custom-wait-conditions/
"""
import time
from selenium.webdriver.support import wait


class BrowserIsReady:
    """
    This condition uses JavaScript to check the documents ready state is 'complete'
    Has an initial wait to avoid false positive, gives browser a chance to refresh
    """

    def __init__(self):
        pass

    def __call__(self, driver):
        time.sleep(wait.POLL_FREQUENCY)
        return driver.execute_script("return document.readyState") == "complete"
