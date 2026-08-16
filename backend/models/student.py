from models.person import Person


class Student(Person):
    def __init__(self, national_id: str, first_name: str, last_name: str,
                 student_number: str, major: str):
        super().__init__(national_id, first_name, last_name)
        student_number = str(student_number).strip()
        major = str(major).strip()
        if not student_number or not major:
            raise ValueError("student_number and major are required fields.")
        self.student_number = student_number
        self.major = major
        self.selected_courses: list = []

    def select_course(self, course) -> None:
        if course not in self.selected_courses:
            self.selected_courses.append(course)

    def drop_course(self, course) -> None:
        if course in self.selected_courses:
            self.selected_courses.remove(course)

    def get_courses(self) -> list:
        return list(self.selected_courses)

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "student_number": self.student_number,
            "major": self.major,
            "selected_courses": [
                c if isinstance(c, str) else c.course_id
                for c in self.selected_courses
            ],
        })
        return base
