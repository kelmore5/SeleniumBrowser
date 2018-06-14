import os
import pickle
import sys
from typing import Callable, Any, Union, List, Optional, Tuple

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

selenium_module_path: str = ''
try:
    selenium_module_path = os.path.dirname(os.path.realpath(__file__))
except NameError:
    selenium_module_path = os.path.dirname(os.path.abspath(sys.argv[0]))

path_append: str = os.path.dirname(selenium_module_path)
sys.path.append(path_append) if path_append not in sys.path else 0

from Selenium_Browser.GetElementProps import GetElementProps
from Selenium_Browser.XPathLookupProps import XPathLookupProps
from Selenium_Browser.utils.utils.errors.ErrorCodes import ErrorCodes
from Selenium_Browser.utils.utils.errors.ErrorHandler import ErrorHandler, Logger
from Selenium_Browser.utils.utils.db.Errors import Errors
from Selenium_Browser.utils.utils.Files import Files
from Selenium_Browser.utils.utils.Arrays import Arrays

Point = Tuple[int, int]
WebType = Union[WebElement, WebDriver]
WebLookup = Union[None, List[WebElement], WebElement]


# TODO: Probably going to have to go back to using XVFB....Some pages just don't load right without a display
class SeleniumBrowser(object):
    """
        A class to extend the functionality of Selenium's headless web browser,
        found here: https://github.com/SeleniumHQ/selenium.

        This is a small class right now and assumes the use of Chrome with Selenium.
        Therefore, it needs Chrome's WebDriver to work, found here:
        https://sites.google.com/a/chromium.org/chromedriver/downloads.

        This class includes things like initializing Selenium browser with default display
        properties and checking the absence or presence of an HTML element within a web page.

        Personally, I mostly use Selenium to crawl web pages, format data, and store information.
        There are also certain applications where login is required, which Selenium is great
        for crawling. Because of this, much of the work I used Selenium for has been visiting
        pages, clicking buttons or links, and then parsing or downloading data.

        Now, I mentioned the above because the main purpose of this helper class is an attempt to
        take out some of the guess work when using a headless browser (selenium or otherwise).
        Since web pages change at a rate faster than jets these days, the two main helper
        functions "check_presence_of_element" and "check_absence_of_element" are used before
        selecting elements on an HTML page.

        For example, a script written to download a web page today will inevitably change
        upon a future update. So, wherever there is a specific link that needs to be
        clicked on a page being parsed, the above functions give the user the ability to
        check the link for its existence before carrying out the rest of the script.

        Then, once said web page is updated, it should be easy to identify the parts of
        the script that need updating (if everything is being checked, like it should).

        This may seem like a lengthy description for such a small use case, but this class
        gives a basis for writing a web parser that once broken will at least identify
        areas of the website that have been updated, making said script adaptable.

        Hopefully in time this class will grow to include numerous handy functions to parse
        web pages accurately and efficiently.

        At the time, this is all I need.
    """
    default_pos: Point = (100, 50)

    width: int = 800
    height: int = 800

    path_to_chromedriver: str
    browser: webdriver.Chrome
    options: webdriver.ChromeOptions

    logger: Logger
    errors: ErrorHandler

    def __init__(self, path_to_chromedriver: str = Files.concat(os.getcwd(), 'chromedriver'),
                 chrome_options: webdriver.ChromeOptions = webdriver.ChromeOptions(),
                 headless: bool = True, errors: ErrorHandler = None):
        """
        Initializes the SeleniumBrowser class, ie creates an instance of selenium using
        Chrome with default properties to start a headless session.

        This class will start by creating a virtual display using the pyvirtualdisplay module,
        and then starting selenium's Chrome browser (to create a usable headless browser).

        Starts the browser with 0 visibility and size 800 x 600, but can be changed after
        initialization if need be.

        To initialize the class, the path to Chrome's WebDriver is needed (see above) and
        an optional ChromeOptions class from Selenium can be passed.

        The chrome_options arg can be used to set things like the download location
        for the browser or a proxy if needed.

        :param path_to_chromedriver: The path to the downloaded chromedriver file
            Default: current_working_directory + '/chromedriver'
        :param chrome_options?: Optional - A Selenium.ChromeOptions class, used to set
            options for Chrome's headless browser
        """
        self.errors = \
            errors if errors is not None else ErrorHandler(Files.concat(selenium_module_path, 'lib', 'logs'))
        self.logger = self.errors

        if headless:
            chrome_options.add_argument('headless')

        chrome_options.add_argument('ignore-certificate-errors')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        self.options = chrome_options  # Save options to global variable

        # Initialize internal selenium browser with given chromedriver path and chrome_options
        self.path_to_chromedriver = path_to_chromedriver
        self.start_browser()

    def save_cookies(self, url: str, load_check: XPathLookupProps, file: Files) -> bool:
        if self.browse_to_url(url, load_check):
            pickle.dump(self.browser.get_cookies(), open(file.full_path, 'wb'))
            return True
        return False

    def load_cookies(self, url: str, load_check: XPathLookupProps, file: Files) -> bool:
        if self.browse_to_url(url, load_check):
            # TODO: Figure out what error pickle throughs and catch appropriately
            try:
                cookies: List[dict] = pickle.load(open(file.full_path, 'rb'))
            except Exception as e:
                file.remove_if_exists()
                return False

            for cookie in cookies:
                self.browser.add_cookie(cookie)
            return True
        return False

    @staticmethod
    def get_chrome_position(point: Point) -> str:
        return '--window-position={},{}'.format(str(point[0]), str(point[1]))

    def move_screen_helper(self, pos: Point = None, size: Point = None, reload: bool = False, tiny: bool = False):
        pos: Point = self.default_pos if pos is None else pos
        if size is None and tiny:
            size = (50, 50)
        elif size is None:
            size = (self.width, self.height)

        self.move_reload(pos, reload)
        self.browser.set_window_size(size[0], size[1])

    def off_screen(self, reload: bool = False, tiny: bool = False):
        pos: Point = (-32000, -32000)
        self.move_screen_helper(pos=pos, reload=reload, tiny=tiny)

    def on_screen(self, reload: bool = False, tiny: bool = False):
        self.move_screen_helper(reload=reload, tiny=tiny)

    def move_reload(self, point: Point = None, reload: bool = False):
        self.clear_window_position()

        point = self.default_pos if point is None else point
        if reload:
            self.options.arguments.append(SeleniumBrowser.get_chrome_position(point))
            self.restart_browser()

        self.browser.set_window_position(point[0], point[1])

    def tiny(self, reload: bool = False):
        self.move_screen_helper(reload=reload, tiny=True)

    def normal(self, reload: bool = False):
        self.move_screen_helper(reload=reload, tiny=False)

    def show_browser(self, tiny: bool = False):
        self.clear_window_position()

        if 'headless' in self.options.arguments:
            self.options.arguments.remove('headless')
        self.options.set_headless(False)

        point: Point = self.default_pos
        self.options.add_argument(SeleniumBrowser.get_chrome_position(point))

        self.restart_browser()

        self.browser.set_window_position(point[0], point[1])
        self.tiny() if tiny else self.normal()

    def clear_window_position(self):
        args: List[str] = self.options.arguments
        check: str = 'window-position'
        remove_idxs: List[int] = []
        for idx in range(len(args)):
            arg: str = args[idx]
            if check in arg:
                remove_idxs.append(idx)
        Arrays.remove_indexes(self.options.arguments, remove_idxs)

    def hide_browser(self):
        self.clear_window_position()

        self.options.add_argument('headless')
        self.options.set_headless(True)
        self.restart_browser()

    def start_browser(self) -> None:
        self.browser = webdriver.Chrome(self.path_to_chromedriver, chrome_options=self.options)

    def restart_browser(self) -> None:
        self.browser.quit()
        self.browser = webdriver.Chrome(self.path_to_chromedriver, chrome_options=self.options)

    def quit(self) -> None:
        """
        Stops the instance of Chrome and remove the virtual display that was created
        for this session
        """
        self.browser.quit()

    def get_browser(self) -> webdriver.Chrome:
        """
        :return: The headless browser session via Selenium
        """
        return self.browser

    # TODO: Remove props all together and just use present function
    # TODO: Maybe add four methods for browse - just to clarify (like find_elements vs find_elements_tag_name)
    def browse_to_url(self, url: str, props: Optional[XPathLookupProps] = None, absent: Optional[bool] = False,
                      present_function: Callable[[], bool] = None) -> bool:
        """
        Sets the current url to the one passed. Will run a search command using props
        and return when the page has fully loaded.

        Helpful when using a headless browser to go to a page and need a specific
        link or button on the page being loaded

        :param present_function:
        :param url: The url to load
        :param props: Specifies what to look for on the page to be loaded to determine when
            it has fully been loaded. Especially helpful when trying to access a specific
            link or button a page
        :param absent: If True, checks for the absence of an element on the page being left. If False, checks
            for the presence of an element on the page being loaded. Default: False
        :return: True if page was loaded successfully, False otherwise
        """
        default_error: Errors = ErrorCodes.selenium_err({
            'input_key': url,
            'uid': 'Web Page Load Failed - {}'.format(url),
            'error_code': ErrorCodes.selenium.connect,
            'message': 'The page at {} could not be loaded'.format(url)
        })

        try:
            self.browser.get(url)
        except WebDriverException:
            return False
        except Exception as e:
            default_error.message += '\n{}\n'.format(e)
            self.errors.err(default_error)
            return False

        if present_function is not None:
            return present_function()
        elif props is not None:
            if absent:
                return self.check_absence_of_element(props)
            else:
                return self.check_presence_of_element(props)
        else:
            return False

    # noinspection PyArgumentList
    def check_presence_helper(self, presence_function: Any, props: XPathLookupProps) -> bool:
        """
        A helper function for checking the presence (or absence) of an element within a web page
        via Selenium browser.

        See functions check_presence_of_element and check_absence_of_element below for more details

        :param presence_function: Function from expected conditions (ec) of Selenium browser, should be
             either ec.presence_of_element_located or ec.invisibility_of_element_located. Used to check
             for absence or presence of an element within a web page after a given time
        :param props: The elements being searched for on the page, see class XPathLookupProps
        :return: True if page was loaded successfully, False otherwise
        """

        try:
            WebDriverWait(self.browser, props.delay).until(presence_function)
            if props.done_message is not None:
                self.logger.output(self.browser.title + " is ready" if props.done_message == "" else props.done_message)
        except TimeoutException:
            self.errors.err(props.error)
            return False
        return True

    # TODO: Maybe move to utils class?
    @staticmethod
    def check_results(statements: List[Callable[[], Any]]) -> bool:
        result: bool = False
        for statement in statements:
            result = result or statement()
            if result:
                break
        return result

    @staticmethod
    def check_all_results(statements: List[Callable[[], Any]]) -> bool:
        result: bool = True
        for statement in statements:
            result = result and statement()
            if not result:
                break
        return result

    # TODO: Create check_presence_of_one/all helper method
    def check_presence_of_one(self, props: List[XPathLookupProps],
                              main_prop: Optional[XPathLookupProps] = None) -> bool:
        main_prop = props[0] if main_prop is None else main_prop
        lookup_statements: List[Callable[[], List[WebElement]]] = [x.find_elements(self.browser) for x in props]
        check_statement: Callable[[], bool] = lambda driver: SeleniumBrowser.check_results(lookup_statements)

        if main_prop.error is None:
            main_prop.error = ErrorCodes.selenium_err({
                'input_key': self.browser.title,
                'uid': 'No Elements Found - {}'.format(main_prop.search_param),
                'message': 'None of the elements within the given list of {} elements were found on the page. '
                           'Starting element search ID: {}'.format(len(props), main_prop.search_param)
            })

        return self.check_presence_helper(check_statement, main_prop)

    def check_presence_of_all(self, props: List[XPathLookupProps],
                              main_prop: Optional[XPathLookupProps] = None) -> bool:
        main_prop = props[0] if main_prop is None else main_prop
        lookup_statements: List[Callable[[], List[WebElement]]] = [x.find_elements for x in props]
        check_statement: Callable[[], bool] = lambda driver: SeleniumBrowser.check_all_results(lookup_statements)

        if main_prop.error is None:
            main_prop.error = ErrorCodes.selenium_err({
                'input_key': self.browser.title,
                'uid': 'Some Elements Not Found - {}'.format(main_prop.search_param),
                'message': 'One or more of the elements within the given list of {} elements were not found on the '
                           'page. Starting element search ID: {}'.format(len(props), main_prop.search_param)
            })

        return self.check_presence_helper(check_statement, main_prop)

    def check_presence_of_element(self, props: XPathLookupProps) -> bool:
        """
        Checks for the presence of an element within the web page. Used before accessing
        specific parts of a site or to confirm a page has fully loaded

        :param props: The properties of the HTML element to search for
        :return: True if element is present, False otherwise
        """

        if props.error is None:
            props.error = ErrorCodes.selenium_err({
                'input_key': self.browser.title,
                'uid': 'Element was not found - {}'.format(props.search_param),
                'message': 'The element with XPath {} at {} could not be found after {} '
                           'seconds on the web page'.format(props.search_param, self.browser.title, props.delay)
            })

        check_statement: Callable[[], bool] = ec.presence_of_element_located(props.get_element_lookup())
        return self.check_presence_helper(check_statement, props)

    def check_absence_of_element(self, props: XPathLookupProps) -> bool:
        """
        Contrary to check_presence_of_element (above), checks for the absence of an element
        within the web page. Can be helpful when pop-ups are involved.

        Used primarily to check if a page has completely loaded.

        :param props: The properties of the HTML element to search for
        :return: True if element is absent, False otherwise
        """

        if props.error is None:
            props.error = ErrorCodes.selenium_err({
                'input_key': self.browser.title,
                'uid': 'Element was found - {}'.format(props.search_param),
                'message': 'The element with XPath {} at {} was found after waiting {} '
                           'seconds on the web page'.format(props.search_param, self.browser.title, props.delay)
            })

        check_statement: Callable[[], bool] = ec.invisibility_of_element_located(props.get_element_lookup())
        return self.check_presence_helper(check_statement, props)

    def get_html_elements(self, props: GetElementProps, element: Optional[WebType] = None) -> WebLookup:
        """
        Returns an html element from the browser. If element is specified, will search
        for the html element with element. Otherwise, searches are conducted on the browser

        :param props: A class to dictate what kind of search to perform
        :param element: Optional - An HTML element to search. Will search within
            internal browser if not specified
        :return: The HTML element or None is none is found
        """
        browser = self.browser if element is None else element
        try:
            output: List[WebElement] = []
            if props.by_id is not None:
                output = browser.find_elements_by_id(props.by_id)
            elif props.by_class is not None:
                output = browser.find_elements_by_class_name(props.by_class)
            elif props.by_tag is not None:
                output = browser.find_elements_by_tag_name(props.by_tag)
            elif props.by_xpath is not None:
                output = browser.find_elements_by_xpath(props.by_xpath)

            if len(output) == 0:
                return None
            elif len(output) == 1:
                return output[0]
            else:
                return output
        except NoSuchElementException:
            return None

    def get_html(self, element: WebElement = None):
        if element is not None:
            return element.find_element_by_xpath(".//*").get_attribute("outerHTML")
        else:
            return self.browser.page_source
