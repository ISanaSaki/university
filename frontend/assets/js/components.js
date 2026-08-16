export function modal(html, { title = "" } = {}) {
  const overlay = document.createElement("div");
  overlay.className = "modal-overlay";
  overlay.innerHTML = `
    <section class="modal" role="dialog" aria-modal="true" aria-label="${title}">
      <button type="button" class="modal-close" aria-label="بستن">×</button>
      <div class="modal-content">${html}</div>
    </section>`;

  const close = () => overlay.remove();
  overlay.querySelector(".modal-close").addEventListener("click", close);
  overlay.addEventListener("click", (event) => { if (event.target === overlay) close(); });
  const onKey = (event) => {
    if (event.key === "Escape") {
      close();
      document.removeEventListener("keydown", onKey);
    }
  };
  document.addEventListener("keydown", onKey);
  return overlay;
}

export function loading(message = "در حال دریافت اطلاعات...") {
  return `<div class="state"><span class="spinner"></span><p>${message}</p></div>`;
}

export function empty(message) {
  return `<div class="state empty-state"><span>—</span><p>${message}</p></div>`;
}
