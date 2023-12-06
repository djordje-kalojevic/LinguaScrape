from dataclasses import dataclass
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QCheckBox,
                             QLabel, QDialog, QComboBox, QLineEdit, QTextEdit,
                             QHBoxLayout, QScrollBar, QGridLayout)
from widgets import CheckBox, Tooltip


def get_user_input() -> tuple[str, dict[str, bool]]:
    """Returns user input if the input was provided, otherwise closes the program."""

    method_selector = ScrapeMethodSelector()
    scraping_method = method_selector.selected_method

    if not scraping_method:
        raise SystemExit

    window = SettingsSelector()
    settings = window.selected_settings

    if not settings:
        raise SystemExit

    return scraping_method, settings


class SettingsSelector(QDialog):
    """Custom searchable widget for displaying and selecting multiple languages."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle("LinguaScrape")

        self.checkboxes: list[QCheckBox] = []
        self.selected_settings: dict[str, bool] = {}

        self.confirm_button = QPushButton("Confirm Selection", self)
        self.confirm_button.clicked.connect(self._confirm_selection)

        self.checkboxes_layout = QGridLayout()
        self._add_checkboxes()

        self.vertical_layout = QVBoxLayout()
        label = QLabel("Text processing options:", self)
        self.vertical_layout.addWidget(label)
        self.vertical_layout.addLayout(self.checkboxes_layout)
        self.vertical_layout.addWidget(self.confirm_button)
        self.setLayout(self.vertical_layout)

        self.exec()

    def _add_checkboxes(self) -> None:
        """Adds a checkbox with the given label,
        and tooltip text to a two-column grid layout."""

        self.checkbox_data = AdvancedOptions.options
        for label, tooltip_text in self.checkbox_data.items():
            checkbox = CheckBox(self, label, tooltip_text)
            self.checkboxes_layout.addWidget(checkbox)

    def _confirm_selection(self) -> None:
        """Confirms the selection from the selection listbox and checkboxes."""

        for box in self.checkboxes:
            self.selected_settings[box.text()] = box.isChecked()

        self.close()


@dataclass
class ScrapeMethodSelector(QDialog):
    def __init__(self):
        super().__init__()
        self.selected_method = ""
        self.setWindowTitle("LinguaScrape")

        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        layout = QGridLayout(self)

        label = QLabel("Please select desired scraping method:", self)
        layout.addWidget(label, 0, 0, 1, 3)

        combo_box_layout = QHBoxLayout()
        self.combo_box = QComboBox()
        self.combo_box.addItems(["Toolsyep", "Textise"])
        self.combo_box_tooltip = Tooltip(
            self,
            "Toolsyep offers significantly faster scraping (up to 50 times), "
            "but it does not preserve paragraph formatting. "
            "Each paragraph line is converted into a new line. "
            "On the other hand, Textise is slower "
            "but retains the original paragraph formatting.")

        combo_box_layout.addWidget(self.combo_box)
        combo_box_layout.addWidget(self.combo_box_tooltip)
        layout.addLayout(combo_box_layout, 1, 1)

        layout.addWidget(QWidget(), 2, 0, 2, 1)

        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self._select_method)
        layout.addWidget(self.confirm_button, 3, 0, 1, 3)
        self.setLayout(layout)
        self.exec()

    def _select_method(self):
        self.selected_method = self.combo_box.currentText()
        self.close()


@dataclass
class CSSSelectorInput(QDialog):

    def __init__(self):
        super().__init__()

        self.css_input = ""

        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle("LinguaScrape")

        self.label = QLabel("Enter the CSS selector:")
        self.input = QLineEdit()

        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self._confirm_selection)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.input)
        layout.addWidget(self.confirm_button)

        self.setLayout(layout)
        self.exec()

    def _confirm_selection(self):
        self.css_input = self.input.text()
        self.close()


class ScrapedTextDisplay(QDialog):

    def __init__(self, text):
        super().__init__()

        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle("LinguaScrape")

        self.confirmed = False

        self.scraped_text = QTextEdit()
        self.scraped_text.setAlignment(Qt.AlignmentFlag.AlignJustify)

        # QTextEdit does not support extend
        for line in text:
            self.scraped_text.append(line)

        self.scraped_text.moveCursor(QTextCursor.MoveOperation.Start)
        self.scraped_text.setFixedSize(300, 400)
        self.scraped_text.setVerticalScrollBar(QScrollBar())

        self.cancel_button = QPushButton("Cancel")
        self.confirm_button = QPushButton("Confirm")
        self.cancel_button.clicked.connect(self._cancel)
        self.confirm_button.clicked.connect(self._confirm)

        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addWidget(self.confirm_button)

        self.v_layout = QVBoxLayout()
        label = QLabel("Is this the text you wanted to scrape?", self)
        self.v_layout.addWidget(label)
        self.v_layout.addWidget(self.scraped_text)
        self.v_layout.addLayout(self.button_layout)
        self.setLayout(self.v_layout)

        self.exec()

    def _confirm(self):
        self.confirmed = True
        self.close()

    def _cancel(self):
        self.confirmed = False
        self.close()


@dataclass
class AdvancedOptions():
    """format - checkbox label: tooltip"""

    options = {
        "Remove repetitions":
        ("Recommended to leave enabled unless repetitions are truly needed, "
         "e.g. for translation purposes."),
        "Remove image names":
        ("By default Textise saves the names of images from pages in processes. "
         "Recommended to leave enabled unless such names are needed."),
        "Remove protected emails":
        ("By default Textise does not save some scraped emails, "
         "this option will remove them as they contain no useful information. "
         "If there are properly scraped emails they are left intact."),
        "Remove untranslatables":
        "Removes various types of untranslatables from extracted text.",
        "Remove measurements":
        "Removes SI units and measurements from extracted text.",
        "Remove hyperlinks":
        "Removes hyperlinks from extracted text.",
        "Remove source links":
        ("Removes links where from particular data was extracted, "
         "uncheck if this is useful information for you.")
    }
