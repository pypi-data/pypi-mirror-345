

from bs4 import BeautifulSoup
from lxml import html
from lxml import etree


from bs4 import BeautifulSoup
from lxml import html
from lxml import etree

'''
# ScrapingHelp Overview

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
'''

def xpathToHtml(pageSource, xpath):
    '''
    ### `xpathToHtml(pageSource, xpath)`

    **Description**  
    Extracts the HTML of a single element from a page using an XPath.

    **Explanation**  
    This function parses the raw HTML using `lxml`, applies the given XPath to locate the desired element, ensures only one element matches, and returns its HTML as a byte string.

    **Example**  
    ```python
    html = '<div><p>Hello</p><p>World</p></div>'
    xpath = '//p[1]'
    print(xpathToHtml(html, xpath))
    # Output: b'<p>Hello</p>'```
    '''

    tree = html.fromstring( pageSource )
    
    selected_elements = tree.xpath( xpath )
    
    assert len(selected_elements) == 1 , len(selected_elements)
    
    return html.tostring( selected_elements[0])

def xpathToSoup(pageSource, xpath):
    '''
    ### `xpathToSoup(pageSource, xpath)`

    **Description**  
    Converts an XPath-matched element into a BeautifulSoup object.

    **Explanation**  
    This wraps the `xpathToHtml` function and parses the resulting HTML fragment using BeautifulSoup with the HTML parser.

    **Example**  
    ```python
    html = '<div><p>Hello</p><p>World</p></div>'
    xpath = '//p[1]'
    soup = xpathToSoup(html, xpath)
    print(soup.text)  # Output: Hello
    ```
    '''
    thisSoup = BeautifulSoup( xpathToHtml(pageSource, xpath), 'html.parser')
    return thisSoup

###################

def soupToXpath(element):
    '''
    ### `soupToXpath(element)`

    **Description**  
    Generates the XPath for a BeautifulSoup element.

    **Explanation**  
    This function walks up the DOM tree from the given element, building an XPath expression that uniquely identifies its location.

    **Example**  
    ```python
    from bs4 import BeautifulSoup

    soup = BeautifulSoup('<div><p>Hello</p><p>World</p></div>', 'html.parser')
    element = soup.find_all('p')[1]
    print(soupToXpath(element))
    # Output: /html/body/div/p[2]  (actual path may vary depending on the full HTML structure)
    ```
    '''
    components = []
    target = element if element.name else element.parent
    for node in (target, *target.parents)[-2::-1]:  # type: bs4.element.Tag
        tag = '%s:%s' % (node.prefix, node.name) if node.prefix else node.name
        siblings = node.parent.find_all(tag, recursive=False)
        components.append(tag if len(siblings) == 1 else '%s[%d]' % (tag, next(
            index
            for index, sibling in enumerate(siblings, 1)
            if sibling is node
            )))
    return '/%s' % '/'.join(components)

def getPathTwoElements( pageSource, phrase1 = "never hear about the 10", phrase2 = "what a beautiful blue sky"):
    '''
    ### `getPathTwoElements(pageSource, phrase1, phrase2)`

    **Description**  
    Finds the XPath to the smallest HTML element that contains both `phrase1` and `phrase2`.

    **Explanation**  
    It uses BeautifulSoup to find the innermost tag that contains both phrases and then converts that tag to an XPath using `soupToXpath`.

    **Example**  
    ```python
    html = '<div><p>Hello world</p><div><span>never hear about the 10 and what a beautiful blue sky</span></div></div>'
    print(getPathTwoElements(html, 'never hear about the 10', 'what a beautiful blue sky'))
    # Output: XPath to the <span> element
    ```
    '''
    # thanks https://gist.github.com/ergoithz/6cf043e3fdedd1b94fcf
    
    soup = BeautifulSoup( pageSource , 'html.parser')

    def getInnermostElement(phrase1, phrase2):
        # Function to check if an element contains both phrases
        def contains_both_phrases(element):
            # Check if both phrases are found in the element's text (or any of its descendants)
            return phrase1 in element.get_text() and phrase2 in element.get_text()

        # Find the innermost element that contains both phrases
        innermost_element = None
        for element in soup.find_all(True):  # `True` finds all tags
            if contains_both_phrases(element):
                # If this element is contained within a previous innermost, update it
                if not innermost_element or len(element.find_all(True)) < len(innermost_element.find_all(True)):
                    innermost_element = element

        # Print the innermost element containing both phrases
        if innermost_element:
            print("Found it")
            return innermost_element
        else:
            print("No element contains both phrases.")
            return None
    innermost_element = getInnermostElement( phrase1, phrase2)

    xpath = soupToXpath( innermost_element )

    innerEl_forAssert = xpathToSoup( pageSource, xpath )
    assert phrase1 in innerEl_forAssert.decode_contents()
    assert phrase2 in innerEl_forAssert.decode_contents()
    
    # xpath: /html/body/shreddit-app/div/div[1]/div[2]/main/div[2]/shreddit-feed
    # print("xpath:",xpath)
    return xpath

def getPathOneElement(pageSource, phrase1):
    '''
    ### `getPathOneElement(pageSource, phrase1)`

    **Description**  
    Finds the XPath to the smallest HTML element that contains the given phrase.

    **Explanation**  
    Similar to `getPathTwoElements`, but only searches for one phrase.

    **Example**  
    ```python
    html = '<div><p>Hello world</p><div><span>never hear about the 10</span></div></div>'
    print(getPathOneElement(html, 'never hear about the 10'))
    # Output: XPath to the <span> element
    ```
    '''
    soupp = BeautifulSoup( pageSource , 'html.parser')

    # Function to check if an element contains both phrases
    def contains_both_phrases(element):
        # Check if both phrases are found in the element's text (or any of its descendants)
        return phrase1 in element.get_text() or phrase1 in element.decode_contents()

    # Find the innermost element that contains both phrases
    innermost_element = None
    for element in soupp.find_all(True):  # `True` finds all tags
        if contains_both_phrases(element):
            # If this element is contained within a previous innermost, update it
            if not innermost_element or len(element.find_all(True)) < len(innermost_element.find_all(True)):
                innermost_element = element

    #return innermost_element
    xpath = soupToXpath( innermost_element )
    return xpath

###################

def justText_alternativeGetMultipleXpathsFromSearchText( html_content, search_text ):
    '''
    ### `justText_alternativeGetMultipleXpathsFromSearchText(html_content, search_text)`

    **Description**  
    Finds all XPaths where elements contain the search text in their visible text.

    **Explanation**  
    Uses `lxml.etree` to parse the HTML and finds all elements whose text content includes the specified search text.

    **Example**  
    ```python
    html = '<div><p>Match me</p><a href="#">Do not</a></div>'
    print(justText_alternativeGetMultipleXpathsFromSearchText(html, 'Match'))
    # Output: ['/html/body/div/p']
    ```
    '''

    root = etree.fromstring( html_content , parser=etree.HTMLParser())

    tree = etree.ElementTree(root)
    matching_elements = tree.xpath(f"//*[contains(text(), '{search_text}')]")

    allResults = []
    for e in matching_elements:
        allResults.append(tree.getpath(e))

    return allResults

def alternativeGetMultipleXpathsFromSearchText(html_content, search_text):
    '''
    ### `alternativeGetMultipleXpathsFromSearchText(html_content, search_text)`

    **Description**  
    Finds all XPaths where elements contain the search text in either their text content or their `href` attribute.

    **Explanation**  
    Expands the previous function by searching both the text and the `href` attribute for matches.

    **Example**  
    ```python
    html = '<div><a href="https://example.com/match">Click me</a></div>'
    print(alternativeGetMultipleXpathsFromSearchText(html, 'match'))
    # Output: ['/html/body/div/a']
    ```
    '''
    root = etree.fromstring(html_content, parser=etree.HTMLParser())
    tree = etree.ElementTree(root)
    
    # Find elements that contain search_text in either their text content or href attribute
    matching_elements = tree.xpath(f"//*[contains(text(), '{search_text}') or contains(@href, '{search_text}')]")
    
    allResults = []
    for e in matching_elements:
        allResults.append(tree.getpath(e))
    
    return allResults
