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
from core.database import get_all_leads # Legacy, todo: move to repo
from core.texts import TYPES_DATA
from core.dependencies import user_service

router = Router()


def is_owner(user_id: int) -> bool:
    """Check if user is the owner"""
    return user_id == settings.OWNER_ID


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Admin panel"""
    user_id = message.from_user.id
    
    # Check access
    if not is_owner(user_id) and not await user_service.is_admin(user_id):
        await message.answer("❌ У вас нет доступа к админ-панели.")
        return
    
    role = "👑 Владелец" if is_owner(user_id) else "👤 Админ"
    
    # Get stats
    stats = await user_service.get_statistics()
    
    # Build admin panel URL
    admin_url = ""
    if settings.ADMIN_PANEL_SECRET and settings.WEB_APP_URL:
        base_url = settings.WEB_APP_URL.rstrip('/')
        admin_url = f"{base_url}/app/admin?key={settings.ADMIN_PANEL_SECRET}"
    
    text = (
        f"🔐 <b>Админ-панель</b>\n\n"
        f"Ваша роль: {role}\n\n"
        f"📊 <b>Быстрая сводка:</b>\n"
        f"• Заявок: {stats.get('total_leads', 0)}\n"
        f"• Тестов: {stats.get('total_tests', 0)}\n"
    )
    
    if admin_url:
        text += (
            f"\n🌐 <b>Веб-админка:</b>\n"
            f"<a href=\"{admin_url}\">Открыть панель управления</a>\n\n"
        )
    
    text += (
        f"\n<b>Быстрые команды:</b>\n"
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
    
    await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)


@router.message(Command("leads"))
async def cmd_leads(message: Message):
    """View recent leads with quick stats"""
    user_id = message.from_user.id
    
    if not is_owner(user_id) and not await user_service.is_admin(user_id):
        await message.answer("❌ У вас нет доступа.")
        return
    
    # Get stats
    stats = await user_service.get_statistics()
    
    # Get leads (legacy call for complex query)
    leads = await get_all_leads(limit=5)
    
    text = (
        f"📋 <b>Сводка по лидам</b>\n\n"
        f"📊 <b>Статистика:</b>\n"
        f"• Сегодня: <b>{stats.get('leads_today', 0)}</b> лидов, <b>{stats.get('tests_today', 0)}</b> тестов\n"
        f"• За 7 дней: <b>{stats.get('leads_7d', 0)}</b> лидов, <b>{stats.get('tests_7d', 0)}</b> тестов\n"
        f"• Всего: <b>{stats.get('total_leads', 0)}</b> лидов, <b>{stats.get('total_tests', 0)}</b> тестов\n"
    )
    
    if leads:
        text += "\n📥 <b>Последние 5 заявок:</b>\n\n"
        for i, lead in enumerate(leads, 1):
            type_emoji = ""
            if lead.get('result_type'):
                type_info = TYPES_DATA.get(lead['result_type'])
                type_emoji = f" {type_info.emoji}" if type_info else ""
            
            status = lead.get('status', 'new')
            status_emoji = {'new': '🟢', 'in_progress': '🟡', 'done': '🔵', 'spam': '🔴'}.get(status, '⚪')
            
            text += (
                f"<b>{i}. {lead.get('name', 'Н/Д')}</b>{type_emoji} {status_emoji}\n"
                f"   📞 {lead.get('phone', '-')} | 💼 {lead.get('company', '-')}\n"
            )
    else:
        text += "\n📭 Заявок пока нет."
    
    # Add web admin link
    if settings.ADMIN_PANEL_SECRET and settings.WEB_APP_URL:
        base_url = settings.WEB_APP_URL.rstrip('/')
        admin_url = f"{base_url}/app/admin/leads?key={settings.ADMIN_PANEL_SECRET}"
        text += f"\n\n🔗 <a href=\"{admin_url}\">Подробнее в веб-админке</a>"
    
    await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """View detailed statistics"""
    user_id = message.from_user.id
    
    if not is_owner(user_id) and not await user_service.is_admin(user_id):
        await message.answer("❌ У вас нет доступа.")
        return
    
    stats = await user_service.get_statistics()
    admins = await user_service.get_admins()
    
    leads_count = stats.get('total_leads', 0)
    tests_count = stats.get('total_tests', 0)
    
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
    
    await user_service.add_admin(new_admin_id, username="unknown", role='admin', added_by=message.from_user.id)
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
    
    await user_service.remove_admin(admin_id)
    await message.answer(f"✅ Пользователь {admin_id} удалён из админов.")


@router.message(Command("admins"))
async def cmd_admins(message: Message):
    """List all admins"""
    if not is_owner(message.from_user.id):
        await message.answer("❌ Только владелец может смотреть список админов.")
        return
    
    admins = await user_service.get_admins()
    
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
