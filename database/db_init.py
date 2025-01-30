#db_init

import sqlite3
import logging
from pathlib import Path

def init_database():
    """Initialize the SQLite database with required tables"""
    try:
        # Ensure data directory exists
        project_root = Path(__file__).parent.parent
        data_dir = project_root / "data"
        data_dir.mkdir(exist_ok=True)
        db_path = data_dir / "courses.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Drop existing tables to reset schema
        cursor.execute('DROP TABLE IF EXISTS cart')
        cursor.execute('DROP TABLE IF EXISTS course_sessions')
        cursor.execute('DROP TABLE IF EXISTS courses')

#___________________Course Search Info_______________________
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            course_code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            credit INTEGER NOT NULL,
            instructor TEXT NOT NULL DEFAULT 'STAFF'
        )
        ''')

        # Create course_sessions table (session details)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS course_sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            day INTEGER NOT NULL CHECK (day >= 0 AND day <= 4),
            venue TEXT NOT NULL DEFAULT 'TBA',
            credit INTEGER NOT NULL,
            start_time TEXT NOT NULL CHECK (start_time LIKE '__:__'),
            end_time TEXT NOT NULL CHECK (end_time LIKE '__:__'),
            instructor TEXT NOT NULL DEFAULT 'STAFF',
            remarks TEXT NOT NULL DEFAULT 'NONE',
            FOREIGN KEY (course_code) REFERENCES courses (code)
        )
        ''')
# ___________________Cart Info_______________________
        # Create cart table (stores selected courses)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            course_code TEXT,
            FOREIGN KEY (course_code) REFERENCES courses (code)
        )
        ''')

        # Insert sample data if tables are empty
        cursor.execute('SELECT COUNT(*) FROM courses')
        if cursor.fetchone()[0] == 0:
            # Insert courses
            sample_courses = [
                ("TEST404 A", "Lecture Test 01", 3, "Prof Eggyolk"),
            ]
            cursor.executemany('''
            INSERT INTO courses (course_code, name, credit, instructor)
            VALUES (?, ?, ?, ?)
            ''', sample_courses)

            # Insert course sessions
            sample_sessions = [
                ("TEST404 A", "Lecture Test 01", "Lec", 0, "TA101", 3, "10:00", "11:30", "Prof Eggyolk","None"),

            ]
            cursor.executemany('''
            INSERT INTO course_sessions (course_code, name, type, day, venue, credit, start_time, end_time, instructor, remarks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_sessions)

# ___________________Course Trans Info_______________________

            # Create programs table
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS programs (
                        program_code TEXT PRIMARY KEY,
                        program_name TEXT NOT NULL,
                        description TEXT
                    )
                    ''')

            # Create program_majors table
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS program_majors (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        program_code TEXT NOT NULL,
                        major_code TEXT NOT NULL,
                        major_name TEXT NOT NULL,
                        FOREIGN KEY (program_code) REFERENCES programs (program_code),
                        UNIQUE (program_code, major_code)
                    )
                    ''')

            # Create course_groups table
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS course_groups (
                        group_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        group_name TEXT NOT NULL CHECK (
                            group_name IN (
                                'University Core',
                                '1st Major Required',
                                '1st Major Elective',
                                '2nd Major Required',
                                '2nd Major Elective'
                            )
                        )
                    )
                    ''')

            # Create major_requirements table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS major_requirements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    program_code TEXT NOT NULL,
                    major_code TEXT NOT NULL,
                    group_name TEXT NOT NULL,
                    course_code TEXT NOT NULL,
                    campus TEXT NOT NULL CHECK (campus IN ('HK', 'SZ')),
                    FOREIGN KEY (program_code) REFERENCES programs (program_code)
                )
            ''')

            # Create course_equivalences table
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS course_equivalences (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sz_code TEXT NOT NULL,
                        hk_code TEXT NOT NULL,
                        course_name TEXT NOT NULL,
                        credits INTEGER NOT NULL,
                        description TEXT,
                        UNIQUE (sz_code, hk_code)
                    )
                    ''')

        conn.commit()
        conn.close()

        logging.info("Database initialized successfully")
        return True

    except sqlite3.Error as e:
        logging.error(f"Database initialization error: {str(e)}")
        return False