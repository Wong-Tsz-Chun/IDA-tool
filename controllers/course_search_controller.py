print("Loading course_search_controller.py")
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox
import logging
from database.db_manager import DatabaseManager
from views.course_search_page import CourseSearchPage


class CourseSearchController:
    def __init__(self, parent_window, db_manager=None):
        self.parent = parent_window
        self.search_page = CourseSearchPage()
        self.db = db_manager or DatabaseManager()

        # Connect signals
        self.setup_connections()

        # Load initial courses
        self.load_all_courses()

        logging.info("Course search controller initialized")

    def show_error_message(self, title: str, message: str):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    def show_conflict_confirmation(self, message: str) -> bool:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Time Conflict")
        msg_box.setText(message)
        msg_box.setInformativeText("Do you still want to add this course?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        return msg_box.exec() == QMessageBox.Yes

    def setup_connections(self):
        # Connect search bar signals
        self.search_page.search_bar.textChanged.connect(self.handle_search)
        self.search_page.search_bar.returnPressed.connect(self.handle_search)

        # Connect course list signals
        self.search_page.course_list.course_added.connect(self.handle_course_added)

        logging.info("Course search controller connections set up")

    def handle_search(self):
        try:
            search_text = self.search_page.search_bar.text().strip()

            if not search_text:
                self.load_all_courses()
                return

            # Search courses in database
            courses = self.db.search_courses(search_text)
            self.search_page.set_courses(courses)

        except Exception as e:
            error_msg = f"Error during course search: {str(e)}"
            self.show_error_message("Search Error", error_msg)
            logging.error(error_msg)

    def handle_course_added(self, course_code):
        try:
            # First try to add normally
            success, message = self.db.add_to_cart(course_code, force=False)

            if success:
                self.parent.update_cart_count()
                self.parent.statusBar().showMessage(f"Course {course_code} added to cart", 3000)
            else:
                if "Time Conflict" in message:
                    # Show conflict confirmation dialog
                    if self.show_conflict_confirmation(message):
                        # Force add the course
                        success, force_message = self.db.add_to_cart(course_code, force=True)
                        if success:
                            self.parent.update_cart_count()
                            self.parent.statusBar().showMessage(f"Course {course_code} force added to cart", 3000)
                        else:
                            self.show_error_message("Force Add Failed", force_message)
                else:
                    self.show_error_message("Course Addition Failed", message)

        except Exception as e:
            error_msg = f"Error adding course to cart: {str(e)}"
            self.show_error_message("Error", error_msg)
            logging.error(error_msg)

    def load_all_courses(self):
        try:
            courses = self.db.get_all_courses()

            if not courses:
                self.show_error_message("No Courses", "No courses found in the database")
                return

            self.search_page.set_courses(courses)

        except Exception as e:
            error_msg = f"Error loading courses: {str(e)}"
            self.show_error_message("Loading Error", error_msg)
            logging.error(error_msg)

    def refresh_courses(self):
        self.load_all_courses()