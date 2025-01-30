# views/import_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QProgressBar, QMessageBox,
    QTextEdit
)
from PySide6.QtCore import Qt, Signal
import logging
from database.db_manager import DatabaseManager
import os
import pandas as pd


class ImportDialog(QDialog):
    import_completed = Signal(bool, str)  # Success status and message

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.setup_ui()
        self.selected_file = None

    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Import Courses")
        self.setMinimumWidth(500)
        layout = QVBoxLayout(self)

        # File selection area
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("padding: 5px; background: #f0f0f0; border-radius: 3px;")
        file_layout.addWidget(self.file_label)

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(self.browse_button)
        layout.addLayout(file_layout)

        # Preview area
        layout.addWidget(QLabel("Preview:"))
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(150)
        layout.addWidget(self.preview_text)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status message
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #666;")
        layout.addWidget(self.status_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.import_button = QPushButton("Import")
        self.import_button.setEnabled(False)
        self.import_button.clicked.connect(self.import_courses)
        button_layout.addWidget(self.import_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Course File",
            "",
            "Course Files (*.csv *.xlsx *.xls);;CSV Files (*.csv);;Excel Files (*.xlsx *.xls);;All Files (*.*)"
        )

        if file_path:
            self.selected_file = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.validate_and_preview_file()

    def validate_and_preview_file(self):
        if not self.selected_file:
            return

        # Validate file format
        is_valid, message = self.db.validate_file_format(self.selected_file)

        if is_valid:
            self.status_label.setText("File format is valid")
            self.status_label.setStyleSheet("color: green;")
            self.import_button.setEnabled(True)
            self.show_preview()
        else:
            self.status_label.setText(f"Error: {message}")
            self.status_label.setStyleSheet("color: red;")
            self.import_button.setEnabled(False)
            self.preview_text.clear()

    def show_preview(self):
        try:
            file_extension = self.selected_file.lower().split('.')[-1]

            if file_extension == 'csv':
                df = pd.read_csv(self.selected_file)
                self._show_course_preview(df)
            elif file_extension in ['xlsx', 'xls']:
                xls = pd.ExcelFile(self.selected_file)
                translation_sheets = ['Programs', 'Program_Majors', 'Course_Groups',
                                      'Major_Requirements', 'Course_Equivalences']

                if all(sheet in xls.sheet_names for sheet in translation_sheets):
                    self._show_translation_preview(xls)
                else:
                    df = pd.read_excel(self.selected_file)
                    self._show_course_preview(df)
            else:
                raise ValueError("Unsupported file format")

        except Exception as e:
            self.preview_text.setText(f"Error reading file: {str(e)}")

    def import_courses(self):
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            self.import_button.setEnabled(False)
            self.browse_button.setEnabled(False)
            self.status_label.setText("Importing courses...")

            # Import courses
            courses_added = self.db.import_courses_from_file(self.selected_file)

            if courses_added > 0:
                message = f"Successfully imported {courses_added} courses"
                self.status_label.setText(message)
                self.status_label.setStyleSheet("color: green;")
                self.import_completed.emit(True, message)

                # Show success message
                QMessageBox.information(
                    self,
                    "Import Successful",
                    message
                )
                self.accept()
            else:
                raise Exception("No courses were imported")

        except Exception as e:
            error_message = f"Import failed: {str(e)}"
            self.status_label.setText(error_message)
            self.status_label.setStyleSheet("color: red;")
            self.import_completed.emit(False, error_message)

            # Show error message
            QMessageBox.critical(
                self,
                "Import Failed",
                error_message
            )

        finally:
            self.progress_bar.setVisible(False)
            self.import_button.setEnabled(True)
            self.browse_button.setEnabled(True)

    def _show_course_preview(self, df):
        preview_text = "Headers:\n"
        preview_text += ", ".join(df.columns) + "\n\n"
        preview_text += "First 5 rows:\n"
        preview_text += df.head().to_string()
        self.preview_text.setText(preview_text)

    def _show_translation_preview(self, xls):
        preview_text = "Translation Data Sheets:\n\n"
        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet)
            preview_text += f"{sheet}:\n"
            preview_text += "Headers: " + ", ".join(df.columns) + "\n"
            preview_text += "Row count: " + str(len(df)) + "\n\n"
        self.preview_text.setText(preview_text)