# main.py
import sys
from PySide6.QtWidgets import QApplication
from controllers.main_controller import MainController
from database.db_init import init_database
from app_context import AppContext
import logging


def main():
    #_____________________________________________Configure logging_____________________________________________
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('log.txt'),
            logging.StreamHandler()
        ]
    )

    # _____________________________________________Initialize database_____________________________________________
    if not init_database():
        logging.error("Failed to initialize database")
        sys.exit(1)

    #_____________________________________________Create application_____________________________________________
    app = QApplication(sys.argv)

    try:
        context = AppContext()
        controller = MainController(context)
        controller.show()
        sys.exit(app.exec())
    except Exception as e:
        logging.error(f"Application error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()