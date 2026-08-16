import api from "../assets/js/api.js";
import { empty, loading } from "../assets/js/components.js";
import { escapeHtml, fullName, handleError, toast } from "../assets/js/utils.js";

export default async function SelectionPage() {
  const page = document.createElement("main");
  page.className = "page";
  page.innerHTML = `
    <header class="page-header"><div><span class="eyebrow">COURSE SELECTION</span><h1>انتخاب واحد</h1><p>دانشجو را انتخاب کنید و دروس او را اضافه یا حذف کنید.</p></div></header>
    <section class="panel selector-panel"><label class="form-field compact"><span>دانشجو</span><select id="student"><option value="">انتخاب دانشجو...</option></select></label><div id="student-meta" class="student-meta"></div></section>
    <section class="selection-grid"><article class="panel"><div class="panel-title"><div><span class="eyebrow">AVAILABLE</span><h2>دروس قابل انتخاب</h2></div></div><div id="available">${empty("ابتدا دانشجو را انتخاب کنید.")}</div></article><article class="panel"><div class="panel-title"><div><span class="eyebrow">SELECTED</span><h2>دروس انتخاب‌شده</h2></div></div><div id="selected">${empty("ابتدا دانشجو را انتخاب کنید.")}</div></article></section>`;

  const studentSelect = page.querySelector("#student");
  const availableBox = page.querySelector("#available");
  const selectedBox = page.querySelector("#selected");
  let students = [];
  let courses = [];
  let professors = [];
  let currentNumber = "";

  try {
    [students, courses, professors] = await Promise.all([api.students.getAll(), api.courses.getAll(), api.professors.getAll()]);
    studentSelect.innerHTML += students.map((s) => `<option value="${escapeHtml(s.student_number)}">${escapeHtml(fullName(s))} — ${escapeHtml(s.student_number)}</option>`).join("");
  } catch (error) { handleError(error); }

  studentSelect.addEventListener("change", async () => {
    currentNumber = studentSelect.value;
    if (!currentNumber) {
      page.querySelector("#student-meta").innerHTML = "";
      availableBox.innerHTML = empty("ابتدا دانشجو را انتخاب کنید.");
      selectedBox.innerHTML = empty("ابتدا دانشجو را انتخاب کنید.");
      return;
    }
    await refresh();
  });

  async function refresh() {
    availableBox.innerHTML = loading();
    selectedBox.innerHTML = loading();
    try {
      const [student, latestCourses, selectedCourses] = await Promise.all([
        api.students.get(currentNumber), api.courses.getAll(), api.students.courses(currentNumber),
      ]);
      courses = latestCourses;
      const selectedIds = new Set(selectedCourses.map((c) => c.course_id));
      const availableCourses = courses.filter((c) => !selectedIds.has(c.course_id));
      page.querySelector("#student-meta").innerHTML = `<b>${escapeHtml(fullName(student))}</b><span>${escapeHtml(student.major)} · ${selectedCourses.reduce((sum, c) => sum + c.unit, 0)} واحد انتخاب‌شده</span>`;
      renderAvailable(availableCourses);
      renderSelected(selectedCourses);
    } catch (error) {
      handleError(error);
      availableBox.innerHTML = empty("دروس دریافت نشد.");
      selectedBox.innerHTML = empty("دروس دریافت نشد.");
    }
  }

  function professorName(code) {
    const p = professors.find((item) => item.personnel_code === code);
    return p ? fullName(p) : "بدون استاد";
  }

  function renderAvailable(items) {
    if (!items.length) { availableBox.innerHTML = empty("درس دیگری برای انتخاب وجود ندارد."); return; }
    availableBox.innerHTML = `<div class="course-cards">${items.map((c) => {
      const full = c.students.length >= c.capacity;
      return `<article class="course-card"><div><span class="course-code">${escapeHtml(c.code)}</span><h3>${escapeHtml(c.title)}</h3><p>${c.unit} واحد · ${escapeHtml(professorName(c.professor))}</p><small>ظرفیت: ${c.students.length}/${c.capacity}</small></div><button class="btn primary" data-select="${escapeHtml(c.course_id)}" ${full ? "disabled" : ""}>${full ? "ظرفیت تکمیل" : "انتخاب درس"}</button></article>`;
    }).join("")}</div>`;
    availableBox.querySelectorAll("[data-select]").forEach((button) => button.addEventListener("click", async () => {
      button.disabled = true;
      try { const result = await api.selection.select(currentNumber, button.dataset.select); toast(result.message); await refresh(); }
      catch (error) { button.disabled = false; handleError(error); }
    }));
  }

  function renderSelected(items) {
    if (!items.length) { selectedBox.innerHTML = empty("این دانشجو هنوز درسی انتخاب نکرده است."); return; }
    selectedBox.innerHTML = `<div class="course-cards">${items.map((c) => `<article class="course-card selected"><div><span class="course-code">${escapeHtml(c.code)}</span><h3>${escapeHtml(c.title)}</h3><p>${c.unit} واحد · ${escapeHtml(professorName(c.professor))}</p><small>شناسه: ${escapeHtml(c.course_id)}</small></div><button class="btn danger" data-drop="${escapeHtml(c.course_id)}">حذف درس</button></article>`).join("")}</div>`;
    selectedBox.querySelectorAll("[data-drop]").forEach((button) => button.addEventListener("click", async () => {
      button.disabled = true;
      try { const result = await api.selection.drop(currentNumber, button.dataset.drop); toast(result.message); await refresh(); }
      catch (error) { button.disabled = false; handleError(error); }
    }));
  }

  return page;
}
