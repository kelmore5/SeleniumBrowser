from typing import Union, Optional, Dict


class StringSearch(object):
    start_sub: str
    end_sub: str

    def __init__(self, start_sub: str, end_sub: Optional[str] = None):
        self.start_sub = start_sub
        self.end_sub = end_sub

    def parse(self, string: str) -> Union[str, None]:
        if self.start_sub in string:
            string = string[string.index(self.start_sub) + len(self.start_sub):]

            if self.end_sub is not None and self.end_sub in string:
                return string[:string.index(self.end_sub)]
            return string
        return None


class GetElementProps(object):
    """
    A property class to carry out element retrievals within a web page.
    Used for functions within the SeleniumBrowser class. Simply set
    one of the global variables below to perform the search

    by_class = Search for elements by class name
    by_id = Search for elements by id
    by_tag = Search for elements by tag name
    by_xpath = Search for elements by xpath
    """
    inner_elements: Dict[str, 'GetElementProps']

    prefer_text: bool
    grab_attrib: str
    ignore_list: bool
    force_list: bool

    by_class: str
    by_id: str
    by_tag: str
    by_xpath: str

    def __init__(self, by_xpath: str = None, by_class: str = None, by_id: str = None, by_tag: str = None,
                 prefer_text: Optional[bool] = False, grab_attrib: Optional[str] = None,
                 ignore_list: Optional[bool] = False, force_list: Optional[bool] = False):
        """
        Initializes the property class.

        :param by_class: Specifies a search by class
        :param by_id: Specifies a search by an HTML element's ID
        :param by_tag: Specifies a searcy by tag name
        :param by_xpath: Specifies a search by xpath
        """
        self.inner_elements = {}

        self.by_class = by_class
        self.by_id = by_id
        self.by_tag = by_tag
        self.by_xpath = by_xpath

        self.force_list = force_list
        self.ignore_list = ignore_list
        self.prefer_text = prefer_text
        self.grab_attrib = grab_attrib

    def __copy__(self) -> 'GetElementProps':
        return GetElementProps(by_class=self.by_class, by_id=self.by_id, by_xpath=self.by_xpath,
                               by_tag=self.by_tag, prefer_text=self.prefer_text, grab_attrib=self.grab_attrib,
                               ignore_list=self.ignore_list, force_list=self.force_list)

    def get_ref(self):
        if self.by_id is not None:
            return self.by_id
        elif self.by_class is not None:
            return self.by_class
        elif self.by_tag is not None:
            return self.by_tag
        else:
            return self.by_xpath

    @staticmethod
    def parent():
        return GetElementProps(by_xpath='.//')
