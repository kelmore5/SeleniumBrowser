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
