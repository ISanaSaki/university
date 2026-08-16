import api from "../assets/js/api.js";
import { empty, loading, modal } from "../assets/js/components.js";
import { byText, confirmAction, escapeHtml, formData, fullName, handleError, handleFormError, toast, validateForm } from "../assets/js/utils.js";

export default async function ProfessorsPage() {
  const page = document.createElement("main");
  page.className = "page";
  page.innerHTML = `
    <header class="page-header"><div><span class="eyebrow">PROFESSORS</span><h1>اساتید</h1><p>مدیریت اطلاعات اساتید و مشاهده دروس تخصیص‌یافته.</p></div><button class="btn primary" id="add">+ افزودن استاد</button></header>
    <section class="panel"><div class="toolbar"><label class="search"><span>⌕</span><input id="search" placeholder="جستجو بر اساس نام، کد پرسنلی یا دانشکده"></label><span class="count" id="count"></span></div><div id="content">${loading()}</div></section>`;

  let professors = [];
  const content = page.querySelector("#content");
  const search = page.querySelector("#search");
  page.querySelector("#add").addEventListener("click", () => openForm());
  search.addEventListener("input", render);
  await load();

  async function load() {
    content.innerHTML = loading();
    try { professors = await api.professors.getAll(); render(); }
    catch (error) { handleError(error); content.innerHTML = empty("لیست اساتید دریافت نشد."); }
  }

  function render() {
    const rows = byText(professors, search.value, ["first_name", "last_name", "personnel_code", "department", "national_id"]);
    page.querySelector("#count").textContent = `${rows.length} استاد`;
    if (!rows.length) { content.innerHTML = empty("استادی برای نمایش وجود ندارد."); return; }
    content.innerHTML = `<div class="table-wrap"><table><thead><tr><th>کد پرسنلی</th><th>نام و نام خانوادگی</th><th>کد ملی</th><th>دانشکده</th><th>تعداد درس</th><th>عملیات</th></tr></thead><tbody>${rows.map((p) => `<tr><td><b>${escapeHtml(p.personnel_code)}</b></td><td>${escapeHtml(fullName(p))}</td><td>${escapeHtml(p.national_id)}</td><td>${escapeHtml(p.department)}</td><td>${p.courses.length}</td><td><div class="actions"><button class="btn tiny" data-view="${escapeHtml(p.personnel_code)}">مشاهده</button><button class="btn tiny primary" data-edit="${escapeHtml(p.personnel_code)}">ویرایش</button><button class="btn tiny danger" data-delete="${escapeHtml(p.personnel_code)}">حذف</button></div></td></tr>`).join("")}</tbody></table></div>`;
    content.querySelectorAll("[data-view]").forEach((b) => b.addEventListener("click", () => viewProfessor(b.dataset.view)));
    content.querySelectorAll("[data-edit]").forEach((b) => b.addEventListener("click", () => openForm(professors.find((p) => p.personnel_code === b.dataset.edit))));
    content.querySelectorAll("[data-delete]").forEach((b) => b.addEventListener("click", () => remove(b.dataset.delete)));
  }

  function openForm(professor = null) {
    const editing = Boolean(professor);
    const overlay = modal(`<form id="professor-form" novalidate><div class="modal-heading"><span class="eyebrow">PROFESSOR</span><h2>${editing ? "ویرایش استاد" : "افزودن استاد"}</h2></div><div class="form-grid">
      ${editing ? "" : field("national_id", "کد ملی", "", 3, 20)}
      ${field("first_name", "نام", professor?.first_name, 2, 50)}
      ${field("last_name", "نام خانوادگی", professor?.last_name, 2, 50)}
      ${field("personnel_code", "کد پرسنلی", professor?.personnel_code, 3, 20)}
      ${field("department", "دانشکده / دپارتمان", professor?.department, 2, 80)}
    </div><div class="form-actions"><button class="btn primary" type="submit">${editing ? "ذخیره تغییرات" : "ثبت استاد"}</button></div></form>`, { title: "استاد" });
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
          await api.professors.update(professor.personnel_code, { first_name: data.first_name, last_name: data.last_name, personnel_code: data.personnel_code, department: data.department });
          toast("اطلاعات استاد بروزرسانی شد.");
        } else {
          await api.professors.create(data);
          toast("استاد با موفقیت ثبت شد.");
        }
        overlay.remove(); await load();
      } catch (error) { button.disabled = false; handleFormError(form, error); }
    });
  }

  async function viewProfessor(code) {
    try {
      const [professor, courses] = await Promise.all([api.professors.get(code), api.courses.getAll()]);
      const assigned = courses.filter((course) => course.professor === professor.personnel_code);
      const overlay = modal(`<div class="modal-heading"><span class="eyebrow">PROFESSOR DETAIL</span><h2>${escapeHtml(fullName(professor))}</h2></div><dl class="details"><div><dt>کد پرسنلی</dt><dd>${escapeHtml(professor.personnel_code)}</dd></div><div><dt>کد ملی</dt><dd>${escapeHtml(professor.national_id)}</dd></div><div><dt>دانشکده</dt><dd>${escapeHtml(professor.department)}</dd></div></dl><h3 class="subheading">دروس ارائه‌شده</h3>${assigned.length ? `<ul class="course-list">${assigned.map((c) => `<li><b>${escapeHtml(c.title)}</b><span>${escapeHtml(c.code)} · ${c.unit} واحد</span></li>`).join("")}</ul>` : empty("درسی به این استاد تخصیص داده نشده است.")}`, { title: "جزئیات استاد" });
      document.body.appendChild(overlay);
    } catch (error) { handleError(error); }
  }

  async function remove(code) {
    if (!confirmAction("آیا از حذف این استاد مطمئن هستید؟ دروس او بدون استاد باقی می‌مانند.")) return;
    try { await api.professors.delete(code); toast("استاد حذف شد."); await load(); }
    catch (error) { handleError(error); }
  }

  return page;
}

function field(name, label, value = "", min = 0, max = 100) {
  return `<label class="form-field"><span>${label}</span><input name="${name}" value="${escapeHtml(value)}" required minlength="${min}" maxlength="${max}"></label>`;
}
