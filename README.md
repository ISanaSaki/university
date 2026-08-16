# UniReg - سیستم ساده انتخاب واحد دانشگاهی

این نسخه بر اساس صورت پروژه درس «برنامه‌نویسی پیشرفته» بازبینی و تکمیل شده است. پروژه عمداً ساده نگه داشته شده و فقط روی پنج بخش موردنیاز تمرکز دارد: داشبورد، دانشجویان، اساتید، دروس و انتخاب واحد.

## ساختار پروژه

```text
unireg_final/
├── backend/                 FastAPI + Pydantic + JSON persistence
│   ├── models/              کلاس‌های Person, Student, Professor, Course
│   ├── schemas/             ورودی‌ها و Response Modelها
│   ├── services/            منطق CRUD و انتخاب واحد
│   ├── routers/             endpointهای FastAPI
│   ├── exceptions/          استثناهای سفارشی
│   ├── data/                فایل‌های JSON و persistence
│   ├── tests/               تست‌های API و integrity
│   └── main.py              هسته برنامه + summary/data + exception handlers
├── frontend/                Vanilla HTML/CSS/JS، RTL و Responsive
│   ├── pages/               ۵ صفحه اصلی
│   └── assets/
├── docs/assignment.pdf      صورت پروژه استاد
└── docker-compose.yml
```

## اجرای سریع روی Windows / PowerShell

### 1) بک‌اند

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

### 2) فرانت

در یک ترمینال جدید:

```powershell
cd frontend
py -m http.server 5500 --bind 127.0.0.1
```

سپس:

```text
http://127.0.0.1:5500
```

> فایل `index.html` را مستقیم با `file://` باز نکنید؛ فرانت را با HTTP server اجرا کنید.

## اجرای تست‌ها

```powershell
cd backend
pip install -r requirements-dev.txt
pytest -q
```

تست‌ها شامل CRUD، انتخاب و حذف درس، ظرفیت، تخصیص مجدد استاد، پاک‌سازی referenceها هنگام حذف و persistence هستند.

## اجرا با Docker Compose

از ریشه پروژه:

```powershell
docker compose up --build
```

- Frontend: `http://127.0.0.1:5500`
- Backend: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`

## APIهای اصلی

| Method | Endpoint | کاربرد |
|---|---|---|
| GET | `/summary` | خلاصه تعداد دانشجو، استاد، درس، انتخاب‌ها و ظرفیت |
| GET | `/data` | نمایش یکجای همه دانشجویان، اساتید و دروس |
| POST/GET | `/students/` | ایجاد / لیست دانشجویان |
| GET/PUT/DELETE | `/students/{student_number}` | مشاهده / ویرایش / حذف دانشجو |
| GET | `/students/{student_number}/courses` | دروس دانشجو |
| POST/GET | `/professors/` | ایجاد / لیست اساتید |
| GET/PUT/DELETE | `/professors/{personnel_code}` | مشاهده / ویرایش / حذف استاد |
| POST/GET | `/courses/` | ایجاد / لیست دروس |
| GET/PUT/DELETE | `/courses/{course_id}` | مشاهده / ویرایش / حذف درس |
| POST | `/selection/select` | انتخاب درس؛ `student_number` و `course_id` query parameter هستند |
| DELETE | `/selection/drop` | حذف درس از دانشجو |
| POST | `/selection/assign-professor` | تخصیص استاد؛ `personnel_code` و `course_id` query parameter هستند |

## اصلاحات مهم این نسخه

- اضافه شدن APIهای الزامی `summary` و `data` مطابق صورت پروژه.
- اضافه شدن Response Modelهای Pydantic برای کنترل خروجی API.
- انتقال مدیریت استثناهای سفارشی به هسته `main.py`.
- اصلاح حذف دانشجو تا از `Course.students` هم حذف شود.
- اصلاح حذف استاد تا درس‌های مربوطه بدون استاد شوند و reference ناسالم باقی نماند.
- اصلاح حذف درس تا از دانشجوها و استاد مربوطه نیز حذف شود.
- اصلاح تخصیص مجدد استاد؛ درس از لیست استاد قبلی پاک می‌شود.
- جلوگیری از کاهش ظرفیت به کمتر از تعداد دانشجویان ثبت‌شده.
- مقاوم‌تر شدن load/save فایل‌های JSON و پاک‌سازی referenceهای خراب.
- بازنویسی اتصال فرانت و بک‌اند و رفع نام‌های اشتباه `remove`, `professor_number`, `major` و پارامتر تخصیص استاد.
- فرانت نهایی فقط ۵ بخش موردنیاز را دارد و Login/ترم/شهریه/نمره و امکانات خارج از صورت پروژه اضافه نشده‌اند.

## نکته درباره داده‌های نمونه

داده‌های نمونه قبلی حفظ شده‌اند. reference نامعتبر استاد `P001` در درس نمونه به حالت «بدون استاد» اصلاح شده تا داده‌ها consistent باشند.
