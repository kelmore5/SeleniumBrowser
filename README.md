# SeleniumBrowser

SeleniumBrowser is a fairly small tool to be used in conjunction with Selenium automated browser via Chrome.
Previously, I had been building a web crawler and needed a helper class to deal with some of the smaller,
yet important intricacies. This class does very few things, but does them well.

SeleniumBrowser is meant primarily to be a container for a selenium headless browsing setup that
routinely checks for the existence of links, buttons, images, etc the user needs when crawling
through a site.

The class takes two arguments: The path to an installed version of chromedriver (required) and
a ChromeOptions class that can be created via Selenium (optional).

Once initialized, the class will create a headless (virtual/invisible) chrome browser. Afterwards,
the user can use the class to browse to different URLs while also easily checking for loaded pages
and required elements.

I do not have specific plans right now to expand this project further but may in the future as needed.

## Install

### Dependencies

- python 3.5 or 3.6
- [selenium](http://selenium-python.readthedocs.io/installation.html)
- [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/)

*Selenium and chromedriver are used for headless browsing

### Import

Once the dependencies are installed, importing is as simple as:

```python
from SeleniumBrowser import SeleniumBrowser

path_to_chromedriver = '/home/user/chromedriver'
browser = new SeleniumBrowser(path_to_chromedriver)
```

Afterwards, use the `XPathLookupProps` class to create property classes for page request checks
and then the function `SeleniumBrowser.browse_to_url` to do the actual browsing.

## Extra Links

- [Selenium](https://www.seleniumhq.org/)
- [Selenium Python Docs](http://selenium-python.readthedocs.io/)