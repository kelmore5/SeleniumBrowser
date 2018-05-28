class GetElementProps(object):
    """
    A property class to carry out element retrievals within a web page.
    Used for functions within the SeleniumBrowser class. Simply set
    one of the global variables below to perform the search

    by_id = Search for elements by id
    by_class = Search for elements by class name
    by_xpath = Search for elements by xpath
    """

    by_id: str
    by_class: str
    by_xpath: str

    def __init__(self, by_id: str = None, by_class: str = None, by_xpath: str = None):
        """
        Initializes the property class.

        :param by_id: Specifies a search by an HTML element's ID
        :param by_class: Specifies a search by class
        :param by_xpath: Specifies a search by xpath
        """
        self.by_id = by_id
        self.by_class = by_class
        self.by_xpath = by_xpath
