// Telegram WebApp Integration
const tg = window.Telegram ? window.Telegram.WebApp : null;
if (tg) {
  tg.expand();
  tg.enableClosingConfirmation();
}

// Data: Types
const TYPES = {
  BIRD: { label: "🐦 Птица", icon: "🐦" },
  HAMSTER: { label: "🐹 Хомяк", icon: "🐹" },
  FOX: { label: "🦊 Лиса", icon: "🦊" },
  RAT: { label: "🐀 Крыса", icon: "🐀" },
  PRO: { label: "👔 Профи", icon: "👔" },
  BEAR: { label: "🐻 Медведь", icon: "🐻" },
  ALPHA: { label: "🅰️ Альфа", icon: "🅰️" },
  BETA: { label: "🅱️ Бета", icon: "🅱️" },
};

// Data: Characters (6 people)
const CHARACTERS = [
  {
    id: "mikhail",
    name: "Михаил",
    role: "собственник компании",
    correct_type: "BEAR",
    description:
      "Основатель. Ценит стабильность и надёжных людей. Осторожен к новым идеям, долго принимает решения. Если встал за кого-то горой — это навсегда.",
    explanation:
      "Классический Медведь: опора на опыт, осторожность к переменам, ценит лояльность и «своих»."
  },
  {
    id: "natalia",
    name: "Наталья",
    role: "генеральный директор",
    correct_type: "ALPHA",
    description:
      "Лицо компании. Вдохновляет команду, говорит о ценностях и миссии. Не любит микроменеджмент. Готова на жёсткие решения ради идеи.",
    explanation:
      "Альфа-лидер: работает через смыслы и ценности, зажигает людей, задаёт вектор."
  },
  {
    id: "sergey",
    name: "Сергей",
    role: "руководитель отдела продаж",
    correct_type: "BETA",
    description:
      "Проводник между верхом и низом. Переводит идеи в задачи. Чувствует людей, защищает команду, но и спрашивает строго. Часто перегружен.",
    explanation:
      "Бета-лидер: держит процессы, балансирует интересы, переводит стратегию в тактику."
  },
  {
    id: "katya",
    name: "Катя",
    role: "менеджер по продажам",
    correct_type: "BIRD",
    description:
      "Быстро загорается новым: акции, ивенты, движ. Если начинается рутина — скучает и смотрит по сторонам. Ценит свободу и внимание.",
    explanation:
      "Птица: тяга к новизне, быстрый старт, быстрое выгорание от рутины."
  },
  {
    id: "marina",
    name: "Марина",
    role: "аккаунт-менеджер",
    correct_type: "FOX",
    description:
      "Обаятельна, легко ладит с VIP-клиентами. Любит статусные встречи и мероприятия. Ищет, где выгоднее и перспективнее лично для неё.",
    explanation:
      "Лиса: ориентация на статус, выгоду и социальные связи. Важно быть «в центре»."
  },
  {
    id: "anton",
    name: "Антон",
    role: "топ-менеджер по продажам",
    correct_type: "RAT",
    description:
      "Делает большую выручку и кичится этим. В курилке ругает руководство. Может шантажировать уходом, если что-то не по его.",
    explanation:
      "Крыса: сильный результат, но игра против правил. Использует успех для шантажа."
  }
];

// Data: Scenes
const SCENES = [
  {
    id: "TEAM_LEAD",
    title: "Сцена 1. Лицо отдела",
    description:
      "Продажи растут. Нужно выбрать, кто станет «лицом» отдела продаж и внутренним лидером. На кого будут равняться остальные?",
    question: "Кого назначишь?",
    options: [
      {
        code: "SERGEY",
        label: "Сергей (Бета-лидер)",
        d_money: 10,
        d_engagement: 10,
        d_risk: -5,
        comment:
          "Бета-лидер устойчиво тянет процессы и держит баланс. Хороший выбор для стабильности."
      },
      {
        code: "ANTON",
        label: "Антон (Крыса)",
        d_money: 15,
        d_engagement: -20,
        d_risk: 20,
        comment:
          "Крыса усиливает токсичность. Результат есть, но команда чувствует несправедливость."
      },
      {
        code: "MARINA",
        label: "Марина (Лиса)",
        d_money: 5,
        d_engagement: 5,
        d_risk: 5,
        comment:
          "Лиса хороша с клиентами, но может тянуть одеяло на себя без сильного контроля."
      },
      {
        code: "KATYA",
        label: "Катя (Птица)",
        d_money: 0,
        d_engagement: -10,
        d_risk: 10,
        comment:
          "Птица даёт эмоции, но не системность. Команде не хватает опоры."
      }
    ]
  },
  {
    id: "BONUSES",
    title: "Сцена 2. Премия",
    description:
      "Успешный квартал! Как распределить бонусный фонд? Это сигнал команде о том, что ты ценишь.",
    question: "Твоё решение?",
    options: [
      {
        code: "EQUAL",
        label: "Всем поровну",
        d_money: -10,
        d_engagement: 5,
        d_risk: 5,
        comment:
          "Хомяки рады, но сильные игроки демотивированы уравниловкой."
      },
      {
        code: "TOP3",
        label: "Только Топ-3",
        d_money: 15,
        d_engagement: -10,
        d_risk: 15,
        comment:
          "Гонка за результатом. Лисы довольны, остальные чувствуют себя за бортом."
      },
      {
        code: "CORE_PLUS",
        label: "База всем + Бонус ядру",
        d_money: -5,
        d_engagement: 15,
        d_risk: -5,
        comment:
          "Справедливо и укрепляет ядро команды. Лучший баланс."
      }
    ]
  },
  {
    id: "RAT_CRISIS",
    title: "Сцена 3. Шантаж",
    description:
      "Антон (Крыса) шантажирует уходом, требуя особых условий. Он делает кассу, но токсичен.",
    question: "Что делать?",
    options: [
      {
        code: "IGNORE",
        label: "Уступить (ради денег)",
        d_money: 10,
        d_engagement: -20,
        d_risk: 25,
        comment:
          "Ты показал, что токсичность окупается. Ядро команды начинает выгорать."
      },
      {
        code: "FRAME",
        label: "Жёсткие рамки",
        d_money: -5,
        d_engagement: 5,
        d_risk: -10,
        comment:
          "Попытка сохранить и деньги, и правила. Сработает временно."
      },
      {
        code: "FAREWELL",
        label: "Уволить",
        d_money: -15,
        d_engagement: 20,
        d_risk: -20,
        comment:
          "Больно краткосрочно, но спасает систему. Команда видит силу лидера."
      }
    ]
  }
];

// State
const state = {
  mode: "QUIZ", // 'QUIZ' or 'SIMULATION'
  quizIndex: 0,
  quizScore: 0,
  currentScene: 0,
  money: 100,
  engagement: 70,
  risk: 20,
  decisions: []
};

const screen = document.getElementById("screen");

// Utils
function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function formatDelta(x) {
  return x >= 0 ? "+" + x : x.toString();
}

// --- QUIZ LOGIC ---

function renderQuiz() {
  if (state.quizIndex >= CHARACTERS.length) {
    startSimulation();
    return;
  }

  const char = CHARACTERS[state.quizIndex];
  screen.innerHTML = "";

  const card = document.createElement("div");
  card.className = "card";

  const title = document.createElement("h2");
  title.className = "card-title";
  title.textContent = `${char.name} — ${char.role}`;

  const text = document.createElement("p");
  text.className = "card-text";
  text.textContent = char.description;

  const question = document.createElement("p");
  question.className = "card-text";
  question.style.fontWeight = "600";
  question.style.marginTop = "1rem";
  question.textContent = "Кто это по типажу?";

  const grid = document.createElement("div");
  grid.className = "quiz-grid";

  Object.entries(TYPES).forEach(([code, type]) => {
    const btn = document.createElement("button");
    btn.className = "quiz-btn";
    btn.innerHTML = `<span class="quiz-btn-icon">${type.icon}</span><span>${type.label}</span>`;
    btn.onclick = () => handleQuizAnswer(code);
    grid.appendChild(btn);
  });

  card.appendChild(title);
  card.appendChild(text);
  card.appendChild(question);
  card.appendChild(grid);
  screen.appendChild(card);
}

function handleQuizAnswer(selectedCode) {
  const char = CHARACTERS[state.quizIndex];
  const isCorrect = selectedCode === char.correct_type;

  if (isCorrect) {
    state.quizScore++;
    showFeedback(true, char);
  } else {
    showFeedback(false, char, selectedCode);
  }
}

function showFeedback(isCorrect, char, selectedCode = null) {
  const overlay = document.createElement("div");
  overlay.className = "modal-overlay active";

  const card = document.createElement("div");
  card.className = "modal-card";

  const icon = document.createElement("div");
  icon.className = "feedback-icon";
  icon.textContent = isCorrect ? "✅" : "❌";

  const title = document.createElement("div");
  title.className = "feedback-title";
  title.textContent = isCorrect ? "Верно!" : "Ошибка";

  const text = document.createElement("div");
  text.className = "feedback-text";

  if (isCorrect) {
    text.textContent = char.explanation;
  } else {
    const correctLabel = TYPES[char.correct_type].label;
    text.innerHTML = `Правильный ответ: <b>${correctLabel}</b>.<br><br>${char.explanation}`;
  }

  const btn = document.createElement("button");
  btn.className = "btn-feedback";
  btn.textContent = "Далее";
  btn.onclick = () => {
    document.body.removeChild(overlay);
    state.quizIndex++;
    renderQuiz();
  };

  card.appendChild(icon);
  card.appendChild(title);
  card.appendChild(text);
  card.appendChild(btn);
  overlay.appendChild(card);
  document.body.appendChild(overlay);
}

// --- SIMULATION LOGIC ---

function startSimulation() {
  state.mode = "SIMULATION";
  renderSimulationIntro();
}

function renderSimulationIntro() {
  screen.innerHTML = "";

  const card = document.createElement("div");
  card.className = "card";

  const title = document.createElement("h2");
  title.className = "card-title";
  title.textContent = "Часть 2. Управление";

  const text = document.createElement("p");
  text.className = "card-text";
  text.textContent =
    `Ты верно определил ${state.quizScore} из ${CHARACTERS.length} сотрудников.\n\n` +
    "Теперь переходим к практике. Тебе предстоит принять 3 сложных решения. " +
    "Следи за показателями: деньги, вовлечённость и риск.";

  const btnStart = document.createElement("button");
  btnStart.className = "btn btn-primary";
  btnStart.textContent = "Начать симуляцию";
  btnStart.onclick = () => {
    renderCurrentScene();
  };

  card.appendChild(title);
  card.appendChild(text);
  card.appendChild(btnStart);
  screen.appendChild(card);
}

function renderMetrics(container) {
  const metrics = document.createElement("div");
  metrics.className = "metrics";

  function addMetric(label, value, min, max, isRisk = false) {
    const row = document.createElement("div");
    row.className = "metric-row";

    const labelEl = document.createElement("span");
    labelEl.textContent = label;

    const valueEl = document.createElement("span");
    valueEl.className = "metric-value";
    valueEl.textContent = value;

    row.appendChild(labelEl);
    row.appendChild(valueEl);
    metrics.appendChild(row);

    const bar = document.createElement("div");
    bar.className = "metric-bar";

    const fill = document.createElement("div");
    fill.className = "metric-bar-fill";

    const percent = ((value - min) / (max - min)) * 100;
    fill.style.width = clamp(percent, 0, 100) + "%";

    if (isRisk) {
      fill.style.background = "linear-gradient(90deg, #22c55e, #ef4444)";
    }

    bar.appendChild(fill);
    metrics.appendChild(bar);
  }

  addMetric("💰 Деньги", state.money, 0, 200);
  addMetric("🔥 Вовлечённость", state.engagement, 0, 120);
  addMetric("⚠️ Риск", state.risk, 0, 120, true);

  container.appendChild(metrics);
}

function renderCurrentScene() {
  if (state.currentScene >= SCENES.length) {
    renderSummary();
    return;
  }

  const scene = SCENES[state.currentScene];
  screen.innerHTML = "";

  const card = document.createElement("div");
  card.className = "card";

  const title = document.createElement("h2");
  title.className = "card-title";
  title.textContent = scene.title;

  const text = document.createElement("p");
  text.className = "card-text";
  text.textContent = scene.description;

  const question = document.createElement("p");
  question.className = "card-text";
  question.style.fontWeight = "600";
  question.textContent = scene.question;

  card.appendChild(title);
  card.appendChild(text);
  card.appendChild(question);

  renderMetrics(card);

  const buttons = document.createElement("div");
  buttons.className = "buttons";

  scene.options.forEach((opt, idx) => {
    const btn = document.createElement("button");
    btn.className = "btn";
    btn.innerHTML = `<span>${opt.label}</span><span class="chevron">›</span>`;
    btn.onclick = () => handleOptionClick(idx);
    buttons.appendChild(btn);
  });

  card.appendChild(buttons);
  screen.appendChild(card);
}

function handleOptionClick(optionIndex) {
  const scene = SCENES[state.currentScene];
  const opt = scene.options[optionIndex];

  state.money = clamp(state.money + opt.d_money, 0, 200);
  state.engagement = clamp(state.engagement + opt.d_engagement, 0, 120);
  state.risk = clamp(state.risk + opt.d_risk, 0, 120);

  state.decisions.push({
    sceneTitle: scene.title,
    optionLabel: opt.label,
    d_money: opt.d_money,
    d_engagement: opt.d_engagement,
    d_risk: opt.d_risk,
    comment: opt.comment
  });

  state.currentScene++;
  renderCurrentScene();
}

function renderSummary() {
  screen.innerHTML = "";

  const card = document.createElement("div");
  card.className = "card";

  const title = document.createElement("h2");
  title.className = "card-title";
  title.textContent = "Итоги";

  renderMetrics(card);

  const list = document.createElement("div");
  list.style.marginTop = "1rem";

  state.decisions.forEach(d => {
    const item = document.createElement("div");
    item.style.marginBottom = "1rem";
    item.style.paddingBottom = "1rem";
    item.style.borderBottom = "1px solid rgba(255,255,255,0.1)";

    item.innerHTML = `
      <div style="font-weight:600; margin-bottom:0.25rem">${d.sceneTitle}</div>
      <div style="color:var(--text-muted); font-size:0.9rem; margin-bottom:0.5rem">Выбор: ${d.optionLabel}</div>
      <div style="font-size:0.85rem; color:#e2e8f0">${d.comment}</div>
      <div style="font-size:0.8rem; margin-top:0.25rem; opacity:0.7">
        💰${formatDelta(d.d_money)} 🔥${formatDelta(d.d_engagement)} ⚠️${formatDelta(d.d_risk)}
      </div>
    `;
    list.appendChild(item);
  });

  const btnRestart = document.createElement("button");
  btnRestart.className = "btn btn-primary";
  btnRestart.style.marginTop = "1rem";
  btnRestart.textContent = "Сыграть ещё раз";
  btnRestart.onclick = renderStartScreen;

  card.appendChild(list);
  card.appendChild(btnRestart);
  screen.appendChild(card);
}

function renderStartScreen() {
  // Reset all state
  state.mode = "QUIZ";
  state.quizIndex = 0;
  state.quizScore = 0;
  state.currentScene = 0;
  state.money = 100;
  state.engagement = 70;
  state.risk = 20;
  state.decisions = [];

  screen.innerHTML = "";

  const card = document.createElement("div");
  card.className = "card";

  const title = document.createElement("h2");
  title.className = "card-title";
  title.textContent = "Теремок";

  const text = document.createElement("p");
  text.className = "card-text";
  text.textContent =
    "Добро пожаловать в симулятор.\n\n" +
    "Часть 1: Определи типажи сотрудников.\n" +
    "Часть 2: Прими управленческие решения.";

  const btnStart = document.createElement("button");
  btnStart.className = "btn btn-primary";
  btnStart.textContent = "Начать";
  btnStart.onclick = () => {
    renderQuiz();
  };

  card.appendChild(title);
  card.appendChild(text);
  card.appendChild(btnStart);
  screen.appendChild(card);
}

// Init
renderStartScreen();
