10.6.1 / 2025-03-17
===================
- Improved `remove_invalid_characters` function to handle a full range of invalid characters, ensuring all special characters like spaces, slashes, colons, and question marks are correctly removed or replaced

10.6.0 / 2024-07-29
===================
- Fix for concurrency issue in taking and moving screenshots
  - Updated BrowserHandler.take_screenshot so that it will store the name of the file that has been saved in a property
      on the class itself.
  - Updated BrowserHandler.move_screenshots_to_folder to take an optional parameter, file_names, that (if provided) will
      override the default behaviour of moving all .png files from the source to the target folder, and instead will 
      only move files matching the file_names from the source to the target folder.

10.5.0 / 2024-01-10
===================
- Added the ability to specify which _rules_ to use when running Axe reports on a page. This is not a breaking change as the default is still running the report on the full page using default rules
  - An example of filtering rules using tags: rule_filter={"runOnly": ['wcag2a', 'wcag2aa']} - this will run WCAG
             2.0 Level A and Level AA rules only
- Full Axe accessibility report is now returned regardless of whether violations are found

10.4.1 / 2023-08-18
===================
- Updated Readme to cover work around for using 10.4.0 with Chromium in Linux

10.4.0 / 2023-08-16
===================
- Updated Selenium to version 4.11.2 to enable Chrome For Testing support

10.3.2 / 2023-06-23
===================
- Updated Selenium to version 4.10.0
    - No longer required to _manually_ download ChromeDriver, GeckoDriver or EdgeDriver and add to browser_executables folder - **Selenium will handle this for you** (since v4.6.0)
- Updated required packages to the latest versions in setup.py

10.3.1 / 2022-12-08
===================
- Resolved string formatting issue which prevented the 'for_element_to_have_attribute' method from working

10.3.0 / 2022-11-22
===================
- Axe-core is now fully integrated in to the uitestcore framework
    - No longer necessary to pip install _axe-selenium-python-nhsuk_ in your test pack, the framework handles this
    - No longer necessary to initialise Axe in your test pack, the framework handles this

10.2.0 / 2022-11-03
===================
- Added the ability to include/exclude elements when running Axe reports on a page. This is not a breaking change as the default is still running the report on the full page

10.1.0 / 2022-11-02
===================
- No longer necessary to define the 'context.browser_options' variable in _environment.py_ if you do not intend on using 'browser_options' in the config
- Updated required packages to the latest versions in setup.py
- Updated required packages to the latest versions in azure-pipelines.yml

10.0.1 / 2022-08-19
===================
- Bug fix - You can now set the browser via command line parameters 
- If setting browser via command line, using _-Dbrowser=chrome_ will set context.browser_name to "chrome"

10.0.0 / 2022-08-01
===================
- Added support for attaching files to build runs (previously this was only release runs)
    - The `attach_files()` method has been refactored out to `attach_files_release()` and `attach_files_build()`. These new methods **no longer accept cli system arguments** for the release/build id and access token being used. Instead these parameters should be given directly from the calling code.
    - Updated to the latest API version for Azure GET requests

9.1.0 / 2022-07-22
===================
- Added support for setting extra arguments against the webdriver browser options
    - These can be given as a list set to context.browser_options
- Geckodriver executable path removed for Linux

9.0.0 / 2022-07-15
===================
- Upgrade to Selenium 4
    - This might require a change in any test pack that uses deprecated Selenium functions such as 'find_element_by_id'
    - Framework functions have been updated to work with Selenium 4.3.0 including the unit tests
- Added support for Edge for Windows and macOS 
- Added support for Firefox for macOS
- New Interrogator functions
    - 'get_list_of_texts' - returns a list when you pass a generic locator
    - 'get_list_of_attributes' - returns a list when you pass in a generic locator and attribute

8.0.0 / 2022-03-15
===================
- Added Axe reporting functionality
- Added ability to run non-headless tests on macOS using Chrome 
- Updated invalid characters to be replaced in 'remove_invalid_characters' function 

7.0.2 / 2021-11-29
===================
- Updated required packages to the latest versions in setup.py
- Updated required packages to the latest versions in azure-pipelines.yml

7.0.1 / 2021-06-16
===================
- Updated required packages to the latest versions in setup.py

7.0.0 / 2020-01-22
===================
- Added logic for the is_element_visible function which reduces implicit wait when no wait parameter is passed to the function
- This might require a change in any test packs due to timing changes

6.0.1 / 2019-11-13
===================
- Completed feature #16 - added logging when finding elements

6.0.0 / 2019-10-31
===================
- Fixed Bug #22 - context.browser can be both a browser name and a webdriver object
- Required change in any test packs
    - Whenever context.browser is expected to be a string e.g. when setting it from the config file, this should be
    changed to context.browser_name

5.1.1 / 2019-10-07
===================
- Add support for Firefox
- Handle unknown browser name when opening the browser

5.0.0 / 2019-10-01
===================
- Rename screenshots_api to attachments_api
- Parameterise organisation name in attachments_api
- Remove all other references to NHS in code

4.2.0 / 2019-09-26
===================
- Add function to interactor to clear all cookies

4.1.0 / 2019-09-24
===================
- Update screenshots code to handle slashes in file name

4.0.0 / 2019-09-20
===================
- Changed logging so that it was an optional argument when instantiating BasePage
- Created auto_log decorator for helper classes

3.3.5 / 2019-09-13
===================
- Adding pull request template
- Starting change log

3.3.3 / 2019-09-12
===================
- Fix close_current_window

3.2.4 / 2019-09-05
===================
- Changed the screenshots functionality to emit azure warnings and errors instead of failures when past test results 
were reporting ghost test failures

3.2.0 / 2019-09-04
===================
- Added unit test coverage and linting checks to build

3.0.0 / 2019-08-28
===================
- Removed Behave fixture and dependencies

2.6.0 / 2019-08-28
===================
- Create interact method to switch out of frame - switch_to_default_content()

2.0.0 / 2019-08-01
===================
- assert_no_failures function in custom_assertion