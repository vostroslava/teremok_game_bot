from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from bot.keyboards import back_to_menu_keyboard
from core.database import save_lead

router = Router()

class FeedbackState(StatesGroup):
    waiting_for_message = State()

@router.callback_query(F.data == "contact_form")
async def cb_contact_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FeedbackState.waiting_for_message)
    await callback.message.edit_text(
        "📝 **Связаться с человеком**\n\n"
        "Напишите ваш вопрос или опишите ситуацию. Мы передадим её экспертам и свяжемся с вами.\n"
        "Укажите также ваше имя и телефон.",
        reply_markup=back_to_menu_keyboard(),
        parse_mode="Markdown"
    )

@router.message(FeedbackState.waiting_for_message)
async def feedback_message(message: Message, state: FSMContext):
    # Save to DB (or send to admin chat)
    user_id = message.from_user.id
    text = message.text
    
    # Save to SQLite
    await save_lead(user_id=user_id, contact_info=f"@{message.from_user.username}", message=text)
    
    # Notify Admin (if configured)
    # from core.config import settings
    # if settings.ADMIN_ID:
    #     await message.bot.send_message(settings.ADMIN_ID, f"📩 Новая заявка:\n{text}\nОт: @{message.from_user.username}")
    
    await state.clear()
    await message.answer(
        "✅ **Сообщение отправлено!**\n\nСпасибо, мы скоро свяжемся с вами.",
        reply_markup=back_to_menu_keyboard(),
        parse_mode="Markdown"
    )
