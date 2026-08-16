export function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

export function formData(form) {
  return Object.fromEntries([...new FormData(form).entries()].map(([key, value]) => [key, typeof value === "string" ? value.trim() : value]));
}

export function toast(message, type = "success") {
  const container = document.getElementById("toast-container");
  const item = document.createElement("div");
  item.className = `toast toast-${type}`;
  item.textContent = message;
  container.appendChild(item);
  requestAnimationFrame(() => item.classList.add("show"));
  setTimeout(() => {
    item.classList.remove("show");
    setTimeout(() => item.remove(), 220);
  }, 3200);
}

export function handleError(error) {
  console.error(error);
  toast(error?.message || "خطایی رخ داده است.", "error");
}

function fieldLabel(field) {
  return field.closest(".form-field")?.querySelector(":scope > span")?.textContent?.trim()
    || field.name
    || "این فیلد";
}

function frontendValidationMessage(field) {
  const label = fieldLabel(field);
  const validity = field.validity;

  if (validity.valueMissing) return `فیلد «${label}» الزامی است.`;
  if (validity.badInput || validity.typeMismatch) return `مقدار واردشده برای «${label}» از نوع صحیح نیست.`;
  if (validity.tooShort) return `فیلد «${label}» باید حداقل ${field.minLength} کاراکتر باشد.`;
  if (validity.tooLong) return `فیلد «${label}» باید حداکثر ${field.maxLength} کاراکتر باشد.`;
  if (validity.rangeUnderflow) return `مقدار «${label}» باید حداقل ${field.min} باشد.`;
  if (validity.rangeOverflow) return `مقدار «${label}» باید حداکثر ${field.max} باشد.`;
  if (validity.stepMismatch) return `مقدار «${label}» باید یک عدد صحیح معتبر باشد.`;
  if (validity.patternMismatch) return `فرمت واردشده برای «${label}» معتبر نیست.`;
  return `مقدار واردشده برای «${label}» معتبر نیست.`;
}

export function clearFormErrors(form) {
  form.querySelectorAll(".field-error").forEach((item) => item.remove());
  form.querySelectorAll(".field-invalid").forEach((field) => {
    field.classList.remove("field-invalid");
    field.removeAttribute("aria-invalid");
    field.removeAttribute("aria-describedby");
  });
}

function setFieldError(field, message) {
  if (!field) return false;
  const holder = field.closest(".form-field") || field.parentElement;
  if (!holder) return false;

  field.classList.add("field-invalid");
  field.setAttribute("aria-invalid", "true");

  const errorId = `error-${field.name || "field"}-${Math.random().toString(36).slice(2, 8)}`;
  const messageBox = document.createElement("small");
  messageBox.className = "field-error";
  messageBox.id = errorId;
  messageBox.textContent = message;
  holder.appendChild(messageBox);
  field.setAttribute("aria-describedby", errorId);
  return true;
}

export function validateForm(form) {
  clearFormErrors(form);
  let firstInvalid = null;

  for (const field of form.querySelectorAll("input, select, textarea")) {
    if (field.disabled || field.validity.valid) continue;
    setFieldError(field, frontendValidationMessage(field));
    firstInvalid ||= field;
  }

  if (firstInvalid) {
    firstInvalid.focus();
    toast("لطفاً خطاهای فرم را اصلاح کنید.", "error");
    return false;
  }
  return true;
}

export function applyApiFieldErrors(form, error) {
  clearFormErrors(form);
  let mapped = 0;
  let firstInvalid = null;

  for (const item of error?.errors || []) {
    const fieldName = String(item?.field || "").split(".").pop();
    if (!fieldName) continue;
    const field = [...form.elements].find((element) => element.name === fieldName);
    if (!field) continue;
    if (setFieldError(field, item.message || error.message)) {
      mapped += 1;
      firstInvalid ||= field;
    }
  }

  firstInvalid?.focus();
  return mapped;
}

export function handleFormError(form, error) {
  console.error(error);
  const mapped = applyApiFieldErrors(form, error);
  if (mapped) {
    toast(error?.message || "لطفاً خطاهای فرم را اصلاح کنید.", "error");
    return;
  }
  handleError(error);
}

export function confirmAction(message) {
  return window.confirm(message);
}

export function fullName(person) {
  return `${person?.first_name ?? ""} ${person?.last_name ?? ""}`.trim() || "-";
}

export function byText(items, query, fields) {
  const normalized = query.trim().toLocaleLowerCase("fa");
  if (!normalized) return items;
  return items.filter((item) => fields.some((field) => String(item[field] ?? "").toLocaleLowerCase("fa").includes(normalized)));
}
