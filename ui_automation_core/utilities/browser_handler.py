import datetime
import json
import os
import shutil
from selenium import webdriver
from ui_automation_core.utilities.logger import Logger
from ui_automation_core.utilities.string_util import remove_invalid_characters


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
        open_browser(context.browser, context)

        # Set Implicit Wait on Selenium Driver
        context.browser.implicitly_wait(context.implicit_wait)

        # Check if Maximize Browser Flag has been activated
        if context.maximize_browser:
            context.browser.maximize_window()

        # If the logging flag is false, disable the logger
        if not context.logging_flag:
            context.logger.disabled = True
        else:
            # Create the file to write logs to
            context.logger = Logger.create_log_file()

    @staticmethod
    def take_screenshot(driver, description):
        """
        Save a screenshot of the browser window - should be used after a test fails
        :param driver: the browser driver
        :param description: information about the screenshot to be added to the file name
        """
        window_width = driver.get_window_size()["width"]
        scroll_height = driver.execute_script("return document.body.scrollHeight")

        # Set the browser to the full height of the page so that everything is captured
        driver.set_window_size(window_width, scroll_height)

        # Create the screenshots folder
        if not os.path.exists(SCREENSHOTS_PATH):
            os.makedirs(SCREENSHOTS_PATH)

        # Create a file name and ensure it is not too long
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.%f")
        file_name = f"{SCREENSHOTS_PATH}/{timestamp}_{description}"
        file_name = remove_invalid_characters(file_name)
        file_name = (file_name[:100] + "---.png") if len(file_name) > 100 else file_name + ".png"

        # Save the screenshot
        driver.save_screenshot(file_name)

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


def parse_config_data(context):
    """
    Set any relevant config items on the context
    :param context: the test context instance
    """
    if context.config.userdata:

        for key, value in context.config.userdata.items():

            if key.lower() == 'base_url':
                context.url = value
                continue

            elif key.lower() == "logging_flag":

                if value.lower() == "false":
                    context.logging_flag = False
                    continue

                else:
                    context.logging_flag = True
                    continue

            elif key.lower() == "maximize_browser_flag":

                if value.lower() == "false":
                    context.maximize_browser = False
                    continue

                else:
                    context.maximize_browser = True
                    continue

            elif key.lower() == "browser":
                open_browser(value, context)

    else:
        print("No Command line Params detected, using Config file values")


def open_chrome(context):
    """
    Open the Chrome browser
    :param context: the test context instance
    """
    if os.name == 'nt':
        context.browser = webdriver.Chrome(executable_path=r"./browser_executables/chromedriver.exe")

    else:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=1420,1080')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        # no need to specify the executable as we're using one installed via pip in Dockerfile
        context.browser = webdriver.Chrome(chrome_options=chrome_options)

    BrowserHandler.set_browser_size(context)


def open_firefox(context):
    """
    Open the Firefox browser
    :param context: the test context instance
    """
    context.browser = webdriver.Firefox(executable_path=r"browser_executables/geckodriver.exe")
    BrowserHandler.set_browser_size(context)


def open_ie(context):
    """
    Open the Internet Explorer browser
    :param context: the test context instance
    """
    context.browser = webdriver.Ie(executable_path=r"browser_executables/IEDriverServer.exe")
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


def open_browser(browser_name, context):
    """
    Open the required browser
    :param browser_name: the name of the browser to open
    :param context: the test context instance
    """
    if browser_name.lower() == "chrome":
        open_chrome(context)

    elif browser_name.lower() == "firefox":
        open_firefox(context)

    elif browser_name.lower() == "ie":
        open_ie(context)

    elif browser_name.lower() == "browserstack":
        start_browserstack(context)
