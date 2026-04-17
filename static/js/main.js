// DataPure — main.js (shared utilities, loaded on every page)

// ── Toast helper ─────────────────────────────────────────────────
function showToast(msg, type = 'info') {
  const icons = {
    info:    'fa-circle-info',
    success: 'fa-circle-check',
    error:   'fa-circle-xmark',
    warning: 'fa-triangle-exclamation',
  };
  let area = document.querySelector('.dp-flash-area');
  if (!area) {
    area = document.createElement('div');
    area.className = 'dp-flash-area';
    document.body.appendChild(area);
  }
  const toast = document.createElement('div');
  toast.className = `dp-toast dp-toast--${type}`;
  toast.innerHTML = `
    <i class="fa-solid ${icons[type] || icons.info}"></i>
    <span>${msg}</span>
    <button class="dp-toast__close" onclick="this.parentElement.remove()">
      <i class="fa-solid fa-xmark"></i>
    </button>`;
  area.appendChild(toast);
  setTimeout(() => toast.remove(), 5000);
}

// ── Auto-dismiss flash toasts after 5 s ──────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.dp-toast').forEach(t => {
    setTimeout(() => t.remove(), 5000);
  });
});