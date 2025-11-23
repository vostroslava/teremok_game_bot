// Telegram WebApp Integration
const tg = window.Telegram ? window.Telegram.WebApp : null;
if (tg) {
  tg.expand();
  tg.enableClosingConfirmation();
}

// --- CONFIG & DATA ---

const CONFIG = {
  START_BUDGET: 1000000, // 1M rub
  MANAGEMENT_POINTS_PER_TURN: 2,
  MAX_TURNS: 6, // 6 months to build the team
  CORE_SLOTS: 2,
  TEAM_SLOTS: 4,
};

const TYPES = {
  BIRD: {
    id: "BIRD",
    label: "Птица",
    icon: "🐦",
    desc: "Генератор идей. Нужна для новизны, но нестабильна.",
    revealHint: "«Мне скучно, давайте запустим что-то новое!»",
    impact: {
      core: { profit: -50000, stability: -20, msg: "Птица в Ядре: Хаос и потеря фокуса." },
      team: { profit: 150000, stability: -5, msg: "Птица в Команде: Генерирует отличные идеи." }
    }
  },
  HAMSTER: {
    id: "HAMSTER",
    label: "Хомяк",
    icon: "🐹",
    desc: "Исполнитель. Надежный тыл, но не лидер.",
    revealHint: "«Я всё сделал по инструкции. Что дальше?»",
    impact: {
      core: { profit: -20000, stability: 10, msg: "Хомяк в Ядре: Стагнация, нет развития." },
      team: { profit: 50000, stability: 10, msg: "Хомяк в Команде: Надежно закрывает тылы." }
    }
  },
  FOX: {
    id: "FOX",
    label: "Лиса",
    icon: "🦊",
    desc: "Коммерсант. Эффективна, но требует контроля.",
    revealHint: "«А какой у меня будет бонус с этой сделки?»",
    impact: {
      core: { profit: 100000, stability: -15, msg: "Лиса в Ядре: Тянет одеяло на себя, риски растут." },
      team: { profit: 200000, stability: -5, msg: "Лиса в Команде: Приносит отличную выручку." }
    }
  },
  RAT: {
    id: "RAT",
    label: "Крыса",
    icon: "🐀",
    desc: "Токсик. Разрушает систему изнутри.",
    revealHint: "«Это не моя вина, это они накосячили.»",
    impact: {
      core: { profit: -300000, stability: -40, msg: "Крыса в Ядре: Катастрофа! Токсичность убивает бизнес." },
      team: { profit: -50000, stability: -20, msg: "Крыса в Команде: Саботирует работу коллег." }
    }
  },
  PRO: {
    id: "PRO",
    label: "Профи",
    icon: "👔",
    desc: "Эксперт. Идеален для Ядра.",
    revealHint: "«Я проанализировал риски и предлагаю такое решение.»",
    impact: {
      core: { profit: 250000, stability: 20, msg: "Профи в Ядре: Системный подход дает результат." },
      team: { profit: 100000, stability: 10, msg: "Профи в Команде: Усиливает коллег." }
    }
  },
  BETA: {
    id: "BETA",
    label: "Бета",
    icon: "🅱️",
    desc: "Интегратор. Цемент системы.",
    revealHint: "«Я прослежу, чтобы все задачи были выполнены в срок.»",
    impact: {
      core: { profit: 200000, stability: 30, msg: "Бета в Ядре: Идеальный порядок и контроль." },
      team: { profit: 80000, stability: 15, msg: "Бета в Команде: Помогает держать строй." }
    }
  }
};

const NAMES = ["Александр", "Елена", "Дмитрий", "Ольга", "Максим", "Анна"];
const ROLES = ["Коммерческий директор", "РОП", "Маркетолог", "Key Account", "Менеджер", "Аналитик"];

// --- CLASSES ---

class Employee {
  constructor(id, typeId, name, role) {
    this.id = id;
    this.name = name;
    this.role = role;
    this.realType = TYPES[typeId];
    this.isRevealed = false;
    this.zone = "TEAM"; // 'CORE' or 'TEAM'
  }

  reveal() {
    this.isRevealed = true;
  }
}

class GameState {
  constructor() {
    this.budget = CONFIG.START_BUDGET;
    this.turn = 1;
    this.mp = CONFIG.MANAGEMENT_POINTS_PER_TURN; // Management Points
    this.employees = this.generateEmployees();
    this.logs = [];
    this.gameOver = false;
  }

  generateEmployees() {
    // Fixed set for balance: 1 Rat, 1 Fox, 1 Bird, 1 Hamster, 1 Pro, 1 Beta
    // But shuffled
    const types = ["RAT", "FOX", "BIRD", "HAMSTER", "PRO", "BETA"];
    // Shuffle types
    for (let i = types.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [types[i], types[j]] = [types[j], types[i]];
    }

    return types.map((typeId, idx) => {
      return new Employee(
        `emp_${idx}`,
        typeId,
        NAMES[idx],
        ROLES[idx]
      );
    });
  }

  addLog(msg, type = "info") {
    this.logs.unshift({ turn: this.turn, msg, type });
  }

  moveToZone(empId, zone) {
    const emp = this.employees.find(e => e.id === empId);
    if (!emp) return;

    // Check limits
    const coreCount = this.employees.filter(e => e.zone === "CORE").length;
    if (zone === "CORE" && coreCount >= CONFIG.CORE_SLOTS && emp.zone !== "CORE") {
      alert("В Ядре только 2 места!");
      return;
    }

    emp.zone = zone;
    renderDashboard();
  }

  investigate(empId) {
    if (this.mp <= 0) {
      alert("Нет очков управления!");
      return;
    }
    const emp = this.employees.find(e => e.id === empId);
    if (emp.isRevealed) return;

    this.mp--;
    emp.reveal();
    this.addLog(`Диагностика: ${emp.name} оказался типажом "${emp.realType.label}"`, "info");
    renderDashboard();
  }

  runMonth() {
    if (this.gameOver) return;

    let monthlyProfit = 0;
    let monthlyStability = 0;
    const report = [];

    // Calculate Impact
    this.employees.forEach(emp => {
      const impact = emp.zone === "CORE" ? emp.realType.impact.core : emp.realType.impact.team;
      monthlyProfit += impact.profit;
      monthlyStability += impact.stability;

      // Special logic: Rat in Core multiplies negativity
      if (emp.zone === "CORE" && emp.realType.id === "RAT") {
        monthlyProfit -= 200000; // Extra damage
        report.push(`☣️ ${emp.name} (Крыса) в Ядре уничтожает бизнес!`);
      }
    });

    // Core Synergy Bonus
    const core = this.employees.filter(e => e.zone === "CORE");
    const hasBeta = core.some(e => e.realType.id === "BETA");
    const hasPro = core.some(e => e.realType.id === "PRO");
    const hasAlpha = core.some(e => e.realType.id === "ALPHA"); // Not in current set but for future

    if (hasBeta && hasPro) {
      monthlyProfit += 100000;
      report.push("✅ Синергия Ядра: Бета + Профи работают идеально.");
    }

    this.budget += monthlyProfit;
    this.turn++;
    this.mp = CONFIG.MANAGEMENT_POINTS_PER_TURN; // Reset MP

    this.addLog(`Месяц ${this.turn - 1}: ${monthlyProfit > 0 ? '+' : ''}${monthlyProfit}₽`, monthlyProfit > 0 ? "success" : "error");
    report.forEach(r => this.addLog(r, "warning"));

    if (this.turn > CONFIG.MAX_TURNS || this.budget <= 0) {
      this.endGame();
    } else {
      renderDashboard();
    }
  }

  endGame() {
    this.gameOver = true;
    renderEndScreen();
  }
}

// --- UI RENDERING ---

const game = new GameState();
const screen = document.getElementById("screen");

function renderDashboard() {
  if (game.gameOver) return;

  screen.innerHTML = "";

  // 1. Header
  const header = document.createElement("div");
  header.className = "dashboard-header";
  header.innerHTML = `
    <div class="stat-box">
      <div class="stat-label">Бюджет</div>
      <div class="stat-value ${game.budget < 0 ? 'text-danger' : 'text-success'}">${game.budget.toLocaleString()}₽</div>
    </div>
    <div class="stat-box">
      <div class="stat-label">Месяц</div>
      <div class="stat-value">${game.turn} / ${CONFIG.MAX_TURNS}</div>
    </div>
    <div class="stat-box">
      <div class="stat-label">Очки Упр.</div>
      <div class="stat-value">${game.mp}</div>
    </div>
  `;
  screen.appendChild(header);

  // 2. The Core (Center)
  const coreZone = document.createElement("div");
  coreZone.className = "zone-container core-zone";
  coreZone.innerHTML = `<div class="zone-title">ЯДРО КОМАНДЫ (2 места)</div>`;

  const coreGrid = document.createElement("div");
  coreGrid.className = "zone-grid";

  // Render Core Slots
  game.employees.filter(e => e.zone === "CORE").forEach(emp => {
    coreGrid.appendChild(renderEmployeeCard(emp));
  });

  // Empty slots
  const coreCount = game.employees.filter(e => e.zone === "CORE").length;
  for (let i = 0; i < CONFIG.CORE_SLOTS - coreCount; i++) {
    const empty = document.createElement("div");
    empty.className = "card-placeholder";
    empty.textContent = "Перетащи сюда";
    coreGrid.appendChild(empty);
  }
  coreZone.appendChild(coreGrid);
  screen.appendChild(coreZone);

  // 3. The Team (Bottom)
  const teamZone = document.createElement("div");
  teamZone.className = "zone-container team-zone";
  teamZone.innerHTML = `<div class="zone-title">КОМАНДА (Орбита)</div>`;

  const teamGrid = document.createElement("div");
  teamGrid.className = "zone-grid";

  game.employees.filter(e => e.zone === "TEAM").forEach(emp => {
    teamGrid.appendChild(renderEmployeeCard(emp));
  });
  teamZone.appendChild(teamGrid);
  screen.appendChild(teamZone);

  // 4. Action Bar
  const actionBar = document.createElement("div");
  actionBar.className = "action-bar";

  const btnRun = document.createElement("button");
  btnRun.className = "btn btn-primary btn-lg";
  btnRun.textContent = `Запустить месяц ▶`;
  btnRun.onclick = () => game.runMonth();

  actionBar.appendChild(btnRun);
  screen.appendChild(actionBar);

  // 5. Logs
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

function renderEmployeeCard(emp) {
  const card = document.createElement("div");
  card.className = `emp-card ${emp.isRevealed ? 'revealed' : 'masked'} type-${emp.realType.id}`;

  // Header
  const header = document.createElement("div");
  header.className = "emp-header";
  header.innerHTML = `
    <div class="emp-avatar">${emp.isRevealed ? emp.realType.icon : '👤'}</div>
    <div class="emp-info">
      <div class="emp-name">${emp.name}</div>
      <div class="emp-role">${emp.role}</div>
    </div>
  `;
  card.appendChild(header);

  // Body
  const body = document.createElement("div");
  body.className = "emp-body";
  if (emp.isRevealed) {
    body.innerHTML = `<div class="emp-type-label">${emp.realType.label}</div><div class="emp-desc">${emp.realType.desc}</div>`;
  } else {
    body.innerHTML = `<div class="emp-hint">Типаж скрыт</div>`;
  }
  card.appendChild(body);

  // Actions
  const actions = document.createElement("div");
  actions.className = "emp-actions";

  // Investigate Button
  if (!emp.isRevealed) {
    const btnInvestigate = document.createElement("button");
    btnInvestigate.className = "btn-mini btn-info";
    btnInvestigate.textContent = "🔍 Проверить (1 MP)";
    btnInvestigate.onclick = (e) => { e.stopPropagation(); game.investigate(emp.id); };
    actions.appendChild(btnInvestigate);
  }

  // Move Button
  const btnMove = document.createElement("button");
  btnMove.className = "btn-mini btn-secondary";
  btnMove.textContent = emp.zone === "CORE" ? "⬇ В Команду" : "⬆ В Ядро";
  btnMove.onclick = (e) => {
    e.stopPropagation();
    game.moveToZone(emp.id, emp.zone === "CORE" ? "TEAM" : "CORE");
  };
  actions.appendChild(btnMove);

  card.appendChild(actions);
  return card;
}

function renderEndScreen() {
  screen.innerHTML = "";
  const card = document.createElement("div");
  card.className = "card center";

  const profit = game.budget - CONFIG.START_BUDGET;
  const isWin = profit > 0;

  card.innerHTML = `
    <h1>${isWin ? '🏆 Победа!' : '💀 Банкротство'}</h1>
    <p>Итоговый бюджет: <b>${game.budget.toLocaleString()}₽</b></p>
    <p>Прибыль: <span class="${isWin ? 'text-success' : 'text-danger'}">${profit.toLocaleString()}₽</span></p>
    <div style="margin: 1rem 0; text-align: left; font-size: 0.9rem; color: #ccc;">
      <h3>Разбор полетов:</h3>
      ${game.employees.map(e => `<div>${e.name}: <b>${e.realType.label}</b> (${e.zone === 'CORE' ? 'В Ядре' : 'В Команде'})</div>`).join('')}
    </div>
    <button class="btn btn-primary" onclick="location.reload()">Сыграть еще раз</button>
  `;
  screen.appendChild(card);
}

// Init
renderDashboard();
