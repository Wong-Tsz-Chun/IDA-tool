# app_context.py
from database.db_manager import DatabaseManager
from utils.cart_manager import CartManager
from utils.timetable_service import TimetableService

class AppContext:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.cart_manager = CartManager()
        self.timetable_service = TimetableService()

    @property
    def database(self):
        return self.db_manager

    @property
    def cart(self):
        return self.cart_manager

    @property
    def timetable(self):
        return self.timetable_service