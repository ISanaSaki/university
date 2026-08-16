import api from "../assets/js/api.js";
import { empty, loading, modal } from "../assets/js/components.js";
import { byText, confirmAction, escapeHtml, formData, fullName, handleError, handleFormError, toast, validateForm } from "../assets/js/utils.js";

export default async function CoursesPage() {
  const page = document.createElement("main");
  page.className = "page";
  page.innerHTML = `
    <header class="page-header"><div><span class="eyebrow">COURSES</span><h1>دروس</h1><p>مدیریت دروس، ظرفیت‌ها و تخصیص استاد.</p></div><button class="btn primary" id="add">+ افزودن درس</button></header>
    <section class="panel"><div class="toolbar"><label class="search"><span>⌕</span><input id="search" placeholder="جستجو بر اساس عنوان، شناسه یا کد درس"></label><span class="count" id="count"></span></div><div id="content">${loading()}</div></section>`;

  let courses = [];
  let professors = [];
  const content = page.querySelector("#content");
  const search = page.querySelector("#search");
  page.querySelector("#add").addEventListener("click", () => openForm());
  search.addEventListener("input", render);
  await load();

  async function load() {
    content.innerHTML = loading();
    try {
      [courses, professors] = await Promise.all([api.courses.getAll(), api.professors.getAll()]);
      render();
    } catch (error) { handleError(error); content.innerHTML = empty("لیست دروس دریافت نشد."); }
  }

  function professorName(code) {
    const professor = professors.find((p) => p.personnel_code === code);
    return professor ? fullName(professor) : "تخصیص داده نشده";
  }

  function render() {
    const rows = byText(courses, search.value, ["course_id", "title", "code"]);
    page.querySelector("#count").textContent = `${rows.length} درس`;
    if (!rows.length) { content.innerHTML = empty("درسی برای نمایش وجود ندارد."); return; }
    content.innerHTML = `<div class="table-wrap"><table><thead><tr><th>شناسه</th><th>عنوان درس</th><th>کد درس</th><th>واحد</th><th>ظرفیت</th><th>استاد</th><th>عملیات</th></tr></thead><tbody>${rows.map((c) => `<tr><td><b>${escapeHtml(c.course_id)}</b></td><td>${escapeHtml(c.title)}</td><td>${escapeHtml(c.code)}</td><td>${c.unit}</td><td><span class="capacity ${c.students.length >= c.capacity ? "full" : ""}">${c.students.length}/${c.capacity}</span></td><td>${escapeHtml(professorName(c.professor))}</td><td><div class="actions"><button class="btn tiny" data-assign="${escapeHtml(c.course_id)}">تخصیص استاد</button><button class="btn tiny primary" data-edit="${escapeHtml(c.course_id)}">ویرایش</button><button class="btn tiny danger" data-delete="${escapeHtml(c.course_id)}">حذف</button></div></td></tr>`).join("")}</tbody></table></div>`;
    content.querySelectorAll("[data-assign]").forEach((b) => b.addEventListener("click", () => assignProfessor(b.dataset.assign)));
    content.querySelectorAll("[data-edit]").forEach((b) => b.addEventListener("click", () => openForm(courses.find((c) => c.course_id === b.dataset.edit))));
    content.querySelectorAll("[data-delete]").forEach((b) => b.addEventListener("click", () => remove(b.dataset.delete)));
  }

  function openForm(course = null) {
    const editing = Boolean(course);
    const overlay = modal(`<form novalidate><div class="modal-heading"><span class="eyebrow">COURSE</span><h2>${editing ? "ویرایش درس" : "افزودن درس"}</h2></div><div class="form-grid">
      ${editing ? `<label class="form-field"><span>شناسه درس</span><input value="${escapeHtml(course.course_id)}" disabled></label>` : field("course_id", "شناسه درس", "", "text", 2, 20)}
      ${field("title", "عنوان درس", course?.title, "text", 2, 100)}
      ${field("code", "کد درس", course?.code, "text", 2, 20)}
      ${field("unit", "تعداد واحد", course?.unit ?? 3, "number", 1, 5)}
      ${field("capacity", "ظرفیت", course?.capacity ?? 30, "number", 1, 200)}
    </div><div class="form-actions"><button class="btn primary" type="submit">${editing ? "ذخیره تغییرات" : "ثبت درس"}</button></div></form>`, { title: "درس" });
    document.body.appendChild(overlay);
    overlay.querySelector("form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const form = event.currentTarget;
      if (!validateForm(form)) return;
      const button = form.querySelector("button[type=submit]"); button.disabled = true;
      const data = formData(form);
      const payload = { title: data.title, code: data.code, unit: Number(data.unit), capacity: Number(data.capacity) };
      try {
        if (editing) { await api.courses.update(course.course_id, payload); toast("اطلاعات درس بروزرسانی شد."); }
        else { await api.courses.create({ course_id: data.course_id, ...payload }); toast("درس با موفقیت ثبت شد."); }
        overlay.remove(); await load();
      } catch (error) { button.disabled = false; handleFormError(form, error); }
    });
  }

  function assignProfessor(courseId) {
    if (!professors.length) { toast("ابتدا حداقل یک استاد ثبت کنید.", "error"); return; }
    const course = courses.find((c) => c.course_id === courseId);
    const overlay = modal(`<form novalidate><div class="modal-heading"><span class="eyebrow">ASSIGN PROFESSOR</span><h2>تخصیص استاد</h2><p>${escapeHtml(course.title)}</p></div><label class="form-field"><span>استاد</span><select name="personnel_code" required><option value="">انتخاب استاد...</option>${professors.map((p) => `<option value="${escapeHtml(p.personnel_code)}" ${p.personnel_code === course.professor ? "selected" : ""}>${escapeHtml(fullName(p))} — ${escapeHtml(p.personnel_code)}</option>`).join("")}</select></label><div class="form-actions"><button class="btn primary" type="submit">ثبت تخصیص</button></div></form>`, { title: "تخصیص استاد" });
    document.body.appendChild(overlay);
    overlay.querySelector("form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const form = event.currentTarget;
      if (!validateForm(form)) return;
      const data = formData(form);
      try { const result = await api.selection.assignProfessor(data.personnel_code, courseId); toast(result.message); overlay.remove(); await load(); }
      catch (error) { handleFormError(form, error); }
    });
  }

  async function remove(courseId) {
    if (!confirmAction("آیا از حذف این درس مطمئن هستید؟ این درس از لیست دانشجویان و استاد مربوطه هم حذف می‌شود.")) return;
    try { await api.courses.delete(courseId); toast("درس حذف شد."); await load(); }
    catch (error) { handleError(error); }
  }

  return page;
}

function field(name, label, value = "", type = "text", min = 0, max = 100) {
  const length = type === "text" ? `minlength="${min}" maxlength="${max}"` : `min="${min}" max="${max}" step="1" inputmode="numeric"`;
  return `<label class="form-field"><span>${label}</span><input type="${type}" name="${name}" value="${escapeHtml(value)}" required ${length}></label>`;
}
