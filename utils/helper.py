import logging

def show_date(day_number: int) -> str:
    """Convert day number (0-4) to abbreviated day name"""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    try:
        return days[day_number]
    except (IndexError, TypeError):
        logging.error(f"Error converting day {day_number}: Invalid day")
        return None

def format_time(time_str: str) -> str:
    """Format time string nicely"""
    try:
        start_time, end_time = time_str.split('-')
        return f"{start_time.strip()} - {end_time.strip()}"
    except:
        return time_str

import os
import sys

def resource_path(relative_path):
    """Get absolute path to resource"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)