const toast = document.querySelector(".toast");
let toastTimer;

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("is-visible");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("is-visible"), 1600);
}

document.querySelectorAll("[data-copy]").forEach((swatch) => {
  swatch.addEventListener("click", async () => {
    const value = swatch.dataset.copy;
    try {
      await navigator.clipboard.writeText(value);
      showToast(`${value} copied`);
    } catch {
      showToast(value);
    }
  });
});
