# database/db_manager.py
import sqlite3
import os
from typing import List, Dict
import logging
from contextlib import contextmanager
import pandas as pd
import sys
import os

def resource_path(relative_path):
    """Get absolute path to resource"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class DatabaseManager:
    def __init__(self):
        self.db_path = resource_path(os.path.join('data', 'courses.db'))

        if not os.path.exists(self.db_path):
            logging.error(f"Database file not found at: {self.db_path}")
            raise FileNotFoundError(f"Database file not found at: {self.db_path}")

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            yield conn
        except sqlite3.Error as e:
            logging.error(f"Database connection error: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

#_________________formating________________________
    def _is_valid_time(self, time_str):
        """Validate time format HH:MM"""
        try:
            hours, minutes = map(int, time_str.split(':'))
            return (0 <= hours <= 23) and (0 <= minutes <= 59)
        except:
            return False

    def _validate_day(self, day):
        """Validate day format (0-4 or abbreviated day name)"""
        day_map = {
            'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4,
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4,
            '0': 0, '1': 1, '2': 2, '3': 3, '4': 4
        }
        if day in day_map or (isinstance(day, int) and 0 <= day <= 4):
            return True
        return False

    def validate_file_format(self, file_path: str) -> tuple:
        """Validate file format for both course and translation data"""
        try:
            # If the file_path is a relative path in your data directory
            if not os.path.isabs(file_path):
                file_path = resource_path(file_path)

            file_extension = file_path.lower().split('.')[-1]

            if file_extension not in ['csv', 'xlsx', 'xls']:
                return False, "Unsupported file format"

            if file_extension == 'csv':
                df = pd.read_csv(file_path)
                # Check if it's a course file
                required_columns = ['course_code', 'name', 'type', 'day', 'venue', 'credit',
                                    'start_time', 'end_time', 'instructor', 'remarks']
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    return False, f"Missing required columns: {', '.join(missing_columns)}"
                return True, "Valid course file"
            else:
                # Excel file - check for translation data sheets
                xls = pd.ExcelFile(file_path)
                translation_sheets = ['Programs', 'Program_Majors', 'Course_Groups',
                                      'Major_Requirements', 'Course_Equivalences']

                if all(sheet in xls.sheet_names for sheet in translation_sheets):
                    return True, "Valid translation file"

            return False, "Invalid file format or missing required columns/sheets"

        except Exception as e:
            return False, f"Error validating file: {str(e)}"

#_________________CSV import_______________________________________

    def import_courses_from_file(self, file_path: str) -> int:
        """Import courses from file"""
        file_extension = file_path.lower().split('.')[-1]

        # Check if it's a translation data file
        if file_extension in ['xlsx', 'xls']:
            xls = pd.ExcelFile(file_path)
            translation_sheets = ['Programs', 'Program_Majors', 'Course_Groups',
                                  'Major_Requirements', 'Course_Equivalences']
            if all(sheet in xls.sheet_names for sheet in translation_sheets):
                return self.import_translation_data(file_path)

        try:
            # Read the file
            if file_extension == 'csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Clear existing data
                cursor.execute('DELETE FROM course_sessions')
                cursor.execute('DELETE FROM courses')

                courses_added = 0
                processed_courses = set()

                for _, row in df.iterrows():
                    try:
                        # Use full course code including type
                        full_course_code = str(row['course_code'])  # e.g., "CS101 A LEC" or "CS101 A TUT"

                        # Insert base course if not exists
                        if full_course_code not in processed_courses:
                            cursor.execute('''
                                INSERT INTO courses 
                                (course_code, name, credit, instructor) 
                                VALUES (?, ?, ?, ?)
                            ''', (
                                full_course_code,
                                str(row['name']),
                                int(row['credit']),
                                str(row['instructor'])
                            ))
                            processed_courses.add(full_course_code)

                        # Insert session
                        cursor.execute('''
                            INSERT INTO course_sessions 
                            (course_code, name, type, day, venue, credit, 
                             start_time, end_time, instructor, remarks) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            full_course_code,
                            str(row['name']),
                            str(row['type']),
                            int(row['day']),
                            str(row['venue']),
                            int(row['credit']),
                            str(row['start_time']),
                            str(row['end_time']),
                            str(row['instructor']),
                            str(row.get('remarks', 'None'))
                        ))
                        courses_added += 1
                        logging.info(f"Added course session: {full_course_code}")

                    except Exception as e:
                        logging.error(f"Error processing course {row.get('course_code', 'Unknown')}: {str(e)}")
                        continue

                conn.commit()
                logging.info(f"Successfully imported {courses_added} course sessions")
                return courses_added

        except Exception as e:
            logging.error(f"Error importing courses: {str(e)}")
            return 0

    def import_translation_data(self, file_path: str) -> int:
        """Import translation data from Excel file"""
        conn = None
        cursor = None
        try:
            xls = pd.ExcelFile(file_path)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Begin transaction
            cursor.execute("BEGIN TRANSACTION")

            try:
                # Import Programs
                df_programs = pd.read_excel(xls, 'Programs')
                # Clean data by splitting on comma if needed
                if isinstance(df_programs.columns[0], str) and ',' in df_programs.columns[0]:
                    df_programs = pd.read_excel(xls, 'Programs', header=None)
                    headers = df_programs.iloc[0].str.split(',').iloc[0]
                    df_programs = pd.DataFrame([x.split(',') for x in df_programs.iloc[1:, 0]], columns=headers)

                logging.info(f"Programs data preview:\n{df_programs.head()}")
                cursor.execute('DELETE FROM programs')
                for _, row in df_programs.iterrows():
                    cursor.execute('''
                        INSERT INTO programs (program_code, program_name, description)
                        VALUES (?, ?, ?)
                    ''', (row['program_code'].strip(),
                          row['program_name'].strip(),
                          row['description'].strip()))

                # Import Program Majors
                df_majors = pd.read_excel(xls, 'Program_Majors')
                if isinstance(df_majors.columns[0], str) and ',' in df_majors.columns[0]:
                    df_majors = pd.read_excel(xls, 'Program_Majors', header=None)
                    headers = df_majors.iloc[0].str.split(',').iloc[0]
                    df_majors = pd.DataFrame([x.split(',') for x in df_majors.iloc[1:, 0]], columns=headers)

                logging.info(f"Program Majors data preview:\n{df_majors.head()}")
                cursor.execute('DELETE FROM program_majors')
                for _, row in df_majors.iterrows():
                    cursor.execute('''
                        INSERT INTO program_majors (program_code, major_code, major_name)
                        VALUES (?, ?, ?)
                    ''', (row['program_code'].strip(),
                          row['major_code'].strip(),
                          row['major_name'].strip()))

                # Import Course Groups
                df_groups = pd.read_excel(xls, 'Course_Groups')
                if isinstance(df_groups.columns[0], str) and ',' in df_groups.columns[0]:
                    df_groups = pd.read_excel(xls, 'Course_Groups', header=None)
                    headers = df_groups.iloc[0].str.split(',').iloc[0]
                    df_groups = pd.DataFrame([x.split(',') for x in df_groups.iloc[1:, 0]], columns=headers)

                logging.info(f"Course Groups data preview:\n{df_groups.head()}")
                cursor.execute('DELETE FROM course_groups')
                for _, row in df_groups.iterrows():
                    cursor.execute('''
                        INSERT INTO course_groups (group_name)
                        VALUES (?)
                    ''', (row['group_name'].strip(),))

                # Import Major Requirements
                df_requirements = pd.read_excel(xls, 'Major_Requirements')
                if isinstance(df_requirements.columns[0], str) and ',' in df_requirements.columns[0]:
                    df_requirements = pd.read_excel(xls, 'Major_Requirements', header=None)
                    headers = df_requirements.iloc[0].str.split(',').iloc[0]
                    df_requirements = pd.DataFrame([x.split(',') for x in df_requirements.iloc[1:, 0]], columns=headers)

                logging.info(f"Major Requirements data preview:\n{df_requirements.head()}")
                cursor.execute('DELETE FROM major_requirements')
                for _, row in df_requirements.iterrows():
                    cursor.execute('''
                        INSERT INTO major_requirements 
                        (program_code, major_code, group_id, course_code, campus)
                        VALUES (?, ?, 
                            (SELECT group_id FROM course_groups WHERE group_name = ?), 
                            ?, ?)
                    ''', (row['program_code'].strip(),
                          row['major_code'].strip(),
                          row['group_name'].strip(),
                          row['course_code'].strip(),
                          row['campus'].strip()))

                # Import Course Equivalences
                df_equivalences = pd.read_excel(xls, 'Course_Equivalences')
                if isinstance(df_equivalences.columns[0], str) and ',' in df_equivalences.columns[0]:
                    df_equivalences = pd.read_excel(xls, 'Course_Equivalences', header=None)
                    headers = df_equivalences.iloc[0].str.split(',').iloc[0]
                    df_equivalences = pd.DataFrame([x.split(',') for x in df_equivalences.iloc[1:, 0]], columns=headers)

                logging.info(f"Course Equivalences data preview:\n{df_equivalences.head()}")
                cursor.execute('DELETE FROM course_equivalences')
                for _, row in df_equivalences.iterrows():
                    cursor.execute('''
                        INSERT INTO course_equivalences 
                        (sz_code, hk_code, course_name, credits, description)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (row['sz_code'].strip(),
                          row['hk_code'].strip(),
                          row['course_name'].strip(),
                          float(str(row['credits']).strip()),
                          row['description'].strip()))

                # Commit transaction
                conn.commit()

                # Return total number of records imported
                total_records = (
                        len(df_programs) + len(df_majors) + len(df_groups) +
                        len(df_requirements) + len(df_equivalences)
                )
                logging.info(f"Successfully imported {total_records} records")
                return total_records

            except Exception as e:
                if conn:
                    conn.rollback()
                logging.error(f"Error during import: {str(e)}")
                raise e

        except Exception as e:
            logging.error(f"Error importing translation data: {str(e)}")
            raise

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

#____________________________________Search___________________________________________________

    def search_courses(self, query: str) -> List[Dict]:
        """Search courses by code, name, or schedule"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        c.course_code,
                        c.name,
                        cs.type,
                        cs.day,
                        cs.venue,
                        c.credit,
                        cs.start_time,
                        cs.end_time,
                        c.instructor,
                        cs.remarks
                    FROM courses c
                    LEFT JOIN course_sessions cs ON c.course_code = cs.course_code
                    WHERE c.course_code LIKE ? OR c.name LIKE ?
                    ORDER BY c.course_code, cs.day, cs.start_time
                ''', (f'%{query}%', f'%{query}%'))

                columns = ["course_code", "name", "type", "day", "venue", "credit", "start_time", "end_time", "instructor", "remarks"]
                results = []

                for row in cursor.fetchall():
                    course_dict = dict(zip(columns, row))
                    results.append(course_dict)

                return results

        except sqlite3.Error as e:
            logging.error(f"Error searching courses: {str(e)}")
            return []  # 返回空列表

    def get_all_courses(self) -> List[Dict]:
        """Get all courses with their sessions"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        c.course_code,
                        c.name,
                        cs.type,
                        cs.day,
                        cs.venue,
                        c.credit,
                        cs.start_time,
                        cs.end_time,
                        c.instructor,
                        cs.remarks
                    FROM courses c
                    LEFT JOIN course_sessions cs ON c.course_code = cs.course_code
                    ORDER BY c.course_code, cs.day, cs.start_time
                ''')

                columns = ["course_code", "name", "type", "day", "venue", "credit", "start_time", "end_time", "instructor", "remarks"]
                results = []

                for row in cursor.fetchall():
                    course_dict = dict(zip(columns, row))
                    results.append(course_dict)
                return results

        except sqlite3.Error as e:
            logging.error(f"Error fetching all courses: {str(e)}")
            return []  # 返回空列表

    def get_cart_courses(self) -> List[Dict]:
        """Get courses in cart with their sessions"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        c.course_code,
                        c.name,
                        cs.type,
                        cs.day,
                        cs.venue,
                        c.credit,
                        cs.start_time,
                        cs.end_time,
                        c.instructor,
                        cs.remarks
                    FROM courses c
                    JOIN cart ct ON c.course_code = ct.course_code
                    JOIN course_sessions cs ON c.course_code = cs.course_code
                    ORDER BY c.course_code, cs.day, cs.start_time
                ''')

                columns = ["course_code", "name", "type", "day", "venue", "credit", "start_time", "end_time", "instructor", "remarks"]
                results = []

                for row in cursor.fetchall():
                    course_dict = dict(zip(columns, row))
                    results.append(course_dict)

                logging.info(f"Courses in cart: {results}")  # 添加调试日志
                return results

        except sqlite3.Error as e:
            logging.error(f"Error fetching cart courses: {str(e)}")
            return []  # 返回空列表而不是None

# ___________________Cart_______________________

    def add_to_cart(self, course_code: str, force: bool = False) -> tuple[bool, str]:
        """
        Add course to cart with validation and detailed conflict checking
        Returns: (success: bool, message: str)
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Check if course exists and get its details
                cursor.execute('''
                    SELECT cs.course_code, cs.name, cs.day, cs.start_time, cs.end_time, cs.type 
                    FROM course_sessions cs 
                    WHERE cs.course_code = ?
                ''', (course_code,))
                course_details = cursor.fetchone()

                if not course_details:
                    error_msg = f"Course {course_code} not found in database"
                    logging.error(error_msg)
                    return False, error_msg

                # Check if course is already in cart
                cursor.execute('SELECT 1 FROM cart WHERE course_code = ?', (course_code,))
                if cursor.fetchone():
                    msg = f"Course {course_code} is already in cart"
                    logging.info(msg)
                    return False, msg

                # Get all courses in cart with their schedules
                cursor.execute('''
                    SELECT cs.course_code, cs.name, cs.day, cs.start_time, cs.end_time, cs.type
                    FROM course_sessions cs
                    JOIN cart ct ON cs.course_code = ct.course_code
                ''')
                cart_courses = cursor.fetchall()

                # Check for time conflicts if not force adding
                if not force:
                    new_code = course_details[0]
                    new_name = course_details[1]
                    new_day = course_details[2]
                    new_start = course_details[3]
                    new_end = course_details[4]
                    new_type = course_details[5]

                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

                    # Convert new course times to minutes
                    new_start_mins = sum(int(x) * y for x, y in zip(new_start.split(':'), [60, 1]))
                    new_end_mins = sum(int(x) * y for x, y in zip(new_end.split(':'), [60, 1]))

                    for cart_course in cart_courses:
                        cart_code = cart_course[0]
                        cart_name = cart_course[1]
                        cart_day = cart_course[2]
                        cart_start = cart_course[3]
                        cart_end = cart_course[4]
                        cart_type = cart_course[5]

                        if new_day == cart_day:  # Same day
                            # Convert cart course times to minutes
                            cart_start_mins = sum(int(x) * y for x, y in zip(cart_start.split(':'), [60, 1]))
                            cart_end_mins = sum(int(x) * y for x, y in zip(cart_end.split(':'), [60, 1]))

                            if not (new_end_mins <= cart_start_mins or new_start_mins >= cart_end_mins):
                                conflict_msg = (
                                    f"Time Conflict on {days[new_day]}:\n\n"
                                    f"New Course:\n"
                                    f"{new_code} ({new_type})\n"
                                    f"{new_name}\n"
                                    f"Time: {new_start} - {new_end}\n\n"
                                    f"Conflicts with:\n"
                                    f"{cart_code} ({cart_type})\n"
                                    f"{cart_name}\n"
                                    f"Time: {cart_start} - {cart_end}"
                                )
                                logging.warning(f"Time conflict detected: {conflict_msg}")
                                return False, conflict_msg

                # If all checks pass or force is True, add to cart
                cursor.execute('INSERT INTO cart (course_code) VALUES (?)', (course_code,))
                conn.commit()

                success_msg = f"Successfully added {course_code} to cart"
                if force:
                    success_msg += " (Force added)"
                logging.info(success_msg)
                return True, success_msg

        except sqlite3.Error as e:
            error_msg = f"Database error while adding {course_code} to cart: {str(e)}"
            logging.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error while adding {course_code} to cart: {str(e)}"
            logging.error(error_msg)
            return False, error_msg

    def remove_from_cart(self, course_code: str) -> bool:
        """Remove course from cart"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM cart WHERE course_code = ?', (course_code,))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logging.error(f"Error removing course from cart: {str(e)}")
            return False

    def clear_cart(self) -> bool:
        """Clear all courses from cart"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM cart')
                conn.commit()
                return True
        except sqlite3.Error as e:
            logging.error(f"Error clearing cart: {str(e)}")
            return False

    def is_in_cart(self, course_code: str) -> bool:
        """Check if course is in cart"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1 FROM cart WHERE course_code = ?', (course_code,))
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            logging.error(f"Error checking cart status: {str(e)}")
            return False

#___________________Course Translation_______________________

    def get_available_programs(self):
        """Get list of available programs"""
        try:
            query = "SELECT program_code, program_name FROM programs"
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                programs = cursor.fetchall()

                # Convert to dictionary
                program_dict = {row[0]: row[1] for row in programs}

                logging.info(f"Retrieved programs: {program_dict}")
                return {'success': True, 'programs': program_dict}
        except Exception as e:
            logging.error(f"Error getting programs: {str(e)}")
            return {'success': False, 'message': str(e)}

    def get_majors_for_program(self, program_code: str) -> dict:
        """Get available majors for a specific program"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT major_code, major_name 
                    FROM program_majors 
                    WHERE program_code = ?
                """, (program_code,))
                majors = {row[0]: row[1] for row in cursor.fetchall()}
                return {"success": True, "majors": majors}
        except sqlite3.Error as e:
            return {"success": False, "message": str(e)}

    def get_groups_for_major(self, program_code: str, major_code: str) -> dict:
        """Get available course groups for a specific major in a program"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT g.group_id, g.group_name
                    FROM course_groups g
                    JOIN major_requirements mr ON g.group_id = mr.group_id
                    WHERE mr.program_code = ? AND mr.major_code = ?
                """, (program_code, major_code))
                groups = {row[0]: row[1] for row in cursor.fetchall()}
                return {"success": True, "groups": groups}
        except sqlite3.Error as e:
            return {"success": False, "message": str(e)}

    def get_courses_for_group(self, program_code: str, major_code: str, group_id: int) -> dict:
        """Get available courses for a specific group in a major"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT mr.course_code, ce.course_name
                    FROM major_requirements mr
                    JOIN course_equivalences ce ON mr.course_code = ce.sz_code
                    WHERE mr.program_code = ? AND mr.major_code = ? AND mr.group_id = ?
                """, (program_code, major_code, group_id))
                courses = {row[0]: row[1] for row in cursor.fetchall()}
                return {"success": True, "courses": courses}
        except sqlite3.Error as e:
            return {"success": False, "message": str(e)}

    def get_course_equivalence(self, course_code: str) -> dict:
        """Get course equivalence information"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT sz_code, hk_code, course_name, credits, description
                    FROM course_equivalences
                    WHERE sz_code = ? OR hk_code = ?
                """, (course_code, course_code))
                result = cursor.fetchone()

                if result:
                    return {
                        "success": True,
                        "data": {
                            "sz_code": result[0],
                            "hk_code": result[1],
                            "course_name": result[2],
                            "credits": result[3],
                            "description": result[4]
                        }
                    }
                return {"success": False, "message": "Course not found"}
        except sqlite3.Error as e:
            return {"success": False, "message": str(e)}

    def get_filtered_courses(self, program_code: str, major_code: str, group_name: str, campus: str = None) -> dict:
        """Get courses based on selected filters with debug logging"""
        try:
            logging.info(f"Executing query with parameters:")
            logging.info(f"Program: {program_code}")
            logging.info(f"Major: {major_code}")
            logging.info(f"Group: {group_name}")
            logging.info(f"Campus: {campus}")

            with self.get_connection() as conn:
                cursor = conn.cursor()

                query = """
                    SELECT DISTINCT mr.course_code, mr.campus
                    FROM major_requirements mr
                    JOIN course_groups cg ON mr.group_id = 
                        (SELECT group_id FROM course_groups WHERE group_name = ?)
                    WHERE mr.program_code = ? 
                    AND mr.major_code = ?
                """
                params = [group_name, program_code, major_code]

                if campus:
                    query += " AND mr.campus = ?"
                    params.append(campus)

                cursor.execute(query, params)
                courses = cursor.fetchall()
                logging.info(f"Found {len(courses)} matching courses")

                result_courses = {}
                for course in courses:
                    course_code = course[0]
                    campus = course[1]
                    display_text = f"{course_code} ({campus})"
                    result_courses[course_code] = display_text
                    logging.info(f"Processed course: {course_code} - Campus: {campus}")

                return result_courses

        except Exception as e:
            logging.error(f"Error in get_filtered_courses: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            return {}

    # Add this helper method to debug database content
    def debug_tables(self):
        """Print table contents for debugging"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                tables = ['programs', 'program_majors', 'course_groups',
                          'major_requirements', 'course_equivalences']

                for table in tables:
                    cursor.execute(f"SELECT * FROM {table} LIMIT 5")
                    rows = cursor.fetchall()
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [col[1] for col in cursor.fetchall()]

                    logging.info(f"\n{table} columns: {columns}")
                    logging.info(f"{table} data: {rows}")

        except Exception as e:
            logging.error(f"Error in debug_tables: {str(e)}")

    def debug_database_content(self):
        """Debug function to show database content"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Check all tables
                tables = [
                    'programs', 'program_majors', 'course_groups',
                    'major_requirements', 'course_equivalences'
                ]

                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    logging.info(f"Table {table} has {count} records")

                    # Show sample data
                    cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                    samples = cursor.fetchall()
                    logging.info(f"Sample data from {table}: {samples}")

        except Exception as e:
            logging.error(f"Error in debug_database_content: {str(e)}")
            raise