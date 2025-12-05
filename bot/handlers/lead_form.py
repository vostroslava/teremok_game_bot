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
    await state.update_data(request=message.text)
    
    # Get all collected data
    data = await state.get_data()
    
    # Save to database
    try:
        await save_lead(
            user_id=message.from_user.id,
            contact_info=f"{data.get('name', 'N/A')} | {data.get('contacts', 'N/A')}",
            message=f"Роль: {data.get('role', 'N/A')}\nКомпания: {data.get('company', 'N/A')}\nКоманда: {data.get('team_size', 'N/A')}\n\nЗапрос: {data.get('request', 'N/A')}"
        )
    except Exception as e:
        logging.error(f"Failed to save lead to database: {e}")
    
    # Send to manager
    success = await send_to_manager(message.bot, message.from_user, data)
    
    if success:
        await message.answer(
            "✅ **Спасибо! Ваша заявка отправлена.**\n\n"
            f"Менеджер свяжется с вами в ближайшее время по указанным контактам:\n"
            f"{data.get('contacts', 'не указаны')}",
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            "⚠️ Сейчас не получается отправить заявку менеджеру, попробуйте, пожалуйста, позже.\n\n"
            "Или свяжитесь с нами напрямую:\n"
            "📧 office@stalking.by\n"
            "📞 +375 29 113 113 2\n"
            "💬 @stalkermedia1",
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


async def send_to_manager(bot, user, data: dict) -> bool:
    """Send lead to manager chat"""
    if not settings.MANAGER_CHAT_ID:
        logging.error("MANAGER_CHAT_ID is not set in environment variables")
        return False
    
    # Format message for manager
    username = f"@{user.username}" if user.username else "не указан"
    
    manager_message = (
        "📩 **Новая заявка из бота \"Теремок\"**\n\n"
        f"👤 **Имя:** {data.get('name', 'Не указано')}\n"
        f"💼 **Роль:** {data.get('role', 'Не указано')}\n"
        f"🏢 **Компания:** {data.get('company', 'Не указано')}\n"
        f"👥 **Размер команды:** {data.get('team_size', 'Не указано')}\n"
        f"📞 **Контакты:** {data.get('contacts', 'Не указано')}\n\n"
        f"💬 **Запрос/ситуация:**\n{data.get('request', 'Не указано')}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"Данные из бота: {username} (ID: {user.id})"
    )
    
    try:
        await bot.send_message(
            chat_id=settings.MANAGER_CHAT_ID,
            text=manager_message,
            parse_mode="Markdown"
        )
        logging.info(f"Lead sent to manager from user {user.id}")
        return True
    except Exception as e:
        logging.error(f"Failed to send lead to manager: {e}")
        return False
