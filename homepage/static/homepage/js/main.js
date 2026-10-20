"use strict";
// Кнопка возвращает пользователя к форме без старых параметров поиска.
document.querySelectorAll("[data-clear-filters]").forEach((button) => {
  button.addEventListener("click", () => window.location.assign(button.dataset.clearFilters));
});
// Дополнительные сведения о проекте доступны и без JavaScript через details.
document.querySelectorAll("details[data-about]").forEach((details) => {
  details.addEventListener("toggle", () => {
    details.querySelector("summary").textContent = details.open ? "Скрыть сведения" : "О проекте";
  });
});
