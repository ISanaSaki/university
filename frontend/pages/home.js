import api from "../assets/js/api.js";
import { empty, loading } from "../assets/js/components.js";
import { escapeHtml, fullName, handleError } from "../assets/js/utils.js";

export default async function HomePage() {
  const page = document.createElement("main");
  page.className = "page";
  page.innerHTML = `
    <header class="page-header"><div><span class="eyebrow">DASHBOARD</span><h1>داشبورد</h1><p>نمای کلی اطلاعات ثبت‌شده در سیستم انتخاب واحد.</p></div></header>
    <section id="stats" class="stats-grid">${loading()}</section>
    <section class="content-grid three" id="previews"></section>`;

  try {
    const [summary, data] = await Promise.all([api.system.summary(), api.system.allData()]);
    page.querySelector("#stats").innerHTML = [
      ["دانشجویان", summary.students_count, "تعداد دانشجویان ثبت‌شده"],
      ["اساتید", summary.professors_count, "تعداد اساتید ثبت‌شده"],
      ["دروس", summary.courses_count, "تعداد دروس ارائه‌شده"],
      ["انتخاب‌ها", summary.selections_count, "مجموع انتخاب درس‌ها"],
      ["دروس دارای استاد", summary.assigned_courses_count, "تخصیص استاد انجام‌شده"],
      ["ظرفیت باقی‌مانده", summary.remaining_capacity, `از مجموع ${summary.total_capacity} نفر`],
    ].map(([label, value, note]) => `<article class="stat-card"><span>${label}</span><strong>${value}</strong><small>${note}</small></article>`).join("");

    const previews = page.querySelector("#previews");
    previews.innerHTML = `
      ${preview("آخرین دانشجویان", data.students.slice(-4).reverse().map((item) => `<li><b>${escapeHtml(fullName(item))}</b><span>${escapeHtml(item.student_number)} · ${escapeHtml(item.major)}</span></li>`).join(""), "هنوز دانشجویی ثبت نشده است.")}
      ${preview("آخرین اساتید", data.professors.slice(-4).reverse().map((item) => `<li><b>${escapeHtml(fullName(item))}</b><span>${escapeHtml(item.personnel_code)} · ${escapeHtml(item.department)}</span></li>`).join(""), "هنوز استادی ثبت نشده است.")}
      ${preview("آخرین دروس", data.courses.slice(-4).reverse().map((item) => `<li><b>${escapeHtml(item.title)}</b><span>${escapeHtml(item.course_id)} · ${item.unit} واحد · ${item.students.length}/${item.capacity}</span></li>`).join(""), "هنوز درسی ثبت نشده است.")}`;
  } catch (error) {
    handleError(error);
    page.querySelector("#stats").innerHTML = empty("اطلاعات داشبورد دریافت نشد.");
  }
  return page;
}

function preview(title, items, emptyText) {
  return `<article class="panel"><div class="panel-title"><h2>${title}</h2></div>${items ? `<ul class="preview-list">${items}</ul>` : empty(emptyText)}</article>`;
}
