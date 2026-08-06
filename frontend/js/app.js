// app.js — routing and initialization

function showScreen(name) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    const screen = document.getElementById(`screen-${name}`);
    if (screen) screen.classList.add('active');
    
    if (name === 'estimates') loadEstimates();
    if (name === 'login') {
        currentEstimateId = null;
        document.getElementById('calculator-area').innerHTML = '<p class="empty">Выберите смету или создайте новую</p>';
    }
}

// Theme toggle
function toggleTheme() {
    const html = document.documentElement;
    const current = html.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
}

// Show/hide password
function togglePW(inputId, btn) {
    const input = document.getElementById(inputId);
    if (input.type === 'password') {
        input.type = 'text';
        btn.textContent = '🙈';
    } else {
        input.type = 'password';
        btn.textContent = '👁';
    }
}

// Init
document.addEventListener('DOMContentLoaded', () => {
    // Theme
    const saved = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', saved);
    document.getElementById('btn-theme').addEventListener('click', toggleTheme);

    // Login tabs
    document.querySelectorAll('.tab').forEach(t => {
        t.addEventListener('click', () => {
            document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
            t.classList.add('active');
            document.querySelectorAll('.tab-content').forEach(x => x.classList.remove('active'));
            document.getElementById(`tab-${t.dataset.tab}`).classList.add('active');
        });
    });

    // Show register / login toggles
    document.getElementById('show-register').addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('tab-password').style.display = 'none';
        document.getElementById('tab-register').style.display = 'block';
        document.querySelector('.tab[data-tab="password"]').textContent = 'Регистрация';
    });
    document.getElementById('show-login').addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('tab-register').style.display = 'none';
        document.getElementById('tab-password').style.display = 'block';
        document.querySelector('.tab[data-tab="password"]').textContent = 'Пароль';
    });

    // Login form
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const u = document.getElementById('login-username').value;
        const p = document.getElementById('login-password').value;
        try {
            await doLogin(u, p);
            showScreen('estimates');
        } catch (err) { toast(err.message, 'error'); }
    });

    // Register form
    document.getElementById('register-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const u = document.getElementById('reg-username').value.trim();
        const p = document.getElementById('reg-password').value;
        const p2 = document.getElementById('reg-password2').value;
        const errEl = document.getElementById('reg-error');
        
        // Validate
        if (u.length < 3) {
            errEl.textContent = 'Логин должен быть не менее 3 символов';
            errEl.style.display = 'block';
            return;
        }
        if (p.length < 6) {
            errEl.textContent = 'Пароль должен быть не менее 6 символов';
            errEl.style.display = 'block';
            return;
        }
        if (!/[a-zA-Zа-яА-Я]/.test(p)) {
            errEl.textContent = 'Пароль должен содержать хотя бы одну букву';
            errEl.style.display = 'block';
            return;
        }
        if (!/[0-9]/.test(p)) {
            errEl.textContent = 'Пароль должен содержать хотя бы одну цифру';
            errEl.style.display = 'block';
            return;
        }
        if (p !== p2) {
            errEl.textContent = 'Пароли не совпадают';
            errEl.style.display = 'block';
            return;
        }
        errEl.style.display = 'none';
        
        try {
            await doRegister(u, p);
            showScreen('estimates');
        } catch (err) { toast(err.message, 'error'); }
    });

    // Logout
    document.getElementById('btn-logout').addEventListener('click', doLogout);

    // New estimate
    document.getElementById('btn-new-estimate').addEventListener('click', createEstimate);

    // Check if already logged in (try loading estimates)
    // First get CSRF cookie
    fetch('/api/auth/csrf/', { credentials: 'same-origin' })
        .then(() => get('/api/estimates/'))
        .then(() => showScreen('estimates'))
        .catch(() => showScreen('login'));
});

// Telegram callback handling
window.addEventListener('message', (event) => {
    if (event.origin !== 'https://oauth.telegram.org') return;
    // Telegram widget redirects after auth — just show estimates
    showScreen('estimates');
});
