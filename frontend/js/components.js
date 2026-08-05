// components.js — UI helpers

function toast(msg, type = 'success') {
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 3000);
}

function formatPrice(n) {
    return Number(n).toLocaleString('ru-RU') + ' ₽';
}

function formatDate(s) {
    if (!s) return '';
    const d = new Date(s);
    return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' });
}
