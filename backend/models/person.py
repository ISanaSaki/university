class Person:
    def __init__(self, national_id: str, first_name: str, last_name: str):
        national_id = str(national_id).strip()
        first_name = str(first_name).strip()
        last_name = str(last_name).strip()
        if not national_id or not first_name or not last_name:
            raise ValueError("national_id, first_name and last_name are required fields.")
        self.national_id = national_id
        self.first_name = first_name
        self.last_name = last_name

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def to_dict(self) -> dict:
        return {
            "national_id": self.national_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }
