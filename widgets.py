from dataclasses import dataclass
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (QWidget, QCheckBox, QLabel, QFormLayout,
                             QDialog, QMessageBox, QStyle)


@dataclass
class CheckBox(QWidget):
    """A custom widget for displaying a checkbox with tooltip."""

    def __init__(self, parent: QDialog, label: str,
                 tooltip_text: str, icon_size=QSize(16, 16)) -> None:
        super().__init__(parent)

        form_layout = QFormLayout()
        self.checkbox = QCheckBox(label)
        self.checkbox.setChecked(True)
        self.tooltip = QLabel()
        self.tooltip = Tooltip(self, tooltip_text, icon_size)
        form_layout.addRow(self.checkbox, self.tooltip)
        form_layout.setContentsMargins(form_layout.contentsMargins().left(), 0,
                                       form_layout.contentsMargins().right(), 0)

        parent.checkboxes.append(self.checkbox)
        self.setLayout(form_layout)


@dataclass
class ErrorDialog(QDialog):

    def __init__(self, message, title: str = " "):
        super().__init__()

        self.setWindowTitle(title)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setFixedSize(400, 150)\

        self.message_label = QLabel(message, self)
        self.message_label.setWordWrap(True)

        self.message_box = QMessageBox(self)
        self.message_box.setIcon(QMessageBox.Icon.Critical)
        self.message_box.setText(message)
        self.message_box.setWindowTitle(title)

        self.message_box.exec()


@dataclass
class InfoDialog(QDialog):

    def __init__(self, message, title: str = " "):
        super().__init__()

        self.setWindowTitle(title)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setFixedSize(400, 150)

        self.message_label = QLabel(message, self)
        self.message_label.setWordWrap(True)

        self.message_box = QMessageBox(self)
        self.message_box.setIcon(QMessageBox.Icon.Information)
        self.message_box.setText(message)
        self.message_box.setWindowTitle(title)

        self.message_box.exec()


class Tooltip(QLabel):
    """A custom tooltip widget."""

    def __init__(self, parent=None, tooltip_text="", icon_size=QSize(16, 16)):
        super().__init__(parent)

        pixmap_name = QStyle.StandardPixmap.SP_MessageBoxQuestion
        pixmap = self.style().standardPixmap(pixmap_name)
        resized_pixmap = pixmap.scaled(icon_size,
                                       Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(resized_pixmap)
        self.setToolTip(tooltip_text)


@dataclass
class YesNoDialog(QDialog):

    def __init__(self, question: str, title: str = " ") -> None:
        super().__init__()

        self.setWindowTitle(title)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setMinimumWidth(200)
        self.setMinimumHeight(100)

        self.message_box = QMessageBox(self)
        self.message_box.setIcon(QMessageBox.Icon.Question)
        self.message_box.setText(question)
        self.message_box.setWindowTitle(title)

        self.no_button = self.message_box.addButton(
            QMessageBox.StandardButton.No)
        self.no_button.clicked.connect(self.no_clicked)

        self.yes_button = self.message_box.addButton(
            QMessageBox.StandardButton.Yes)
        self.yes_button.clicked.connect(self.yes_clicked)

        self.message_box.exec()

    def yes_clicked(self) -> None:
        self.answer = "Yes"

    def no_clicked(self) -> None:
        self.answer = "No"
