const tg = window.Telegram.WebApp;
const grid = document.getElementById('types-grid');
const detail = document.getElementById('type-detail');

// Initialize
tg.expand();

async function fetchTypes() {
    try {
        const response = await fetch('/api/types');
        const types = await response.json();
        return types;
    } catch (e) {
        console.error("Failed to fetch types", e);
        return {};
    }
}

function renderGrid(types) {
    grid.innerHTML = '';

    Object.keys(types).forEach(key => {
        const t = types[key];
        const card = document.createElement('div');
        card.className = 'card';
        card.onclick = () => showDetail(t);
        card.innerHTML = `
            <span class="emoji">${t.emoji}</span>
            <h3>${t.name_ru}</h3>
        `;
        grid.appendChild(card);
    });
}

function showDetail(typeData) {
    grid.classList.add('hidden');
    detail.classList.remove('hidden');

    const markersHtml = typeData.markers.map(m => `<li>${m}</li>`).join('');

    detail.innerHTML = `
        <button class="back-btn" onclick="goBack()">⬅ Назад</button>
        <div style="text-align: center; margin-bottom: 20px;">
            <span style="font-size: 4em;">${typeData.emoji}</span>
            <h2>${typeData.name_ru}</h2>
        </div>
        
        <div class="section">
            <p>${typeData.short_desc}</p>
        </div>

        <div class="section">
            <h4>📋 Как узнать?</h4>
            <ul>${markersHtml}</ul>
        </div>
        
        <div class="section">
            <h4>⚠️ Риски</h4>
            <p>${typeData.risks}</p>
        </div>
        
        <div class="section">
            <h4>🔧 Совет</h4>
            <div style="background: #e3f2fd; padding: 10px; border-radius: 8px;">
                ${typeData.management_advice}
            </div>
        </div>
    `;

    tg.BackButton.show();
    tg.BackButton.onClick(goBack);
}

function goBack() {
    detail.classList.add('hidden');
    grid.classList.remove('hidden');
    tg.BackButton.hide();
}

// Start
document.addEventListener('DOMContentLoaded', async () => {
    const types = await fetchTypes();
    renderGrid(types);
});
