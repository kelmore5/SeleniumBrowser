import os
import sys
from typing import Optional, Union, Callable, List

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

selenium_module_path: str = ''
try:
    selenium_module_path = os.path.dirname(os.path.realpath(__file__))
except NameError:
    selenium_module_path = os.path.dirname(os.path.abspath(sys.argv[0]))

path_append: str = os.path.dirname(selenium_module_path)
sys.path.append(path_append) if path_append not in sys.path else 0

from Selenium_Browser import GetElementProps
from Selenium_Browser.utils.utils.db import Errors


# TODO: Create input for error message
class XPathLookupProps(object):
    """
    A property class to carry out xpath searches within a web page. Used for functions
    within the SeleniumBrowser class
    """
    html_element_type: str
    search_param: str
    delay: Optional[int]
    done_message: Optional[str]
    error: Optional[Errors]

    def __init__(self, html_element_type: Optional[str] = By.XPATH, search_param: Optional[str] = '//',
                 props: Optional[GetElementProps] = None, delay: int = 30,
                 done_message: Optional[str] = '', error: Optional[Errors] = None):
        """
        Initializes the property class.

        :param html_element_type: The HTML element type to search for on the web page (e.g. a, br, div, link, etc)
        :param search_param: An additional search param to identify a specific element
        :param delay: The amount of time to wait before launching a TimeoutException. Default: 30
        :param done_message: A message to be printed once the page has fully loaded.
            Default: "'Page Title' has loaded"
        """
        self.html_element_type = html_element_type
        self.search_param = search_param
        self.delay = delay
        self.done_message = done_message
        self.error = error

        if props is not None:
            self.update_from_props(props)

    def __str__(self):
        return 'XPathLookupProps<{}>'.format(str({'element': self.html_element_type, 'search': self.search_param}))

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def any_element_check() -> 'XPathLookupProps':
        return XPathLookupProps(By.XPATH, '//*')

    def update_from_props(self, props: 'GetElementProps'):
        if props.by_id is not None:
            self.html_element_type = By.ID
        elif props.by_class is not None:
            self.html_element_type = By.CLASS_NAME
        elif props.by_tag is not None:
            self.html_element_type = By.TAG_NAME
        else:
            self.html_element_type = By.XPATH

        self.search_param = props.get_ref()

    def find_element(self, driver: Union[WebDriver, WebElement]) -> Callable[[], WebElement]:
        return lambda: driver.find_element(self.html_element_type, self.search_param)

    def find_elements(self, driver: Union[WebDriver, WebElement]) -> Callable[[], List[WebElement]]:
        return lambda: driver.find_elements(self.html_element_type, self.search_param)

    def get_element_lookup(self):
        return self.html_element_type, self.search_param

    def __copy__(self) -> 'XPathLookupProps':
        props: XPathLookupProps = XPathLookupProps(self.html_element_type, self.search_param)
        props.delay = self.delay
        props.done_message = self.done_message
        return props
