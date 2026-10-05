"""
Settings Tab Widget.
Configures the folder location to store incoming telemetry logs in .csv format.
"""

import os
from qtpy.QtCore import Qt, QUrl, Signal
from qtpy.QtGui import QDesktopServices
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QFileDialog, QMessageBox
)
from app.config import COLORS
from app.core.logger import TelemetryCsvLogger


class SettingsTabWidget(QFrame):
    """
    Settings page: specifies the folder location to save incoming telemetry in .csv format.
    """

    log_dir_changed = Signal(str)

    def __init__(self, logger: TelemetryCsvLogger = None, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsCard")
        self.logger = logger or TelemetryCsvLogger()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Header Title
        header_row = QHBoxLayout()
        header_row.setSpacing(8)

        bar = QFrame()
        bar.setFixedWidth(3)
        bar.setFixedHeight(14)
        bar.setStyleSheet(f"background-color: {COLORS['accent_yellow']}; border-radius: 1px;")

        title_label = QLabel("LOG STORAGE SETTINGS")
        title_label.setObjectName("CardTitle")

        header_row.addWidget(bar)
        header_row.addWidget(title_label)
        header_row.addStretch()
        layout.addLayout(header_row)

        # Main settings area
        content_box = QVBoxLayout()
        content_box.setSpacing(8)

        lbl_prompt = QLabel("Select folder location to store telemetry logs (.csv):")
        lbl_prompt.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 12px; font-weight: 600;")
        content_box.addWidget(lbl_prompt)

        # Path input and action buttons
        path_row = QHBoxLayout()
        path_row.setSpacing(8)

        self.txt_log_dir = QLineEdit()
        self.txt_log_dir.setText(self.logger.log_dir)
        self.txt_log_dir.setFixedHeight(30)
        self.txt_log_dir.setPlaceholderText("Select folder location...")

        self.btn_browse = QPushButton("Browse Folder...")
        self.btn_browse.setObjectName("PrimaryButton")
        self.btn_browse.setFixedHeight(30)
        self.btn_browse.clicked.connect(self._on_browse_folder)

        self.btn_open_folder = QPushButton("Open Folder")
        self.btn_open_folder.setFixedHeight(30)
        self.btn_open_folder.clicked.connect(self._on_open_folder)

        path_row.addWidget(self.txt_log_dir, 1)
        path_row.addWidget(self.btn_browse)
        path_row.addWidget(self.btn_open_folder)
        content_box.addLayout(path_row)

        layout.addLayout(content_box)
        layout.addStretch()

    def _on_browse_folder(self):
        """Opens native directory picker dialog."""
        initial_dir = self.txt_log_dir.text().strip() or os.getcwd()
        selected_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Telemetry CSV Log Destination Folder",
            initial_dir,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if selected_dir:
            self.txt_log_dir.setText(selected_dir)
            self.logger.set_log_dir(selected_dir)
            self.log_dir_changed.emit(selected_dir)

    def _on_open_folder(self):
        """Opens the selected log folder in Windows Explorer."""
        folder = self.txt_log_dir.text().strip()
        if os.path.exists(folder):
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder))
        else:
            QMessageBox.warning(self, "Folder Not Found", f"The directory does not exist yet:\n{folder}")


