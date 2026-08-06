// calculator.js — estimate line management

let currentEstimate = null;
let categories = [];
let workItems = [];

async function loadCalculator(id) {
    try {
        currentEstimate = await get(`/api/estimates/${id}/`);
        categories = await get('/api/categories/');
        workItems = await get('/api/work-items/');
        renderCalculator();
    } catch (e) { toast(e.message, 'error'); }
}

function renderCalculator() {
    const area = document.getElementById('calculator-area');
    const e = currentEstimate;
    const lines = e.lines || [];
    const total = lines.reduce((sum, l) => sum + (l.total || l.price * l.quantity || 0), 0);

    area.innerHTML = `
        <div class="estimate-header">
            <h3>${escHtml(e.name)}</h3>
            <div style="display:flex; gap:8px; margin-top:8px;">
                <button class="btn-small" onclick="exportPDF()">📄 PDF</button>
                <button class="btn-small" onclick="exportCSV()">📊 CSV</button>
                <button class="btn-small" onclick="copyShareLink()">🔗 Поделиться</button>
                <button class="btn-danger" onclick="deleteEstimate(${e.id})">🗑</button>
            </div>
        </div>

        <div class="estimate-lines">
            ${lines.map((l, i) => `
                <div class="line-row">
                    <span class="line-name">${escHtml(l.work_item_name || l.custom_name || '—')}</span>
                    <span>${escHtml(l.unit || 'ед.')}</span>
                    <input type="number" value="${l.price}" min="0" step="0.01"
                        onchange="updateLine(${l.id}, 'price', this.value)" title="Цена за единицу">
                    <span>×</span>
                    <input type="number" value="${l.quantity}" min="0" step="0.01"
                        onchange="updateLine(${l.id}, 'quantity', this.value)" title="Количество">
                    <span>=</span>
                    <span class="line-total">${formatPrice(l.total || l.price * l.quantity)}</span>
                    <button class="btn-danger" style="padding:4px 8px;font-size:12px;"
                        onclick="deleteLine(${l.id})">✕</button>
                </div>
            `).join('')}
        </div>

        <div class="add-line-form">
            <select id="sel-category" onchange="filterWorkItems()">
                <option value="">Все категории</option>
                ${categories.map(c => `<option value="${c.id}">${escHtml(c.name)}</option>`).join('')}
            </select>
            <select id="sel-work-item">
                <option value="">Выберите работу</option>
                ${workItems.map(w => `
                    <option value="${w.id}" data-price="${w.avg_price}" data-unit="${escHtml(w.unit)}" data-cat="${w.category}">
                        ${escHtml(w.name)} (${formatPrice(w.avg_price)}/${escHtml(w.unit)})
                    </option>
                `).join('')}
            </select>
            <input type="number" id="new-quantity" value="1" min="0.01" step="0.01" placeholder="Кол-во" style="width:80px">
            <button class="btn-primary" style="width:auto" onclick="addLine()">+ Добавить</button>
        </div>

        <div class="total-bar">ИТОГО: ${formatPrice(total)}</div>
    `;
}

function filterWorkItems() {
    const catId = document.getElementById('sel-category')?.value;
    const sel = document.getElementById('sel-work-item');
    if (!sel) return;
    Array.from(sel.options).forEach(opt => {
        if (!opt.value) return;
        opt.style.display = (!catId || opt.dataset.cat === catId) ? '' : 'none';
    });
}

async function addLine() {
    const sel = document.getElementById('sel-work-item');
    const qty = document.getElementById('new-quantity');
    if (!sel.value) { toast('Выберите работу', 'error'); return; }
    
    const opt = sel.selectedOptions[0];
    const price = parseFloat(opt.dataset.price) || 0;
    const unit = opt.dataset.unit || 'ед.';
    
    try {
        await post(`/api/estimates/${currentEstimate.id}/lines/`, {
            work_item: Number(sel.value),
            price,
            quantity: parseFloat(qty.value) || 1,
            unit,
        });
        toast('Добавлено');
        await loadCalculator(currentEstimate.id);
    } catch (e) { toast(e.message, 'error'); }
}

async function updateLine(lineId, field, value) {
    const data = { [field]: parseFloat(value) || 0 };
    try {
        await patch(`/api/estimates/${currentEstimate.id}/lines/${lineId}/`, data);
        await loadCalculator(currentEstimate.id);
    } catch (e) { toast(e.message, 'error'); }
}

async function deleteLine(lineId) {
    try {
        await del(`/api/estimates/${currentEstimate.id}/lines/${lineId}/`);
        toast('Строка удалена');
        await loadCalculator(currentEstimate.id);
    } catch (e) { toast(e.message, 'error'); }
}

function exportPDF() { window.print(); }

function exportCSV() {
    const e = currentEstimate;
    const lines = e.lines || [];
    let csv = 'Работа,Ед.изм,Цена,Количество,Сумма\n';
    lines.forEach(l => {
        const total = l.total || l.price * l.quantity || 0;
        csv += `"${l.work_item_name || l.custom_name || ''}","${l.unit || ''}",${l.price},${l.quantity},${total}\n`;
    });
    const total = lines.reduce((s, l) => s + (l.total || l.price * l.quantity || 0), 0);
    csv += `"","","","ИТОГО:",${total}`;
    
    const blob = new Blob(['\uFEFF' + csv], {type: 'text/csv;charset=utf-8'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `${e.name}.csv`;
    a.click();
}

async function copyShareLink() {
    try {
        const data = await post(`/api/estimates/${currentEstimate.id}/share/`);
        await navigator.clipboard.writeText(data.url);
        toast('Ссылка скопирована!');
    } catch (e) {
        // Fallback for HTTP
        const data = await post(`/api/estimates/${currentEstimate.id}/share/`);
        prompt('Ссылка для шаринга (Ctrl+C):', data.url);
    }
}
