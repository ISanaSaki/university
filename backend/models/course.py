class Course:
    def __init__(self, course_id: str, title: str, code: str,
                 unit: int, capacity: int):
        course_id = str(course_id).strip()
        title = str(title).strip()
        code = str(code).strip()
        if not course_id or not title or not code:
            raise ValueError("course_id, title and code are required fields.")
        self.course_id = course_id
        self.title = title
        self.code = code
        self.unit = unit
        self.capacity = capacity
        self.professor = None
        self.students: list = []

    def is_full(self) -> bool:
        return len(self.students) >= self.capacity

    def add_student(self, student) -> None:
        if student not in self.students:
            self.students.append(student)

    def remove_student(self, student) -> None:
        if student in self.students:
            self.students.remove(student)

    def assign_professor(self, professor) -> None:
        self.professor = professor

    def to_dict(self) -> dict:
        return {
            "course_id": self.course_id,
            "title": self.title,
            "code": self.code,
            "unit": self.unit,
            "capacity": self.capacity,
            "professor": (
                self.professor
                if isinstance(self.professor, str) or self.professor is None
                else self.professor.personnel_code
            ),
            "students": [
                s if isinstance(s, str) else s.student_number
                for s in self.students
            ],
        }
