# main_window.py
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QMenuBar, QStatusBar, QWidget, QHBoxLayout
from config import WINDOW_TITLE, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT
from views.import_dialog import ImportDialog


class SubNavBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QMenuBar {
                background-color: #455A64;
                color: white;
                padding: 4px;
                font-size: 13px;
            }
            QMenuBar::item {
                padding: 4px 15px;
                margin-right: 5px;
                background-color: transparent;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #546E7A;
            }
            QMenuBar::item:pressed {
                background-color: #607D8B;
            }
        """)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

# _____________________________________________main window styling_________________________________________
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F5F5;
            }
            QMenuBar {
                background-color: #37474F;
                color: white;
                padding: 4px;
                font-size: 14px;
            }
            QMenuBar::item {
                padding: 4px 10px;
                background-color: transparent;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #455A64;
            }
            QMenuBar::item:pressed {
                background-color: #546E7A;
            }
            QMenu {
                background-color: #FAFAFA;
                border: 1px solid #E0E0E0;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 25px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #E0E0E0;
            }
            QStatusBar {
                background-color: #37474F;
                color: white;
                padding: 4px;
                font-size: 13px;
            }
            QStackedWidget {
                background-color: #FAFAFA;
                border-top: 1px solid #E0E0E0;
            }
        """)

#_____________________________________________nav container_________________________________________
        self.nav_container = QWidget()
        self.nav_layout = QHBoxLayout(self.nav_container)
        self.nav_layout.setSpacing(0)
        self.nav_layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.pages = {}

        # Initialize controller references
        self.timetable_controller = None
        self.cart_controller = None
        self.search_controller = None

        self.setup_ui()

    def setup_ui(self):
        self.setup_menu_bars()
        self.setup_status_bar()

    # _____________________________________________menu bar_____________________________________________
    def setup_menu_bars(self):
        # Main navigation bar
        self.menubar = QMenuBar()
        self.setMenuBar(self.menubar)

        # Add menu items
        self.file_menu = self.menubar.addMenu("&File")
        self.import_action = self.file_menu.addAction("Import Courses...")
        self.import_action.triggered.connect(self.show_import_dialog)

        exit_action = self.file_menu.addAction("Exit")
        exit_action.setStatusTip("Exit application")

        # Add Plan button to main menu
        self.plan_action = self.menubar.addAction("&Plan")
        self.plan_action.triggered.connect(self.toggle_sub_nav)

        # Sub navigation bar (initially hidden)
        self.sub_nav = SubNavBar(self)
        self.sub_nav.hide()

        # Add view actions to sub nav
        self.view_search = self.sub_nav.addAction("Course Search")
        self.view_cart = self.sub_nav.addAction("Shopping Cart")
        self.view_timetable = self.sub_nav.addAction("Timetable")

        # Connect sub nav actions
        self.view_search.triggered.connect(lambda: self.show_page("search"))
        self.view_cart.triggered.connect(lambda: self.show_page("cart"))
        self.view_timetable.triggered.connect(lambda: self.show_page("timetable"))

        # Position sub nav below main nav
        self.sub_nav.setGeometry(0, self.menubar.height(), self.width(), 30)

        # In MainWindow.setup_menu_bars method:
        self.view_translation = self.sub_nav.addAction("Translation")
        self.view_translation.triggered.connect(lambda: self.show_page("translation"))

    def toggle_sub_nav(self):
        if self.sub_nav.isHidden():
            self.sub_nav.show()
            # Adjust main content margin to accommodate sub nav
            self.stack.setContentsMargins(0, self.sub_nav.height(), 0, 0)
        else:
            self.sub_nav.hide()
            # Reset main content margin
            self.stack.setContentsMargins(0, 0, 0, 0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Update sub nav width when window is resized
        if self.sub_nav:
            self.sub_nav.setGeometry(0, self.menubar.height(), self.width(), 30)


    def setup_status_bar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready")  # Default status message

    # _____________________________________________functioning_____________________________________________
    def add_page(self, page, name):
        self.pages[name] = page
        self.stack.addWidget(page)

    def show_page(self, name):
        if name in self.pages:
            # Call show method on controller if available
            controller_name = f"{name}_controller"
            if hasattr(self, controller_name):
                controller = getattr(self, controller_name)
                if hasattr(controller, 'show'):
                    controller.show()

            self.stack.setCurrentWidget(self.pages[name])

    def update_cart_count(self):
        """Update cart count in status bar"""
        try:
            cart_courses = self.cart_controller.cart_manager.get_cart_courses()
            count = len(cart_courses)
            self.statusbar.showMessage(f"Cart: {count} course{'s' if count != 1 else ''}")
        except Exception as e:
            self.statusbar.showMessage("Error updating cart count")

    def set_controllers(self, timetable_ctrl, cart_ctrl, search_ctrl,translation_ctrl):
        """Set controller references"""
        self.timetable_controller = timetable_ctrl
        self.cart_controller = cart_ctrl
        self.search_controller = search_ctrl
        self.translation_controller = translation_ctrl

    def show_import_dialog(self):
        """Show the import dialog"""
        dialog = ImportDialog(self)
        dialog.import_completed.connect(self.on_import_completed)
        dialog.exec()

    def on_import_completed(self, success, message):
        """Handle import completion"""
        if success:
            # Refresh all views
            if self.search_controller:
                self.search_controller.refresh_courses()
            if self.cart_controller:
                self.cart_controller.refresh_cart()
            if self.timetable_controller:
                self.timetable_controller.refresh_timetable()
            self.statusbar.showMessage("Courses imported successfully", 3000)
        else:
            self.statusbar.showMessage("Import failed", 3000)