# UiTestCore

This package helps with writing UI tests by providing a wrapper around Selenium and other useful functions. UiTestCore was designed with Page Object Model in mind, and makes it easy to create an acceptance test pack without the need to write any Selenium code.

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

### Unit tests and linting

The unit tests for this package can be found in the tests folder and are written using PyTest. Pylint is being used to ensure code qaulity.

### Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the tags on the repository. 

### License

This project is licensed under the MIT License - see the LICENSE.md file for details