from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from core.config import settings

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    from bot.keyboards import hub_menu_keyboard
    
    await message.answer(
        "👋 **Добро пожаловать!**\n\n"
        "Выберите интересующий раздел:\n\n"
        "🐭 **Теремок** — модель типажей и мотивации сотрудников\n\n"
        "⚙️ **Формула команды** — системность, роли и уровни развития\n\n"
        "📢 **Telegram-канал** — новости и материалы\n\n"
        "_Все интерактивы и тесты доступны через веб-приложение._",
        reply_markup=hub_menu_keyboard(),
        parse_mode="Markdown"
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    await cmd_start(message)

@router.message(Command("id"))
async def cmd_id(message: Message):
    await message.answer(
        f"👤 Username: @{message.from_user.username or 'не указан'}",
        parse_mode="Markdown"
    )

@router.message(Command("formula"))
async def cmd_formula(message: Message):
    """Launch Formula RSP Test"""
    base_url = settings.WEB_APP_URL.rstrip('/') if settings.WEB_APP_URL else "https://localhost:8000"
    
    markup = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="🧪 Открыть меню Формулы", 
            web_app=WebAppInfo(url=base_url + "/app/formula/overview")
        )
    ]])
    
    await message.answer(
        "⚙️ **Формула Успешной Команды**\n\n"
        "Пройдите тест, чтобы определить свой управленческий тип (Результатник / Статусник / Процессник).",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@router.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    """Handle data from Telegram Web App (contact form)"""
    import json
    from core.dependencies import user_service
    from core.config import settings
    
    try:
        data = json.loads(message.web_app_data.data)
        
        if data.get('type') == 'contact_form':
            name = data.get('name', 'Не указано')
            contact = data.get('contact', 'Не указано')
            user_message = data.get('message', '')
            result_type = data.get('result_type', '')
            
            # Save to database via Service
            await user_service.submit_lead(
                name=name,
                contact=contact,
                message=f"Результат: {result_type}\n\n{user_message}" if result_type else user_message
            )
            
            # Send notification to manager
            if settings.MANAGER_CHAT_ID:
                notification_text = (
                    "📩 <b>Новая заявка с веб-приложения!</b>\n\n"
                    f"👤 <b>Имя:</b> {name}\n"
                    f"📞 <b>Контакт:</b> {contact}\n"
                )
                if result_type:
                    notification_text += f"🎯 <b>Результат диагностики:</b> {result_type}\n"
                if user_message:
                    notification_text += f"\n💬 <b>Сообщение:</b>\n{user_message}"
                
                notification_text += f"\n\n_От пользователя:_ @{message.from_user.username or 'без username'} (ID: <code>{message.from_user.id}</code>)"
                
                try:
                    await message.bot.send_message(
                        chat_id=settings.MANAGER_CHAT_ID,
                        text=notification_text,
                        parse_mode="HTML"
                    )
                except Exception as e:
                    print(f"Failed to send notification: {e}")
            
            # Confirm to user
            await message.answer(
                "✅ Спасибо! Ваша заявка отправлена.\n"
                "Мы свяжемся с вами в ближайшее время."
            )
    except Exception as e:
        print(f"Error handling web app data: {e}")
        await message.answer("❌ Произошла ошибка при отправке заявки. Попробуйте еще раз.")
