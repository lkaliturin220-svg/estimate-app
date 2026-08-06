// estimates.js — estimates list management

let currentEstimateId = null;
let estimates = [];

async function loadEstimates() {
    try {
        estimates = await get('/api/estimates/');
        renderEstimatesList();
    } catch (e) {
        if (!e.message.includes('Session')) toast(e.message, 'error');
    }
}

function renderEstimatesList() {
    const container = document.getElementById('estimates-list');
    if (!estimates.length) {
        container.innerHTML = '<p class="empty">Нет смет. Создайте первую!</p>';
        return;
    }
    container.innerHTML = estimates.map(e => `
        <div class="list-item${e.id === currentEstimateId ? ' active' : ''}" data-id="${e.id}">
            <div class="item-row">
                <div class="item-info" onclick="event.stopPropagation()">
                    <div class="name">${escHtml(e.name)}</div>
                    <div class="meta">${formatDate(e.created_at)} · ${formatPrice(e.total || 0)}</div>
                </div>
                <button class="btn-icon-sm" onclick="event.stopPropagation();duplicateEstimate(${e.id})" title="Дублировать">📋</button>
            </div>
        </div>
    `).join('');

    container.querySelectorAll('.list-item').forEach(el => {
        el.addEventListener('click', () => selectEstimate(Number(el.dataset.id)));
    });
}

async function selectEstimate(id) {
    currentEstimateId = id;
    renderEstimatesList();
    await loadCalculator(id);
}

async function createEstimate() {
    const name = prompt('Название сметы:', 'Новая смета');
    if (!name) return;
    try {
        await post('/api/estimates/', { name });
        toast('Смета создана');
        await loadEstimates();
        // select the last one
        const last = await get('/api/estimates/');
        if (last.length) selectEstimate(last[last.length - 1].id);
    } catch (e) { toast(e.message, 'error'); }
}

async function duplicateEstimate(id) {
    try {
        await post(`/api/estimates/${id}/duplicate/`);
        toast('Смета скопирована');
        await loadEstimates();
    } catch (e) { toast(e.message, 'error'); }
}

async function deleteEstimate(id) {
    if (!confirm('Удалить смету?')) return;
    try {
        await del(`/api/estimates/${id}/`);
        if (currentEstimateId === id) {
            currentEstimateId = null;
            document.getElementById('calculator-area').innerHTML = '<p class="empty">Выберите смету или создайте новую</p>';
        }
        toast('Смета удалена');
        await loadEstimates();
    } catch (e) { toast(e.message, 'error'); }
}

function escHtml(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
}
