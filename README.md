# UiTestCore

This package helps with writing UI tests by providing a wrapper around Selenium and other useful functions. UiTestCore was designed with Page Object Model in mind, and makes it easy to create an acceptance test pack without the need to write any Selenium code.<br><br>
The repository for this project can be found on GitHub: https://github.com/nhsuk/ui-test-core

### Example

The below example shows how you can create a class representing a web page, in this case a login page.

```python
from uitestcore.page import BasePage
from uitestcore.page_element import PageElement
from selenium.webdriver.common.by import By


class MyLoginPage(BasePage):

    # Define elements to interact with
    header_logo = PageElement(By.ID, "company-logo")
    username_field = PageElement(By.ID, "input-user")
    password_field = PageElement(By.CLASS_NAME, "field-password")
    login_button = PageElement(By.XPATH, "//button[text()='Login']")

    def open_login_page(self):
        self.interact.open_url("https://mysite.com/login")
        self.wait.for_page_to_load()

    def logo_visible(self):
        return self.interrogate.is_element_visible(self.header_logo)

    def enter_username(self, username):
        self.interact.enter_text(self.username_field, username)

    def enter_password(self, password):
        self.interact.enter_text(self.password_field, password)

    def click_login_button(self):
        self.interact.click_element(self.login_button)
```

The "BasePage" class is provided so that any page classes in the test pack can inherit from it, giving access to many useful functions which are separated into "find", "interrogate", "interact" and "wait". The "PageElement" class is used to define any elements which your tests need to interact with, so they can be reused without needing to remember whether you're looking for a class, ID etc (all Selenium selector types are supported).<br><br>
The above page class could then be used in the test steps to perform any required actions and assertions.
You must supply a [selenium.webdriver](https://selenium-python.readthedocs.io/api.html) driver object when instantiating the page


```python
    login_page = MyLoginPage(driver)
    login_page.open_login_page()
```

### Installation
This package is located on PyPI: https://pypi.org/project/uitestcore/ - it can be installed in the usual way i.e. `pip install uitestcore`

The easiest way to include this package in your project is by adding it to your requirements.txt. 
Here is an example of the line which should be added to this file, we recommend using a specific version but it's your call: 

`uitestcore==3.3.0`

### Deployment to PyPI
PyPI deployment is configured in the release pipeline of the NHS.UK Azure Devops project. Any changes merged into master will be automatically deployed to PyPI, and any changes pushed to a branch starting with "test/" will be automatically deployed to TestPyPI.


### License

This project is licensed under the MIT License - see the LICENSE.md file for details

### Dependencies

The package dependencies along with links to their licenses are as follows:


certifi - http://mozilla.org/MPL/2.0/<br>
chardet - https://github.com/chardet/chardet/blob/master/LICENSE<br>
idna - https://github.com/kjd/idna/blob/master/LICENSE.rst<br>
pyhamcrest - https://github.com/hamcrest/PyHamcrest/blob/master/LICENSE.txt<br>
python-dateutil - https://github.com/pganssle/dateutil/blob/master/LICENSE<br>
requests - https://github.com/psf/requests/blob/master/LICENSE<br>
selenium - https://github.com/SeleniumHQ/selenium/blob/master/LICENSE<br>
six - https://github.com/benjaminp/six/blob/master/LICENSE<br>
urllib3 - https://github.com/urllib3/urllib3/blob/master/LICENSE.txt


## Contribute

Read our [contributing guidelines](CONTRIBUTING.md) to contribute to UiTestCore.