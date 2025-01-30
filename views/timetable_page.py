# views/timetable_page.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QToolTip
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
import logging

class CustomTableWidgetItem(QTableWidgetItem):
    def __init__(self, code, name, venue, day, start_time, end_time, instructor):
        super().__init__()
        self.code = code
        self.name = name
        self.venue = venue
        self.day = day
        self.start_time = start_time
        self.end_time = end_time
        self.instructor = instructor
        self.setToolTip(
            f"Course: {code} - {name}\n"
            f"Venue: {venue}\n"
            f"Instructor: {instructor}\n"
            f"Time: {start_time}-{end_time}\n"
        )

class TimetablePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

        self.day_to_column = {
            "Monday": 0,
            "Tuesday": 1,
            "Wednesday": 2,
            "Thursday": 3,
            "Friday": 4
        }

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Navigation controls
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        nav_layout.addWidget(self.prev_button)

        self.nav_status = QLabel("Schedule 0 of 0")
        nav_status_container = QHBoxLayout()
        nav_status_container.addStretch()
        nav_status_container.addWidget(self.nav_status)
        nav_status_container.addStretch()
        nav_layout.addLayout(nav_status_container)

        self.next_button = QPushButton("Next")
        nav_layout.addWidget(self.next_button)

        layout.addLayout(nav_layout)

        # Timetable widget
        self.timetable = QTableWidget()
        self.setup_timetable()
        layout.addWidget(self.timetable)

    def setup_timetable(self):
        time_slots = [f"{i:02d}:00" for i in range(8, 18)]
        self.timetable.setRowCount(len(time_slots))
        self.timetable.setVerticalHeaderLabels(time_slots)

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.timetable.setColumnCount(len(days))
        self.timetable.setHorizontalHeaderLabels(days)

        # Adjust table properties
        self.timetable.setShowGrid(True)
        self.timetable.setSelectionMode(QTableWidget.SelectionMode.NoSelection)

        # Calculate row height to fit the frame
        available_height = 650  # Accounting for navigation and margins
        row_height = available_height // len(time_slots)

        # Calculate column width to fit the frame
        available_width = 960  # Accounting for margins and vertical header
        column_width = available_width // len(days)

        # Set row heights and column widths
        for i in range(len(time_slots)):
            self.timetable.setRowHeight(i, row_height)

        header = self.timetable.horizontalHeader()
        for i in range(len(days)):
            self.timetable.setColumnWidth(i, column_width)
            header.setSectionResizeMode(i, header.ResizeMode.Fixed)

    def update_schedule(self, schedule):
        try:
            logging.info(f"Updating schedule with: {schedule}")
            self.timetable.clearContents()

            for course in schedule:
                try:
                    if isinstance(course, dict):
                        code = course.get('code', '')
                        name = course.get('name', '')
                        day_index = self.day_to_column.get(course.get('day'))
                        start_time = course.get('start_time', '')
                        end_time = course.get('end_time', '')
                        instructor = course.get('instructor', 'N/A')
                        print(code, name, instructor, "____________________")
                        print(instructor)
                        venue = course.get('venue', '')
                    else:
                        logging.error(f"Unsupported course data type: {type(course)}")
                        continue

                    start_hour = int(start_time.split(":")[0])
                    end_hour = int(end_time.split(":")[0])
                    row = start_hour - 8
                    row_span = end_hour - start_hour
                    col = day_index

                    if col is None:
                        logging.error(f"Invalid day value: {day_index}")
                        continue

                    item = CustomTableWidgetItem(code, name, venue, day_index, start_time, end_time, instructor)
                    display_text = (
                        f"{code}\n"
                        f"{start_time}-{end_time}\n"
                        f"{instructor}\n"
                        f"@ {venue}"
                    )
                    item.setText(display_text)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                    font = QFont()
                    font.setPointSize(8)
                    item.setFont(font)

                    item.setBackground(self.get_course_color(f"{code}_{schedule}"))

                    self.timetable.setItem(row, col, item)
                    if row_span > 1:
                        self.timetable.setSpan(row, col, row_span, 1)

                except (ValueError, IndexError) as e:
                    logging.error(f"Error processing course: {str(e)}")
                    continue

        except Exception as e:
            logging.error(f"Error updating schedule: {str(e)}")

    def get_course_color(self, course_code):
        hash_value = sum(ord(c) for c in course_code)
        hue = (hash_value % 360) / 360.0
        color = QColor()
        color.setHsvF(hue, 0.3, 1.0, 0.3)
        return color

    def update_navigation_status(self, current, total):
        self.nav_status.setText(f"Schedule {current} of {total}")
        logging.info(f"Navigation status updated to: Schedule {current} of {total}")

    def clear_timetable(self):
        self.timetable.clearContents()