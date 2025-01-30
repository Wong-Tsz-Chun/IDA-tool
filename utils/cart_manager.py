# utils/cart_manager.py
from database.db_manager import DatabaseManager
import re
import logging
from datetime import datetime


class CartManager:

    def __init__(self):
        self.db = DatabaseManager()

    def get_cart_courses(self):
        courses = self.db.get_cart_courses()
        return courses


    def add_to_cart(self, course_code: str) -> bool:
        return self.db.add_to_cart(course_code)

    def remove_from_cart(self, course_code: str) -> bool:
        return self.db.remove_from_cart(course_code)
