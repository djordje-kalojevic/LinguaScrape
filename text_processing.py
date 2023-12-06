"""This module defines functions used to process text data by filtering out
entries that do not contain any translatable text.
These filters are optional, as this text might be useful for some users.

This includes removing:
- emails failed to be scraped,
- image file names,
- hyperlinks,
- non-letter patterns,
- SI units and measurements,
- other various untranslatables."""

from csv import writer
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import askyesno
import re
from pandas import Series


def process_scraped_text(scraped_text: list[str],
                         settings: dict[str, bool]) -> Series:
    """Processes scraped text by cleaning it using various regular expressions.

    This includes removing:
        - emails failed to be scraped,
        - image file names,
        - hyperlinks,
        - non-letter patterns,
        - SI units and measurements,
        - other various untranslatables.

    Args:
        - scraped_text (list[str]): List of strings containing the scraped text.

    Returns:
        - series: Pandas Series object containing the cleaned text."""

    series = Series(scraped_text).str.strip()

    if settings["Remove repetitions"]:
        series = Series(series.unique())

    if settings["Remove source links"]:
        pattern = re.compile(r"^Original page: (https?://|www.)\S+?$")
        series = series.replace(pattern, None, regex=True)

    if settings["Remove protected emails"]:
        series = _remove_emails(series)

    if settings["Remove image names"]:
        series = _remove_image_names(series)

    if settings["Remove untranslatables"]:
        series = _remove_untranslatables(series)

    if settings["Remove measurements"]:
        series = _remove_measurements(series)

    if settings["Remove hyperlinks"]:
        series = _remove_hyperlinks(series)

    pattern = re.compile(r"^Text-only page created by https://toolsyep.com")
    series = series.replace(pattern, None, regex=True)

    return series.str.strip().replace("", None).dropna(how="any")


def save_scraped_text(scraped_text: Series) -> None:
    """Saves scraped text to a file in either Excel or text formats.
    Additionally it saves discarded links to a separate .txt file.

    Args:
        - scraped_text (Series): A Pandas Series object containing the scraped text."""

    output_file_name = asksaveasfilename(title="Please save extracted text",
                                         initialfile="scraped text",
                                         defaultextension=".xlsx",
                                         filetypes=[("Excel file", "*.xlsx"),
                                                    ("Text file", "*.txt")])
    if not output_file_name:
        raise SystemExit

    if output_file_name.endswith(".xlsx"):
        scraped_text.to_excel(output_file_name, index=False, header=False)

    elif output_file_name.endswith(".txt"):
        scraped_text.to_csv(output_file_name, index=False, header=False)


def _remove_emails(series: Series) -> Series:
    """Removes email addresses from the given Pandas Series.

    Args:
        - series: Scrapped text.

    Returns:
        - Series: New Pandas Series with email addresses removed."""

    pattern = re.compile(r"\[email protected\]")

    return series.replace(pattern, None, regex=True)


def _remove_image_names(series: Series) -> Series:
    """Removes image names from the given Pandas Series.

    Args:
        - series: Scrapped text.

    Returns:
        - Series: New Pandas Series with image names removed."""

    pattern = re.compile(r"(\[Image.*\]|^media/image/\S+$)")
    series = series.replace(pattern, None, regex=True)
    pattern = re.compile(r"^media/image/\S+$")

    return series.replace(pattern, None, regex=True)


def _remove_untranslatables(series: Series) -> Series:
    """Cleans the given Pandas Series by removing lines that only contain numbers,
    and other non-translatable text.

    Args:
        - series: Scrapped text.

    Returns:
        - Series: New Pandas Series object with cleaned text."""

    pattern = re.compile(r"(?i)^[\W\d_xX]*?([A-Z])?(\s|\d)*?[\W\d_xX]*?$")
    series = series.replace(pattern, None, regex=True)

    pattern = re.compile(r"(?i)^(?:[a-z]{,3}\d+[a-z]{,3}\d*)+$")
    series = series.replace(pattern, None, regex=True)

    pattern = re.compile(r"(?i)^(?:\d+[a-z]{,3}\d+[a-z]{,3})+$")

    return series.replace(pattern, None, regex=True)


def _remove_measurements(series: Series) -> Series:
    """Removes SI units and measurements from the given Pandas Series.

    Args:
        - series: Scrapped text.

    Returns:
        - Series: New Pandas Series with measurements removed."""

    pattern = re.compile(
        r"(?i)\d+(?:\.\d+)?(?:\s*[eE][+-]?\d+)?\s*"
        r"(?:\b(?:M|k|m|c)?(?:m|g|s|A|Hz|N|Pa|J|W|V|F|Ω|S|T|H|lm|lx)\b)")

    return series.replace(pattern, None, regex=True)


def _remove_hyperlinks(series: Series) -> Series:
    """Removes hyperlinks from the given Pandas Series.

    Args:
        - series: Scrapped text.

    Returns:
        - Series: New Pandas Series with hyperlinks removed."""

    pattern = re.compile(r"^(https?://|www.)\S+?$")

    return series.replace(pattern, None, regex=True)


def save_report(invalid_links: dict) -> None:
    """Saves a report of invalid links to a CSV file.
    If the invalid_links dictionary is empty, it simply returns.
    If it is not empty, it asks the user if they want to save the report.

    Args:
        - dict: Links that failed to be scraped and the reason why."""

    if not invalid_links:
        raise SystemExit

    if askyesno(
            title="Invalid links found!",
            message=("Do you want to save the invalid link report?\n"
                     "This report will contain links, "
                     "and the reasoning as to why they were found invalid.")):

        report = asksaveasfilename(title="Please save report",
                                   initialfile="invalid link report",
                                   defaultextension=".csv",
                                   filetypes=[("CSV file", "*.csv")])
        if not report:
            raise SystemExit

        with open(report, "w", encoding="utf-8", newline="") as file:
            csv = writer(file)
            csv.writerow(["Error", "Link"])
            for link, error in invalid_links.items():
                csv.writerow([error, link])
