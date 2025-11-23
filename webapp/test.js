// test.js – Interactive Diagnostic Test
// This script runs in test.html and provides a simple flow:
// 1. Load a list of test employees (one per type).
// 2. For each employee show a card with a masked avatar and the first marker.
// 3. "Show more" button reveals the next marker until all are shown.
// 4. After markers are revealed, user selects a type from buttons.
// 5. If the answer is wrong, show the correct type and a detailed explanation.
// 6. After the first pass, offer a deep‑dive: load three extra employees of the chosen type.

// NOTE: This is a minimal implementation for demonstration purposes.

const TEST_EMPLOYEES = [
    {
        id: "bird1",
        type: "BIRD",
        name: "Птица 1",
        markers: [
            "Любит новизну и быстрые впечатления",
            "Легко загорается, но быстро остывает",
            "Ориентирована на креативные задачи"
        ],
        explanation: "🐦 Птица – живёт впечатлениями и новизной; легко загорается и так же легко остывает. Она приносит высокий поток, но требует постоянного вдохновения."
    },
    {
        id: "hamster1",
        type: "HAMSTER",
        name: "Хомяк 1",
        markers: [
            "Ценит стабильность и чёткие правила",
            "Болезненно реагирует на хаос",
            "Работает над рутиной и поддержкой"
        ],
        explanation: "🐹 Хомяк – ценит деньги, стабильность и понятные правила; болезненно реагирует на хаос. Он обеспечивает надёжность и постоянный доход."
    },
    {
        id: "fox1",
        type: "FOX",
        name: "Лиса 1",
        markers: [
            "Ориентирована на личную выгоду и статус",
            "Обладает сильными социальными навыками",
            "Ищет возможности для роста"
        ],
        explanation: "🦊 Лиса – ориентирована на личную выгоду, статус и возможности; сильные социальные навыки. При правильном управлении может увеличить продажи."
    },
    {
        id: "rat1",
        type: "RAT",
        name: "Крыса 1",
        markers: [
            "Токсична, использует влияние против системы",
            "Манипулирует коллегами",
            "Сосредоточена на личных выгодах"
        ],
        explanation: "🐀 Крыса – Лиса, ушедшая в токсик: использует результат и влияние, чтобы играть против системы. Вызывает падение морального климата."
    },
    {
        id: "pro1",
        type: "PRO",
        name: "Профи 1",
        markers: [
            "Строит мотивацию на качестве и экспертизе",
            "Ставит высокие стандарты",
            "Фокусируется на долгосрочном росте"
        ],
        explanation: "👔 Профессионал – строит мотивацию на качестве, экспертизе и стандартах. Обеспечивает стабильный рост и высокое качество работы."
    },
    {
        id: "beta1",
        type: "BETA",
        name: "Бета‑лидер 1",
        markers: [
            "Держит команду и процессы",
            "Переводит идеи в действия",
            "Обеспечивает стабильность операций"
        ],
        explanation: "🅱️ Бета‑лидер – держит команду и процессы, переводит идею в конкретные действия. Обеспечивает устойчивость и исполнение планов."
    }
];

let currentIndex = 0;
let revealedCount = 0;
let deepDiveMode = false;
let deepDiveType = null;

function renderCurrentEmployee() {
    const container = document.getElementById("test-screen");
    container.innerHTML = "";
    const emp = TEST_EMPLOYEES[currentIndex];
    const card = document.createElement("div");
    card.className = "emp-card masked";
    const header = document.createElement("div");
    header.className = "emp-header";
    const avatar = document.createElement("div");
    avatar.className = "emp-avatar";
    avatar.textContent = "❓"; // masked avatar
    const info = document.createElement("div");
    info.className = "emp-info";
    const name = document.createElement("div");
    name.className = "emp-name";
    name.textContent = emp.name;
    const marker = document.createElement("div");
    marker.className = "emp-hint";
    marker.id = "marker";
    marker.textContent = emp.markers[0]; // first marker always shown
    const showMoreBtn = document.createElement("button");
    showMoreBtn.className = "btn-mini btn-info";
    showMoreBtn.textContent = "Показать ещё";
    showMoreBtn.onclick = () => {
        revealedCount++;
        if (revealedCount < emp.markers.length) {
            document.getElementById("marker").textContent = emp.markers[revealedCount];
        } else {
            // all markers revealed, show answer buttons
            showMoreBtn.style.display = "none";
            renderAnswerButtons(emp);
        }
    };
    header.appendChild(avatar);
    header.appendChild(info);
    info.appendChild(name);
    info.appendChild(marker);
    card.appendChild(header);
    card.appendChild(showMoreBtn);
    container.appendChild(card);
}

function renderAnswerButtons(emp) {
    const container = document.getElementById("test-screen");
    const btnContainer = document.createElement("div");
    btnContainer.className = "emp-actions";
    const types = ["BIRD", "HAMSTER", "FOX", "RAT", "PRO", "BETA"];
    types.forEach(t => {
        const btn = document.createElement("button");
        btn.className = "btn-mini btn-secondary";
        btn.textContent = t;
        btn.onclick = () => handleAnswer(t, emp);
        btnContainer.appendChild(btn);
    });
    container.appendChild(btnContainer);
}

function handleAnswer(selected, emp) {
    const container = document.getElementById("test-screen");
    const result = document.createElement("div");
    result.className = "emp-body";
    if (selected === emp.type) {
        result.innerHTML = `<p class="text-success">✅ Правильно! ${emp.explanation}</p>`;
    } else {
        result.innerHTML = `<p class="text-danger">❌ Неправильно. Правильный тип: ${emp.type}. ${emp.explanation}</p>`;
    }
    container.appendChild(result);
    const nextBtn = document.createElement("button");
    nextBtn.className = "btn btn-primary";
    nextBtn.textContent = deepDiveMode ? "Завершить" : "Следующий";
    nextBtn.onclick = () => {
        if (deepDiveMode) {
            // after deep‑dive we finish
            container.innerHTML = "<h2>Тест завершён. Спасибо!</h2>";
        } else {
            currentIndex++;
            if (currentIndex >= TEST_EMPLOYEES.length) {
                // offer deep‑dive
                offerDeepDive();
            } else {
                revealedCount = 0;
                renderCurrentEmployee();
            }
        }
    };
    container.appendChild(nextBtn);
}

function offerDeepDive() {
    const container = document.getElementById("test-screen");
    container.innerHTML = "";
    const msg = document.createElement("p");
    msg.textContent = "Хотите углубиться в один из типажей? Выберите тип:";
    container.appendChild(msg);
    const types = ["BIRD", "HAMSTER", "FOX", "RAT", "PRO", "BETA"];
    const btnContainer = document.createElement("div");
    btnContainer.className = "emp-actions";
    types.forEach(t => {
        const btn = document.createElement("button");
        btn.className = "btn-mini btn-info";
        btn.textContent = t;
        btn.onclick = () => startDeepDive(t);
        btnContainer.appendChild(btn);
    });
    container.appendChild(btnContainer);
}

function startDeepDive(type) {
    deepDiveMode = true;
    deepDiveType = type;
    // generate three extra employees of the chosen type (simple clones)
    const extra = [];
    for (let i = 1; i <= 3; i++) {
        extra.push({
            id: `${type.toLowerCase()}_deep_${i}`,
            type,
            name: `${type} (доп. ${i})`,
            markers: [
                `Маркер 1 для ${type}`,
                `Маркер 2 для ${type}`,
                `Маркер 3 для ${type}`
            ],
            explanation: `Подробное объяснение типажа ${type} из методологии «Теремок».`
        });
    }
    // replace TEST_EMPLOYEES with deep‑dive set and reset index
    TEST_EMPLOYEES.splice(0, TEST_EMPLOYEES.length, ...extra);
    currentIndex = 0;
    revealedCount = 0;
    renderCurrentEmployee();
}

// Initialize
window.onload = () => {
    renderCurrentEmployee();
};
