from PySide6.QtCore import Qt, QObject
import logging
from database.db_manager import DatabaseManager
from views.translation_page import TranslationPage


class TranslationController(QObject):
    def __init__(self, parent_window, db_manager=None):
        super().__init__()
        self.parent = parent_window
        self.translation_page = TranslationPage()
        self.db = db_manager or DatabaseManager()
        self.setup_connections()
        self.load_programs()

    def setup_connections(self):
        self.translation_page.program_combo.currentIndexChanged.connect(
            lambda: self.on_selection_change('program'))
        self.translation_page.major_combo.currentIndexChanged.connect(
            lambda: self.on_selection_change('major'))
        self.translation_page.group_combo.currentIndexChanged.connect(
            lambda: self.on_selection_change('group'))
        self.translation_page.course_combo.currentTextChanged.connect(
            self.handle_course_change)

    def on_selection_change(self, source):
        try:
            program_code = self.translation_page.program_combo.currentData()
            major_code = self.translation_page.major_combo.currentData()
            group_name = self.translation_page.group_combo.currentText()

            if source == 'program':
                if not program_code or self.translation_page.program_combo.currentIndex() == 0:
                    self.translation_page.clear_selections('major')
                    return
                self.handle_program_change(program_code)

            elif source == 'major':
                if not major_code or self.translation_page.major_combo.currentIndex() == 0:
                    self.translation_page.clear_selections('group')
                    return
                self.handle_major_change(major_code)

            elif source == 'group':
                if not group_name or self.translation_page.group_combo.currentIndex() == 0:
                    self.translation_page.clear_selections('course')
                    return
                if all([program_code, major_code, group_name]):
                    self.filter_courses(program_code, major_code, group_name)

        except Exception as e:
            logging.error(f"Error in selection change: {str(e)}")
            self.translation_page.clear_selections('major')

    def load_programs(self):
        try:
            result = self.db.get_available_programs()
            if result['success']:
                self.translation_page.populate_programs(result['programs'])
        except Exception as e:
            logging.error(f"Error loading programs: {str(e)}")

    def handle_program_change(self, program_code: str):
        try:
            result = self.db.get_majors_for_program(program_code)
            if result['success']:
                self.translation_page.populate_majors(result['majors'])
                self.translation_page.clear_selections('group')
        except Exception as e:
            logging.error(f"Error loading majors: {str(e)}")
            self.translation_page.clear_selections('major')

    def handle_major_change(self, major_code: str):
        try:
            program_code = self.translation_page.program_combo.currentData()
            result = self.db.get_groups_for_major(program_code, major_code)
            if result['success']:
                self.translation_page.populate_groups(result['groups'])
                self.translation_page.clear_selections('course')
        except Exception as e:
            logging.error(f"Error loading groups: {str(e)}")
            self.translation_page.clear_selections('group')

    def filter_courses(self, program_code: str, major_code: str, group_name: str):
        try:
            logging.info(f"Filtering courses for: {program_code}, {major_code}, {group_name}")
            courses = self.db.get_filtered_courses(program_code, major_code, group_name)
            logging.info(f"Received courses from database: {courses}")

            if isinstance(courses, dict):  # Check if courses is a dictionary
                self.translation_page.populate_courses(courses)
            else:
                logging.warning(f"Unexpected courses data type: {type(courses)}")
                self.translation_page.clear_selections('course')

        except Exception as e:
            logging.error(f"Error in filter_courses: {str(e)}")
            self.translation_page.clear_selections('course')

    def handle_course_change(self, course_text: str):
        try:
            # Get the course code from the combo box's current data
            course_code = self.translation_page.course_combo.currentData()

            if not course_code or self.translation_page.course_combo.currentIndex() == 0:
                self.translation_page.result_text.clear()
                return

            # Remove any whitespace and extract the course code if it contains campus info
            course_code = course_code.split('(')[0].strip()

            logging.info(f"Getting equivalence for course: {course_code}")
            result = self.db.get_course_equivalence(course_code)
            logging.info(f"Got course equivalence result: {result}")

            if result and result.get('success'):
                self.translation_page.display_course_info(result)
            else:
                # Create a basic result for courses without equivalence
                current_text = self.translation_page.course_combo.currentText()
                campus = "HK" if "(HK)" in current_text else "SZ"

                no_equiv_result = {
                    "success": False,
                    "data": {
                        "course_code": course_code,
                        "campus": campus
                    }
                }
                self.translation_page.display_course_info(no_equiv_result)

        except Exception as e:
            logging.error(f"Error loading course information: {str(e)}")
            self.translation_page.result_text.setText("Error loading course information")
