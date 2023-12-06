import requests
from concurrent.futures import ThreadPoolExecutor
from urllib3.exceptions import ProtocolError
from requests.exceptions import ConnectTimeout
from bs4 import BeautifulSoup
from soupsieve.util import SelectorSyntaxError
from alive_progress import alive_bar
from gui import CSSSelectorInput, ScrapedTextDisplay
from widgets import InfoDialog

LINK_PREFIX = "https://toolsyep.com/en/webpage-to-plain-text/?u=www."

HEADERS = {
    "user-agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/112.0.0.0 Safari/537.36 OPR/98.0.0.0")
}


def site_translation_requests(urls: list[str], num_workers=32) -> list[str]:
    """Threaded approach to scraping which sacrifices paragraph formatting for speed.
    Recommended unless formatting is very important, for example in site translation.

    Args:
        - urls (list[str]): URLs to extract text from.
        - num_workers (int): Number of threads,
                             default is 32 based on the official documentation's recommendation.

    Return:
        - list[str]: Extracted text."""

    css_selector = _verify_css_selector(urls[0])

    return _scrape_urls_requests(urls, css_selector, num_workers)


def _scrape_urls_requests(urls: list[str], css_selector: str, num_workers: int) -> list[str]:
    """Extracts text from each URL in the given list using the given CSS Selector.
    This approach is fully threaded and uses requests.

    Args:
        - urls (list[str]): URLs to extract text from.
        - CSS Selector (str): CSS Selector to use to extract the text.
        - num_workers (int): Number of threads.

    Returns:
        - list[str]: Extracted text."""

    text: list[str] = []

    with alive_bar(len(urls), spinner="classic",
                   title="URL processing:") as progress_bar:
        with ThreadPoolExecutor(num_workers) as executor:
            tasks = [
                executor.submit(_parse_url, url, css_selector) for url in urls
            ]
            for task in tasks:
                text.extend(task.result())
                progress_bar()  # pylint: disable=not-callable

    return text


def _parse_url(url: str, css_selector: str) -> list[str]:
    """Searches and parses the element, returning it's text content.

    Args:
        - url (str): URL to extract text from.
        - css_selector (str): Selector with which to search for the element.

    Returns:
        - list[str]: Extracted text."""

    while True:
        try:
            html = requests.get(url=LINK_PREFIX + url,
                                headers=HEADERS,
                                timeout=60,
                                verify=True)

            element = BeautifulSoup(
                html.content, "lxml").select_one(css_selector)
            if not element:
                return []

            element_text = element.get_text().split("\n")
            if element_text[1] == "HOME":
                element_text = element_text[2:]

            return element_text

        except (ConnectTimeout, ProtocolError):
            continue


def _verify_css_selector(url: str, css_selector="body > div > pre") -> str:
    """Prompts the user for a CSS Selector and attempts to
    extract text from the given URL using said CSS Selector.
    If the extracted text is verified by the user, the function returns the CSS Selector.
    Otherwise, it prompts the user to enter a new selector.

    Args:
        - url (str): URL to extract text from.
        - css_selector (str): Selector with which to search for the element.

    Returns:
        - str: The correct CSS Selector to extract the desired text."""

    while True:
        try:
            text = _parse_url(url, css_selector)
            text = [line for line in text if line]
            if text:
                display_text = ScrapedTextDisplay(text)
                if display_text.confirmed:
                    return css_selector

            else:
                InfoDialog(title="No text found!",
                           message="Please try another CSS Selector")

        except SelectorSyntaxError:
            InfoDialog(title="Error occurred!",
                       message="Please try another CSS Selector")

        string_input = CSSSelectorInput()
        css_selector = string_input.css_input

        if not css_selector:
            raise SystemExit
