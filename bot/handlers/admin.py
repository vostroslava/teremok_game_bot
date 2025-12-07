"""
Admin handlers for the bot.
Commands:
- /admin - Admin panel
- /leads - View recent leads
- /stats - View statistics
- /addadmin <user_id> - Add admin (owner only)
- /deladmin <user_id> - Remove admin (owner only)
- /admins - List admins
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from core.config import settings
from core.database import (
    is_admin, get_admin_role, add_admin, remove_admin, 
    get_all_admins, get_all_leads, get_leads_count, get_tests_count
)
from core.texts import TYPES_DATA

router = Router()


def is_owner(user_id: int) -> bool:
    """Check if user is the owner"""
    return user_id == settings.OWNER_ID


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Admin panel"""
    user_id = message.from_user.id
    
    # Check access
    if not is_owner(user_id) and not await is_admin(user_id):
        await message.answer("❌ У вас нет доступа к админ-панели.")
        return
    
    role = "👑 Владелец" if is_owner(user_id) else "👤 Админ"
    
    # Get stats
    leads_count = await get_leads_count()
    tests_count = await get_tests_count()
    
    text = (
        f"🔐 <b>Админ-панель</b>\n\n"
        f"Ваша роль: {role}\n\n"
        f"📊 <b>Статистика:</b>\n"
        f"• Заявок (контактов): {leads_count}\n"
        f"• Пройденных тестов: {tests_count}\n\n"
        f"<b>Команды:</b>\n"
        f"/leads — Последние заявки\n"
        f"/stats — Подробная статистика\n"
    )
    
    if is_owner(user_id):
        text += (
            f"\n<b>Управление (только владелец):</b>\n"
            f"/addadmin &lt;user_id&gt; — Добавить админа\n"
            f"/deladmin &lt;user_id&gt; — Удалить админа\n"
            f"/admins — Список админов\n"
        )
    
    await message.answer(text, parse_mode="HTML")


@router.message(Command("leads"))
async def cmd_leads(message: Message):
    """View recent leads"""
    user_id = message.from_user.id
    
    if not is_owner(user_id) and not await is_admin(user_id):
        await message.answer("❌ У вас нет доступа.")
        return
    
    leads = await get_all_leads(limit=10)
    
    if not leads:
        await message.answer("📭 Заявок пока нет.")
        return
    
    text = "📋 <b>Последние заявки:</b>\n\n"
    
    for i, lead in enumerate(leads, 1):
        type_emoji = ""
        if lead.get('result_type'):
            type_info = TYPES_DATA.get(lead['result_type'])
            type_emoji = f" {type_info.emoji}" if type_info else ""
        
        text += (
            f"<b>{i}. {lead.get('name', 'Н/Д')}</b>{type_emoji}\n"
            f"   📞 {lead.get('phone', '-')}\n"
            f"   💼 {lead.get('role', '-')} @ {lead.get('company', '-')}\n"
            f"   👥 {lead.get('team_size', '-')}\n"
        )
        
        if lead.get('telegram_username'):
            text += f"   💬 @{lead['telegram_username']}\n"
        
        if lead.get('result_type'):
            type_info = TYPES_DATA.get(lead['result_type'])
            type_name = type_info.name_ru if type_info else lead['result_type']
            text += f"   🧾 Тест: {type_name}\n"
        
        text += "\n"
    
    await message.answer(text, parse_mode="HTML")


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """View detailed statistics"""
    user_id = message.from_user.id
    
    if not is_owner(user_id) and not await is_admin(user_id):
        await message.answer("❌ У вас нет доступа.")
        return
    
    leads_count = await get_leads_count()
    tests_count = await get_tests_count()
    admins = await get_all_admins()
    
    text = (
        f"📊 <b>Статистика</b>\n\n"
        f"📋 Всего заявок: <b>{leads_count}</b>\n"
        f"🧾 Пройдено тестов: <b>{tests_count}</b>\n"
        f"👥 Админов: <b>{len(admins)}</b>\n\n"
        f"Конверсия (тесты/заявки): <b>{(tests_count/leads_count*100) if leads_count > 0 else 0:.1f}%</b>\n"
    )
    
    await message.answer(text, parse_mode="HTML")


@router.message(Command("addadmin"))
async def cmd_addadmin(message: Message):
    """Add admin (owner only)"""
    if not is_owner(message.from_user.id):
        await message.answer("❌ Только владелец может добавлять админов.")
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer(
            "Использование: /addadmin &lt;user_id&gt;\n\n"
            "Чтобы узнать user_id пользователя, попросите его отправить /id боту.",
            parse_mode="HTML"
        )
        return
    
    try:
        new_admin_id = int(args[1])
    except ValueError:
        await message.answer("❌ user_id должен быть числом.")
        return
    
    await add_admin(new_admin_id, role='admin', added_by=message.from_user.id)
    await message.answer(f"✅ Пользователь {new_admin_id} добавлен как админ.")


@router.message(Command("deladmin"))
async def cmd_deladmin(message: Message):
    """Remove admin (owner only)"""
    if not is_owner(message.from_user.id):
        await message.answer("❌ Только владелец может удалять админов.")
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Использование: /deladmin &lt;user_id&gt;", parse_mode="HTML")
        return
    
    try:
        admin_id = int(args[1])
    except ValueError:
        await message.answer("❌ user_id должен быть числом.")
        return
    
    await remove_admin(admin_id)
    await message.answer(f"✅ Пользователь {admin_id} удалён из админов.")


@router.message(Command("admins"))
async def cmd_admins(message: Message):
    """List all admins"""
    if not is_owner(message.from_user.id):
        await message.answer("❌ Только владелец может смотреть список админов.")
        return
    
    admins = await get_all_admins()
    
    if not admins:
        text = "👥 Админов нет.\n\nДобавить: /addadmin &lt;user_id&gt;"
    else:
        text = "👥 <b>Список админов:</b>\n\n"
        for admin in admins:
            username = f"@{admin['username']}" if admin.get('username') else ''
            text += f"• {admin['user_id']} {username} ({admin['role']})\n"
    
    await message.answer(text, parse_mode="HTML")


@router.message(Command("id"))
async def cmd_id(message: Message):
    """Get user ID"""
    await message.answer(
        f"🆔 Ваш user_id: <code>{message.from_user.id}</code>\n\n"
        f"Отправьте это владельцу бота, чтобы он мог добавить вас как админа.",
        parse_mode="HTML"
    )
