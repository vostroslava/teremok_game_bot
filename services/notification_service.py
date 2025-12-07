from aiogram import Bot
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, bot: Bot = None):
        self.bot = bot

    def set_bot(self, bot: Bot):
        """Set bot instance for sending notifications"""
        self.bot = bot

    def get_bot_instance(self):
        """Get bot instance"""
        return self.bot

    async def notify_manager(self, text: str, parse_mode: str = "HTML") -> bool:
        """Send message to manager chat"""
        if not self.bot:
            logger.warning("NotificationService: Bot instance not set")
            return False
            
        if not settings.MANAGER_CHAT_ID:
            logger.warning("NotificationService: MANAGER_CHAT_ID not set")
            return False
            
        try:
            await self.bot.send_message(
                chat_id=settings.MANAGER_CHAT_ID,
                text=text,
                parse_mode=parse_mode
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send notification to manager: {e}")
            return False

    async def notify_new_lead(self, name: str, contact: str, message: str = None, 
                              result_type: str = None, source: str = "Bot", 
                              username: str = None, user_id: int = None) -> bool:
        """Format and send new lead notification"""
        text = (
            f"📩 <b>Новая заявка ({source})</b>\n\n"
            f"👤 <b>Имя:</b> {name}\n"
            f"📞 <b>Контакт:</b> {contact}\n"
        )
        
        if result_type:
            text += f"🎯 <b>Результат:</b> {result_type}\n"
            
        if message:
            text += f"\n💬 <b>Сообщение:</b>\n{message}"
            
        if username or user_id:
            user_str = f"@{username}" if username else "без username"
            id_str = f"(ID: <code>{user_id}</code>)" if user_id else ""
            text += f"\n\n_От:_ {user_str} {id_str}"

        return await self.notify_manager(text)

    async def notify_test_result(self, result_type: str, answers: dict = None, 
                                 contact: dict = None, user_id: int = None, 
                                 product: str = "teremok", scores: dict = None) -> bool:
        """Format and send test result notification"""
        from core.texts import TYPES_DATA
        
        product_name = "Теремок" if product == "teremok" else "Формула команды"
        type_info = TYPES_DATA.get(result_type)
        type_emoji = type_info.emoji if type_info else "🎯"
        type_name = type_info.name_ru if type_info else result_type
        
        text = (
            f"🧩 <b>Прохождение теста ({product_name})</b>\n\n"
            f"{type_emoji} <b>Результат:</b> {type_name}\n"
        )
        
        if scores:
             # Basic score summary if needed, or skip to keep it clean
             pass
             
        if contact:
            text += (
                f"\n👤 <b>Пользователь:</b>\n"
                f"• Имя: {contact.get('name', 'Не указано')}\n"
                f"• Роль: {contact.get('role', 'Не указано')}\n"
                f"• Компания: {contact.get('company', 'Не указано')}\n"
                f"• Телефон: {contact.get('phone', 'Не указано')}\n"
            )
        
        if user_id:
            text += f"\n🆔 ID: <code>{user_id}</code>"
            
        return await self.notify_manager(text)
