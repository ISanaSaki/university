import { currentPath, navigate } from "./router.js";

const items = [
  ["/", "⌂", "داشبورد"],
  ["/students", "ST", "دانشجویان"],
  ["/professors", "PR", "اساتید"],
  ["/courses", "CO", "دروس"],
  ["/selection", "SE", "انتخاب واحد"],
];

export function layout(content) {
  const root = document.createElement("div");
  root.className = "app-layout";
  const path = currentPath();
  root.innerHTML = `
    <aside class="sidebar">
      <div class="brand"><span class="brand-mark">U</span><div><strong>UniReg</strong><small>سیستم انتخاب واحد</small></div></div>
      <nav>${items.map(([route, icon, label]) => `<button class="nav-item ${route === path ? "active" : ""}" data-route="${route}"><span>${icon}</span>${label}</button>`).join("")}</nav>
      <div class="sidebar-note">FastAPI · Vanilla JS</div>
    </aside>
    <div class="main-shell">
      <header class="topbar"><button class="menu-button" type="button">☰</button><div><b>سیستم انتخاب واحد دانشگاهی</b><small>پنل مدیریت ساده و یکپارچه</small></div></header>
      <div class="page-container"></div>
    </div>
    <div class="backdrop"></div>`;

  root.querySelector(".page-container").append(content);
  root.querySelectorAll("[data-route]").forEach((button) => button.addEventListener("click", () => {
    navigate(button.dataset.route);
    root.querySelector(".sidebar").classList.remove("open");
    root.querySelector(".backdrop").classList.remove("show");
  }));
  root.querySelector(".menu-button").addEventListener("click", () => {
    root.querySelector(".sidebar").classList.add("open");
    root.querySelector(".backdrop").classList.add("show");
  });
  root.querySelector(".backdrop").addEventListener("click", () => {
    root.querySelector(".sidebar").classList.remove("open");
    root.querySelector(".backdrop").classList.remove("show");
  });
  return root;
}
