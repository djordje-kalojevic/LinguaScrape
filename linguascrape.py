"""Utility used primarily for site translation, or the scraping of whole web sites."""

import chromedriver_autoinstaller
from PyQt6.QtWidgets import QApplication
from gui import get_user_input
from gui_utils import configure_theme
from file_processing import browse_and_process_file
from link_scraping import site_translation
from link_scraping_requests import site_translation_requests
from text_processing import process_scraped_text, save_report, save_scraped_text


def scrape() -> None:
    app = QApplication([])
    configure_theme()

    scraping_method, settings = get_user_input()
    urls = browse_and_process_file()

    if scraping_method == "Toolsyep":
        scraped_text = site_translation_requests(urls)
        processed_text = process_scraped_text(scraped_text, settings)
        save_scraped_text(processed_text)

    elif scraping_method == "Textise":
        chromedriver_autoinstaller.install()
        scraped_text, invalid_links = site_translation(urls)
        processed_text = process_scraped_text(scraped_text, settings)
        save_scraped_text(processed_text)

        if invalid_links:
            save_report(invalid_links)

    app.closeAllWindows()


if __name__ == "__main__":
    scrape()
