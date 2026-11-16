"use strict";

// Отправка остаётся обычным POST: JS только показывает состояние кнопки.
document.querySelectorAll('form[method="post"]').forEach((form) => {
  form.addEventListener("submit", () => {
    const button = form.querySelector("button[type=submit][data-pending-label]");
    if (!button) return;
    button.dataset.originalLabel = button.textContent;
    button.textContent = button.dataset.pendingLabel;
    button.disabled = true;
    form.setAttribute("aria-busy", "true");
  });
});

// Возврат назад из истории браузера восстанавливает доступность формы.
window.addEventListener("pageshow", () => {
  document.querySelectorAll("button[data-original-label]").forEach((button) => {
    button.textContent = button.dataset.originalLabel;
    button.disabled = false;
    button.closest("form").removeAttribute("aria-busy");
  });
});
