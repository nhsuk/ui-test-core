from hamcrest import assert_that, equal_to
from selenium.webdriver.common.by import By
from uitestcore.page_element import PageElement


def test_add():
    page_heading = PageElement(By.XPATH, "//*[@class='heading']")

    page_heading_link = page_heading + "//a"

    assert_that(page_heading_link.locator_value, equal_to("//*[@class='heading']//a"), "Incorrect result when adding "
                                                                                       "value to existing PageElement")
