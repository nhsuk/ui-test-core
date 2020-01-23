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