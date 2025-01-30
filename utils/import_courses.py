# utils/import_courses.py
import logging
from database.db_manager import DatabaseManager


def import_courses_from_csv(csv_path):
    db = DatabaseManager()

    # Validate CSV format
    is_valid, message = db.validate_csv_format(csv_path)
    if not is_valid:
        logging.error(f"CSV validation failed: {message}")
        return False

    # Import courses
    courses_added = db.import_courses_from_csv(csv_path)
    if courses_added > 0:
        logging.info(f"Successfully imported {courses_added} courses")
        return True
    else:
        logging.error("Failed to import courses")
        return False


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Import courses
    csv_path = 'data/courses.csv'
    if import_courses_from_csv(csv_path):
        print("Courses imported successfully")
    else:
        print("Failed to import courses")