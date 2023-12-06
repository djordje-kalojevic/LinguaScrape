LinguaScrape is a Python library featuring a user-friendly graphical user interface (GUI) designed for efficient text scraping from websites. The library offers two scraping modes, each with its unique advantages, and provides a range of options for processing the extracted text.

## Key Features

- **Two Scraping Modes:**
  - **[Toolsyep.com Mode](https://toolsyep.com/en/webpage-to-plain-text/):** Utilizes requests and is fully multithreaded for faster scraping. While it is thorough, it does not retain paragraph formatting, saving each paragraph line separately.
  - **[Textise.net Mode](https://www.textise.net):** Although slower, this method is reliable as it utilizes Selenium for web scraping. Textise mode maintains paragraph formatting, ensuring the structure of the scraped text. Requires Google Chrome installation and the correct Xpath selector obtainable from [Textise.net](https://www.textise.net) by inputting the link you want to scrape the text from, then right-clicking -> Inspect Element.

- **Text Processing Options:**
  - Remove Text Repetitions: Removes redundant text from the scraped text, particularly useful for translating websites.
  - Remove Hyperlinks: Removes hyperlinks and URLs from the scraped text.
  - Remove Untranslatables: Removes text that cannot be translated, including strings without any text, various codes, etc.
  - Remove Measurements: Excludes measurements and units from the scraped text.

- **Export to Excel:**
  - The scraped and processed text is stored in an Excel file, allowing for further analysis, translation, or manipulation.

## Usage

To get started with LinguaScrape, follow these steps:

1. Install the library and its dependencies, or simply clone this repository.
2. Launch the program.
3. Choose the desired scraping mode (Toolsyep or Textise) via GUI.
4. Configure text processing options.
5. Provide the website's URL(s) for scraping.
6. Confirm the selection to start the process.
7. The scraped and processed text will be saved to an Excel file.

## Installation

Install LinguaScrape using pip:

```python
pip install linguascrape
```

Import and utilize the scraper:

```python
from linguascrape import scrape


if __name__ == "__main__":
    scrape()
```

## Real-world application

As part of my job responsibilities, I was tasked with extracting text from webpages for the purposes of site translation. Back then this was done completely manually, and for a website of ~480 pages it took 7.5 hours to extract and process that text. However with a previous version of this script the same project was performed from scratch in ~15 minutes, this includes additional time for standard QA procedures.

Not only is this new approach faster, it also possesses a lot lower probability of human error compared to previous manual approach. Additionally, the quality of the extracted text is better due to automated extraction process.

## Contributing

Contributions are welcome! If you have ideas for improvements or encounter any issues, please feel free to open an issue or submit a pull request.