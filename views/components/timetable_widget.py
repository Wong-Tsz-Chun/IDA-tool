from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from config import COURSE_COLORS, DAY_NAMES, MIN_HOUR, MAX_HOUR
import logging

class TimeTableWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.schedule = None
        self.courses = []
        self.initUI()

    def initUI(self):
        self.setMinimumSize(800, 600)
        self.time_width = 60
        self.day_height = 30
        self.hour_height = 60

        # Generate time slots (8:30 to 18:30)
        self.times = [f"{h:02d}:{m:02d}"
                      for h in range(MIN_HOUR, MAX_HOUR + 1)
                      for m in (0, 30)]

        # Calculate total width and height
        self.total_width = self.time_width + (len(DAY_NAMES) * 150)
        self.total_height = self.day_height + (len(self.times) * self.hour_height // 2)
        self.setMinimumSize(self.total_width, self.total_height)

    def update_schedule(self, schedule):
        self.schedule = schedule
        self.update()

    def paintEvent(self, event):
        if not self.schedule:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw time labels
        painter.setPen(QPen(Qt.black, 1))
        for i, time in enumerate(self.times):
            y = self.day_height + (i * self.hour_height // 2)
            painter.drawText(5, y + 20, time)

        # Draw day headers
        for i, day in enumerate(DAY_NAMES):
            x = self.time_width + (i * 150)
            painter.drawText(x + 10, 20, day)

        # Draw grid
        for i in range(len(self.times) + 1):
            y = self.day_height + (i * self.hour_height // 2)
            painter.drawLine(self.time_width, y, self.total_width, y)

        for i in range(len(DAY_NAMES) + 1):
            x = self.time_width + (i * 150)
            painter.drawLine(x, self.day_height, x, self.total_height)

        # Draw courses
        for idx, course in enumerate(self.schedule):
            # Get course data
            day = course['day']
            start_time = course['start_time']
            end_time = course['end_time']
            code = course['course_code']
            instructor = course['instructor']

            # Convert time to position
            try:
                start_idx = self.times.index(start_time)
                end_idx = self.times.index(end_time)

                x = self.time_width + (day * 150)
                y1 = self.day_height + (start_idx * self.hour_height // 2)
                y2 = self.day_height + (end_idx * self.hour_height // 2)

                # Draw course block
                color = QColor(COURSE_COLORS[idx % len(COURSE_COLORS)])
                painter.fillRect(x + 1, y1 + 1, 148, y2 - y1 - 1, color)

                # Draw course code and instructor
                painter.setPen(Qt.black)
                font = painter.font()
                font.setBold(True)
                painter.setFont(font)
                painter.drawText(x + 5, y1 + 20, f"{code}\n{instructor}")  # Draw code and instructor
            except ValueError as e:
                logging.error(f"Error drawing course {code}: {str(e)}")