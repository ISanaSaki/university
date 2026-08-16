import api from "../assets/js/api.js";
import { empty, loading, modal } from "../assets/js/components.js";
import { byText, confirmAction, escapeHtml, formData, fullName, handleError, handleFormError, toast, validateForm } from "../assets/js/utils.js";

export default async function StudentsPage() {
  const page = document.createElement("main");
  page.className = "page";
  page.innerHTML = `
    <header class="page-header"><div><span class="eyebrow">STUDENTS</span><h1>دانشجویان</h1><p>ایجاد، مشاهده، ویرایش و حذف دانشجو.</p></div><button class="btn primary" id="add">+ افزودن دانشجو</button></header>
    <section class="panel"><div class="toolbar"><label class="search"><span>⌕</span><input id="search" placeholder="جستجو بر اساس نام، شماره دانشجویی یا رشته"></label><span class="count" id="count"></span></div><div id="content">${loading()}</div></section>`;

  let students = [];
  const content = page.querySelector("#content");
  const search = page.querySelector("#search");

  page.querySelector("#add").addEventListener("click", () => openForm());
  search.addEventListener("input", render);
  await load();

  async function load() {
    content.innerHTML = loading();
    try { students = await api.students.getAll(); render(); }
    catch (error) { handleError(error); content.innerHTML = empty("لیست دانشجویان دریافت نشد."); }
  }

  function render() {
    const rows = byText(students, search.value, ["first_name", "last_name", "student_number", "major", "national_id"]);
    page.querySelector("#count").textContent = `${rows.length} دانشجو`;
    if (!rows.length) { content.innerHTML = empty("دانشجویی برای نمایش وجود ندارد."); return; }
    content.innerHTML = `<div class="table-wrap"><table><thead><tr><th>شماره دانشجویی</th><th>نام و نام خانوادگی</th><th>کد ملی</th><th>رشته</th><th>عملیات</th></tr></thead><tbody>${rows.map((s) => `<tr><td><b>${escapeHtml(s.student_number)}</b></td><td>${escapeHtml(fullName(s))}</td><td>${escapeHtml(s.national_id)}</td><td>${escapeHtml(s.major)}</td><td><div class="actions"><button class="btn tiny" data-view="${escapeHtml(s.student_number)}">مشاهده</button><button class="btn tiny primary" data-edit="${escapeHtml(s.student_number)}">ویرایش</button><button class="btn tiny danger" data-delete="${escapeHtml(s.student_number)}">حذف</button></div></td></tr>`).join("")}</tbody></table></div>`;
    content.querySelectorAll("[data-view]").forEach((b) => b.addEventListener("click", () => viewStudent(b.dataset.view)));
    content.querySelectorAll("[data-edit]").forEach((b) => b.addEventListener("click", () => openForm(students.find((s) => s.student_number === b.dataset.edit))));
    content.querySelectorAll("[data-delete]").forEach((b) => b.addEventListener("click", () => remove(b.dataset.delete)));
  }

  function openForm(student = null) {
    const editing = Boolean(student);
    const overlay = modal(`<form id="student-form" novalidate><div class="modal-heading"><span class="eyebrow">STUDENT</span><h2>${editing ? "ویرایش دانشجو" : "افزودن دانشجو"}</h2></div><div class="form-grid">
      ${editing ? "" : field("national_id", "کد ملی", "", 3, 20)}
      ${field("first_name", "نام", student?.first_name, 2, 50)}
      ${field("last_name", "نام خانوادگی", student?.last_name, 2, 50)}
      ${field("student_number", "شماره دانشجویی", student?.student_number, 3, 20)}
      ${field("major", "رشته تحصیلی", student?.major, 2, 80)}
    </div><div class="form-actions"><button class="btn primary" type="submit">${editing ? "ذخیره تغییرات" : "ثبت دانشجو"}</button></div></form>`, { title: "دانشجو" });
    document.body.appendChild(overlay);
    overlay.querySelector("form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const form = event.currentTarget;
      if (!validateForm(form)) return;
      const button = form.querySelector("button[type=submit]");
      button.disabled = true;
      const data = formData(form);
      try {
        if (editing) {
          const payload = { first_name: data.first_name, last_name: data.last_name, student_number: data.student_number, major: data.major };
          await api.students.update(student.student_number, payload);
          toast("اطلاعات دانشجو بروزرسانی شد.");
        } else {
          await api.students.create(data);
          toast("دانشجو با موفقیت ثبت شد.");
        }
        overlay.remove(); await load();
      } catch (error) { button.disabled = false; handleFormError(form, error); }
    });
  }

  async function viewStudent(studentNumber) {
    try {
      const [student, courses] = await Promise.all([api.students.get(studentNumber), api.students.courses(studentNumber)]);
      const overlay = modal(`<div class="modal-heading"><span class="eyebrow">STUDENT DETAIL</span><h2>${escapeHtml(fullName(student))}</h2></div><dl class="details"><div><dt>شماره دانشجویی</dt><dd>${escapeHtml(student.student_number)}</dd></div><div><dt>کد ملی</dt><dd>${escapeHtml(student.national_id)}</dd></div><div><dt>رشته</dt><dd>${escapeHtml(student.major)}</dd></div></dl><h3 class="subheading">دروس انتخاب‌شده</h3>${courses.length ? `<ul class="course-list">${courses.map((c) => `<li><b>${escapeHtml(c.title)}</b><span>${escapeHtml(c.code)} · ${c.unit} واحد</span></li>`).join("")}</ul>` : empty("این دانشجو هنوز درسی انتخاب نکرده است.")}`, { title: "جزئیات دانشجو" });
      document.body.appendChild(overlay);
    } catch (error) { handleError(error); }
  }

  async function remove(studentNumber) {
    if (!confirmAction("آیا از حذف این دانشجو مطمئن هستید؟")) return;
    try { await api.students.delete(studentNumber); toast("دانشجو حذف شد."); await load(); }
    catch (error) { handleError(error); }
  }

  return page;
}

function field(name, label, value = "", min = 0, max = 100) {
  return `<label class="form-field"><span>${label}</span><input name="${name}" value="${escapeHtml(value)}" required minlength="${min}" maxlength="${max}"></label>`;
}
