import os

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from lib.XPathLookupProps import XPathLookupProps


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
        Since web pages change at a rate faster than bullets these days, the two main helper
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

    def __init__(self, path_to_chromedriver: str = os.getcwd() + "/chromedriver",
                 chrome_options: webdriver.ChromeOptions = webdriver.ChromeOptions()):
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
        self.display = Display(visible=0, size=(800, 600))  # Create the virtual display for the browser
        self.display.start()  # Start the display
        self.options = chrome_options  # Save options to global variable

        # Initialize internal selenium browser with given chromedriver path and chrome_options
        self.browser = webdriver.Chrome(path_to_chromedriver, chrome_options=chrome_options)

    def quit(self):
        """
        Stops the instance of Chrome and remove the virtual display that was created
        for this session
        """
        self.browser.quit()
        self.display.stop()

    def get_browser(self):
        """
        :return: The headless browser session via Selenium
        """
        return self.browser

    def browse_to_url(self, url: str, props: XPathLookupProps, absent: bool = False):
        """
        Sets the current url to the one passed. Will run a search command using props
        and return when the page has fully loaded.

        Helpful when using a headless browser to go to a page and need a specific
        link or button on the page being loaded

        :param url: The url to load
        :param props: Specifies what to look for on the page to be loaded to determine when
            it has fully been loaded. Especially helpful when trying to access a specific
            link or button a page
        :param absent: If True, checks for the absence of an element on the page being left. If False, checks
            for the presence of an element on the page being loaded. Default: False
        :return: True if page was loaded successfully, False otherwise
        """
        self.browser.get(url)
        if absent:
            return self.check_absence_of_element(props)
        else:
            return self.check_presence_of_element(props)

    def check_presence_of_element(self, props: XPathLookupProps):
        """
        Checks for the presence of an element within the web page. Used before accessing
        specific parts of a site or to confirm a page has fully loaded

        :param props: The properties of the HTML element to search for
        :return: True if element is present, False otherwise
        """
        try:
            element_present = ec.presence_of_element_located((props.html_element_type, props.search_param))
            WebDriverWait(self.browser, props.delay).until(element_present)
            print(self.browser.title + " is ready" if props.done_message == "" else props.done_message)
        except TimeoutException:
            print("Loading took too much time...")
            return False

        return True

    def check_absence_of_element(self, props: XPathLookupProps):
        """
        Contrary to check_presence_of_element (above), checks for the absence of an element
        within the web page. Can be helpful when pop-ups are involved.

        Used primarily to check if a page has completely loaded.

        :param props: The properties of the HTML element to search for
        :return: True if element is absent, False otherwise
        """
        try:
            element_present = ec.invisibility_of_element_located((props.html_element_type, props.search_param))
            WebDriverWait(self.browser, props.delay).until(element_present)
            print(self.browser.title + " is ready" if props.done_message == "" else props.done_message)
        except TimeoutException:
            print("Loading took too much time...")
            return False

        return True
