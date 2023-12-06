from collections import OrderedDict
from pandas import read_xml
from PyQt6.QtWidgets import QFileDialog
from widgets import ErrorDialog, YesNoDialog


def browse_and_process_file() -> list[str]:
    """Prompts the user to select a file containing links,
    reads the file using the process_file function,
    and checks if the file contains suitable links.
    If suitable links are found, it returns the processed links and the directory of the file.
    If no suitable links are found, it prompts the user to select a different file
    or exits the program if the user chooses not to continue.

    Args:
        - root (Tk): The Tk root object for the GUI.

    Returns:
        - processed_links: List of processed links
        - file_dir (str): Directory of the file."""

    while True:
        links = _process_file()
        processed_links = _preprocess_links(links)

        if processed_links:
            return processed_links

        dialog = YesNoDialog(
            title="No suitable links were found!",
            question=("Please select a file containing links suitable for extraction.\n"
                      "Would you like to select a different file?"))

        if dialog.answer == "No":
            raise SystemExit


def _process_file() -> list[str]:
    """Prompts the user to select a file containing links,
    and returns the links and the directory of the selected file.

    Args:
        - root (Tk): The Tk root object for the GUI.

    Returns:
        - list[str]: Links extracted from the selected file."""

    while True:
        file, _ = QFileDialog.getOpenFileName(
            caption="Browse file",
            filter=("Supported Files (*.txt *.xml);;"
                    "Text Files (*.txt);;"
                    "XML Files (*.xml)"))

        if not file:
            raise SystemExit

        if file.endswith(".xml"):
            df = read_xml(file)

            if "loc" in df.columns:
                return df["loc"].tolist()

        elif file.endswith(".txt"):
            with open(file, "r", encoding="utf-8") as txt_file:
                links = txt_file.readlines()

                if links:
                    return links

        ErrorDialog(
            title="Invalid file",
            message="Please insert an .xml file from www.xml-sitemaps.com "
            "or simply a .txt file containing links and try again.")


def _preprocess_links(links: list[str]) -> list[str]:
    """Preprocesses a list of links to be compatible with textise.net.

    The function removes duplicates without disrupting the order of the original list,
    turns all links to lowercase, and removes any invalid links.

    Args:
        - links (List[str]): Links to preprocess.

    Returns:
        - list[str]: Valid, processed links."""

    processed_links: list[str] = []
    links = list(map(str.lower, links))
    unique_links = list(OrderedDict.fromkeys(links))

    for link in unique_links:
        if link.endswith((".pdf", "rss=1", "atom=1")):
            continue

        if link.startswith("https://"):
            processed_link = link[8:]
        elif link.startswith("http://"):
            processed_link = link[7:]
        elif link.startswith("www."):
            processed_link = link[4:]
        else:
            continue

        processed_links.append(processed_link)

    return processed_links
