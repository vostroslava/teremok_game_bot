from aiogram import Router, F
from aiogram.types import CallbackQuery
from bot.keyboards import back_to_menu_keyboard
from core.texts import FAQ_DATA

router = Router()

@router.callback_query(F.data == "faq")
async def cb_faq_list(callback: CallbackQuery):
    # Build FAQ text
    faq_text = "❓ **Часто задаваемые вопросы**\n\n"
    
    for i, item in enumerate(FAQ_DATA, 1):
        faq_text += f"**{i}. {item['question']}**\n"
        faq_text += f"{item['answer']}\n\n"
    
    await callback.message.edit_text(
        faq_text,
        reply_markup=back_to_menu_keyboard(),
        parse_mode="Markdown"
    )
