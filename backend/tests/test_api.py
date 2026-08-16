import pytest
from fastapi.testclient import TestClient

from data import storage
from main import app


@pytest.fixture(autouse=True)
def isolated_storage(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "STUDENTS_FILE", str(tmp_path / "students.json"))
    monkeypatch.setattr(storage, "PROFESSORS_FILE", str(tmp_path / "professors.json"))
    monkeypatch.setattr(storage, "COURSES_FILE", str(tmp_path / "courses.json"))
    storage.reset_storage()
    yield
    storage.reset_storage()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def create_student(client, number="STU001"):
    response = client.post("/students/", json={
        "national_id": "1234567890",
        "first_name": "سارا",
        "last_name": "احمدی",
        "student_number": number,
        "major": "مهندسی کامپیوتر",
    })
    assert response.status_code == 201, response.text
    return response.json()


def create_professor(client, code="P001"):
    response = client.post("/professors/", json={
        "national_id": "9988776655",
        "first_name": "آرمین",
        "last_name": "رشنو",
        "personnel_code": code,
        "department": "مهندسی کامپیوتر",
    })
    assert response.status_code == 201, response.text
    return response.json()


def create_course(client, course_id="C001", capacity=2):
    response = client.post("/courses/", json={
        "course_id": course_id,
        "title": "برنامه نویسی پیشرفته",
        "code": "CS301",
        "unit": 3,
        "capacity": capacity,
    })
    assert response.status_code == 201, response.text
    return response.json()


def test_crud_and_system_endpoints(client):
    create_student(client)
    create_professor(client)
    create_course(client)

    assert client.get("/students/").status_code == 200
    assert client.get("/professors/").status_code == 200
    assert client.get("/courses/").status_code == 200

    summary = client.get("/summary")
    assert summary.status_code == 200
    assert summary.json()["students_count"] == 1
    assert summary.json()["professors_count"] == 1
    assert summary.json()["courses_count"] == 1

    all_data = client.get("/data")
    assert all_data.status_code == 200
    assert set(all_data.json()) == {"students", "professors", "courses"}


def test_selection_capacity_and_duplicate_protection(client):
    create_student(client, "STU001")
    create_student(client, "STU002")
    create_course(client, capacity=1)

    selected = client.post("/selection/select", params={"student_number": "STU001", "course_id": "C001"})
    assert selected.status_code == 200

    duplicate = client.post("/selection/select", params={"student_number": "STU001", "course_id": "C001"})
    assert duplicate.status_code == 409

    full = client.post("/selection/select", params={"student_number": "STU002", "course_id": "C001"})
    assert full.status_code == 400

    courses = client.get("/students/STU001/courses")
    assert courses.status_code == 200
    assert [item["course_id"] for item in courses.json()] == ["C001"]
    assert [item["student_number"] for item in client.get("/courses/C001/students").json()] == ["STU001"]

    dropped = client.delete("/selection/drop", params={"student_number": "STU001", "course_id": "C001"})
    assert dropped.status_code == 200
    assert client.get("/students/STU001/courses").json() == []


def test_reassign_professor_removes_old_reverse_reference(client):
    create_professor(client, "P001")
    create_professor(client, "P002")
    create_course(client)

    assert client.post("/selection/assign-professor", params={"personnel_code": "P001", "course_id": "C001"}).status_code == 200
    assert client.post("/selection/assign-professor", params={"personnel_code": "P002", "course_id": "C001"}).status_code == 200

    assert client.get("/professors/P001").json()["courses"] == []
    assert client.get("/professors/P002").json()["courses"] == ["C001"]
    assert [c["course_id"] for c in client.get("/professors/P002/courses").json()] == ["C001"]
    assert client.get("/courses/C001").json()["professor"] == "P002"


def test_delete_operations_keep_references_consistent(client):
    create_student(client)
    create_professor(client)
    create_course(client)
    client.post("/selection/select", params={"student_number": "STU001", "course_id": "C001"})
    client.post("/selection/assign-professor", params={"personnel_code": "P001", "course_id": "C001"})

    assert client.delete("/students/STU001").status_code == 200
    assert client.get("/courses/C001").json()["students"] == []

    assert client.delete("/professors/P001").status_code == 200
    assert client.get("/courses/C001").json()["professor"] is None


def test_delete_course_cleans_student_and_professor_links(client):
    create_student(client)
    create_professor(client)
    create_course(client)
    client.post("/selection/select", params={"student_number": "STU001", "course_id": "C001"})
    client.post("/selection/assign-professor", params={"personnel_code": "P001", "course_id": "C001"})

    assert client.delete("/courses/C001").status_code == 200
    assert client.get("/students/STU001").json()["selected_courses"] == []
    assert client.get("/professors/P001").json()["courses"] == []


def test_capacity_cannot_be_lower_than_current_enrollment(client):
    create_student(client)
    create_student(client, "STU002")
    create_course(client, capacity=2)
    client.post("/selection/select", params={"student_number": "STU001", "course_id": "C001"})
    client.post("/selection/select", params={"student_number": "STU002", "course_id": "C001"})

    response = client.put("/courses/C001", json={"capacity": 2})
    assert response.status_code == 200

    response = client.put("/courses/C001", json={"capacity": 1})
    assert response.status_code == 400


def test_validation_and_not_found_errors_are_user_friendly(client):
    invalid = client.post("/courses/", json={
        "course_id": "C",
        "title": "X",
        "code": "C",
        "unit": 8,
        "capacity": 0,
    })
    assert invalid.status_code == 422
    assert isinstance(invalid.json().get("detail"), str)

    missing = client.get("/students/UNKNOWN")
    assert missing.status_code == 404
    assert "یافت نشد" in missing.json()["detail"]


def test_persistence_round_trip_preserves_links(client):
    create_student(client)
    create_professor(client)
    create_course(client)
    client.post("/selection/select", params={"student_number": "STU001", "course_id": "C001"})
    client.post("/selection/assign-professor", params={"personnel_code": "P001", "course_id": "C001"})

    storage.save_all()
    storage.students.clear()
    storage.professors.clear()
    storage.courses.clear()
    storage.load_all()

    assert storage.students["STU001"].selected_courses[0] is storage.courses["C001"]
    assert storage.courses["C001"].students[0] is storage.students["STU001"]
    assert storage.courses["C001"].professor is storage.professors["P001"]
    assert storage.courses["C001"] in storage.professors["P001"].courses


def test_wrong_input_types_return_structured_persian_validation_errors(client):
    response = client.post("/courses/", json={
        "course_id": "C100",
        "title": "ساختمان داده",
        "code": "CS210",
        "unit": "3",
        "capacity": "thirty",
    })

    assert response.status_code == 422
    payload = response.json()
    assert payload["code"] == "VALIDATION_ERROR"
    assert isinstance(payload["detail"], str)
    assert isinstance(payload["errors"], list)

    by_field = {item["field"]: item for item in payload["errors"]}
    assert by_field["unit"]["type"] == "int_type"
    assert "عدد صحیح" in by_field["unit"]["message"]
    assert by_field["capacity"]["type"] == "int_type"
    assert "ظرفیت" in by_field["capacity"]["message"]


def test_missing_range_and_unknown_fields_are_reported_separately(client):
    response = client.post("/courses/", json={
        "course_id": "C101",
        "title": "X",
        "code": "CS",
        "unit": 9,
        "capacity": 0,
        "unexpected": "value",
    })

    assert response.status_code == 422
    errors = response.json()["errors"]
    fields = {item["field"] for item in errors}
    assert {"title", "unit", "capacity", "unexpected"}.issubset(fields)
    assert any(item["type"] == "extra_forbidden" for item in errors)


def test_string_fields_reject_non_string_json_values(client):
    response = client.post("/students/", json={
        "national_id": 1234567890,
        "first_name": "سارا",
        "last_name": "احمدی",
        "student_number": "STU900",
        "major": "کامپیوتر",
    })

    assert response.status_code == 422
    error = next(item for item in response.json()["errors"] if item["field"] == "national_id")
    assert error["type"] == "string_type"
    assert "متن" in error["message"]


def test_malformed_json_has_safe_user_friendly_error(client):
    response = client.post(
        "/courses/",
        content='{"course_id": "C102",',
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["code"] == "VALIDATION_ERROR"
    assert payload["errors"][0]["type"] == "json_invalid"
    assert "JSON" in payload["errors"][0]["message"]
