from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from data import storage
from exceptions.error_handlers import register_exception_handlers
from routers import courses, professors, selection, students
from schemas.common_schema import AllDataResponse, SummaryResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    storage.load_all()
    yield
    storage.save_all()


app = FastAPI(
    title="سیستم انتخاب واحد دانشگاهی",
    description="سیستم ساده انتخاب واحد دانشگاهی - پروژه برنامه‌نویسی پیشرفته",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


register_exception_handlers(app)


app.include_router(students.router)
app.include_router(professors.router)
app.include_router(courses.router)
app.include_router(selection.router)


@app.get("/")
def root():
    return {"message": "سیستم انتخاب واحد دانشگاهی - به API خوش آمدید"}


@app.get("/summary", response_model=SummaryResponse, tags=["System"])
def summary():
    selections_count = sum(len(student.selected_courses) for student in storage.students.values())
    total_capacity = sum(course.capacity for course in storage.courses.values())
    return {
        "students_count": len(storage.students),
        "professors_count": len(storage.professors),
        "courses_count": len(storage.courses),
        "selections_count": selections_count,
        "assigned_courses_count": sum(course.professor is not None for course in storage.courses.values()),
        "total_capacity": total_capacity,
        "remaining_capacity": max(total_capacity - selections_count, 0),
    }


@app.get("/data", response_model=AllDataResponse, tags=["System"])
def all_data():
    return {
        "students": [student.to_dict() for student in storage.students.values()],
        "professors": [professor.to_dict() for professor in storage.professors.values()],
        "courses": [course.to_dict() for course in storage.courses.values()],
    }
