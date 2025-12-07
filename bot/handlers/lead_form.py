from aiogram import Router, F, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
import logging

from bot.states import LeadForm
from core.config import settings
from core.database import save_lead

router = Router()

# Тексты вопросов
QUESTIONS = {
    'name': "Как к вам можно обращаться? (Ваше имя)",
    'role': "Какая у вас роль в компании?\n\n(Например: собственник, директор по продажам, HR-менеджер, руководитель отдела)",
    'company': "Как называется ваша компания?",
    'team_size': "Сколько примерно человек в вашем отделе/команде?\n\n(Можно ответить приблизительно: 5, 10-15, около 50 и т.п.)",
    'contacts': "Как с вами лучше связаться?\n\n(Напишите телефон и/или ссылку на ваш Telegram / e-mail)",
    'request': "Коротко опишите вашу ситуацию или запрос по персоналу:\n\n(Какие задачи или проблемы вы хотите обсудить?)"
}


def get_cancel_keyboard():
    """Keyboard with cancel button"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_lead")]
    ])


@router.callback_query(F.data == "start_lead_form")
async def start_lead_form(callback: CallbackQuery, state: FSMContext):
    """Start lead form"""
    await callback.message.edit_text(
        "📝 **Оставить заявку**\n\n"
        "Я задам вам несколько вопросов, чтобы наш менеджер мог лучше подготовиться к разговору с вами.\n\n"
        "Это займет не более 2-3 минут.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Начать", callback_data="begin_lead_form")],
            [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_lead")]
        ]),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "begin_lead_form")
async def begin_lead_form(callback: CallbackQuery, state: FSMContext):
    """Begin asking questions"""
    await callback.message.edit_text(
        f"❓ **Вопрос 1 из 6**\n\n{QUESTIONS['name']}",
       reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(LeadForm.waiting_for_name)


@router.message(LeadForm.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    """Process name input"""
    await state.update_data(name=message.text)
    await message.answer(
        f"❓ **Вопрос 2 из 6**\n\n{QUESTIONS['role']}",
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(LeadForm.waiting_for_role)


@router.message(LeadForm.waiting_for_role)
async def process_role(message: Message, state: FSMContext):
    """Process role input"""
    await state.update_data(role=message.text)
    await message.answer(
        f"❓ **Вопрос 3 из 6**\n\n{QUESTIONS['company']}",
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(LeadForm.waiting_for_company)


@router.message(LeadForm.waiting_for_company)
async def process_company(message: Message, state: FSMContext):
    """Process company input"""
    await state.update_data(company=message.text)
    await message.answer(
        f"❓ **Вопрос 4 из 6**\n\n{QUESTIONS['team_size']}",
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(LeadForm.waiting_for_team_size)


@router.message(LeadForm.waiting_for_team_size)
async def process_team_size(message: Message, state: FSMContext):
    """Process team size input"""
    await state.update_data(team_size=message.text)
    await message.answer(
        f"❓ **Вопрос 5 из 6**\n\n{QUESTIONS['contacts']}",
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(LeadForm.waiting_for_contacts)


@router.message(LeadForm.waiting_for_contacts)
async def process_contacts(message: Message, state: FSMContext):
    """Process contacts input"""
    await state.update_data(contacts=message.text)
    await message.answer(
        f"❓ **Вопрос 6 из 6** (последний)\n\n{QUESTIONS['request']}",
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(LeadForm.waiting_for_request)


@router.message(LeadForm.waiting_for_request)
async def process_request(message: Message, state: FSMContext):
    """Process final request and send to manager"""
    from core.dependencies import user_service, notification_service
    
    await state.update_data(request=message.text)
    
    # Get all collected data
    data = await state.get_data()
    
    try:
        # Save to database via Service
        # Note: submit_lead uses legacy lead table. If we want to use UserContact, we should use register_contact.
        # But lead_form collects specific lead fields (request). 
        # distinct from contact profile. So submit_lead is appropriate for now.
        contact_str = f"{data.get('name', 'N/A')} | {data.get('contacts', 'N/A')}"
        msg_str = f"Роль: {data.get('role', 'N/A')}\nКомпания: {data.get('company', 'N/A')}\nКоманда: {data.get('team_size', 'N/A')}\n\nЗапрос: {data.get('request', 'N/A')}"
        
        await user_service.submit_lead(
            name=data.get('name', 'N/A'),
            contact=data.get('contacts', 'N/A'),
            message=msg_str
        )
        
        # Send to manager via Service
        success = await notification_service.notify_new_lead(
            name=data.get('name', 'N/A'),
            contact=data.get('contacts', 'N/A'),
            message=msg_str,
            source="Bot Lead Form",
            username=message.from_user.username,
            user_id=message.from_user.id
        )
        
        if success:
            await message.answer(
                "✅ **Спасибо! Ваша заявка отправлена.**\n\n"
                f"Менеджер свяжется с вами в ближайшее время по указанным контактам:\n"
                f"{data.get('contacts', 'не указаны')}",
                parse_mode="Markdown"
            )
        else:
             # Fallback if notification fails (though service usually logs error and returns False)
             # But we generally shouldn't tell user it failed if DB save worked.
             # However, if manager notification is critical, we might warn.
             # Let's keep original behavior of showing success if DB worked, usually.
             # But existing code showed error.
             # Service returns bool.
            await message.answer(
                "✅ **Спасибо! Ваша заявка принята.**\n\n"
                f"Менеджер свяжется с вами в ближайшее время.",
                parse_mode="Markdown"
            )

    except Exception as e:
        logging.error(f"Failed to process lead form: {e}")
        await message.answer(
            "⚠️ Произошла ошибка при сохранении заявки.\n"
            "Пожалуйста, попробуйте позже или напишите нам напрямую.",
             parse_mode="Markdown"
        )
    
    # Clear state
    await state.clear()


@router.callback_query(F.data == "cancel_lead")
async def cancel_lead_form(callback: CallbackQuery, state: FSMContext):
    """Cancel lead form"""
    await state.clear()
    await callback.message.edit_text(
        "❌ Заполнение заявки прервано.\n\n"
        "Если понадобится, вы всегда можете начать снова из главного меню.",
        parse_mode="Markdown"
    )
