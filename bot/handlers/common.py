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
