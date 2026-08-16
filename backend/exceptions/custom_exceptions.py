class CourseSelectionException(Exception):
    status_code = 400

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message


class StudentNotFoundException(CourseSelectionException):
    status_code = 404

    def __init__(self, message="دانشجو یافت نشد."):
        super().__init__(message)


class StudentAlreadyExistsException(CourseSelectionException):
    status_code = 409

    def __init__(self, message="دانشجو قبلاً ثبت شده است."):
        super().__init__(message)


class ProfessorNotFoundException(CourseSelectionException):
    status_code = 404

    def __init__(self, message="استاد یافت نشد."):
        super().__init__(message)


class ProfessorAlreadyExistsException(CourseSelectionException):
    status_code = 409

    def __init__(self, message="استاد قبلاً ثبت شده است."):
        super().__init__(message)


class CourseNotFoundException(CourseSelectionException):
    status_code = 404

    def __init__(self, message="درس مورد نظر یافت نشد."):
        super().__init__(message)


class CourseAlreadyExistsException(CourseSelectionException):
    status_code = 409

    def __init__(self, message="این درس قبلاً ثبت شده است."):
        super().__init__(message)


class CourseFullException(CourseSelectionException):
    status_code = 400

    def __init__(self, message="ظرفیت درس تکمیل شده است."):
        super().__init__(message)


class CourseAlreadySelectedException(CourseSelectionException):
    status_code = 409

    def __init__(self, message="این درس قبلاً توسط دانشجو انتخاب شده است."):
        super().__init__(message)


class CourseNotSelectedException(CourseSelectionException):
    status_code = 400

    def __init__(self, message="این درس توسط دانشجو انتخاب نشده است."):
        super().__init__(message)


class InvalidCourseCapacityException(CourseSelectionException):
    status_code = 400

    def __init__(self, message="ظرفیت جدید نمی‌تواند از تعداد دانشجویان ثبت‌نام‌شده کمتر باشد."):
        super().__init__(message)
