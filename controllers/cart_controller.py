# controllers/cart_controller.py
from PySide6.QtWidgets import QMessageBox
import sqlite3
import logging
from views.cart_page import CartPage
from utils.cart_manager import CartManager
from utils.timetable_service import TimetableService


class CartController:
    def __init__(self, parent_window, cart_manager=None):
        self.parent = parent_window
        self.cart_page = CartPage()
        self.cart_manager = cart_manager or CartManager()
        self.timetable_service = TimetableService()
        self.timetable_controller = None

        self.setup_connections()
        logging.info("Cart controller initialized")

    def setup_connections(self):
        try:
            # timetable button
            self.cart_page.generate_button.clicked.connect(self.generate_timetable)

            # remove course buttons
            self.cart_page.course_list.course_removed.connect(self.remove_from_cart)

            # clear cart button
            self.cart_page.clear_button.clicked.connect(self.clear_cart)

            logging.info("Cart controller connections set up successfully")
        except Exception as e:
            logging.error(f"Error setting up cart controller connections: {str(e)}")
            raise

    def show(self):
        try:
            self.update_cart_display()
            logging.info("Cart display updated")
        except Exception as e:
            logging.error(f"Error updating cart display: {str(e)}")

    def update_cart_display(self):
        courses = self.cart_manager.get_cart_courses()
        logging.info(f"Courses in cart: {courses}")
        if courses is None:
            courses = []
        self.cart_page.set_courses(courses)

    def refresh_cart(self):
        self.update_cart_display()

    def generate_timetable(self):
        cart_courses = self.cart_manager.get_cart_courses()
        logging.info(f"Cart courses: {cart_courses}")

        if not cart_courses:
            QMessageBox.warning(
                self.cart_page,
                "Empty Cart",
                "Please add some courses to your cart first."
            )
            return

        try:
            timetable_results = self.timetable_service.generate_timetable_combinations(cart_courses)
            logging.info(f"Timetable results: {timetable_results}")

            if not timetable_results:
                QMessageBox.warning(
                    self.cart_page,
                    "No Valid Combinations",
                    "Could not generate a valid timetable with selected courses. "
                    "Please check for time conflicts."
                )
                return

            logging.info("Setting cart courses in timetable controller")
            self.parent.timetable_controller.set_cart_courses(cart_courses)

            logging.info("Switching to timetable page")
            self.parent.show_page("timetable")

        except Exception as e:
            logging.error(f"Error in generate_timetable: {str(e)}")
            QMessageBox.critical(
                self.cart_page,
                "Error",
                f"Error generating timetable: {str(e)}"
            )

    def remove_from_cart(self, course_code: str):
        if self.cart_manager.remove_from_cart(course_code):
            self.update_cart_display()
            self.parent.update_cart_count()

    def clear_cart(self):
        try:
            with self.cart_manager.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM cart')
                conn.commit()
                self.update_cart_display()
                self.parent.update_cart_count()
        except sqlite3.Error as e:
            QMessageBox.critical(
                self.cart_page,
                "Error",
                f"Error clearing cart: {str(e)}"
            )

    def get_page(self):
        return self.cart_page