"""This module is tasked with verifying CSS Selector entered by the user,
as well as scraping provided URLs.

To ensure successful URL scraping via Textise, URL prefix has been provided."""

import re
from dataclasses import dataclass
from time import perf_counter
from typing import Optional
from seleniumbase import Driver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from alive_progress import alive_bar
from widgets import InfoDialog
from gui import CSSSelectorInput, ScrapedTextDisplay

LINK_PREFIX = "https://www.textise.net/showText.aspx?strURL=https%253A//"
TIMEOUT_LIMIT = 10


def site_translation(urls: list[str]):
    """Scrapes websites or lists of URLs (currently .xml and .txt files are supported as inputs).
    Scraping is done via CSS Selector, and user is required to enter it manually.
    Recommended to use 'www.xml-sitemaps.com' to get all URLs that compose a site,
    otherwise just use a .txt file.
    All URLs are then forwarded to 'www.textise.net' to scrape the text via Seleniumbase.
    Scraped text is then processed and saved."""

    driver = Driver(undetectable=True,
                    headless2=True,
                    page_load_strategy="eager",
                    incognito=True)

    css_selector = _verify_css_selector(driver, urls[0])
    scraped_text, invalid_URLs = _scrape_urls(driver, urls, css_selector)

    return scraped_text, invalid_URLs


def _verify_css_selector(driver: WebDriver, url: str) -> str:
    """Prompts the user for a CSS Selector and attempts to
    extract text from the given URL using said CSS Selector.
    If the extracted text is verified by the user, the function returns the CSS Selector.
    Otherwise, it prompts the user to enter a new selector.

    Args:
        - driver (WebDriver): The WebDriver instance to use.
        - url (str): URL to extract text from.

    Returns:
        - str: The correct CSS Selector to extract the desired text."""

    scraped_text = []

    while True:
        css_input = CSSSelectorInput()
        css_selector = css_input.css_input

        if not css_selector:
            raise SystemExit

        driver.get(LINK_PREFIX + url)
        element, error_type = _is_element_present(driver, css_selector)

        if element:
            scraped_text.append(f"Original link: https://{url}\n")
            scraped_text.extend(element.text.split("\n"))

            display_text = ScrapedTextDisplay(scraped_text)

            if display_text.confirmed:
                return css_selector

        if error_type:
            InfoDialog(title=error_type,
                       message="Please try another CSS Selector")


def _is_element_present(driver: WebDriver,
                        css_selector: str) -> tuple[Optional[WebElement], str]:
    # TODO: update docstring
    """Checks if the given URL is invalid or if the page is inaccessible,
    and prompts the user with an appropriate message if either of these is true.
    If the connection times out, it prompts the user to try another CSS Selector.

    Args:
        - driver (WebDriver): The WebDriver instance to use.
        - css_selector (float): Selector with which to search for the element.

    Returns:
        - bool: True if the URL is invalid or the page is inaccessible, False otherwise."""

    # waits for the page to load in case of CloudFlare detection
    while ("Just a moment..." in driver.page_source
           or driver.execute_script("return document.readyState;") != "complete"):
        continue

    timer_start = perf_counter()

    while perf_counter() - timer_start < TIMEOUT_LIMIT:
        try:
            element = driver.find_element("css selector", css_selector)

            if element:
                return element, ""

        except (NoSuchElementException, StaleElementReferenceException):
            continue

        for pattern, error_type in _Errors.error_massages.items():
            if pattern.search(driver.page_source):
                return None, error_type

    return None, "Timed out - element not found!"


def _scrape_urls(driver: WebDriver, URLs: list[str],
                 css_selector: str) -> tuple[list[str], dict[str, str]]:
    """Extracts text from each URL in the given list using the given CSS Selector.
    If a URL is invalid or the page is inaccessible,
    it adds the URL to a dictionary of invalid URLs.
    Returns a tuple containing a list of all extracted text and a dictionary of invalid URLs.

    Args:
        - driver (WebDriver): WebDriver to use.
        - urls (list[str]): URLs to extract text from.
        - CSS Selector (str): CSS Selector to use to extract the text.

    Returns:
        - list[str]: Extracted text
        - dict[str, str]:  Invalid URLs, error that occurred."""

    all_scraped_text: list[str] = []
    invalid_URLs: dict[str, str] = {}

    with alive_bar(len(URLs), spinner="classic",
                   title="URL processing:") as progress_bar:
        for url in URLs:
            driver.get(LINK_PREFIX + url)
            element, error_type = _is_element_present(driver, css_selector)

            if element:
                all_scraped_text.append(f"Original page: https://{url}")
                all_scraped_text.extend(element.text.split("\n"))

            else:
                invalid_URLs[f"https://{url}"] = error_type

            progress_bar()  # pylint: disable=not-callable

    driver.quit()

    return all_scraped_text, invalid_URLs


@dataclass
class _Errors:
    error_massages = {
        re.compile("Sorry, Textise had a problem with that address"):
        "Invalid URL!",
        re.compile("The site owner may have set restrictions "
                   "that prevent you from accessing the site."):
        "Restricted Access!"
    }
