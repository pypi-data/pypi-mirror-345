
from setuptools import setup, find_packages
with open("README.md", "r") as fh: 
    long_description = fh.read() 

setup(
    name='scrapingHelp',
    version='0.2.5',
    author='Brigham Turner',
    author_email='brighamturner@narratebay.com',
    description='''# ScrapingHelp

This module provides a set of functions to work with HTML content using XPath and BeautifulSoup. It allows for the extraction and manipulation of HTML elements using both `lxml` (with XPath) and `BeautifulSoup` (with Python's HTML parsing). These functions are designed for various tasks, such as locating elements, converting them between formats, and generating XPath expressions for DOM elements.

### Key Capabilities

1. **Extract HTML with XPath**
- `xpathToHtml(pageSource, xpath)`: This function extracts the HTML of a single element from the raw HTML using the provided XPath. It parses the raw HTML and ensures only one element matches the XPath, returning its HTML as a byte string.

2. **Convert XPath-matched element to BeautifulSoup**
- `xpathToSoup(pageSource, xpath)`: This function converts an element selected by an XPath into a BeautifulSoup object. It uses `xpathToHtml` to extract the HTML and then parses the HTML fragment with BeautifulSoup, allowing further manipulation or extraction using the BeautifulSoup API.

3. **Generate XPath from BeautifulSoup element**
- `soupToXpath(element)`: Given a BeautifulSoup element, this function walks up the DOM tree and generates the XPath that uniquely identifies the element’s location. This is useful for reverse-engineering the XPath for a given element in the parsed HTML.

4. **Find XPath for an element containing both phrases**
- `getPathTwoElements(pageSource, phrase1, phrase2)`: This function finds the XPath to the smallest HTML element that contains both specified phrases. It uses BeautifulSoup to locate the innermost element containing both phrases and then converts it to an XPath.

5. **Find XPath for an element containing one phrase**
- `getPathOneElement(pageSource, phrase1)`: Similar to `getPathTwoElements`, this function finds the XPath to the smallest element containing only one phrase. It helps when searching for a single phrase within the HTML.

6. **Find XPaths for elements containing search text**
- `justText_alternativeGetMultipleXpathsFromSearchText(html_content, search_text)`: This function finds all XPaths where elements contain the specified text. It uses `lxml.etree` to parse the HTML and find elements with matching text content.

7. **Find XPaths for elements containing search text or href attribute**
- `alternativeGetMultipleXpathsFromSearchText(html_content, search_text)`: This function expands upon the previous one by searching both the text content and the `href` attribute for matches. It returns all XPaths where either the visible text or the `href` attribute contains the specified search text.

### Usage Scenarios

- **Scraping Web Pages**: The module can be used to extract specific HTML elements from a page based on their content (e.g., finding elements containing certain phrases or text).

- **XPath Generation**: The module allows for generating and working with XPath expressions, which can be useful in web scraping, automation, or testing tools that rely on XPath selectors.

- **HTML Manipulation**: By converting elements to BeautifulSoup objects, this module enables easy manipulation and extraction of data from HTML using the powerful BeautifulSoup API.

- **Link and Text Search**: It provides functions to find elements that contain specific text or links (via `href` attributes), making it useful for content scraping and analysis.

### Example Workflow

You can use these functions in combination to extract and manipulate content from web pages:
- Use `xpathToHtml` to extract raw HTML.
- Convert the raw HTML to BeautifulSoup with `xpathToSoup` for easy parsing and manipulation.
- Generate XPath expressions for specific elements using `soupToXpath`.
- Use `getPathTwoElements` or `getPathOneElement` to find the XPath of elements containing specific text.
- Use `justText_alternativeGetMultipleXpathsFromSearchText` or `alternativeGetMultipleXpathsFromSearchText` to find all matching elements based on text or attribute search.

### Conclusion

This module offers a flexible and powerful toolkit for web scraping, XPath generation, and HTML manipulation. With both XPath-based and BeautifulSoup-based methods, it provides a comprehensive solution for working with HTML data in Python.
''',
    long_description=long_description, 
    long_description_content_type="text/markdown", 

    url="https://github.com/brighamturner12/scrapingHelp.git",
    project_urls={"Documentation": "https://github.com/brighamturner12/scrapingHelp/blob/main/readme.md","Source Code": "https://github.com/brighamturner12/scrapingHelp/blob/main/scrapingHelp.py",},

    packages=find_packages(),
    install_requires=["bs4","lxml","lxml"], 
    license="MIT",
    classifiers=[
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)