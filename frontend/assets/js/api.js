import { API_BASE_URL } from "./config.js";

export class ApiError extends Error {
  constructor(message, { status = 0, code = "API_ERROR", errors = [] } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.errors = Array.isArray(errors) ? errors : [];
    this.fieldErrors = Object.fromEntries(
      this.errors
        .filter((item) => item?.field)
        .map((item) => [item.field, item.message || message]),
    );
  }
}

async function parseResponse(response) {
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    try { return await response.json(); }
    catch { return null; }
  }
  try { return await response.text(); }
  catch { return null; }
}

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
    });
  } catch (error) {
    throw new ApiError(
      "ارتباط با سرور برقرار نشد. مطمئن شوید بک‌اند روی پورت 8000 اجراست.",
      { code: "NETWORK_ERROR" },
    );
  }

  const data = await parseResponse(response);
  if (!response.ok) {
    const detail = data?.detail ?? data?.message;
    const message = typeof detail === "string"
      ? detail
      : typeof data === "string" && data.trim()
        ? data
        : `درخواست با خطای HTTP ${response.status} مواجه شد.`;

    throw new ApiError(message, {
      status: response.status,
      code: data?.code || `HTTP_${response.status}`,
      errors: data?.errors || [],
    });
  }
  return data;
}

const encode = encodeURIComponent;

export const api = {
  system: {
    summary: () => request("/summary"),
    allData: () => request("/data"),
  },
  students: {
    getAll: () => request("/students/"),
    get: (studentNumber) => request(`/students/${encode(studentNumber)}`),
    create: (data) => request("/students/", { method: "POST", body: JSON.stringify(data) }),
    update: (studentNumber, data) => request(`/students/${encode(studentNumber)}`, { method: "PUT", body: JSON.stringify(data) }),
    delete: (studentNumber) => request(`/students/${encode(studentNumber)}`, { method: "DELETE" }),
    courses: (studentNumber) => request(`/students/${encode(studentNumber)}/courses`),
  },
  professors: {
    getAll: () => request("/professors/"),
    get: (personnelCode) => request(`/professors/${encode(personnelCode)}`),
    create: (data) => request("/professors/", { method: "POST", body: JSON.stringify(data) }),
    update: (personnelCode, data) => request(`/professors/${encode(personnelCode)}`, { method: "PUT", body: JSON.stringify(data) }),
    delete: (personnelCode) => request(`/professors/${encode(personnelCode)}`, { method: "DELETE" }),
  },
  courses: {
    getAll: () => request("/courses/"),
    get: (courseId) => request(`/courses/${encode(courseId)}`),
    create: (data) => request("/courses/", { method: "POST", body: JSON.stringify(data) }),
    update: (courseId, data) => request(`/courses/${encode(courseId)}`, { method: "PUT", body: JSON.stringify(data) }),
    delete: (courseId) => request(`/courses/${encode(courseId)}`, { method: "DELETE" }),
  },
  selection: {
    select: (studentNumber, courseId) => {
      const q = new URLSearchParams({ student_number: studentNumber, course_id: courseId });
      return request(`/selection/select?${q}`, { method: "POST" });
    },
    drop: (studentNumber, courseId) => {
      const q = new URLSearchParams({ student_number: studentNumber, course_id: courseId });
      return request(`/selection/drop?${q}`, { method: "DELETE" });
    },
    assignProfessor: (personnelCode, courseId) => {
      const q = new URLSearchParams({ personnel_code: personnelCode, course_id: courseId });
      return request(`/selection/assign-professor?${q}`, { method: "POST" });
    },
  },
};

export default api;
