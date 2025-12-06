const tg = window.Telegram.WebApp;
tg.expand();

// Embedded types data
const TYPES_DATA = {
    bird: { emoji: "🐦", name_ru: "Птица", short_desc: "Сотрудник, часто меняющий работу. Лишен личного пространства и ответственности.", markers: ["Часто меняет работу (летун).", "Выполняет работу только под контролем.", "Нет зоны ответственности.", "При малейших трудностях покидает компанию."], risks: "Уйдёт при первых сложностях, не привязан к результату.", management_advice: "Стратегия: «Подрезать крылья» — создать нужду (кредит, семья). Тактика: «Сделай это — и свободен»." },
    hamster: { emoji: "🐹", name_ru: "Хомяк", short_desc: "Ориентир ован исключительно на деньги и материальные блага здесь и сейчас.", markers: ["Интересует только зарплата, 'плюшки' и оплата прямо сейчас.", "Девиз: «Всё, что не про деньги — понарошку».", "Не интересуется перспективой.", "Может скрывать ресурсы (клиентов) в своей «норке»."], risks: "Уйдёт, если предложат на рубль больше. Может воровать или скрывать ресурсы.", management_advice: "Стратегия: Социализация. Сделать 'норки' прозрачными. Тактика: Коллективная ответственность." },
    fox: { emoji: "🦊", name_ru: "Лиса", short_desc: "Личная выгода. Умна, хитра, может быть как полезной (карьерист), так и токсичной.", markers: ["Создаёт видимость бурной деятельности.", "Важнее казаться, чем быть.", "Отличные коммуникативные навыки.", "На собеседовании продаёт себя лучше всех."], risks: "Может манипулировать, создавать интриги, присваивать чужие заслуги.", management_advice: "Стратегия: Растить в Профессионала. Тактика: Жёсткий контроль результата, конкурентная среда, обучение." },
    rat: { emoji: "🐀", name_ru: "Крыса", short_desc: "Деградировавшая Лиса. Токсичный сотрудник.", markers: ["Интриги, сплетни, стравливание коллег.", "Манипулирует доверием руководителя.", "Присваивает ресурсы, вредит компании скрыто."], risks: "Разрушение коллектива, потеря ключевых сотрудников, кража базы.", management_advice: "Увольнять. Без жалости. Изолировать от коллектива до увольнения." },
    professional: { emoji: "👔", name_ru: "Профессионал", short_desc: "Мотив: Нравится работа. Сплав знаний, навыков и созидательных намерений.", markers: ["Делает по совести, даже без контроля.", "Приносит пользу и себе, и компании (Win-Win).", "Готов исправлять свои ошибки.", "Может быть наставником."], risks: "Может выгореть, если им управляет дурак. Может деградировать в Волка.", management_advice: "Не мешать. Защищать от бюрократии и токсичных Лис. Давать сложные задачи, признание." },
    wolf: { emoji: "🐺", name_ru: "Волк", short_desc: "Деградировавший Профессионал. Собирает «стаю» внутри компании.", markers: ["Создает свою команду, преданную лично ему.", "Диктует условия руководству/собственнику.", "Агрессивно защищает свою территорию."], risks: "Шантаж собственника, увод бизнеса или ключевой команды.", management_advice: "Разделять стаю (отправлять в разные проекты). Лишать ресурса влияния. Увольнять лидеров бунта." },
    bear: { emoji: "🐻", name_ru: "Медведь", short_desc: "«Я исключение из правил». Опытный, авторитетный, но неуправляемый.", markers: ["Игнорирует общие правила и регламенты.", "Считает, что ему можно всё за былые заслуги.", "Работает когда хочет и как хочет."], risks: "Разлагает дисциплину своим примером. Демотивирует новичков.", management_advice: "Вводить конкуренцию (показать, что он не незаменим). Жестко ставить в рамки или переводить в роль консультанта." }
};

// FAQ Data
const FAQ_DATA = [
    { question: "Можно ли изменить типаж сотрудника?", answer: "Да, но не всегда. Лису можно вырастить в Профессионала через обучение и контроль. Птицу можно 'подрезать крылья' (создать нужду). Но Крысу и Медведя лучше увольнять." },
    { question: "Как определить типаж на собеседовании?", answer: "Смотрите на маркеры:\n- Птица: приходит с кем-то, много мест работы\n- Хомяк: первый вопрос про деньги\n- Лиса: красиво говорит, но детали размыты\n- Профессионал: конкретные примеры, вопросы про задачи" },
    { question: "Кого брать в команду?", answer: "Основа — Профессионалы. Хомяков и Лис можно взять, но держать под контролем и растить. Птиц — только на простые задачи. Крыс, Волков, Медведей — не брать." },
    { question: "Как мотивировать каждый типаж?", answer: "Птица: контроль и простые задачи\nХомяк: деньги и KPI\nЛиса: статус, признание, карьера\nПрофессионал: сложные задачи, свобода, признание экспертизы" },
    { question: "Что делать, если вся команда — Хомяки?", answer: "Внедряйте прозрачность (открытые 'норки'), коллективную ответственность, обучение. Растите Лис в Профессионалов. Приводите Профессионалов извне как пример." }
];

// Diagnostic Questions
const DIAGNOSTIC_QUESTIONS = [
    {
        id: 1, text: "Ваш подход к новым задачам на работе?", options: [
            { text: "Делаю только то, что сказали, чтобы не трогали.", score: { bird: 2 } },
            { text: "Сразу спрашиваю: 'А что мне за это доплатят?'", score: { hamster: 2 } },
            { text: "Берусь, если это поможет выделиться перед шефом.", score: { fox: 2 } },
            { text: "Интересно разобраться и сделать качественно.", score: { professional: 2 } }
        ]
    },
    {
        id: 2, text: "Что для вас идеальный рабочий день?", options: [
            { text: "Когда начальник в командировке и можно уйти пораньше.", score: { bird: 1, hamster: 1 } },
            { text: "Когда удалось заключить выгодную сделку и получить бонус.", score: { hamster: 2 } },
            { text: "Когда меня публично похвалили на собрании.", score: { fox: 2 } },
            { text: "Когда удалось решить сложную проблему и увидеть результат.", score: { professional: 2 } }
        ]
    },
    {
        id: 3, text: "Как вы относитесь к ошибкам?", options: [
            { text: "Лучше промолчать, авось не заметят.", score: { bird: 1, rat: 1 } },
            { text: "Виноват не я, это обстоятельства/коллеги.", score: { fox: 1, hamster: 1 } },
            { text: "Признаю, ищу причину и исправляю, чтобы не повторилось.", score: { professional: 2 } },
            { text: "Ошибки? У меня их не бывает, это другие ошибаются.", score: { bear: 1, wolf: 1 } }
        ]
    },
    {
        id: 4, text: "Ваша реакция на просьбу поработать в выходной (без доплаты)?", options: [
            { text: "Ни за что. Нет денег — нет работы.", score: { hamster: 3 } },
            { text: "Если шеф будет и это оценит — выйду.", score: { fox: 2 } },
            { text: "Если это критично для проекта — выйду и сделаю.", score: { professional: 1 } },
            { text: "Промолчу, но просто не приду или заболею.", score: { bird: 2 } }
        ]
    },
    {
        id: 5, text: "Что самое важное в компании для вас?", options: [
            { text: "Чтобы вовремя платили и не трогали.", score: { bird: 1, hamster: 1 } },
            { text: "Возможность карьерного роста и статус.", score: { fox: 2 } },
            { text: "Профессиональный коллектив и интересные задачи.", score: { professional: 2 } },
            { text: "Максимальный доход при минимальных усилиях.", score: { hamster: 2, rat: 1 } }
        ]
    }
];

let diagnosticState = { currentQuestion: 0, scores: {}, answers: {} };

// Helper: Get Telegram user data
function getTelegramUserData() {
    if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initDataUnsafe) {
        const user = window.Telegram.WebApp.initDataUnsafe.user;
        if (user) {
            return {
                id: user.id,
                username: user.username || 'не указан',
                first_name: user.first_name || '',
                last_name: user.last_name || ''
            };
        }
    }
    return null;
}

// Section Navigation
async function showSection(sectionName) {
    // Check if user tries to access test - now checks subscription OR contacts
    if (sectionName === 'diagnostic') {
        const canAccessTest = await checkTestAccess();
        if (!canAccessTest) {
            return; // checkTestAccess() will handle redirect
        }
    }

    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));

    document.getElementById(`${sectionName}-section`).classList.add('active');
    event.target.classList.add('active');

    if (sectionName === 'types') renderTypesGrid();
    if (sectionName === 'faq') renderFAQ();
    if (sectionName === 'diagnostic') startDiagnostic();
}

// Check if user can access test (subscription OR contacts)
async function checkTestAccess() {
    const userData = getTelegramUserData();

    if (!userData) {
        alert('⚠️ Не удалось определить пользователя Telegram');
        return false;
    }

    try {
        // Check subscription on server
        const response = await fetch(`/api/check-subscription?user_id=${userData.id}`);
        const data = await response.json();

        if (data.subscribed) {
            // Subscribed - can access test
            console.log('User is subscribed to channel - access granted');
            return true;
        }

        // Not subscribed - check if has contacts
        const hasContacts = localStorage.getItem('contacts_completed') === 'true';

        if (hasContacts) {
            // Has contacts - can access test
            console.log('User has filled contacts - access granted');
            return true;
        }

        // Neither subscribed nor has contacts - show message
        alert(
            '⚠️ Для прохождения теста необходимо:\n\n' +
            `1. Подписаться на наш канал @${data.channel_username}\n` +
            'ИЛИ\n' +
            '2. Заполнить контактную форму во вкладке "Контакт"'
        );

        // Redirect to contact form
        showSection('contact');
        return false;

    } catch (error) {
        console.error('Error checking test access:', error);
        alert('⚠️ Ошибка при проверке доступа к тесту');
        return false;
    }
}

// Types Grid
function renderTypesGrid() {
    const grid = document.getElementById('types-grid');
    const detail = document.getElementById('type-detail');
    detail.classList.add('hidden');
    grid.innerHTML = '';

    Object.keys(TYPES_DATA).forEach(key => {
        const t = TYPES_DATA[key];
        const card = document.createElement('div');
        card.className = 'type-card';
        card.onclick = () => showTypeDetail(t);
        card.innerHTML = `<span class="emoji">${t.emoji}</span><h3>${t.name_ru}</h3>`;
        grid.appendChild(card);
    });
}

function showTypeDetail(typeData) {
    const grid = document.getElementById('types-grid');
    const detail = document.getElementById('type-detail');
    grid.classList.add('hidden');
    detail.classList.remove('hidden');

    const markersHtml = typeData.markers.map(m => `<li>${m}</li>`).join('');
    detail.innerHTML = `
        <button class="back-btn" onclick="goBackToGrid()">⬅ Назад</button>
        <span class="type-hero-emoji">${typeData.emoji}</span>
        <h2>${typeData.name_ru}</h2>
        <p style="text-align: center; color: #718096; margin-bottom: 20px;">${typeData.short_desc}</p>
        
        <div class="detail-section">
            <h4>📋 Как узнать?</h4>
            <ul>${markersHtml}</ul>
        </div>
        
        <div class="detail-section">
            <h4>⚠️ Риски</h4>
            <p style="color: #718096;">${typeData.risks}</p>
        </div>
        
        <div class="detail-section">
            <h4>🔧 Советы по управлению</h4>
            <div class="advice-box">${typeData.management_advice}</div>
        </div>
    `;
}

function goBackToGrid() {
    document.getElementById('type-detail').classList.add('hidden');
    document.getElementById('types-grid').classList.remove('hidden');
}

// FAQ
function renderFAQ() {
    const list = document.getElementById('faq-list');
    list.innerHTML = '';

    FAQ_DATA.forEach((item, i) => {
        const faqItem = document.createElement('div');
        faqItem.className = 'faq-item';
        faqItem.innerHTML = `
            <div class="faq-question">${i + 1}. ${item.question}</div>
            <div class="faq-answer">${item.answer}</div>
        `;
        list.appendChild(faqItem);
    });
}

// Diagnostic
function startDiagnostic() {
    diagnosticState = { currentQuestion: 0, scores: {} };
    showQuestion();
}

function showQuestion() {
    const content = document.getElementById('diagnostic-content');
    const q = DIAGNOSTIC_QUESTIONS[diagnosticState.currentQuestion];

    const progress = ((diagnosticState.currentQuestion) / DIAGNOSTIC_QUESTIONS.length) * 100;

    const optionsHtml = q.options.map((opt, i) =>
        `<button class="option-btn" onclick="answerQuestion(${i})">${opt.text}</button>`
    ).join('');

    content.innerHTML = `
        <div class="progress-bar"><div class="progress-fill" style="width: ${progress}%"></div></div>
        <div class="diagnostic-card">
            <p style="color: #718096; margin-bottom: 10px">Вопрос ${diagnosticState.currentQuestion + 1} из ${DIAGNOSTIC_QUESTIONS.length}</p>
            <h3 class="question-text">${q.text}</h3>
            ${optionsHtml}
        </div>
    `;
}

function answerQuestion(optionIndex) {
    const q = DIAGNOSTIC_QUESTIONS[diagnosticState.currentQuestion];
    const score = q.options[optionIndex].score;

    for (let type in score) {
        diagnosticState.scores[type] = (diagnosticState.scores[type] || 0) + score[type];
    }

    diagnosticState.currentQuestion++;

    if (diagnosticState.currentQuestion >= DIAGNOSTIC_QUESTIONS.length) {
        showResult();
    } else {
        showQuestion();
    }
}

function showResult() {
    const sorted = Object.entries(diagnosticState.scores).sort((a, b) => b[1] - a[1]);
    const winnerId = sorted[0][0];
    const typeData = TYPES_DATA[winnerId];

    // Save result for contact form
    localStorage.setItem('diagnosticResult', `${typeData.emoji} ${typeData.name_ru}`);

    const content = document.getElementById('diagnostic-content');
    content.innerHTML = `
        <div class="result-card">
            <span class="result-emoji">${typeData.emoji}</span>
            <h2>Вы ближе к типажу:</h2>
            <h1 style="margin-bottom: 20px">${typeData.name_ru}</h1>
            <p>${typeData.short_desc}</p>
            <p style="margin-top: 20px; opacity: 0.8; font-size: 0.9em;">Это лишь гипотеза. Для точного результата нужны глубокие собеседования.</p>
        </div>
        <button class="cta-button" style="margin-top: 20px" onclick="startDiagnostic()">Пройти снова</button>
        <button class="cta-button" style="margin-top: 10px; background: linear-gradient(135deg, #00d4aa 0%, #00b894 100%)" onclick="showSectionWithResult('contact')">
            Получить консультацию →
        </button>
    `;
}

// Lead Form functionality
const LEAD_QUESTIONS = [
    { id: 'name', title: 'Как к вам можно обращаться?', hint: 'Ваше имя', type: 'text' },
    { id: 'role', title: 'Какая у вас роль в компании?', hint: 'Например: собственник, директор по продажам, HR-менеджер, руководитель отдела', type: 'text' },
    { id: 'company', title: 'Как называется ваша компания?', hint: '', type: 'text' },
    { id: 'team_size', title: 'Сколько примерно человек в вашем отделе/команде?', hint: 'Можно ответить приблизительно: 5, 10-15, около 50 и т.п.', type: 'text' },
    { id: 'contacts', title: 'Как с вами лучше связаться?', hint: 'Напишите телефон и/или ссылку на ваш Telegram / e-mail', type: 'text' },
    { id: 'request', title: 'Коротко опишите вашу ситуацию или запрос', hint: 'Какие задачи или проблемы вы хотите обсудить?', type: 'textarea' }
];

let leadFormState = {
    currentStep: 0,
    answers: {}
};

function startLeadForm() {
    leadFormState = { currentStep: 0, answers: {} };
    document.getElementById('lead-intro').classList.add('hidden');
    document.getElementById('form-progress').classList.remove('hidden');
    document.getElementById('lead-form').classList.remove('hidden');
    showLeadQuestion();
}

function showLeadQuestion() {
    const question = LEAD_QUESTIONS[leadFormState.currentStep];
    const progress = ((leadFormState.currentStep + 1) / LEAD_QUESTIONS.length) * 100;

    document.getElementById('lead-progress-fill').style.width = progress + '%';
    document.getElementById('progress-text').textContent = `Вопрос ${leadFormState.currentStep + 1} из ${LEAD_QUESTIONS.length}`;
    document.getElementById('question-title').textContent = question.title;
    document.getElementById('question-hint').textContent = question.hint;

    const input = document.getElementById('lead-input');
    const textarea = document.getElementById('lead-textarea');

    if (question.type === 'textarea') {
        input.classList.add('hidden');
        textarea.classList.remove('hidden');
        textarea.value = leadFormState.answers[question.id] || '';
        textarea.focus();
    } else {
        textarea.classList.add('hidden');
        input.classList.remove('hidden');
        input.value = leadFormState.answers[question.id] || '';
        input.focus();
    }
}

function nextLeadQuestion() {
    const question = LEAD_QUESTIONS[leadFormState.currentStep];
    const input = question.type === 'textarea' ?
        document.getElementById('lead-textarea') :
        document.getElementById('lead-input');

    const answer = input.value.trim();

    if (!answer) {
        alert('Пожалуйста, ответьте на вопрос');
        return;
    }

    leadFormState.answers[question.id] = answer;

    if (leadFormState.currentStep < LEAD_QUESTIONS.length - 1) {
        leadFormState.currentStep++;
        showLeadQuestion();
    } else {
        submitLeadForm();
    }
}

async function submitLeadForm() {
    // Save contact data
    const contactData = {
        name: leadFormState.answers.name,
        role: leadFormState.answers.role,
        company: leadFormState.answers.company,
        team_size: leadFormState.answers.team_size,
        contacts: leadFormState.answers.contacts,
        request: leadFormState.answers.request
    };

    // Get Telegram user if available
    let telegramUser = null;
    if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initDataUnsafe) {
        const user = window.Telegram.WebApp.initDataUnsafe.user;
        if (user) {
            telegramUser = {
                id: user.id,
                username: user.username || 'не указан',
                first_name: user.first_name || '',
                last_name: user.last_name || ''
            };
        }
    }

    // Mark contacts as completed
    localStorage.setItem('contacts_completed', 'true');

    // Store for later submission with test results
    sessionStorage.setItem('leadContactData', JSON.stringify(contactData));
    sessionStorage.setItem('telegramUser', JSON.stringify(telegramUser));

    // Hide form and show test intro
    document.getElementById('lead-form').classList.add('hidden');
    document.getElementById('form-progress').classList.add('hidden');

    startContactTest();
}

function startContactTest() {
    // Show test intro
    const container = document.getElementById('lead-form-container');
    container.innerHTML = `
        <div class="test-intro" style="text-align: center; padding: 40px 20px;">
            <h2 style="margin-bottom: 20px;">✅ Спасибо! Контакты сохранены.</h2>
            <p style="font-size: 1.1em; margin-bottom: 30px; color: #718096;">
                Теперь предлагаем пройти короткий тест для определения вашего типажа сотрудника.
            </p>
            <p style="margin-bottom: 30px; color: #718096;">
                Это займет 2-3 минуты и поможет нам лучше понять вашу ситуацию.
            </p>
            <button class="cta-button" onclick="beginContactTest()">
                🧩 Начать тест
            </button>
        </div>
    `;
}

function beginContactTest() {
    const container = document.getElementById('lead-form-container');
    diagnosticState = { currentQuestion: 0, scores: {}, answers: [] };

    container.innerHTML = `
        <div id="test-container">
            <div class="form-progress">
                <div class="progress-bar">
                    <div class="progress-fill" id="test-progress-fill"></div>
                </div>
                <p class="progress-text" id="test-progress-text">Вопрос 1 из ${DIAGNOSTIC_QUESTIONS.length}</p>
            </div>
            <div id="test-question-container" class="diagnostic-card"></div>
        </div>
    `;

    showContactTestQuestion();
}

function showContactTestQuestion() {
    const q = DIAGNOSTIC_QUESTIONS[diagnosticState.currentQuestion];
    const progress = ((diagnosticState.currentQuestion + 1) / DIAGNOSTIC_QUESTIONS.length) * 100;

    document.getElementById('test-progress-fill').style.width = progress + '%';
    document.getElementById('test-progress-text').textContent =
        `Вопрос ${diagnosticState.currentQuestion + 1} из ${DIAGNOSTIC_QUESTIONS.length}`;

    const optionsHtml = q.options.map((opt, i) =>
        `<button class="option-btn" onclick="answerContactTest(${i})">${opt.text}</button>`
    ).join('');

    document.getElementById('test-question-container').innerHTML = `
        <h3 class="question-text">${q.text}</h3>
        ${optionsHtml}
    `;
}

function answerContactTest(optionIndex) {
    const q = DIAGNOSTIC_QUESTIONS[diagnosticState.currentQuestion];
    const option = q.options[optionIndex];
    const score = option.score;

    // Save answer
    diagnosticState.answers.push({
        question: q.text,
        answer: option.text
    });

    // Update scores
    for (let type in score) {
        diagnosticState.scores[type] = (diagnosticState.scores[type] || 0) + score[type];
    }

    diagnosticState.currentQuestion++;

    if (diagnosticState.currentQuestion >= DIAGNOSTIC_QUESTIONS.length) {
        showContactTestResult();
    } else {
        showContactTestQuestion();
    }
}

async function showContactTestResult() {
    const sorted = Object.entries(diagnosticState.scores).sort((a, b) => b[1] - a[1]);
    const winnerId = sorted[0][0];
    const typeData = TYPES_DATA[winnerId];

    const container = document.getElementById('lead-form-container');
    container.innerHTML = `
        <div class="result-card">
            <span class="result-emoji">${typeData.emoji}</span>
            <h2>Ваш типаж:</h2>
            <h1 style="margin-bottom: 20px">${typeData.name_ru}</h1>
            <p>${typeData.short_desc}</p>
            <p style="margin-top: 20px; opacity: 0.8; font-size: 0.9em;">
                Отправляем результаты менеджеру...
            </p>
        </div>
    `;

    // Get user data
    const userData = getTelegramUserData();

    if (!userData) {
        console.error('Cannot get user data for test submission');
        container.innerHTML = `
            <div class="form-message error">
                <h3>⚠️ Ошибка</h3>
                <p style="margin-top: 15px;">Не удалось определить пользователя</p>
            </div>
        `;
        return;
    }

    // Submit to new API
    try {
        const response = await fetch('/api/test/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: userData.id,
                answers: diagnosticState.scores
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            // Show final success
            setTimeout(() => {
                container.innerHTML = `
                    <div class="form-message success">
                        <h3>✅ Отлично! Все данные отправлены.</h3>
                        <p style="margin-top: 15px;">
                            Ваш результат: <strong>${data.result.emoji} ${data.result.name}</strong>
                        </p>
                        <p style="margin-top: 15px;">
                            ${data.result.description}
                        </p>
                        <p style="margin-top: 20px; color: #718096;">
                            Менеджер свяжется с вами в ближайшее время.
                        </p>
                    </div>
                `;

                // Cleanup
                sessionStorage.removeItem('leadContactData');
                sessionStorage.removeItem('telegramUser');
            }, 1500);

        } else {
            throw new Error(data.message || 'Unknown error');
        }

    } catch (error) {
        console.error('Error submitting test:', error);
        container.innerHTML = `
            <div class="form-message error">
                <h3>⚠️ Не удалось отправить результаты</h3>
                <p style="margin-top: 15px;">
                    Но мы сохранили ваш результат: <strong>${typeData.emoji} ${typeData.name_ru}</strong>
                </p>
                <p style="margin-top: 15px;">
                    Свяжитесь с нами напрямую:<br>
                    💬 <a href="https://t.me/stalkermedia1" target="_blank" style="color: white;">@stalkermedia1</a>
                </p>
            </div>
        `;
    }
}

function cancelLeadForm() {
    if (confirm('Вы уверены, что хотите отменить заполнение заявки?')) {
        resetLeadForm();
    }
}

function resetLeadForm() {
    leadFormState = { currentStep: 0, answers: {} };
    document.getElementById('lead-intro').classList.remove('hidden');
    document.getElementById('lead-form').classList.add('hidden');
    document.getElementById('form-progress').classList.add('hidden');
    document.getElementById('lead-success').classList.add('hidden');
    document.getElementById('lead-error').classList.add('hidden');
    document.getElementById('lead-input').value = '';
    document.getElementById('lead-textarea').value = '';
}

// Write to bot function
function writeToBot() {
    if (window.Telegram && window.Telegram.WebApp) {
        window.Telegram.WebApp.close();
    }
}

// Init
renderTypesGrid();
updateTestButtonState();
