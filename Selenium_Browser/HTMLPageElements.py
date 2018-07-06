import os.path
import sys
from typing import Union, Dict

module_path: str = ''
try:
    module_path = os.path.dirname(os.path.realpath(__file__))
except NameError:
    module_path = os.path.dirname(os.path.abspath(sys.argv[0]))

path_append: str = os.path.dirname(module_path)
sys.path.append(path_append) if path_append not in sys.path else 0

try:
    from .XPathLookupProps import XPathLookupProps
    from .GetElementProps import GetElementProps
except ValueError:
    from Selenium_Browser import XPathLookupProps, GetElementProps
except ModuleNotFoundError:
    from Selenium_Browser import XPathLookupProps, GetElementProps


class HTMLPageElements(object):
    all_elements: Dict[str, GetElementProps]

    url: Union[str, None]
    load_check: XPathLookupProps

    def __init__(self, url: Union[str, None], load_check: XPathLookupProps):
        self.all_elements = {}

        self.url = url
        self.load_check = load_check


class LoopPageElements(HTMLPageElements):
    start_num: int
    end_num: int

    def __init__(self, url: Union[str, None], load_check: XPathLookupProps, end_num: int, start_num: int = 1):
        super().__init__(url, load_check)
        self.start_num = start_num
        self.end_num = end_num