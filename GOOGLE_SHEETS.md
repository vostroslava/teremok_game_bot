# Google Sheets Integration (via Webhook)

## Быстрая настройка

Мы используем Google Apps Script как вебхук, чтобы не возиться с сервисными аккаунтами и сложной настройкой прав.

### 1. Подготовка таблицы

1. Создайте Google Таблицу (или используйте существующую).
2. Перейдите в **Расширения** (Extensions) -> **Apps Script**.
3. Вставьте следующий код в редактор скриптов (файл `Code.gs`):

```javascript
function doPost(e) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const data = JSON.parse(e.postData.contents);
  
  // Определяем лист
  let sheetName = data.type === 'test' ? 'Тесты' : 'Лиды';
  let sheet = ss.getSheetByName(sheetName);
  
  // Создаём лист, если нет
  if (!sheet) {
    sheet = ss.insertSheet(sheetName);
    if (data.type === 'test') {
      sheet.appendRow(['Дата', 'Имя', 'Роль', 'Компания', 'Телефон', 'Результат', 'Баллы', 'Продукт', 'User ID']);
    } else {
      sheet.appendRow(['Дата', 'Имя', 'Роль', 'Компания', 'Телефон', 'Telegram', 'Статус', 'Размер команды', 'User ID']);
    }
  }
  
  // Формируем строку
  let row = [];
  if (data.type === 'test') {
    row = [
      new Date(),
      data.name || '',
      data.role || '',
      data.company || '',
      data.phone || '',
      data.result_type || '',
      data.scores || '',
      data.product || 'teremok',
      data.user_id || ''
    ];
  } else {
    row = [
      new Date(),
      data.name || '',
      data.role || '',
      data.company || '',
      data.phone || '',
      data.telegram || '',
      data.status || 'new',
      data.team_size || '',
      data.user_id || ''
    ];
  }
  
  sheet.appendRow(row);
  return ContentService.createTextOutput(JSON.stringify({status: 'ok'}));
}
```

### 2. Публикация вебхука

1. Нажмите кнопку **Начать развертывание** (Deploy) -> **Новое развертывание** (New deployment).
2. Выберите тип: **Веб-приложение** (Web app).
3. Заполните поля:
   - **Описание**: Webhook for Teremok Bot
   - **Выполнять как**: *Про меня* (Me)
   - **У кого есть доступ**: **Все** (Anyone) — **ВАЖНО!**
4. Нажмите **Начать развертывание** (Deploy).
5. Скопируйте **URL веб-приложения**.

### 3. Настройка бота

В файле `.env` укажите:

```bash
GOOGLE_SHEETS_ENABLED=true
GOOGLE_SHEETS_WEBHOOK_URL=https://script.google.com/macros/s/AKfycb.../exec
```

(Вставьте ваш скопированный URL)

---

## Проверка

После настройки, все новые заявки и результаты тестов будут автоматически попадать в таблицу.
В таблице сами создадутся листы "Лиды" и "Тесты".
