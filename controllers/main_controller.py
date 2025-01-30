# controllers/main_controller.py
import logging
import sys
from main_window import MainWindow
from controllers.timetable_controller import TimetableController
from controllers.course_search_controller import CourseSearchController
from controllers.cart_controller import CartController
from controllers.translation_controller import TranslationController
from database.db_init import init_database


class MainController:
    def __init__(self, app_context=None):
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        # Store app context
        self.app_context = app_context

        # Initialize database
        if not init_database():
            logging.error("Failed to initialize database")
            sys.exit(1)

        # Create main window
        self.main_window = MainWindow()

        # Initialize controllers with app context if available
        self.timetable_controller = TimetableController(self.main_window)
        self.search_controller = CourseSearchController(
            self.main_window,
            self.app_context.database if self.app_context else None
        )
        self.cart_controller = CartController(
            self.main_window,
            self.app_context.cart if self.app_context else None
        )
        self.translation_controller = TranslationController(
            self.main_window,
            self.app_context.database if self.app_context else None
        )

        # Set controller references in main window
        self.main_window.set_controllers(
            self.timetable_controller,
            self.cart_controller,
            self.search_controller,
            self.translation_controller
        )

        # Add pages to main window
        self.main_window.add_page(self.timetable_controller.timetable_page, "timetable")
        self.main_window.add_page(self.search_controller.search_page, "search")
        self.main_window.add_page(self.cart_controller.cart_page, "cart")
        self.main_window.add_page(self.translation_controller.translation_page,"translation")

        # Connect controllers
        self.connect_controllers()

        # Show initial page
        self.main_window.show_page("search")

        logging.info("MainController initialized successfully")

    def connect_controllers(self):
        # Give cart controller access to timetable controller
        self.cart_controller.timetable_controller = self.timetable_controller

        # Update cart count when switching to cart page
        self.main_window.view_cart.triggered.connect(self.cart_controller.show)

    def show(self):
        self.main_window.show()