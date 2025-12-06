"""
Проверка подписки на Telegram канал
"""
import logging
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramAPIError
from core.config import settings

logger = logging.getLogger(__name__)


async def is_subscribed_to_required_channel(bot: Bot, user_id: int) -> bool:
    """
    Проверяет подписку пользователя на обязательный канал.
    
    Args:
        bot: Экземпляр aiogram Bot
        user_id: Telegram user_id пользователя
        
    Returns:
        True если пользователь подписан на канал, False если нет или произошла ошибка
    """
    # Проверяем, включена ли проверка подписки
    if not settings.CHECK_SUBSCRIPTION_ENABLED:
        logger.info("Проверка подписки отключена в конфигурации")
        return False
    
    try:
        # Формируем username канала с @
        channel = f"@{settings.REQUIRED_CHANNEL_USERNAME}"
        
        # Запрашиваем информацию о участнике канала
        member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        
        # Статусы, при которых считаем пользователя подписанным
        subscribed = member.status in ["member", "administrator", "creator"]
        
        logger.info(
            f"Проверка подписки для user_id={user_id}: "
            f"status={member.status}, subscribed={subscribed}"
        )
        
        return subscribed
        
    except (TelegramBadRequest, TelegramForbiddenError) as e:
        # Бот не добавлен в канал или нет необходимых прав
        logger.error(
            f"Не удалось проверить подписку для user_id={user_id}. "
            f"Возможно, бот не добавлен в канал {settings.REQUIRED_CHANNEL_USERNAME}: {e}"
        )
        return False
        
    except TelegramAPIError as e:
        # Другие ошибки API Telegram
        logger.error(f"Ошибка Telegram API при проверке подписки: {e}")
        return False
        
    except Exception as e:
        # Непредвиденные ошибки
        logger.error(f"Неожиданная ошибка при проверке подписки: {e}")
        return False
