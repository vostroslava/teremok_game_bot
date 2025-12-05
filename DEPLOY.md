# 🚀 Deployment Guide (GitHub → Render.com)

## Шаг 1: Создайте GitHub репозиторий

1. Зайдите на [GitHub](https://github.com) и создайте **новый приватный репозиторий**
2. Назовите его, например: `teremok-bot`
3. **Не инициализируйте** с README/LICENSE

## Шаг 2: Загрузите код на GitHub

В терминале выполните:

```bash
cd /Library/teremok_game_bot
git remote add origin https://github.com/ВАШ_USERNAME/teremok-bot.git
git branch -M main
git push -u origin main
```

## Шаг 3: Деплой на Render.com

1. Зайдите на [Render.com](https://render.com) и войдите через GitHub
2. Нажмите **"New +"** → **"Web Service"**
3. Подключите ваш GitHub репозиторий `teremok-bot`
4. Render автоматически найдет `render.yaml`
5. Добавьте **Environment Variables**:
   - `BOT_TOKEN` = `8200223342:AAHbh2Poc73PA65-HN9zrDGwmnESU5kw-ac`
   - `ADMIN_ID` = ваш Telegram ID (опционально)
   - `WEB_APP_URL` = оставьте пустым сейчас (обновим позже)

6. Нажмите **"Create Web Service"**

## Шаг 4: Получите URL и обновите WEB_APP_URL

После деплоя Render выдаст URL типа:
```
https://teremok-bot-abc123.onrender.com
```

1. Скопируйте этот URL
2. Вернитесь в настройки **Environment Variables** на Render
3. Установите `WEB_APP_URL = https://teremok-bot-abc123.onrender.com`
4. Сохраните (Render автоматически перезапустит бота)

## Шаг 5: Настройте Menu Button в BotFather

1. Откройте @BotFather в Telegram
2. Отправьте `/mybots` → выберите вашего бота
3. **Bot Settings** → **Menu Button** → **Configure Menu Button**
4. Введите URL: `https://teremok-bot-abc123.onrender.com`

✅ Готово! Теперь бот работает 24/7 с Web App!
