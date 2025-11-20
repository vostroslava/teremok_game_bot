// Попытка подключиться к Telegram WebApp API (если запущено внутри Telegram)
const tg = window.Telegram ? window.Telegram.WebApp : null;
if (tg) {
  tg.expand();
}

// Сцены те же, что во второй части Python-бота
const SCENES = [
  {
    id: "TEAM_LEAD",
    title: "Сцена 1. Кого сделать лицом отдела продаж?",
    description:
      "Продажи растут, и собственник с директором решают: нужно чётко обозначить, кто будет «лицом» отдела продаж и внутренним лидером.\n\nОт этого решения зависит, на кого начнут равняться остальные и какую логику управления они будут считать нормой.",
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
    title: "Сцена 2. Как раздать премию за удачный квартал?",
    description:
      "Квартал закрыт успешно, у компании есть деньги на премии. От того, как ты сейчас распределишь деньги, зависит, какие типажи будут считать систему справедливой и куда поедет мотивация.",
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
    title: "Сцена 3. Крыса качает лодку",
    description:
      "Антон усиливает давление: намекает на уход, собирает вокруг себя группу недовольных, ставит ультиматумы по условиям. При этом его выручка выше средней по отделу.\n\nОт твоего решения зависит, что будет важнее для компании — краткосрочные деньги или долгосрочное здоровье системы.",
    question: "Как поступишь с Антоном и ситуацией вокруг него?",
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
        label: "Жёсткий разговор 1:1 и понятные рамки: остаётся, но по правилам",
        d_money: -5,
        d_engagement: 5,
        d_risk: -10,
        comment:
          "Сигнал команде: результат важен, но правила общие. Часть риска снимается, но если рамки только на словах, ситуация вернётся."
      },
      {
        code: "FAREWELL",
        label: "Готовим замену и прощаемся, перестраивая систему под команду",
        d_money: -15,
        d_engagement: 20,
        d_risk: -20,
        comment:
          "Краткосрочно больно по деньгам, но команда видит, что система важнее шантажа. Это усиливает ядро и даёт сигнал, что токсичность не окупается."
      }
    ]
  }
];

const state = {
  started: false,
  currentScene: 0,
  money: 100,
  engagement: 70,
  risk: 20,
  decisions: []
};

const screen = document.getElementById("screen");

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function renderStartScreen() {
  state.started = false;
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
  title.textContent = "Как ты управляешь Теремком?";

  const text = document.createElement("p");
  text.className = "card-text";
  text.textContent =
    "Перед тобой короткая симуляция. Ты примешь несколько ключевых решений по людям: кто станет лидером, как раздать деньги и что делать с Крысой. На выходе увидишь, как это бьёт по деньгам, вовлечённости и риску выгорания.";

  const btnStart = document.createElement("button");
  btnStart.className = "btn btn-primary";
  btnStart.textContent = "▶️ Начать симуляцию";
  btnStart.addEventListener("click", () => {
    state.started = true;
    state.currentScene = 0;
    renderCurrentScene();
  });

  const btnInfo = document.createElement("button");
  btnInfo.className = "btn";
  btnInfo.innerHTML = "<span class=\"label\">ℹ️ Напомнить про типажи Теремка</span>";

  btnInfo.addEventListener("click", () => {
    alert(
      "Кратко о типажах:\n\n" +
        "🐦 Птица — живёт новизной и впечатлениями, быстро загорается и быстро остывает.\n" +
        "🐹 Хомяк — деньги, стабильность, понятные правила.\n" +
        "🦊 Лиса — личная выгода, статус, влияние.\n" +
        "🐀 Крыса — Лиса, играющая против системы и шантажирующая результатом.\n" +
        "👔 Профессионал — экспертиза, стандарты, качество.\n" +
        "🐻 Медведь — опорный собственник/руководитель, ценит устойчивость.\n" +
        "🅰️ Альфа-лидер — идея, ценности, смысл.\n" +
        "🅱️ Бета-лидер — процессы, команда, проводка решений."
    );
  });

  card.appendChild(title);
  card.appendChild(text);
  card.appendChild(btnStart);
  card.appendChild(btnInfo);

  screen.appendChild(card);
}

function renderMetrics(container) {
  const metrics = document.createElement("div");
  metrics.className = "metrics";

  function addMetric(label, value, min, max) {
    const row = document.createElement("div");
    row.className = "metric-row";

    const labelEl = document.createElement("div");
    labelEl.className = "metric-label";
    labelEl.textContent = label;

    const valueEl = document.createElement("div");
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

    // чуть другая логика цвета для риска
    if (label.includes("Риск")) {
      fill.style.background = "linear-gradient(90deg, #22c55e, #ef4444)";
    }

    bar.appendChild(fill);
    metrics.appendChild(bar);
  }

  addMetric("💰 Деньги (база 100)", state.money, 0, 200);
  addMetric("🔥 Вовлечённость", state.engagement, 0, 120);
  addMetric("⚠️ Риск выгорания/токсичности", state.risk, 0, 120);

  container.appendChild(metrics);
}

function renderCurrentScene() {
  const sceneIndex = state.currentScene;
  if (sceneIndex >= SCENES.length) {
    renderSummary();
    return;
  }

  const scene = SCENES[sceneIndex];
  screen.innerHTML = "";

  const card = document.createElement("div");
  card.className = "card";

  const title = document.createElement("h2");
  title.className = "card-title";
  title.textContent = scene.title;

  const text = document.createElement("p");
  text.className = "card-text";
  text.textContent = scene.description + "\n\n" + scene.question;

  card.appendChild(title);
  card.appendChild(text);

  renderMetrics(card);

  const buttons = document.createElement("div");
  buttons.className = "buttons";

  scene.options.forEach((opt, idx) => {
    const btn = document.createElement("button");
    btn.className = "btn";
    btn.innerHTML =
      '<span class="label">' + opt.label + '</span><span class="chevron">›</span>';
    btn.addEventListener("click", () => handleOptionClick(sceneIndex, idx));
    buttons.appendChild(btn);
  });

  card.appendChild(buttons);
  screen.appendChild(card);
}

function handleOptionClick(sceneIndex, optionIndex) {
  const scene = SCENES[sceneIndex];
  const opt = scene.options[optionIndex];

  state.money = clamp(state.money + opt.d_money, 0, 200);
  state.engagement = clamp(state.engagement + opt.d_engagement, 0, 120);
  state.risk = clamp(state.risk + opt.d_risk, 0, 120);

  state.decisions.push({
    sceneId: scene.id,
    sceneTitle: scene.title,
    optionLabel: opt.label,
    d_money: opt.d_money,
    d_engagement: opt.d_engagement,
    d_risk: opt.d_risk,
    comment: opt.comment
  });

  // краткий фидбек перед следующей сценой
  alert(
    scene.title +
      "\n\nТвой выбор:\n" +
      opt.label +
      "\n\nЭффект: деньги " +
      formatDelta(opt.d_money) +
      ", вовлечённость " +
      formatDelta(opt.d_engagement) +
      ", риск " +
      formatDelta(opt.d_risk) +
      "."
  );

  state.currentScene += 1;
  if (state.currentScene < SCENES.length) {
    renderCurrentScene();
  } else {
    renderSummary();
  }
}

function formatDelta(x) {
  return x >= 0 ? "+" + x : x.toString();
}

function renderSummary() {
  screen.innerHTML = "";

  const card = document.createElement("div");
  card.className = "card";

  const title = document.createElement("h2");
  title.className = "card-title";
  title.textContent = "Итоги симуляции";

  const money = state.money;
  const engagement = state.engagement;
  const risk = state.risk;

  let moneyText;
  if (money < 80) {
    moneyText =
      "Компания недозарабатывает или теряет деньги из-за управленческих решений.";
  } else if (money <= 120) {
    moneyText =
      "Финансовый результат в допустимом коридоре: без рывков, но и без провалов.";
  } else {
    moneyText =
      "Агрессивный рост по деньгам, но важно смотреть, какой ценой это достигается.";
  }

  let engagementText;
  if (engagement < 50) {
    engagementText =
      "Вовлечённость просела: часть людей выгорела или ушла в пассивный саботаж.";
  } else if (engagement <= 80) {
    engagementText =
      "Вовлечённость неровная: часть команды тянет, часть работает «по инструкции».";
  } else {
    engagementText =
      "Команда в целом вовлечена и чувствует смысл происходящего.";
  }

  let riskText;
  if (risk > 60) {
    riskText =
      "Риск выгорания и токсичных конфликтов высокий — система держится на отдельных людях.";
  } else if (risk >= 30) {
    riskText =
      "Риск управляемый, но турбулентность присутствует — важны точные решения по людям.";
  } else {
    riskText =
      "Риск выгорания и токсичности низкий — система относительно устойчива.";
  }

  const text = document.createElement("p");
  text.className = "card-text";
  text.textContent =
    "Как твои решения повлияли на компанию:\n\n" +
    "💰 Деньги: " +
    money +
    " (база 100). " +
    moneyText +
    "\n\n" +
    "🔥 Вовлечённость: " +
    engagement +
    ". " +
    engagementText +
    "\n\n" +
    "⚠️ Риск выгорания/токсичности: " +
    risk +
    ". " +
    riskText;

  card.appendChild(title);
  card.appendChild(text);

  // подробно по решениям
  state.decisions.forEach((d) => {
    const block = document.createElement("div");
    block.className = "card-text";
    block.style.borderTop = "1px solid rgba(148, 163, 184, 0.2)";
    block.style.marginTop = "8px";
    block.style.paddingTop = "8px";
    block.textContent =
      d.sceneTitle +
      "\n— Твой выбор: " +
      d.optionLabel +
      "\nЭффект: деньги " +
      formatDelta(d.d_money) +
      ", вовлечённость " +
      formatDelta(d.d_engagement) +
      ", риск " +
      formatDelta(d.d_risk) +
      ".\n" +
      "Комментарий: " +
      d.comment;
    card.appendChild(block);
  });

  const outro = document.createElement("p");
  outro.className = "card-text";
  outro.textContent =
    "Смысл игры: показать, что ставка только на результат любой ценой усиливает Крыс и Лис, выжигает Хомяков и ядро. Ставка на ядро и прозрачные правила даёт меньше краткосрочного выигрыша, но сохраняет систему и деньги в долгую.";

  card.appendChild(outro);

  const buttons = document.createElement("div");
  buttons.className = "buttons";

  const btnRestart = document.createElement("button");
  btnRestart.className = "btn btn-primary";
  btnRestart.textContent = "🔁 Сыграть ещё раз";
  btnRestart.addEventListener("click", renderStartScreen);

  buttons.appendChild(btnRestart);
  card.appendChild(buttons);

  screen.appendChild(card);
}

// Старт
renderStartScreen();
