from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from core.config import settings

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🌐 Открыть Теремок",
            web_app=WebAppInfo(url=settings.WEB_APP_URL or "https://vostroslava.github.io/teremok_game_bot/")
        )]
    ])
    
    await message.answer(
        "👋 **Добро пожаловать в Теремок!**\n\n"
        "🏢 Модель мотивации сотрудников от Stalker Media\n\n"
        "Нажмите кнопку ниже, чтобы открыть интерактивное приложение:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    await cmd_start(message)

@router.message(Command("id"))
async def cmd_id(message: Message):
    await message.answer(
        f"🔑 **Ваш Telegram ID:**\n`{message.from_user.id}`\n\n"
        f"👤 Username: @{message.from_user.username or 'не указан'}",
        parse_mode="Markdown"
    )

@router.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    """Handle data from Telegram Web App (contact form)"""
    import json
    from core.database import save_lead
    from core.config import settings
    
    try:
        data = json.loads(message.web_app_data.data)
        
        if data.get('type') == 'contact_form':
            name = data.get('name', 'Не указано')
            contact = data.get('contact', 'Не указано')
            user_message = data.get('message', '')
            result_type = data.get('result_type', '')
            
            # Save to database
            await save_lead(
                user_id=message.from_user.id,
                contact_info=f"{name} | {contact}",
                message=f"Результат: {result_type}\n\n{user_message}" if result_type else user_message
            )
            
            # Send notification to admin
            if settings.ADMIN_ID:
                notification_text = (
                    "📩 **Новая заявка с веб-приложения!**\n\n"
                    f"👤 **Имя:** {name}\n"
                    f"📞 **Контакт:** {contact}\n"
                )
                if result_type:
                    notification_text += f"🎯 **Результат диагностики:** {result_type}\n"
                if user_message:
                    notification_text += f"\n💬 **Сообщение:**\n{user_message}"
                
                notification_text += f"\n\n_От пользователя:_ @{message.from_user.username or 'без username'} (ID: {message.from_user.id})"
                
                await message.bot.send_message(
                    chat_id=settings.ADMIN_ID,
                    text=notification_text,
                    parse_mode="Markdown"
                )
            
            # Confirm to user
            await message.answer(
                "✅ Спасибо! Ваша заявка отправлена.\n"
                "Мы свяжемся с вами в ближайшее время."
            )
    except Exception as e:
        print(f"Error handling web app data: {e}")
        await message.answer("❌ Произошла ошибка при отправке заявки. Попробуйте еще раз.")
