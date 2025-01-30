print("Loading course_search_page.py")
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QLineEdit, QPushButton)
from views.components.course_list_widget import CourseListWidget

class CourseSearchPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search courses...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                padding: 8px 15px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #4CAF50;
            }
        """)
        layout.addWidget(self.search_bar)

        # Course list - specify this is not a cart list
        self.course_list = CourseListWidget(is_cart=False)
        layout.addWidget(self.course_list)

    def set_courses(self, courses):
        """Update the course list with new courses"""
        self.course_list.set_courses(courses)