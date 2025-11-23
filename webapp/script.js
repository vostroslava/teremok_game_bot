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
  PRO: { label: "👔 Профессионал", icon: "👔" },
  BEAR: { label: "🐻 Медведь", icon: "🐻" },
  ALPHA: { label: "🅰️ Альфа-лидер", icon: "🅰️" },
  BETA: { label: "🅱️ Бета-лидер", icon: "🅱️" },
};

// Data: Characters (6 people)
const CHARACTERS = [
  {
    id: "mikhail",
    name: "Михаил",
    role: "собственник компании",
    correct_type: "BEAR",
    description:
      "Михаил — основатель компании. Он опытный, устойчивый, но иногда кажется «тяжелым» человеком. В принятии решений опирается на прошлый опыт и традиции. Считает себя исключением из правил: «Правила для вас, а я — Медведь».",
    explanation:
      "Классический Медведь: опирается на прошлый опыт, устойчив, но может тормозить инновации. Часто это собственники, которые «выросли» из бизнеса, но не хотят менять подходы."
  },
  {
    id: "natalia",
    name: "Наталья",
    role: "генеральный директор (CEO)",
    correct_type: "ALPHA",
    description:
      "Наталья — вдохновитель. Она задает идею, миссию и ценности компании. Люди идут за ней, потому что верят в её видение. Она собирает команду вокруг Смысла.",
    explanation:
      "Альфа-лидер: человек, преданный Идее. Он создает смыслы и ведет за собой. Это «архитектор» бизнеса."
  },
  {
    id: "sergey",
    name: "Сергей",
    role: "коммерческий директор",
    correct_type: "BETA",
    description:
      "Сергей — надежный тыл Натальи. Он держит процессы, контролирует выполнение задач. Предан лично лидеру (Наталье). Переводит идеи в конкретные действия и цифры.",
    explanation:
      "Бета-лидер: человек, преданный Боссу (Лидеру). Он — «руки» управления, обеспечивает реализацию идей Альфы."
  },
  {
    id: "katya",
    name: "Катя",
    role: "менеджер по продажам (новичок)",
    correct_type: "BIRD",
    description:
      "Катя — легкая на подъем, веселая, но живет одним днем. Ей важны новые впечатления. Легко загорается идеей, но так же легко остывает. Если станет скучно или трудно — может упорхнуть в другую компанию.",
    explanation:
      "Птица: живет впечатлениями, новизной. Мотивация неустойчивая. Нуждается в постоянном внимании и «подрезании крыльев» (фиксации ответственности)."
  },
  {
    id: "marina",
    name: "Марина",
    role: "ведущий менеджер (Key Account)",
    correct_type: "FOX",
    description:
      "Марина — звезда отдела. Она ориентирована на личную выгоду, статус и возможности. Отличные социальные навыки, умеет договориться с кем угодно. Всегда спрашивает: «А что мне за это будет?».",
    explanation:
      "Лиса: ориентирована на личную выгоду и статус. Может быть очень эффективной, если её цели совпадают с целями компании, но требует контроля."
  },
  {
    id: "anton",
    name: "Антон",
    role: "старший менеджер",
    correct_type: "RAT",
    description:
      "Антон — умный, но токсичный сотрудник. Использует свое влияние и результаты, чтобы манипулировать коллегами и играть против правил системы. «Серый кардинал» в негативном смысле.",
    explanation:
      "Крыса: Лиса, ушедшая в «токсик». Использует ресурсы компании для личных игр против системы. Опасный тип, разрушающий коллектив."
  }
];

// Data: Scenes
const SCENES = [
  {
    id: "TEAM_LEAD",
    title: "Сцена 1. Лицо отдела",
    description:
      "Продажи растут, и собственник с директором решают: нужно чётко обозначить, кто будет «лицом» отдела продаж и внутренним лидером. От этого решения зависит, на кого начнут равняться остальные.",
    question: "Кого выберешь опорным лидером отдела продаж?",
    options: [
      {
        code: "SERGEY",
        label: "Назначить Сергея официальным лидером отдела",
        d_money: 10,
        d_engagement: 10,
        d_risk: -5,
        comment:
          "Бета-лидер в роли лидера отдела устойчиво тянет процессы, держит баланс интересов и снимает часть нагрузки с собственника и директора."
      },
      {
        code: "ANTON",
        label: "Фактически сделать Антона главным по продажам",
        d_money: 15,
        d_engagement: -20,
        d_risk: 20,
        comment:
          "Крыса в позиции неформального лидера усиливает токсичность: появляется ощущение, что правила для всех разные, а результат оправдывает поведение."
      },
      {
        code: "MARINA",
        label: "Сделать Марину ведущим менеджером по ключевым клиентам",
        d_money: 5,
        d_engagement: 5,
        d_risk: 5,
        comment:
          "Лиса-аккаунт хорошо держит ключевых клиентов и тянет статусные задачи, но при отсутствии сильного Бета-лидера может начать тянуть одеяло на себя."
      },
      {
        code: "KATYA",
        label: "Поставить Катю в формальные лидеры, чтобы «было больше движухи»",
        d_money: 0,
        d_engagement: -10,
        d_risk: 10,
        comment:
          "Птица в роли формального лидера даёт много энтузиазма, но мало устойчивости. Хомяки и ядро начинают чувствовать нестабильность и хаос."
      }
    ]
  },
  {
    id: "BONUSES",
    title: "Сцена 2. Премия",
    description:
      "Успешный квартал! Как распределить бонусный фонд? Это сигнал команде о том, что ты ценишь. От того, как ты сейчас распределишь деньги, зависит, какие типажи будут считать систему справедливой.",
    question: "Как распределишь премию?",
    options: [
      {
        code: "EQUAL",
        label: "Равномерно всем по отделу",
        d_money: -10,
        d_engagement: 5,
        d_risk: 5,
        comment:
          "Хомяки довольны: всем поровну и предсказуемо. Но сильные Лисы и Птицы видят, что их вклад не особо отличается от остальных."
      },
      {
        code: "TOP3",
        label: "Максимум топ-3 по выручке, остальным символически",
        d_money: 15,
        d_engagement: -10,
        d_risk: 15,
        comment:
          "Лисы и Крыса получают сигнал: главное — результат, остальное неважно. Хомяки и часть ядра воспринимают это как перекос и снижение справедливости."
      },
      {
        code: "CORE_PLUS",
        label: "Минимум всем + заметный бонус ядру и ключевым людям",
        d_money: -5,
        d_engagement: 15,
        d_risk: -5,
        comment:
          "Люди чувствуют, что базовая справедливость есть, при этом ядро и ключевые сотрудники получают признание. Это усиливает устойчивость системы."
      }
    ]
  },
  {
    id: "RAT_CRISIS",
    title: "Сцена 3. Шантаж",
    description:
      "Антон (Крыса) усиливает давление: намекает на уход, собирает вокруг себя группу недовольных, ставит ультиматумы. При этом его выручка выше средней. Что важнее: краткосрочные деньги или здоровье системы?",
    question: "Как поступишь с Антоном?",
    options: [
      {
        code: "IGNORE",
        label: "Закрыть глаза: пока тащит выручку — не трогаем",
        d_money: 10,
        d_engagement: -20,
        d_risk: 25,
        comment:
          "Остальные видят, что токсичность и шантаж сходят с рук, если приносишь деньги. Ядро выгорает, Хомяки уходят в пассив, растёт скрытый саботаж."
      },
      {
        code: "FRAME",
        label: "Жёсткий разговор 1:1 и понятные рамки",
        d_money: -5,
        d_engagement: 5,
        d_risk: -10,
        comment:
          "Сигнал команде: результат важен, но правила общие. Часть риска снимается, но если рамки только на словах, ситуация вернётся."
      },
      {
        code: "FAREWELL",
        label: "Готовим замену и прощаемся",
        d_money: -15,
        d_engagement: 20,
        d_risk: -20,
        comment:
          "Краткосрочно больно по деньгам, но команда видит, что система важнее шантажа. Это усиливает ядро и даёт сигнал, что токсичность не окупается."
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
