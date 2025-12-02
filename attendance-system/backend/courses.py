"""
Course Configuration
List of available BS Computer Science courses
"""

COURSES = [
    {"code": "CS101", "name": "Introduction to Programming"},
    {"code": "CS102", "name": "Object Oriented Programming"},
    {"code": "CS201", "name": "Data Structures and Algorithms"},
    {"code": "CS202", "name": "Database Systems"},
    {"code": "CS203", "name": "Computer Networks"},
    {"code": "CS301", "name": "Operating Systems"},
    {"code": "CS302", "name": "Software Engineering"},
    {"code": "CS303", "name": "Web Development"},
    {"code": "CS304", "name": "Artificial Intelligence"},
    {"code": "CS305", "name": "Machine Learning"},
    {"code": "CS401", "name": "Computer Graphics"},
    {"code": "CS402", "name": "Compiler Construction"},
    {"code": "CS403", "name": "Computer Security"},
    {"code": "CS404", "name": "Mobile App Development"},
    {"code": "CS405", "name": "Cloud Computing"}
]

def get_all_courses():
    """Return list of all available courses"""
    return COURSES

def get_course_codes():
    """Return list of course codes only"""
    return [course['code'] for course in COURSES]

def get_course_by_code(code):
    """Get course details by code"""
    for course in COURSES:
        if course['code'] == code:
            return course
    return None
