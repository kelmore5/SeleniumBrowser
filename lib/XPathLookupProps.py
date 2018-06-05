from typing import Optional, Union


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

    def __init__(self, html_element_type: str, search_param: str, delay: int = 30, done_message: Union[str, None] = ""):
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

    def __copy__(self) -> 'XPathLookupProps':
        props: XPathLookupProps = XPathLookupProps(self.html_element_type, self.search_param)
        props.delay = self.delay
        props.done_message = self.done_message
        return props
