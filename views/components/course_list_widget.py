from PySide6.QtGui import QColor, Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QScrollArea, QGraphicsDropShadowEffect)
from PySide6.QtCore import Signal
import logging
import utils.helper as hp

class CourseCard(QWidget):
    add_to_cart = Signal(str)
    remove_from_cart = Signal(str)

    def __init__(self, course_data_list, is_cart_item=False):
        super().__init__()
        # Group sessions by course_code
        self.course_data = course_data_list[0]  # Use first item for common data
        self.sessions = course_data_list  # All sessions
        self.is_cart_item = is_cart_item

        self.card_widget = QWidget()
        self.card_widget.setObjectName("card")
        # Update card height to accommodate multiple sessions
        self.card_widget.setStyleSheet("""
            QWidget#card {
                background-color: #FAFAFA;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 16px;
                min-height: 180px;
                max-height: 250px;  /* Increased for multiple sessions */
            }
            QWidget#card:hover {
                background-color: #F5F5F5;
                border-color: #D0D0D0;
            }
            QPushButton {
                background-color: #78909C;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                min-width: 120px;
                max-width: 120px;
                height: 35px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #607D8B;
            }
            QPushButton#remove-button {
                background-color: #EF5350;
            }
            QPushButton#remove-button:hover {
                background-color: #E53935;
            }
            QLabel#course-code {
                font-size: 18px;
                font-weight: 600;
                color: #37474F;
                min-height: 24px;
                max-height: 24px;
            }
            QLabel#course-name {
                font-size: 18px;
                font-weight: 600;
                color: #37474F;
                min-height: 24px;
                max-height: 24px;
            }
            QLabel#details {
                color: #78909C;
                font-size: 13px;
                min-height: 16px;
                max-height: 16px;
            }
            QLabel#label-text {
                color: #546E7A;
                font-size: 13px;
                font-weight: 500;
                min-width: 80px;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.card_widget.setGraphicsEffect(shadow)

        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Card layout
        card_layout = QHBoxLayout(self.card_widget)
        card_layout.setSpacing(20)

        # Left side content
        left_content = QVBoxLayout()
        left_content.setSpacing(8)

        # Course header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        course_code_label = QLabel(self.course_data['course_code'])
        course_code_label.setObjectName("course-code")
        course_code_label.setFixedWidth(120)

        name_label = QLabel(self.course_data['name'])
        name_label.setObjectName("course-name")
        name_label.setMaximumWidth(400)

        header_layout.addWidget(course_code_label)
        header_layout.addWidget(name_label, 1)
        header_layout.addStretch()

        # Course details
        details_layout = QVBoxLayout()
        details_layout.setSpacing(6)
        details_layout.setContentsMargins(0, 8, 0, 0)

        # Create info rows with aligned labels
        info_pairs = [
            ("Instructor:", self.course_data['instructor']),
            ("Credit:", self.course_data['credit']),
            ("Schedule:", self._format_sessions()),
            ("Remarks:",
             self.course_data['remarks'][:47] + "..." if len(self.course_data['remarks']) > 50 else self.course_data[
                 'remarks'])
        ]

        for label_text, value in info_pairs:
            row_layout = QHBoxLayout()

            label = QLabel(label_text)
            label.setObjectName("label-text")
            label.setFixedWidth(80)

            value_label = QLabel(str(value))
            value_label.setObjectName("details")
            value_label.setTextFormat(Qt.PlainText)

            row_layout.addWidget(label)
            row_layout.addWidget(value_label, 1)
            row_layout.addStretch()

            details_layout.addLayout(row_layout)

        left_content.addLayout(header_layout)
        left_content.addLayout(details_layout)

        # Right side with button
        right_content = QVBoxLayout()
        right_content.setAlignment(Qt.AlignCenter | Qt.AlignRight)

        if self.is_cart_item:
            action_button = QPushButton("Remove")
            action_button.setObjectName("remove-button")
            action_button.clicked.connect(
                lambda: self.remove_from_cart.emit(self.course_data['course_code'])
            )
        else:
            action_button = QPushButton("Add to Cart")
            action_button.clicked.connect(
                lambda: self.add_to_cart.emit(self.course_data['course_code'])
            )

        right_content.addWidget(action_button)

        # Add content to card layout
        card_layout.addLayout(left_content, stretch=4)
        card_layout.addLayout(right_content, stretch=1)

        # Add card widget to main layout
        main_layout.addWidget(self.card_widget)

    def _format_sessions(self):
        sessions = []
        for session in self.sessions:
            day = hp.show_date(session['day'])
            time = f"{session['start_time']} - {session['end_time']}"
            venue = session['venue']
            type_info = f" ({session['type']})" if session.get('type') else ""
            sessions.append(f"{day} {time} at {venue}{type_info}")
        return " | ".join(sessions)


class CourseListWidget(QScrollArea):
    course_added = Signal(str)
    course_removed = Signal(str)

    def __init__(self, is_cart=False):
        super().__init__()
        self.is_cart = is_cart
        self.setup_ui()

        self.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
            QScrollBar {
                background: #F5F5F5;
                width: 10px;
            }
            QScrollBar::handle {
                background: #B0BEC5;
                border-radius: 5px;
            }
            QScrollBar::handle:hover {
                background: #90A4AE;
            }
        """)

    def setup_ui(self):
        self.setWidgetResizable(True)

        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.addStretch()

        self.setWidget(self.container)

    def set_courses(self, courses):
        if courses is None:
            courses = []
        logging.info(f"Setting courses in CourseListWidget: {courses}")

        # Clear existing cards
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Group courses by course_code
        grouped_courses = {}
        for course in courses:
            course_code = course['course_code']
            if course_code not in grouped_courses:
                grouped_courses[course_code] = []
            grouped_courses[course_code].append(course)

        # Create cards for grouped courses
        for course_code, sessions in grouped_courses.items():
            try:
                course_card = CourseCard(sessions, is_cart_item=self.is_cart)

                if self.is_cart:
                    course_card.remove_from_cart.connect(self.course_removed.emit)
                else:
                    course_card.add_to_cart.connect(self.course_added.emit)

                self.layout.insertWidget(self.layout.count() - 1, course_card)
                logging.info(f"Added course card for: {course_code}")
            except Exception as e:
                logging.error(f"Error creating course card: {str(e)}")
                continue

        if self.layout.count() == 0:
            self.layout.addStretch()

    def handle_course_added(self, course_code):
        logging.info(f"Course added to cart: {course_code}")

    def handle_course_removed(self, course_code):
        logging.info(f"Course removed from cart: {course_code}")