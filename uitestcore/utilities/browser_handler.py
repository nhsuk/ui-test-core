import json
import os
import platform
import shutil
from pathlib import Path
from axe_selenium_python import Axe
from selenium import webdriver
from uitestcore.utilities.config_handler import parse_config_data
from uitestcore.utilities.datetime_handler import get_current_datetime
from uitestcore.utilities.string_util import remove_invalid_characters

SCREENSHOTS_PATH = "screenshots"


class BrowserHandler:
    """
    This class performs any necessary tasks related to the browser
    """

    saved_screenshot_file_names = []

    @staticmethod
    def set_browser_size(context):
        """
        Sets the browser window to the required size e.g. maximized
        :param context: the test context instance
        """
        if context.maximize_browser:
            context.browser.maximize_window()

    @staticmethod
    def prepare_browser(context):
        """
        Set up the browser based on the config options
        :param context: the test context instance
        """
        # Check if we have any command line parameters to parse
        parse_config_data(context)

        # Check the Browser specified in config and load the Selenium Web Driver
        open_browser(context)

        # Set Implicit Wait on Selenium Driver
        context.browser.implicitly_wait(context.implicit_wait)

        # Check if Maximize Browser Flag has been activated
        BrowserHandler.set_browser_size(context)

    @classmethod
    def take_screenshot(cls, driver, description):
        """
        Save a screenshot of the browser window - should be used after a test fails
        :param driver: the browser driver
        :param description: information about the screenshot to be added to the file name
        :return: boolean representing whether saving the screenshot succeeded
        """
        window_width = driver.get_window_size()["width"]
        window_height = driver.get_window_size()["height"]
        scroll_height = driver.execute_script("return document.body.scrollHeight")

        # Set the browser to the full height of the page so that everything is captured
        if scroll_height > window_height:
            driver.set_window_size(window_width, scroll_height)

        # Create the screenshots folder
        if not os.path.exists(SCREENSHOTS_PATH):
            os.makedirs(SCREENSHOTS_PATH)

        # Create a file name and ensure it is not too long
        timestamp = get_current_datetime().strftime("%Y-%m-%d_%H.%M.%S.%f")
        description = remove_invalid_characters(description)
        file_name = f"{SCREENSHOTS_PATH}/{timestamp}_{description}"
        file_name = (file_name[:100] + "---.png") if len(file_name) > 100 else file_name + ".png"

        # Save the screenshot
        result = driver.save_screenshot(file_name)

        # Reset the browser size if it was changed
        if scroll_height > window_height:
            driver.set_window_size(window_width, window_height)

        if result:
            cls.saved_screenshot_file_names.append(file_name)
        return result

    @staticmethod
    def move_screenshots_to_folder(folder_name, file_names=None):
        """
        Create a new folder and move all screenshots from the root screenshot folder into it (to be run at end of test)
        :param folder_name: the name of the folder into which the screenshots should be moved
        :param file_names: (optional) the name of the files to be moved. Default None. If None, then move any files
        ending with .png. Otherwise, move any files that match the given saved_screenshot_file_names.
        """
        folder_name = remove_invalid_characters(folder_name)
        source = f"{SCREENSHOTS_PATH}/"
        destination = source + folder_name
        files = os.listdir(source)

        if not os.path.exists(destination):
            os.makedirs(destination)

        for file in files:
            if file_names is None:
                if file.endswith(".png"):
                    shutil.move(source + file, destination)
            else:
                if any(file in f for f in file_names):
                    shutil.move(source + file, destination)

    @staticmethod
    def run_axe_accessibility_report(context, element_filter=None, rule_filter=None):
        """
        Run Axe accessibility report on the current page and output a file containing violations if found. Returns the
        full Axe accessibility report regardless of whether violations are found.

        :param context: the test context instance. The context should include the Scenario name (context.scenario_name).
        :param element_filter: specify which elements to include/exclude from the run, the default is None. An example
            of include using CSS: element_filter={"include": [["#nhsuk-cookie-banner"]]}. An example of exclude using
            CSS: element_filter={"exclude": [["#nhsuk-cookie-banner"], [".footer"]]}. For more details about this
            parameter, see https://github.com/dequelabs/axe-core/blob/master/doc/API.md#context-parameter.
        :param rule_filter: specify which rules to use in the run, the default is None (use the default rules). An
            example of filtering rules using tags: rule_filter={"runOnly": ['wcag2a', 'wcag2aa']} - this will run WCAG
            2.0 Level A and Level AA rules only. For more details about this parameter, see
            https://github.com/dequelabs/axe-core/blob/master/doc/API.md#options-parameter.
        :return: the full Axe accessibility report for the page tested.
        """
        try:
            context.scenario_name
        except AttributeError:
            context.scenario_name = "No Scenario name passed to function"

        # Initialise and pass the driver/browser instance to the Axe class
        context.axe = Axe(context.browser)

        # Inject axe-core javascript into page
        context.axe.inject()
        # Run axe accessibility checks
        axe_results = context.axe.run(context=element_filter, options=rule_filter)
        # Checks for violations and adds them to a text file if they exist
        if len(axe_results["violations"]) > 0:
            write_axe_violations_to_file(context, axe_results)
        return axe_results


def write_axe_violations_to_file(context, results):
    Path("axe_reports/violations").mkdir(parents=True, exist_ok=True)
    with open("axe_reports/violations/violations.txt", "a+", encoding="utf-8") as violations_file:
        violations_file.write(f"{'=' * 75}\n\n\n"
                              f"Scenario name: {context.scenario_name}\n"
                              f"URL: {results['url']}\n"
                              f"Page title: {context.axe.selenium.title}\n"
                              f"Timestamp: {results['timestamp']}\n"
                              f"Browser: {context.axe.selenium.capabilities['browserName']} "
                              f"{context.axe.selenium.capabilities['browserVersion']}\n"
                              f"axe-core version: {results['testEngine']['version']}\n\n"
                              f"{context.axe.report(results['violations'])}")


def open_browser(context):
    """
    Open the required browser
    :param context: the test context instance
    """
    if context.browser_name.lower() == "chrome":
        open_chrome(context)

    elif context.browser_name.lower() == "edge":
        open_edge(context)

    elif context.browser_name.lower() == "firefox":
        open_firefox(context)

    elif context.browser_name.lower() == "browserstack":
        start_browserstack(context)

    else:
        raise ValueError(f"Browser '{context.browser_name}' not supported")


def open_chrome(context):
    """
    Open the Chrome browser
    :param context: the test context instance
    """
    chrome_options = webdriver.ChromeOptions()

    if platform.system() != 'Windows' and platform.system() != 'Darwin':
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1420,1080")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")

    # Add config browser options to chrome options
    chrome_options = add_browser_options(context, chrome_options)

    context.browser = webdriver.Chrome(options=chrome_options)

    BrowserHandler.set_browser_size(context)


def open_edge(context):
    """
    Open the Edge browser
    :param context: the test context instance
    """
    edge_options = webdriver.EdgeOptions()

    if platform.system() != 'Windows' and platform.system() != 'Darwin':
        edge_options.add_argument("--no-sandbox")
        edge_options.add_argument("--window-size=1420,1080")
        edge_options.add_argument("--headless")
        edge_options.add_argument("--disable-gpu")

    # Add config browser options to edge options
    edge_options = add_browser_options(context, edge_options)

    context.browser = webdriver.Edge(options=edge_options)

    BrowserHandler.set_browser_size(context)


def open_firefox(context):
    """
    Open the Firefox browser
    :param context: the test context instance
    """
    firefox_options = webdriver.FirefoxOptions()

    if platform.system() != 'Windows' and platform.system() != 'Darwin':
        firefox_options.add_argument("--headless")

    # Add config browser options to firefox options
    firefox_options = add_browser_options(context, firefox_options)

    context.browser = webdriver.Firefox(options=firefox_options)

    BrowserHandler.set_browser_size(context)


def add_browser_options(context, browser_options):
    try:
        for option in context.browser_options or []:
            browser_options.add_argument(option)
    except AttributeError:
        print("No config browser_options detected and the variable 'context.browser_options' is not defined")

    return browser_options


def start_browserstack(context):
    """
    Start Browserstack with the required options
    :param context: the test context instance
    """
    config_file = os.environ['CONFIG_FILE'] if 'CONFIG_FILE' in os.environ else 'config/BrowserStackConfig.json'
    task_id = int(os.environ['TASK_ID']) if 'TASK_ID' in os.environ else 0

    with open(config_file) as data_file:
        config = json.load(data_file)

    browserstack_username = os.environ['BROWSERSTACK_USERNAME'] if 'BROWSERSTACK_USERNAME' in os.environ \
        else config['user']
    browserstack_access_key = os.environ['BROWSERSTACK_ACCESS_KEY'] if 'BROWSERSTACK_ACCESS_KEY' in os.environ \
        else config['key']
    desired_capabilities = config['environments'][task_id]
    for key in config["capabilities"]:
        if key not in desired_capabilities:
            desired_capabilities[key] = config["capabilities"][key]
    context.browser = webdriver.Remote(
        desired_capabilities=desired_capabilities,
        command_executor=f"https://{browserstack_username}:{browserstack_access_key}@{config['server']}/wd/hub"
    )
