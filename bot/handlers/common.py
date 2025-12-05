from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.keyboards import main_menu_keyboard
from core.texts import WELCOME_TEXT, ABOUT_TEREMOK_TEXT
from core.database import add_user

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = message.from_user
    await add_user(user.id, user.username, user.first_name)
    await message.answer(WELCOME_TEXT, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("Используйте меню для навигации.", reply_markup=main_menu_keyboard())

@router.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(WELCOME_TEXT, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "about_teremok")
async def cb_about(callback: CallbackQuery):
    await callback.message.edit_text(ABOUT_TEREMOK_TEXT, reply_markup=main_menu_keyboard(), parse_mode="Markdown")
