# utils/timetable_service.py
from datetime import datetime
from models.course import Course
from typing import List, Dict, Set, Tuple
import logging
from collections import defaultdict

class TimetableAlgorithm:
    @staticmethod
    def generate_combinations(courses_input: List[Dict]) -> Tuple[List[Dict], Dict]:
        logging.info(f"Received courses for timetable generation: {courses_input}")

        course_sessions = defaultdict(list)
        for course in courses_input:
            course_day = course['day']
            if course_day is None:
                logging.error(f"Invalid day format: {course['day']} for course {course['course_code']}")
                continue
            course['day'] = course_day
            course_sessions[course['course_code']].append(course)

        if not course_sessions:
            raise ValueError("No valid courses provided")

        course_codes = list(course_sessions.keys())

        def check_conflicts(code1: str, code2: str) -> bool:
            for s1 in course_sessions[code1]:
                for s2 in course_sessions[code2]:
                    if s1['day'] == s2['day']:
                        start1 = datetime.strptime(s1['start_time'], '%H:%M').time()
                        end1 = datetime.strptime(s1['end_time'], '%H:%M').time()
                        start2 = datetime.strptime(s2['start_time'], '%H:%M').time()
                        end2 = datetime.strptime(s2['end_time'], '%H:%M').time()
                        if not (end1 <= start2 or end2 <= start1):
                            return True
            return False

        def find_max_schedules():
            n = len(course_codes)
            max_schedules = []
            max_len = 0

            def backtrack(pos: int, current: List[int]):
                nonlocal max_schedules, max_len

                if pos == n:
                    if len(current) > max_len:
                        max_len = len(current)
                        max_schedules.clear()
                        max_schedules.append(current[:])
                    elif len(current) == max_len:
                        max_schedules.append(current[:])
                    return

                current_code = course_codes[pos]
                can_add = all(not check_conflicts(current_code, course_codes[i])
                              for i in current)

                if can_add:
                    current.append(pos)
                    backtrack(pos + 1, current)
                    current.pop()
                backtrack(pos + 1, current)

            backtrack(0, [])
            return max_schedules, max_len

        max_schedules, max_len = find_max_schedules()

        results = []
        for schedule in max_schedules:
            selected = [course_codes[i] for i in schedule]
            excluded = {}

            for i, course_code in enumerate(course_codes):
                if i not in schedule:
                    conflicts = [course_codes[j] for j in schedule if check_conflicts(course_code, course_codes[j])]
                    excluded[course_code] = conflicts

            results.append({
                'selected': selected,
                'excluded': excluded
            })

        return results, course_sessions


class TimetableService:
    @staticmethod
    def generate_timetable_combinations(courses_input: List[Dict]) -> Tuple[List[Dict], Dict]:
        logging.info(f"Received courses for timetable: {courses_input}")
        schedules, course_groups = TimetableAlgorithm.generate_combinations(courses_input)
        logging.info(f"Generated {len(schedules)} schedules and {len(course_groups)} course groups")
        return schedules, course_groups