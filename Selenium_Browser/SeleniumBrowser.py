import os
import pickle
import sys
from typing import Callable, Any, Union, List, Optional, Tuple, Type, Dict

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException, \
    StaleElementReferenceException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

module_path: str = ''
try:
    module_path = os.path.dirname(os.path.realpath(__file__))
except NameError:
    module_path = os.path.dirname(os.path.abspath(sys.argv[0]))

path_append: str = os.path.dirname(module_path)
sys.path.append(path_append) if path_append not in sys.path else 0

try:
    from .HTMLPageElements import HTMLPageElements
    from .GetElementProps import GetElementProps
    from .XPathLookupProps import XPathLookupProps
    from .utils.utils import Files, Arrays, Utils, Jsons
    from .utils.utils.errors.Logger import LogStamps, Logger
    from .utils.utils.errors.ErrorHandler import ErrorHandler, ErrorCodes
    from .utils.utils.db import Errors
except ValueError:
    from Selenium_Browser import HTMLPageElements, GetElementProps, XPathLookupProps
    from Selenium_Browser.utils.utils import Files, Arrays, Utils, Jsons
    from Selenium_Browser.utils.utils.errors.Logger import Logger, LogStamps
    from Selenium_Browser.utils.utils.errors.ErrorHandler import ErrorCodes, ErrorHandler
    from Selenium_Browser.utils.utils.db import Errors

Point = Tuple[int, int]
WebType = Union[WebElement, WebDriver]
WebLookup = Union[None, List[WebElement], WebElement, str]
GetElementResp = Union[WebElement, str, None]
GetAllElementsResp = Union[List[GetElementResp], GetElementResp]
ElementLookup = Dict[str, GetElementResp]
OWebElement = Optional[WebElement]


class SeleniumBrowserProps(object):
    module_path: str
    path_to_chromedriver: str
    options: webdriver.ChromeOptions

    errors: Type[Errors]
    error_codes: ErrorCodes

    logger: ErrorHandler

    def __init__(self, main_module_path: str, errors: Type[Errors],
                 path_to_chromedriver: Optional[str] = None,
                 chrome_options: Optional[webdriver.ChromeOptions] = webdriver.ChromeOptions(),
                 headless: Optional[bool] = True, error_handler: Optional[ErrorHandler] = None):
        self.module_path = main_module_path
        self.path_to_chromedriver = \
            Utils.first_non_none(path_to_chromedriver, SeleniumBrowser.get_chromedriver_path(self.module_path))

        self.errors = errors
        self.error_codes = ErrorCodes(self.errors)
        self.logger = \
            Utils.first_non_none(error_handler, ErrorHandler(Files.concat(self.module_path, 'logs'), self.errors))

        if headless:
            chrome_options.add_argument('headless')

        chrome_options.add_argument('ignore-certificate-errors')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        self.options = chrome_options  # Save options to global variable


class BrowseReq(object):
    url: str
    props: XPathLookupProps
    present_function: Callable[[], bool]

    def __init__(self, url: str, props: Optional[XPathLookupProps] = None, present_function: Callable[[], bool] = None):
        self.url = url
        self.props = Utils.first_non_none(props, XPathLookupProps.any_element_check())
        self.present_function = present_function


class BrowseElementsReq(BrowseReq):
    def __init__(self, page_elements: HTMLPageElements):
        super().__init__(page_elements.url, props=page_elements.load_check)


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

    errors: Type[Errors]
    error_codes: ErrorCodes

    logger: ErrorHandler

    def __init__(self, props: SeleniumBrowserProps):
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

        :param chrome_options?: Optional - A Selenium.ChromeOptions class, used to set
            options for Chrome's headless browser
        """
        self.errors = props.errors
        self.logger = props.logger
        self.error_codes = self.logger.codes
        self.options = props.options  # Save options to global variable

        # Initialize internal selenium browser with given chromedriver path and chrome_options
        self.path_to_chromedriver = \
            Utils.first_non_none(props.path_to_chromedriver, SeleniumBrowser.get_chromedriver_path(props.module_path))

        self.start_browser()

    def save_cookies(self, url: str, load_check: XPathLookupProps, file: Files) -> bool:
        if self.browse_to_url(BrowseReq(url, props=load_check)):
            pickle.dump(self.browser.get_cookies(), open(file.full_path, 'wb'))
            return True
        return False

    # noinspection PyBroadException
    def load_cookies(self, url: str, load_check: XPathLookupProps, file: Files) -> bool:
        if self.browse_to_url(BrowseReq(url, props=load_check)):
            # TODO: Figure out what error pickle throughs and catch appropriately
            try:
                cookies: List[dict] = pickle.load(open(file.full_path, 'rb'))
            except Exception:
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

        while 'headless' in self.options.arguments:
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
        # self.browser = webdriver.PhantomJS()

    def restart_browser(self) -> None:
        self.browser.quit()
        self.browser = webdriver.Chrome(self.path_to_chromedriver, chrome_options=self.options)
        # self.browser = webdriver.PhantomJS()

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
    def browse_to_url(self, req: BrowseReq) -> bool:
        """
        Sets the current url to the one passed. Will run a search command using props
        and return when the page has fully loaded.

        Helpful when using a headless browser to go to a page and need a specific
        link or button on the page being loaded

        :param req:
        :return: True if page was loaded successfully, False otherwise
        """
        url = req.url

        default_error: Errors = self.error_codes.selenium_err({
            'input_key': url,
            'uid': 'Web Page Load Failed - {}'.format(url),
            'error_code': ErrorCodes.selenium.connect,
            'message': 'The page at {} could not be loaded'.format(url)
        })

        try:
            self.browser.get(url)
            self.load_frame_elements(delay=5)
        except WebDriverException as e:
            self.restart_browser()
            print(e)
            return False
        except Exception as e:
            default_error.message += '\n{}\n'.format(e)
            self.logger.output_err(default_error)
            return False

        self.browser.switch_to.default_content()

        if req.present_function is not None:
            return req.present_function()
        else:
            props = req.props
            return self.check_absence_of_element(props) \
                if props.check_absence else self.check_presence_of_element(props)

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
            self.logger.output_err(props.error)
            return False
        return True

    # TODO: Create check_presence_of_one/all helper method
    def check_presence_of_one(self, props: List[XPathLookupProps],
                              main_prop: Optional[XPathLookupProps] = None) -> bool:
        main_prop = props[0] if main_prop is None else main_prop
        lookup_statements: List[Callable[[], List[WebElement]]] = [x.find_elements(self.browser) for x in props]
        check_statement: Callable[[], bool] = lambda driver: SeleniumBrowser._check_results(lookup_statements)

        if main_prop.error is None:
            main_prop.error = self.error_codes.selenium_err({
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
        check_statement: Callable[[], bool] = lambda driver: SeleniumBrowser._check_all_results(lookup_statements)

        if main_prop.error is None:
            main_prop.error = self.error_codes.selenium_err({
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
            props.error = self.error_codes.selenium_err({
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
            props.error = self.error_codes.selenium_err({
                'input_key': self.browser.title,
                'uid': 'Element was found - {}'.format(props.search_param),
                'message': 'The element with XPath {} at {} was found after waiting {} '
                           'seconds on the web page'.format(props.search_param, self.browser.title, props.delay)
            })

        check_statement: Callable[[], bool] = ec.invisibility_of_element_located(props.get_element_lookup())
        return self.check_presence_helper(check_statement, props)

    def create_element_lookup(self, key: str, props: GetElementProps, lookup: Optional[dict] = None,
                              element: OWebElement = None) -> ElementLookup:
        lookup = Utils.first_non_none(lookup, {})
        lookup[key] = self.get_html_elements(props, element=element)
        return lookup

    def create_batch_element_lookup(self, values: List[str], props: List[GetElementProps],
                                    element: OWebElement = None) -> ElementLookup:
        Arrays.equal_length(props, values, raise_error=True)
        lookup: dict = {}
        for idx in range(len(values)):
            self.create_element_lookup(values[idx], props[idx], lookup=lookup, element=element)
        return lookup

    def get_html_elements(self, props: GetElementProps, element: OWebElement = None) -> GetAllElementsResp:
        elements: GetAllElementsResp = self.get_html_elements_helper(props, element)
        for element_idx in range(len(elements)):
            element = elements[element_idx]
            if props.prefer_text:
                elements[element_idx] = SeleniumBrowser.get_elements_text(element)
        return Arrays.delistify(elements)

    def get_batch_html_elements(self, props: List[GetElementProps], element: OWebElement = None) -> GetAllElementsResp:
        return [self.get_html_elements(x, element) for x in props]

    @staticmethod
    def get_elements_text(elements: WebLookup):
        if isinstance(elements, list):
            for element_idx in range(len(elements)):
                element = elements[element_idx]
                if element is not None:
                    elements[element_idx] = element.text
        elif elements is not None:
            elements = elements.text
        return elements

    def get_html_elements_helper(self, props: GetElementProps, element: OWebElement = None) -> WebLookup:
        """
        Returns an html element from the browser. If element is specified, will search
        for the html element with element. Otherwise, searches are conducted on the browser

        :param element:
        :param props: A class to dictate what kind of search to perform
        :return: The HTML element or None is none is found
        """
        browser = Utils.first_non_none(element, self.browser)
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

            if output is not None and props.grab_attrib is not None:
                output = [x.get_attribute(props.grab_attrib) for x in output]

            if len(output) == 0:
                return None
            elif len(output) == 1:
                return output if props.force_list else output[0]
            elif props.ignore_list:
                return output[0]
            else:
                return output
        except NoSuchElementException:
            return None

    def get_html(self, element: Optional[WebElement] = None):
        if element is not None:
            return element.get_attribute("outerHTML")
        else:
            get_html: WebElement = self.browser.find_element_by_xpath('//*')
            return self.browser.page_source if get_html is None else get_html.get_attribute('outerHTML')

    def load_frame_elements(self, delay: int = 20):
        frames: List[WebElement] = \
            Arrays.listify(self.get_html_elements(GetElementProps(by_tag='frame')))
        frames += Arrays.listify(self.get_html_elements(GetElementProps(by_tag='iframe')))
        if len(frames) == 0:
            return True

        for frame in frames:
            try:
                wait = ec.frame_to_be_available_and_switch_to_it(frame)
                WebDriverWait(self.browser, delay).until(wait)
            except StaleElementReferenceException:
                pass
            except TimeoutException:
                pass

    # TODO: Get rid of noinspection via testing
    # noinspection PyBroadException
    def try_submit(self, button: WebElement, javascript: str = None):
        try:
            button.click()
        except Exception:
            pass

        try:
            button.send_keys(Keys.ENTER)
            button.send_keys(Keys.RETURN)
        except Exception:
            pass

        if javascript is not None:
            try:
                self.browser.execute_script(javascript)
            except Exception:
                pass

        try:
            for x in range(20):
                button.click()
        except Exception:
            return

    # TODO: Maybe move to utils class?
    @staticmethod
    def _check_results(statements: List[Callable[[], Any]]) -> bool:
        result: bool = False
        for statement in statements:
            result = result or statement()
            if result:
                break
        return result

    @staticmethod
    def _check_all_results(statements: List[Callable[[], Any]]) -> bool:
        result: bool = True
        for statement in statements:
            result = result and statement()
            if not result:
                break
        return result

    @staticmethod
    def get_chromedriver_path(main_module_path: str):
        plat = sys.platform
        if plat == 'linux':
            return Files.concat(main_module_path, 'chromedriver', 'linux')
        elif plat == 'darwin':
            return Files.concat(main_module_path, 'chromedriver', 'osx')
        else:
            return Files.concat(main_module_path, 'chromedriver', 'windows')
