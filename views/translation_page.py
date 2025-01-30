from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
                               QLabel, QTextEdit, QGroupBox, QFormLayout, QSizePolicy)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor, QPalette, QFont
import logging


class TranslationPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Selection area
        selection_group = QGroupBox("Course Selection")
        selection_group.setStyleSheet("""
            QGroupBox {
                background-color: #f5f5f5;
                border: 2px solid #dcdcdc;
                border-radius: 8px;
                margin-top: 1em;
                font-size: 14px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2c3e50;
            }
        """)
        selection_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # Fixed height for selection area

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(15, 15, 15, 15)

        # Create comboboxes with placeholder text
        self.program_combo = self.create_styled_combo()
        self.major_combo = self.create_styled_combo()
        self.group_combo = self.create_styled_combo()
        self.course_combo = self.create_styled_combo()

        # Add placeholder texts
        self.program_combo.addItem("Select Program")
        self.major_combo.addItem("Select Major")
        self.group_combo.addItem("Select Group")
        self.course_combo.addItem("Select Course")

        # Set initial states
        self.major_combo.setEnabled(False)
        self.group_combo.setEnabled(False)
        self.course_combo.setEnabled(False)

        # Create styled labels
        label_style = """
            QLabel {
                color: #34495e;
                font-weight: bold;
                font-size: 13px;
            }
        """
        program_label = QLabel("Program:")
        major_label = QLabel("Major:")
        group_label = QLabel("Group:")
        course_label = QLabel("Course:")

        for label in [program_label, major_label, group_label, course_label]:
            label.setStyleSheet(label_style)

        # Add to form layout
        form_layout.addRow(program_label, self.program_combo)
        form_layout.addRow(major_label, self.major_combo)
        form_layout.addRow(group_label, self.group_combo)
        form_layout.addRow(course_label, self.course_combo)

        selection_group.setLayout(form_layout)

        # Result area
        result_group = QGroupBox("Course Information")
        result_group.setStyleSheet("""
            QGroupBox {
                background-color: #f5f5f5;
                border: 2px solid #dcdcdc;
                border-radius: 8px;
                margin-top: 1em;
                font-size: 14px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2c3e50;
            }
        """)
        result_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Make result area expand

        result_layout = QVBoxLayout()
        result_layout.setContentsMargins(15, 15, 15, 15)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                padding: 10px;
                color: #2c3e50;
                font-size: 13px;
                line-height: 1.5;
            }
        """)
        self.result_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Make text edit expand

        result_layout.addWidget(self.result_text)
        result_group.setLayout(result_layout)

        # Add to main layout
        main_layout.addWidget(selection_group)
        main_layout.addWidget(result_group, 1)  # Add stretch factor of 1
        main_layout.setContentsMargins(10, 10, 10, 10)  # Add some padding around the edges
        main_layout.setSpacing(10)  # Space between widgets

    def create_styled_combo(self):
        combo = QComboBox()
        combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #c0c0c0;
                border-radius: 3px;
                padding: 5px;
                padding-right: 20px;  /* Make room for the arrow */
                min-width: 200px;
                min-height: 20px;
            }
            QComboBox:hover {
                border: 1px solid #808080;
            }
            QComboBox:disabled {
                background-color: #f0f0f0;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #404040;
                margin-right: 10px;
            }
            QComboBox::down-arrow:disabled {
                border-top: 5px solid #808080;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #c0c0c0;
                background: white;
                selection-background-color: #e0e0e0;
                selection-color: black;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                min-height: 25px;
                padding: 5px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #f0f0f0;
            }
        """)
        return combo

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                color: #2c3e50;
            }
        """)

    def populate_programs(self, programs: dict):
        self.program_combo.clear()
        self.program_combo.addItem("Select Program", "")
        for code, name in programs.items():
            self.program_combo.addItem(f"{code} - {name}", code)
        self.program_combo.setEnabled(True)

    def populate_majors(self, majors: dict):
        self.major_combo.clear()
        self.major_combo.addItem("Select Major", "")
        for code, name in majors.items():
            self.major_combo.addItem(f"{code} - {name}", code)
        self.major_combo.setEnabled(True)
        self.group_combo.setEnabled(False)
        self.course_combo.setEnabled(False)

    def populate_groups(self, groups: dict):
        self.group_combo.clear()
        self.group_combo.addItem("Select Group", "")
        for name in groups.values():
            self.group_combo.addItem(name, name)
        self.group_combo.setEnabled(True)
        self.course_combo.setEnabled(False)

    def populate_courses(self, courses: dict):
        try:
            self.course_combo.clear()

            if not courses:
                self.course_combo.addItem("No courses available")
                self.course_combo.setEnabled(False)
                return

            self.course_combo.addItem("Select Course", "")
            for code, display_text in courses.items():
                self.course_combo.addItem(display_text, code)

            self.course_combo.setEnabled(True)
            self.course_combo.setCurrentIndex(0)

        except Exception as e:
            logging.error(f"Error in populate_courses: {str(e)}")
            self.course_combo.clear()
            self.course_combo.addItem("Error loading courses")
            self.course_combo.setEnabled(False)

    def clear_selections(self, start_from: str):
        if start_from == 'major':
            self.major_combo.clear()
            self.major_combo.addItem("Select Major", "")
            start_from = 'group'
        if start_from == 'group':
            self.group_combo.clear()
            self.group_combo.addItem("Select Group", "")
            start_from = 'course'
        if start_from == 'course':
            self.course_combo.clear()
            self.course_combo.addItem("Select Course", "")
            self.result_text.clear()

    def display_course_info(self, course_data):
        try:
            if not course_data or not course_data.get('success'):
                hk_course = self.course_combo.currentText().split(' - ')[0].strip()
                info_text = f"""
                    <div style="font-family: Arial, sans-serif; line-height: 1.8;">
                        <div style="font-weight: bold;">CUHK Course:</div>
                        <div style="margin-left: 20px;">Course Code: {hk_course}</div>
                        <div style="margin-left: 20px;">Course Name: N/A</div>
                        <div style="margin-left: 20px;">Credits: N/A</div>
                        <div style="margin-left: 20px;">Description: N/A</div>
                        <br>
                        <div style="font-weight: bold;">CUHK-SZ Equivalent Course:</div>
                        <div style="margin-left: 20px;">No equivalent course available</div>
                    </div>
                """
                self.result_text.setHtml(info_text)
                return

            course_info = course_data.get('data', {})
            if not course_info:
                self.result_text.setPlainText("No course information available.")
                return

            info_text = """
                <div style="font-family: Arial, sans-serif; line-height: 1.8;">
                    <div style="font-weight: bold;">CUHK Course:</div>
                    <div style="margin-left: 20px;">Course Code: {hk_code}</div>
                    <div style="margin-left: 20px;">Course Name: {course_name}</div>
                    <div style="margin-left: 20px;">Credits: {credits}</div>
                    <div style="margin-left: 20px;">Description: {description}</div>
                    <br>
                    <div style="font-weight: bold;">CUHK-SZ Equivalent Course:</div>
                    <br>
                    <div style="margin-left: 20px;">Course Code: {sz_code}</div>
                    <div style="margin-left: 20px;">Course Name: {course_name}</div>
                    <div style="margin-left: 20px;">Credits: {credits}</div>
                </div>
            """.format(
                sz_code=course_info.get('sz_code', 'N/A'),
                hk_code=course_info.get('hk_code', 'N/A'),
                course_name=course_info.get('course_name', 'N/A'),
                credits=course_info.get('credits', 'N/A'),
                description=course_info.get('description', 'N/A')
            )

            self.result_text.setHtml(info_text)

        except Exception as e:
            logging.error(f"Error displaying course info: {str(e)}")
            self.result_text.setPlainText("Error displaying course information.")