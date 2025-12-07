# Google Sheets Integration

## Быстрый старт (одна таблица, 2 листа)

### 1. Создайте Google таблицу

Создайте **одну** таблицу: `Teremok CRM`

Бот автоматически создаст в ней 2 листа:
- **Лиды** — контакты
- **Тесты** — результаты тестов

Скопируйте ID таблицы из URL:
```
https://docs.google.com/spreadsheets/d/<SPREADSHEET_ID>/edit
```

---

### 2. Создайте сервисный аккаунт

1. Откройте [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте проект → включите **Google Sheets API** и **Google Drive API**
3. **IAM & Admin** → **Service Accounts** → **Create**
4. Откройте аккаунт → **Keys** → **Add Key** → **JSON**
5. Скачайте JSON-файл

---

### 3. Дайте доступ к таблице

1. Откройте созданную таблицу
2. **Поделиться** → добавьте email из JSON (`client_email`)
3. Права: **Редактор**

---

### 4. Настройте .env

```bash
GOOGLE_SHEETS_ENABLED=true
GOOGLE_SERVICE_ACCOUNT_JSON='<JSON одной строкой>'
GOOGLE_SHEETS_LEADS_ID=1AbCdEfGhIjKlMnOpQrStUvWxYz
```

> **Примечание:** `GOOGLE_SHEETS_TESTS_ID` не нужен — оба листа создаются в одной таблице.

---

### 5. Перезапустите

```bash
pip install gspread google-auth
python main.py
```

---

## Структура листов

**Лиды:**
| Дата | Источник | Имя | Роль | Компания | Размер команды | Телефон | Telegram | User ID | Статус | Примечание |

**Тесты:**
| Дата | Продукт | Имя | Роль | Компания | Размер команды | Телефон | Telegram | User ID | Типаж | Баллы |

---

## Troubleshooting

| Ошибка | Решение |
|--------|---------|
| `gspread not installed` | `pip install gspread google-auth` |
| `Permission denied` | Добавьте email сервисного аккаунта в таблицу |
| `Spreadsheet not found` | Проверьте ID таблицы в .env |
