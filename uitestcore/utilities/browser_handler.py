import json
import os
import shutil
from selenium import webdriver
from uitestcore.utilities.config_handler import parse_config_data
from uitestcore.utilities.datetime_handler import get_current_datetime
from uitestcore.utilities.string_util import remove_invalid_characters

SCREENSHOTS_PATH = "screenshots"


class BrowserHandler:
    """
    This class performs any necessary tasks related to the browser
    """

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

    @staticmethod
    def take_screenshot(driver, description):
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

        return result

    @staticmethod
    def move_screenshots_to_folder(folder_name):
        """
        Create a new folder and move all screenshots from the root screenshot folder into it (to be run at end of test)
        :param folder_name: the name of the folder into which the screenshots should be moved
        """
        folder_name = remove_invalid_characters(folder_name)
        source = f"{SCREENSHOTS_PATH}/"
        destination = source + folder_name
        files = os.listdir(source)

        if not os.path.exists(destination):
            os.makedirs(destination)

        for file in files:
            if file.endswith(".png"):
                shutil.move(source + file, destination)


def open_browser(context):
    """
    Open the required browser
    :param context: the test context instance
    """
    if context.browser.lower() == "chrome":
        open_chrome(context)

    elif context.browser.lower() == "firefox":
        open_firefox(context)

    elif context.browser.lower() == "browserstack":
        start_browserstack(context)

    else:
        raise ValueError(f"Browser '{context.browser}' not supported")


def open_chrome(context):
    """
    Open the Chrome browser
    :param context: the test context instance
    """
    if os.name == 'nt':
        context.browser = webdriver.Chrome(executable_path=r"./browser_executables/chromedriver.exe")

    else:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1420,1080")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")

        # No need to specify the executable as we're using one installed via pip in Dockerfile
        context.browser = webdriver.Chrome(chrome_options=chrome_options)

    BrowserHandler.set_browser_size(context)


def open_firefox(context):
    """
    Open the Firefox browser
    :param context: the test context instance
    """
    if os.name == 'nt':
        context.browser = webdriver.Firefox(executable_path=r"browser_executables/geckodriver.exe")

    else:
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.add_argument("--headless")

        # The Firefox driver (geckodriver) must be located in the "firefox" folder when running in Docker
        context.browser = webdriver.Firefox(executable_path=r"firefox/geckodriver", firefox_options=firefox_options)

    BrowserHandler.set_browser_size(context)


def start_browserstack(context):
    """
    Start Browserstack with the required options
    :param context: the test context instance
    """
    config_file = os.environ['CONFIG_FILE'] if 'CONFIG_FILE' in os.environ else 'config/BrowserStackConfig.json'
    task_id = int(os.environ['TASK_ID']) if 'TASK_ID' in os.environ else 0

    with open(config_file) as data_file:
        config = json.load(data_file)

    browserstack_username = os.environ['BROWSERSTACK_USERNAME']
    browserstack_access_key = os.environ['BROWSERSTACK_ACCESS_KEY']
    desired_capabilities = config['environments'][task_id]
    for key in config["capabilities"]:
        if key not in desired_capabilities:
            desired_capabilities[key] = config["capabilities"][key]
    context.browser = webdriver.Remote(
        desired_capabilities=desired_capabilities,
        command_executor="http://%s:%s@%s/wd/hub" % (browserstack_username, browserstack_access_key, config['server'])
    )
