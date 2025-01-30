# controllers/timetable_controller.py
from views.timetable_page import TimetablePage
from utils.timetable_service import TimetableService
import logging


class TimetableController:
    def __init__(self, parent_window):
        self.parent = parent_window
        self.timetable_page = TimetablePage()
        self.timetable_service = TimetableService()
        self.schedules = []
        self.course_groups = {}
        self.current_schedule_index = 0
        self.cart_courses = []
        self._is_updating = False

        self.setup_connections()
        logging.info("TimetableController initialized")

    def set_cart_courses(self, cart_courses):
        logging.info(f"Setting cart courses: {cart_courses}")
        self.cart_courses = cart_courses
        try:
            result = self.timetable_service.generate_timetable_combinations(cart_courses)
            if not isinstance(result, tuple) or len(result) != 2:
                logging.error("generate_timetable_combinations did not return a tuple with two elements")
                return

            schedules, course_groups = result
            self.set_schedules(schedules, course_groups)
        except Exception as e:
            logging.error(f"Error generating timetable: {str(e)}")

    def setup_connections(self):
        """Connect navigation buttons"""
        self.timetable_page.prev_button.clicked.connect(self.prev_schedule)
        self.timetable_page.next_button.clicked.connect(self.next_schedule)
        logging.info("Timetable navigation buttons connected")

    def set_schedules(self, schedules, course_groups):
        """Set new schedules and display the first one"""
        if not schedules:
            logging.error("No schedules provided")
            return

        if self._is_updating:
            return

        try:
            self._is_updating = True
            self.schedules = schedules
            self.course_groups = course_groups
            self.current_schedule_index = 0

            if self.schedules:
                self.show_current_schedule()
                self.update_navigation_status()
                self.update_navigation_buttons()

        except Exception as e:
            logging.error(f"Error setting schedules: {str(e)}", exc_info=True)
        finally:
            self._is_updating = False

    def show_current_schedule(self):
        """Display the current schedule"""
        if not self.schedules:
            logging.info("No schedules to display")
            return

        try:
            current_schedule = self.schedules[self.current_schedule_index]
            formatted_schedule = []

            # Format selected courses for the timetable widget
            for course_code in current_schedule['selected']:
                for course in self.course_groups[course_code]:
                    # Convert day number to day name
                    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
                    day = days[course['day']] if 0 <= course['day'] < len(days) else "Unknown"

                    formatted_course = {
                        'code': course['course_code'],
                        'day': day,
                        'start_time': course['start_time'],
                        'end_time': course['end_time'],
                        'venue': course['venue'],
                        'instructor' : course['instructor']
                    }
                    formatted_schedule.append(formatted_course)

            # Update timetable widget with formatted schedule
            self.timetable_page.update_schedule(formatted_schedule)

        except Exception as e:
            logging.error(f"Error showing schedule: {str(e)}", exc_info=True)

    def next_schedule(self):
        """Show next schedule if available"""
        if self._is_updating:
            return

        try:
            self._is_updating = True
            if self.current_schedule_index < len(self.schedules) - 1:
                self.current_schedule_index += 1
                self.show_current_schedule()
                self.update_navigation_status()
                self.update_navigation_buttons()
        finally:
            self._is_updating = False

    def prev_schedule(self):
        """Show previous schedule if available"""
        if self._is_updating:
            return

        try:
            self._is_updating = True
            if self.current_schedule_index > 0:
                self.current_schedule_index -= 1
                self.show_current_schedule()
                self.update_navigation_status()
                self.update_navigation_buttons()
        finally:
            self._is_updating = False

    def update_navigation_buttons(self):
        """Update the enabled state of navigation buttons"""
        self.timetable_page.prev_button.setEnabled(self.current_schedule_index > 0)
        self.timetable_page.next_button.setEnabled(
            self.current_schedule_index < len(self.schedules) - 1
        )

    def update_navigation_status(self):
        """Update the navigation status display"""
        total = len(self.schedules)
        current = self.current_schedule_index + 1 if total > 0 else 0
        self.timetable_page.update_navigation_status(current, total)

    def show(self):
        """Show the timetable page and current schedule"""
        if self._is_updating:
            return

        try:
            self._is_updating = True
            self.show_current_schedule()
            self.update_navigation_buttons()
        finally:
            self._is_updating = False

    def get_page(self):
        """Return the timetable page widget"""
        return self.timetable_page

    def refresh_timetable(self):
        """Refresh the timetable by re-generating the timetable combinations"""
        if self.cart_courses:
            try:
                schedules, course_groups = self.timetable_service.generate_timetable_combinations(self.cart_courses)
                self.set_schedules(schedules, course_groups)
                self.show_current_schedule()
            except Exception as e:
                logging.error(f"Error refreshing timetable: {str(e)}")
        else:
            logging.info("No cart courses to refresh the timetable")