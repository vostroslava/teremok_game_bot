// Telegram WebApp Integration
const tg = window.Telegram ? window.Telegram.WebApp : null;
if (tg) {
  tg.expand();
  tg.enableClosingConfirmation();
}

// --- CONFIG & DATA ---

const CONFIG = {
  START_MONEY: 5000,
  START_FLOW: 0,
  START_STABILITY: 100,
  SALARY_BASE: 100,
  REVENUE_PER_FLOW: 10,
  MAX_TEAM_SIZE: 6,
};

const TYPES = {
  BIRD: {
    id: "BIRD",
    label: "Птица",
    icon: "🐦",
    desc: "Генератор идей. Дает много Потока, но быстро выгорает и теряет Стабильность.",
    baseStats: { flow: 8, stability: 2, cost: 120 },
    effect: "Теряет 10% лояльности каждый ход, если нет «движухи»."
  },
  HAMSTER: {
    id: "HAMSTER",
    label: "Хомяк",
    icon: "🐹",
    desc: "Исполнитель. Стабильный, надежный, но мало Потока.",
    baseStats: { flow: 3, stability: 9, cost: 80 },
    effect: "Дает +5 к стабильности команды."
  },
  FOX: {
    id: "FOX",
    label: "Лиса",
    icon: "🦊",
    desc: "Коммерсант. Приносит деньги и связи, но тянет одеяло на себя.",
    baseStats: { flow: 6, stability: 4, cost: 150 },
    effect: "Требует премию каждые 3 хода, иначе ворует бюджет."
  },
  RAT: {
    id: "RAT",
    label: "Крыса",
    icon: "🐀",
    desc: "Токсик. Умный, но разрушает коллектив.",
    baseStats: { flow: 7, stability: 1, cost: 130 },
    effect: "Каждый ход снижает лояльность соседей на 5%."
  },
  PRO: {
    id: "PRO",
    label: "Профи",
    icon: "👔",
    desc: "Эксперт. Сбалансированный сотрудник.",
    baseStats: { flow: 5, stability: 7, cost: 200 },
    effect: "Нет негативных эффектов."
  },
  BEAR: {
    id: "BEAR",
    label: "Медведь",
    icon: "🐻",
    desc: "Опора. Очень стабильный, но сопротивляется новому.",
    baseStats: { flow: 2, stability: 10, cost: 180 },
    effect: "Блокирует потерю стабильности, но снижает общий Поток на 10%."
  },
  ALPHA: {
    id: "ALPHA",
    label: "Альфа",
    icon: "🅰️",
    desc: "Лидер. Бустит команду, но стоит дорого.",
    baseStats: { flow: 9, stability: 8, cost: 300 },
    effect: "Увеличивает Поток всех остальных на 20%."
  },
  BETA: {
    id: "BETA",
    label: "Бета",
    icon: "🅱️",
    desc: "Интегратор. Связывает команду.",
    baseStats: { flow: 5, stability: 9, cost: 250 },
    effect: "Гасит негативные эффекты Крыс и Лис."
  }
};

const NAMES = [
  "Александр", "Елена", "Дмитрий", "Ольга", "Максим", "Анна",
  "Сергей", "Мария", "Иван", "Наталья", "Андрей", "Екатерина",
  "Артем", "Юлия", "Никита", "Дарья", "Кирилл", "Алиса"
];

const ROLES = [
  "Менеджер", "Аналитик", "Разработчик", "Маркетолог", "Дизайнер", "Бухгалтер"
];

// --- CLASSES ---

class Employee {
  constructor(typeId) {
    const type = TYPES[typeId];
    this.id = Math.random().toString(36).substr(2, 9);
    this.name = NAMES[Math.floor(Math.random() * NAMES.length)];
    this.role = ROLES[Math.floor(Math.random() * ROLES.length)];
    this.type = type;

    // Stats (0-100)
    this.flow = type.baseStats.flow * 10 + Math.floor(Math.random() * 20 - 10);
    this.stability = type.baseStats.stability * 10 + Math.floor(Math.random() * 20 - 10);
    this.loyalty = 80; // Starts high
    this.stress = 0;   // Starts low

    this.salary = type.baseStats.cost;
    this.isRevealed = false; // Type is hidden initially? Let's make it visible for now for strategy depth
  }
}

class GameState {
  constructor() {
    this.money = CONFIG.START_MONEY;
    this.turn = 1;
    this.team = [];
    this.candidates = [];
    this.logs = []; // Event logs
    this.gameOver = false;
  }

  addLog(msg, type = "info") {
    this.logs.unshift({ turn: this.turn, msg, type });
    if (this.logs.length > 20) this.logs.pop();
  }

  // Core Metrics Calculation
  get totalFlow() {
    let flow = this.team.reduce((acc, e) => acc + e.flow, 0);
    // Apply Modifiers
    if (this.team.some(e => e.type.id === "BEAR")) flow *= 0.9;
    if (this.team.some(e => e.type.id === "ALPHA")) flow *= 1.2;
    return Math.floor(flow);
  }

  get totalStability() {
    if (this.team.length === 0) return CONFIG.START_STABILITY;
    let stab = this.team.reduce((acc, e) => acc + e.stability, 0) / this.team.length;
    // Hamster Bonus
    const hamsters = this.team.filter(e => e.type.id === "HAMSTER").length;
    stab += hamsters * 5;
    return Math.floor(Math.min(100, Math.max(0, stab)));
  }

  get totalExpenses() {
    return this.team.reduce((acc, e) => acc + e.salary, 0);
  }

  generateCandidates(count = 3) {
    this.candidates = [];
    const typeKeys = Object.keys(TYPES);
    for (let i = 0; i < count; i++) {
      const randomType = typeKeys[Math.floor(Math.random() * typeKeys.length)];
      this.candidates.push(new Employee(randomType));
    }
  }

  hire(candidateId) {
    if (this.team.length >= CONFIG.MAX_TEAM_SIZE) {
      this.addLog("Офис переполнен! Сначала увольте кого-нибудь.", "error");
      return false;
    }
    const candidateIndex = this.candidates.findIndex(c => c.id === candidateId);
    if (candidateIndex === -1) return false;

    const candidate = this.candidates[candidateIndex];
    if (this.money < candidate.salary) {
      this.addLog("Не хватает денег на найм!", "error");
      return false;
    }

    this.money -= candidate.salary; // Hiring bonus/cost
    this.team.push(candidate);
    this.candidates.splice(candidateIndex, 1);
    this.addLog(`Нанят ${candidate.name} (${candidate.type.label})`, "success");
    return true;
  }

  fire(employeeId) {
    const idx = this.team.findIndex(e => e.id === employeeId);
    if (idx === -1) return;

    const emp = this.team[idx];
    const severance = emp.salary * 2; // Severance pay
    this.money -= severance;
    this.team.splice(idx, 1);
    this.addLog(`Уволен ${emp.name}. Выплачено выходное пособие ${severance}`, "warning");
  }

  nextTurn() {
    this.turn++;

    // 1. Financials
    const revenue = this.totalFlow * CONFIG.REVENUE_PER_FLOW;
    const expenses = this.totalExpenses;
    const profit = revenue - expenses;

    this.money += profit;
    this.addLog(`Месяц ${this.turn}: Доход ${revenue} - Расход ${expenses} = ${profit > 0 ? '+' : ''}${profit}`, profit > 0 ? "success" : "error");

    // 2. Effects & Events
    this.processEffects();
    if (Math.random() < 0.3) this.triggerRandomEvent();

    // 3. Check Game Over
    if (this.money < 0) {
      this.gameOver = true;
      this.addLog("Банкротство! Игра окончена.", "error");
    }

    // 4. Refresh Candidates
    this.generateCandidates();
  }

  triggerRandomEvent() {
    const events = [
      {
        name: "Рынок растет",
        msg: "Спрос на услуги вырос! Доход увеличен.",
        effect: () => { this.money += 500; }
      },
      {
        name: "Кризис",
        msg: "Клиенты урезают бюджеты. Вы потеряли 300$.",
        effect: () => { this.money -= 300; }
      },
      {
        name: "Хедхантеры",
        msg: "Конкуренты пытаются переманить сотрудников.",
        effect: () => {
          if (this.team.length > 0) {
            const target = this.team[Math.floor(Math.random() * this.team.length)];
            target.loyalty -= 20;
            this.addLog(`${target.name} получил оффер от конкурентов (-20 лояльности).`, "warning");
          }
        }
      },
      {
        name: "Тимбилдинг",
        msg: "Команда сходила в бар. Стабильность выросла.",
        effect: () => {
          this.team.forEach(e => { e.stress = Math.max(0, e.stress - 10); });
        }
      }
    ];

    const event = events[Math.floor(Math.random() * events.length)];
    event.effect();
    this.addLog(`СОБЫТИЕ: ${event.name}. ${event.msg}`, "info");
  }

  processEffects() {
    // Rat Effect
    const rats = this.team.filter(e => e.type.id === "RAT");
    const betas = this.team.filter(e => e.type.id === "BETA");

    if (rats.length > 0 && betas.length === 0) {
      this.team.forEach(e => {
        if (e.type.id !== "RAT") {
          e.loyalty -= 5 * rats.length;
          e.stress += 5;
        }
      });
      this.addLog("Крысы отравляют атмосферу! Лояльность падает.", "warning");
    }

    // Bird Effect
    this.team.forEach(e => {
      if (e.type.id === "BIRD") {
        e.loyalty -= 5; // Birds get bored
        if (Math.random() < 0.1) {
          this.addLog(`${e.name} (Птица) скучает и хочет уволиться.`, "warning");
        }
      }
    });

    // Fox Effect
    this.team.forEach(e => {
      if (e.type.id === "FOX" && this.turn % 3 === 0) {
        const bonus = Math.floor(e.salary * 0.5);
        if (this.money >= bonus) {
          this.money -= bonus;
          this.addLog(`${e.name} (Лиса) выбила себе премию ${bonus}.`, "info");
        } else {
          e.loyalty -= 20;
          this.addLog(`${e.name} (Лиса) не получила премию и злится.`, "warning");
        }
      }
    });
  }
}

// --- UI RENDERING ---

const game = new GameState();
const screen = document.getElementById("screen");

function renderDashboard() {
  if (game.gameOver) {
    renderGameOver();
    return;
  }

  screen.innerHTML = "";

  // 1. Header Stats
  const header = document.createElement("div");
  header.className = "dashboard-header";
  header.innerHTML = `
    <div class="stat-box">
      <div class="stat-label">Деньги</div>
      <div class="stat-value ${game.money < 0 ? 'text-danger' : ''}">${game.money}</div>
    </div>
    <div class="stat-box">
      <div class="stat-label">Поток</div>
      <div class="stat-value">${game.totalFlow}</div>
    </div>
    <div class="stat-box">
      <div class="stat-label">Стабильность</div>
      <div class="stat-value">${game.totalStability}%</div>
    </div>
    <div class="stat-box">
      <div class="stat-label">Месяц</div>
      <div class="stat-value">${game.turn}</div>
    </div>
  `;
  screen.appendChild(header);

  // 2. Office Grid (Team)
  const office = document.createElement("div");
  office.className = "office-grid";

  // Render Slots
  for (let i = 0; i < CONFIG.MAX_TEAM_SIZE; i++) {
    const emp = game.team[i];
    const slot = document.createElement("div");
    slot.className = "office-slot " + (emp ? "occupied" : "empty");

    if (emp) {
      slot.innerHTML = `
        <div class="emp-icon">${emp.type.icon}</div>
        <div class="emp-name">${emp.name}</div>
        <div class="emp-role">${emp.role}</div>
        <div class="emp-stats">
          <div class="emp-stat-row"><span>Loyalty</span><div class="bar"><div class="fill" style="width:${emp.loyalty}%"></div></div></div>
          <div class="emp-stat-row"><span>Stress</span><div class="bar"><div class="fill error" style="width:${emp.stress}%"></div></div></div>
        </div>
        <button class="btn-mini danger" onclick="handleFire('${emp.id}')">Уволить</button>
      `;
    } else {
      slot.innerHTML = `<div class="empty-label">Пусто</div>`;
    }
    office.appendChild(slot);
  }
  screen.appendChild(office);

  // 3. Action Area (Hiring & Next Turn)
  const actions = document.createElement("div");
  actions.className = "action-area";

  const btnHire = document.createElement("button");
  btnHire.className = "btn btn-primary";
  btnHire.textContent = "Нанять сотрудника";
  btnHire.onclick = renderHiringScreen;

  const btnNext = document.createElement("button");
  btnNext.className = "btn btn-secondary";
  btnNext.textContent = "Следующий месяц";
  btnNext.onclick = () => {
    game.nextTurn();
    renderDashboard();
  };

  actions.appendChild(btnHire);
  actions.appendChild(btnNext);
  screen.appendChild(actions);

  // 4. Logs
  const logContainer = document.createElement("div");
  logContainer.className = "log-container";
  game.logs.forEach(log => {
    const line = document.createElement("div");
    line.className = `log-line log-${log.type}`;
    line.textContent = `[Мес ${log.turn}] ${log.msg}`;
    logContainer.appendChild(line);
  });
  screen.appendChild(logContainer);
}

function renderHiringScreen() {
  screen.innerHTML = "";

  const title = document.createElement("h2");
  title.className = "page-title";
  title.textContent = "Биржа труда";
  screen.appendChild(title);

  const grid = document.createElement("div");
  grid.className = "hiring-grid";

  if (game.candidates.length === 0) {
    game.generateCandidates();
  }

  game.candidates.forEach(cand => {
    const card = document.createElement("div");
    card.className = "candidate-card";
    card.innerHTML = `
      <div class="cand-header">
        <span class="cand-icon">${cand.type.icon}</span>
        <span class="cand-type">${cand.type.label}</span>
      </div>
      <div class="cand-name">${cand.name}</div>
      <div class="cand-role">${cand.role}</div>
      <div class="cand-desc">${cand.type.desc}</div>
      <div class="cand-stats">
        <div>Поток: ${cand.flow}</div>
        <div>Стаб: ${cand.stability}</div>
      </div>
      <div class="cand-cost">Зарплата: ${cand.salary}$</div>
      <button class="btn btn-sm btn-primary" onclick="handleHire('${cand.id}')">Нанять</button>
    `;
    grid.appendChild(card);
  });

  screen.appendChild(grid);

  const btnBack = document.createElement("button");
  btnBack.className = "btn btn-secondary";
  btnBack.style.marginTop = "1rem";
  btnBack.textContent = "Назад в офис";
  btnBack.onclick = renderDashboard;
  screen.appendChild(btnBack);
}

function renderGameOver() {
  screen.innerHTML = "";
  const card = document.createElement("div");
  card.className = "card center";
  card.innerHTML = `
    <h1>Игра окончена</h1>
    <p>Вы продержались ${game.turn} месяцев.</p>
    <button class="btn btn-primary" onclick="location.reload()">Начать заново</button>
  `;
  screen.appendChild(card);
}

// --- HANDLERS ---

window.handleHire = (id) => {
  if (game.hire(id)) {
    renderDashboard();
  } else {
    // If failed, maybe show alert? For now logs handle it.
    renderDashboard(); // Refresh to show log
  }
};

window.handleFire = (id) => {
  if (confirm("Уволить сотрудника? Это будет стоить 2 оклада.")) {
    game.fire(id);
    renderDashboard();
  }
};

// --- INIT ---
game.generateCandidates();
renderDashboard();
