from aiogram import Router, F, types
from aiogram.types import CallbackQuery
from bot.keyboards import types_menu_keyboard, type_details_keyboard
from core.texts import TYPES_DATA

router = Router()

@router.callback_query(F.data == "types_menu")
async def cb_types_menu(callback: CallbackQuery):
    await callback.message.edit_text("Выберите типаж, чтобы узнать подробнее:", reply_markup=types_menu_keyboard())

@router.callback_query(F.data.startswith("type_"))
async def cb_type_detail(callback: CallbackQuery):
    type_id = callback.data.split("_")[1]
    data = TYPES_DATA.get(type_id)
    if not data:
        await callback.answer("Ошибка: Типаж не найден")
        return

    text = (
        f"**{data.emoji} {data.name_ru}**\n\n"
        f"{data.short_desc}\n\n"
        f"📋 **Маркеры:**\n" + "\n".join([f"- {m}" for m in data.markers]) + "\n\n"
        f"⚠️ **Риски:**\n{data.risks}\n\n"
        f"🔧 **Управление:**\n{data.management_advice}"
    )
    
    await callback.message.edit_text(text, reply_markup=type_details_keyboard(type_id), parse_mode="Markdown")

@router.callback_query(F.data.startswith("example_"))
async def cb_type_example(callback: CallbackQuery):
    type_id = callback.data.split("_")[1]
    data = TYPES_DATA.get(type_id)
    if not data:
        await callback.answer("Ошибка")
        return

    from core.texts import EXAMPLES_EXTENDED
    examples = EXAMPLES_EXTENDED.get(type_id, [data.example])
    
    text = f"**{data.emoji} {data.name_ru} — Примеры из практики**\n\n"
    for i, ex in enumerate(examples, 1):
        text += f"{i}. _{ex}_\n\n"
    
    # Re-use details keyboard to go back easily to THIS type
    await callback.message.edit_text(text, reply_markup=type_details_keyboard(type_id), parse_mode="Markdown")
