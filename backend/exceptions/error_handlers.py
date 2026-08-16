import logging
from typing import Any

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from exceptions.custom_exceptions import CourseSelectionException

logger = logging.getLogger(__name__)

FIELD_LABELS = {
    "national_id": "کد ملی",
    "first_name": "نام",
    "last_name": "نام خانوادگی",
    "student_number": "شماره دانشجویی",
    "major": "رشته تحصیلی",
    "personnel_code": "کد پرسنلی",
    "department": "دانشکده / دپارتمان",
    "course_id": "شناسه درس",
    "title": "عنوان درس",
    "code": "کد درس",
    "unit": "تعداد واحد",
    "capacity": "ظرفیت",
}

LOCATION_PREFIXES = {"body", "query", "path", "header", "cookie"}


def _field_path(loc: tuple[Any, ...] | list[Any]) -> str:
    parts = [str(part) for part in loc if part not in LOCATION_PREFIXES and not isinstance(part, int)]
    return ".".join(parts)


def _label_for(field: str) -> str:
    if not field:
        return "ورودی"
    last = field.rsplit(".", 1)[-1]
    return FIELD_LABELS.get(last, last)


def _validation_message(error: dict[str, Any], field: str) -> str:
    error_type = error.get("type", "")
    ctx = error.get("ctx") or {}
    label = _label_for(field)

    if error_type == "missing":
        return f"فیلد «{label}» الزامی است."
    if error_type in {"string_type", "string_sub_type"}:
        return f"فیلد «{label}» باید از نوع متن باشد."
    if error_type in {"int_type", "int_parsing"}:
        return f"فیلد «{label}» باید یک عدد صحیح باشد."
    if error_type == "bool_type":
        return f"فیلد «{label}» باید مقدار درست/نادرست داشته باشد."
    if error_type == "string_too_short":
        return f"فیلد «{label}» باید حداقل {ctx.get('min_length', '?')} کاراکتر باشد."
    if error_type == "string_too_long":
        return f"فیلد «{label}» باید حداکثر {ctx.get('max_length', '?')} کاراکتر باشد."
    if error_type == "greater_than_equal":
        return f"مقدار «{label}» باید حداقل {ctx.get('ge', '?')} باشد."
    if error_type == "less_than_equal":
        return f"مقدار «{label}» باید حداکثر {ctx.get('le', '?')} باشد."
    if error_type == "greater_than":
        return f"مقدار «{label}» باید بزرگ‌تر از {ctx.get('gt', '?')} باشد."
    if error_type == "less_than":
        return f"مقدار «{label}» باید کوچک‌تر از {ctx.get('lt', '?')} باشد."
    if error_type == "extra_forbidden":
        return f"فیلد «{label}» مجاز نیست."
    if error_type == "json_invalid":
        return "ساختار JSON ارسالی معتبر نیست."
    if error_type in {"model_attributes_type", "dict_type"}:
        return "بدنه درخواست باید یک شیء JSON معتبر باشد."

    return f"مقدار واردشده برای «{label}» معتبر نیست."


def _source_from_loc(loc: tuple[Any, ...] | list[Any]) -> str:
    return str(loc[0]) if loc and loc[0] in LOCATION_PREFIXES else "request"


def register_exception_handlers(app) -> None:
    @app.exception_handler(CourseSelectionException)
    async def course_selection_exception_handler(request: Request, exc: CourseSelectionException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": str(exc),
                "code": exc.__class__.__name__,
                "errors": [],
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        normalized_errors = []
        for error in exc.errors():
            loc = error.get("loc") or ()
            field = _field_path(loc)
            normalized_errors.append(
                {
                    "field": field,
                    "label": _label_for(field),
                    "source": _source_from_loc(loc),
                    "message": _validation_message(error, field),
                    "type": error.get("type", "validation_error"),
                }
            )

        detail = (
            normalized_errors[0]["message"]
            if len(normalized_errors) == 1
            else "اطلاعات واردشده معتبر نیست. لطفاً خطاهای مشخص‌شده را اصلاح کنید."
        )
        return JSONResponse(
            status_code=422,
            content={
                "detail": detail,
                "code": "VALIDATION_ERROR",
                "errors": normalized_errors,
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        detail = exc.detail if isinstance(exc.detail, str) else "درخواست قابل انجام نیست."
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": detail,
                "code": f"HTTP_{exc.status_code}",
                "errors": [],
            },
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled API error: %s %s", request.method, request.url.path, exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "خطای غیرمنتظره‌ای در سرور رخ داد. لطفاً دوباره تلاش کنید.",
                "code": "INTERNAL_SERVER_ERROR",
                "errors": [],
            },
        )
