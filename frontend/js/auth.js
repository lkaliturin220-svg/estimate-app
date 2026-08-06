// auth.js — login, register, telegram, logout

async function doLogin(username, password) {
    const data = await post('/api/auth/login/', { username, password });
    // После логина CSRF токен обновляется — получаем новый
    await fetch('/api/auth/csrf/', { credentials: 'same-origin' });
    return data;
}

async function doRegister(username, password) {
    const data = await post('/api/auth/register/', { username, password });
    // После регистрации CSRF токен обновляется
    await fetch('/api/auth/csrf/', { credentials: 'same-origin' });
    return data;
}

async function doLogout() {
    try { await post('/api/auth/logout/'); } catch (e) { /* ok */ }
    // Обновить CSRF после выхода
    await fetch('/api/auth/csrf/', { credentials: 'same-origin' });
    showScreen('login');
}

// Telegram callback
window.onTelegramAuth = function(user) {
    fetch('/api/auth/csrf/', { credentials: 'same-origin' })
        .then(() => showScreen('estimates'))
        .then(() => loadEstimates());
};
