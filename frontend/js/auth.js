// auth.js — login, register, telegram, logout

async function doLogin(username, password) {
    const data = await post('/api/auth/login/', { username, password });
    return data;
}

async function doRegister(username, password) {
    const data = await post('/api/auth/register/', { username, password });
    return data;
}

async function doLogout() {
    try { await post('/api/auth/logout/'); } catch (e) { /* ok */ }
    showScreen('login');
}

// Telegram callback — widget calls /api/auth/telegram/ automatically
// We handle the redirect after Telegram auth
window.onTelegramAuth = function(user) {
    // user is already logged in via the widget's auth-url redirect
    showScreen('estimates');
    loadEstimates();
};
