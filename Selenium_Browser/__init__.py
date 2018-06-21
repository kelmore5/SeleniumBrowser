import os
import sys

selenium_module_path: str = ''
try:
    selenium_module_path = os.path.dirname(os.path.realpath(__file__))
except NameError:
    selenium_module_path = os.path.dirname(os.path.abspath(sys.argv[0]))

path_append: str = os.path.dirname(selenium_module_path)
sys.path.append(path_append) if path_append not in sys.path else 0

from Selenium_Browser.GetElementProps import GetElementProps
from Selenium_Browser.XPathLookupProps import XPathLookupProps
from Selenium_Browser.SeleniumBrowser import SeleniumBrowser
