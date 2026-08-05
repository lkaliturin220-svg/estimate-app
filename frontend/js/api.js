// api.js — HTTP client with Django sessions (cookies)
const API_BASE = '';

function getCSRF() {
    const m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? m[1] : '';
}

async function api(method, path, body = null) {
    const opts = {
        method,
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRF(),
        },
    };
    if (body) opts.body = JSON.stringify(body);
    
    const res = await fetch(API_BASE + path, opts);
    if (res.status === 403) {
        // session expired
        showScreen('login');
        throw new Error('Session expired');
    }
    if (!res.ok) {
        const err = await res.json().catch(() => ({ error: 'Ошибка сервера' }));
        throw new Error(err.error || err.detail || 'Ошибка');
    }
    return res.json();
}

const get = (p) => api('GET', p);
const post = (p, b) => api('POST', p, b);
const patch = (p, b) => api('PATCH', p, b);
const del = (p) => api('DELETE', p);
