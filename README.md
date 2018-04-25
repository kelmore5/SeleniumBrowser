# SeleniumBrowser

SeleniumBrowser is a fairly small tool to be used in conjunction with Selenium automated browser via Chrome.
Previously, I had been building a web crawler and needed a helper class to deal with some of the smaller,
yet important intricacies. This class does very few things, but does them well.

SeleniumBrowser is meant primarily to be a container for a selenium headless browsing setup that
routinely checks for the existence of links, buttons, images, etc the user needs when crawling
through a site.

The class takes two arguments: The path to an installed version of chromedriver (required) and
a ChromeOptions class that can be created via Selenium (optional).

Once initialized, the class will create a virtual display for chrome to reside in using pyvirtualdisplay and
Xfvb, and then create a headless (virtual/invisible) chrome browser within that display. Afterwards,
the user can use the class to browse to different URLs while also easily checking for loaded pages
and required elements.

And that's it! Simple but handy.

I do not have specific plans right now to expand this project further but may in the future as needed.

## Install

### Dependencies

- python 3.5 or 3.6
- pyvirtualdisplay
- [selenium](http://selenium-python.readthedocs.io/installation.html)
- [Xvfb](https://www.x.org/archive/X11R7.6/doc/man/man1/Xvfb.1.xhtml) (May not be necessary - check install of pyvirtualdisplay)
- [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/)

*pyvirtualdisplay and Xvfb are used to create the headless display, selenium and chromedriver are used for the actual browsing

### Import

Once the dependencies are installed, importing is as simple as:

    import SeleniumBrowser from SeleniumBrowser

    path_to_chromedriver = '/home/user/chromedriver'
    browser = new SeleniumBrowser(path_to_chromedriver)

Afterwards, use the `XPathLookupProps` class to create property classes for page request checks
and then the function `SeleniumBrowser.browse_to_url` to do the actual browsing.

## Extra Links

[Selenium](https://www.seleniumhq.org/)
[Selenium Python Docs](http://selenium-python.readthedocs.io/)