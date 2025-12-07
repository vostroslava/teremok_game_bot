# Google Sheets Integration

## Быстрый старт

### 1. Создайте Google таблицы

Создайте 2 таблицы в Google Sheets:

**Таблица лидов** — назовите: `Teremok Leads`
**Таблица тестов** — назовите: `Teremok Tests`

Скопируйте ID каждой таблицы из URL:
```
https://docs.google.com/spreadsheets/d/<SPREADSHEET_ID>/edit
                                       ^^^^^^^^^^^^^^^^
```

---

### 2. Создайте сервисный аккаунт Google

1. Откройте [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте проект (или выберите существующий)
3. Перейдите в **APIs & Services** → **Enable APIs**
4. Включите **Google Sheets API** и **Google Drive API**
5. Перейдите в **IAM & Admin** → **Service Accounts**
6. Нажмите **Create Service Account**
   - Имя: `teremok-sheets`
   - Роль: не нужна
7. Откройте созданный аккаунт → вкладка **Keys**
8. **Add Key** → **Create new key** → **JSON**
9. Скачайте JSON-файл

---

### 3. Дайте доступ к таблицам

Откройте **каждую** созданную таблицу и:
1. Нажмите **Поделиться** (Share)
2. Добавьте email сервисного аккаунта (из JSON: `"client_email": "..."`)
3. Дайте права **Редактор** (Editor)

---

### 4. Настройте .env

```bash
# Включите интеграцию
GOOGLE_SHEETS_ENABLED=true

# Вставьте JSON как одну строку (без переносов!)
GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account","project_id":"your-project","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"teremok-sheets@your-project.iam.gserviceaccount.com",...}'

# ID таблиц
GOOGLE_SHEETS_LEADS_ID=1AbCdEfGhIjKlMnOpQrStUvWxYz
GOOGLE_SHEETS_TESTS_ID=1ZyXwVuTsRqPoNmLkJiHgFeDcBa
```

---

### 5. Установите зависимости

```bash
pip install gspread google-auth
```

---

### 6. Перезапустите приложение

```bash
lsof -ti:8000 | xargs kill -9; python main.py
```

---

## Структура таблиц

### Лиды (автоматически создаётся при экспорте)
| Дата | Источник | Имя | Роль | Компания | Размер команды | Телефон | Telegram | User ID | Статус | Примечание |

### Тесты
| Дата | Продукт | Имя | Роль | Компания | Размер команды | Телефон | Telegram | User ID | Типаж | Баллы |

---

## Использование

### Автоматический экспорт
При включенной интеграции каждый новый лид и результат теста автоматически добавляется в таблицы.

### Ручной экспорт
В админке (`/app/admin/leads` и `/app/admin/tests`) есть кнопка **Экспорт в Sheets**.
Она очищает таблицу и загружает все данные заново.

---

## Troubleshooting

**Ошибка: `gspread not installed`**
```bash
pip install gspread google-auth
```

**Ошибка: `Permission denied`**
- Проверьте, что email сервисного аккаунта добавлен в таблицу как редактор

**Ошибка: `Spreadsheet not found`**
- Проверьте правильность ID таблицы в .env
