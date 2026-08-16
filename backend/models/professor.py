from models.person import Person


class Professor(Person):
    def __init__(self, national_id: str, first_name: str, last_name: str,
                 personnel_code: str, department: str):
        super().__init__(national_id, first_name, last_name)
        personnel_code = str(personnel_code).strip()
        department = str(department).strip()
        if not personnel_code or not department:
            raise ValueError("personnel_code and department are required fields.")
        self.personnel_code = personnel_code
        self.department = department
        self.courses: list = []

    def assign_course(self, course) -> None:
        if course not in self.courses:
            self.courses.append(course)

    def remove_course(self, course) -> None:
        if course in self.courses:
            self.courses.remove(course)

    def get_courses(self) -> list:
        return list(self.courses)

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "personnel_code": self.personnel_code,
            "department": self.department,
            "courses": [
                c if isinstance(c, str) else c.course_id
                for c in self.courses
            ],
        })
        return base
