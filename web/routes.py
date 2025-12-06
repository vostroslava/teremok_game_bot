from fastapi import FastAPI, APIRouter, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from core.texts import TYPES_DATA
from core.database import save_lead, has_contact, get_contact, save_contact, save_test_result
from core.config import settings
from core.telegram_checks import is_subscribed_to_required_channel
from core.logic import calculate_result
import os
import logging

logger = logging.getLogger(__name__)

app = FastAPI()
router = APIRouter()

# Bot instance for notifications (will be set from main.py)
bot_instance = None

def set_bot(bot):
    global bot_instance
    bot_instance = bot

# API Endpoint to get types
@router.get("/api/types")
async def get_types():
    # Convert dataclasses to dicts
    return {k: v.__dict__ for k, v in TYPES_DATA.items()}

# ==== NEW: Check subscription endpoint ====
@router.get("/api/check-subscription")
async def check_subscription(user_id: int):
    """
    Проверяет подписку пользователя на обязательный канал
    
    Query params:
        user_id: Telegram user_id
    """
    if not bot_instance:
        return JSONResponse({"subscribed": False, "error": "Bot not initialized"})
    
    is_subscribed = await is_subscribed_to_required_channel(bot_instance, user_id)
    
    return JSONResponse({
        "subscribed": is_subscribed,
        "channel_username": settings.REQUIRED_CHANNEL_USERNAME
    })

# ==== NEW: Save contacts endpoint ====
@router.post("/api/contacts")
async def save_user_contacts(request: Request):
    """
    Сохранение контактных данных пользователя
    
    Expected JSON:
        {
            "user_id": int,
            "name": str,
            "role": str,
            "company": str,
            "team_size": str,
            "phone": str,
            "username": str (optional)
        }
    """
    try:
        data = await request.json()
        
        await save_contact(
            user_id=data['user_id'],
            name=data['name'],
            role=data['role'],
            company=data.get('company', ''),
            team_size=data['team_size'],
            phone=data['phone'],
            telegram_username=data.get('username')
        )
        
        logger.info(f"Contacts saved for user {data['user_id']}")
        
        return JSONResponse({"status": "success", "message": "Контакты сохранены"})
        
    except Exception as e:
        logger.error(f"Failed to save contacts: {e}")
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500
        )

# ==== NEW: Submit test results endpoint ====
@router.post("/api/test/submit")
async def submit_test_results(request: Request):
    """
    Сохранение результатов теста и отправка уведомления менеджеру
    
    Expected JSON:
        {
            "user_id": int,
            "answers": dict  # Ответы на вопросы теста
        }
    """
    try:
        data = await request.json()
        user_id = data['user_id']
        answers = data['answers']
        
        # Подсчёт результата
        result = calculate_result(answers)
        result_type = result['type']
        
        # Сохранение в БД
        try:
            await save_test_result(user_id, result_type, answers)
            logger.info(f"Test result saved for user {user_id}: {result_type}")
        except Exception as e:
            logger.error(f"Failed to save test result: {e}")
        
        # Получаем контакты (если есть)
        contact = await get_contact(user_id)
        
        # Отправляем уведомление менеджеру
        if bot_instance and settings.MANAGER_CHAT_ID:
            await send_test_notification_to_manager(
                bot=bot_instance,
                user_id=user_id,
                contact=contact,
                result_type=result_type,
                answers=answers
            )
        
        # Возвращаем результат пользователю
        type_info = TYPES_DATA.get(result_type)
        
        return JSONResponse({
            "status": "success",
            "result": {
                "type": result_type,
                "emoji": type_info.emoji if type_info else "",
                "name": type_info.name_ru if type_info else result_type,
                "description": type_info.short_desc if type_info else ""
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to submit test results: {e}")
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500
        )


async def send_test_notification_to_manager(bot, user_id: int, contact: dict, result_type: str, answers: dict):
    """
    Отправляет уведомление менеджеру о прохождении теста
    
    Args:
        bot: Экземпляр Bot
        user_id: Telegram user_id
        contact: Словарь с контактами или None
        result_type: Результат теста (тип сотрудника)
        answers: Словарь с ответами на вопросы
    """
    type_info = TYPES_DATA.get(result_type)
    
    # Формируем блок с контактами
    if contact:
        contact_info = (
            f"👤 **Имя:** {contact.get('name', 'Н/Д')}\n"
            f"💼 **Роль:** {contact.get('role', 'Н/Д')}\n"
            f"🏢 **Компания:** {contact.get('company', 'Н/Д')}\n"
            f"👥 **Размер команды:** {contact.get('team_size', 'Н/Д')}\n"
            f"📞 **Телефон:** {contact.get('phone', 'Н/Д')}\n"
            f"💬 **Telegram:** @{contact.get('telegram_username', 'не указан')}\n"
        )
    else:
        contact_info = "📢 **Подписан на канал, контакты не оставлены**\n"
    
    # Формируем сообщение
    message = (
        f"🎯 **Пользователь прошёл тест \"Теремок\"**\n\n"
        f"{contact_info}"
        f"🆔 **user_id:** `{user_id}`\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"**Результаты теста:**\n\n"
    )
    
    if type_info:
        message += (
            f"{type_info.emoji} **Типаж:** {type_info.name_ru}\n\n"
            f"**Описание:**\n{type_info.short_desc}\n\n"
        )
        
        # Добавляем маркеры если есть
        if type_info.markers:
            markers_text = "\n".join([f"• {m}" for m in type_info.markers[:5]])
            message += f"**Ключевые маркеры:**\n{markers_text}\n\n"
    else:
        message += f"**Типаж:** {result_type}\n\n"
    
    try:
        await bot.send_message(
            chat_id=settings.MANAGER_CHAT_ID,
            text=message,
            parse_mode="Markdown"
        )
        logger.info(f"Test notification sent to manager for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to send notification to manager: {e}")


# Legacy endpoint (keep for backwards compatibility)
@router.post("/api/submit-lead")
async def submit_lead(request: Request):
    try:
        data = await request.json()
        name = data.get("name", "Не указано")
        contact = data.get("contact", "Не указано")
        message = data.get("message", "")
        result_type = data.get("result_type", "")
        
        # Save to database
        await save_lead(
            user_id=0,  # Web user
            contact_info=f"{name} | {contact}",
            message=f"Результат: {result_type}\n\n{message}" if result_type else message
        )
        
        # Send to manager if bot is available (legacy behavior)
        if bot_instance and settings.MANAGER_CHAT_ID:
            notification_text = (
                "📩 **Новая заявка с веб-приложения!**\n\n"
                f"👤 **Имя:** {name}\n"
                f"📞 **Контакт:** {contact}\n"
            )
            if result_type:
                notification_text += f"🎯 **Результат диагностики:** {result_type}\n"
            if message:
                notification_text += f"\n💬 **Сообщение:**\n{message}"
            
            try:
                await bot_instance.send_message(
                    chat_id=settings.MANAGER_CHAT_ID,
                    text=notification_text,
                    parse_mode="Markdown"
                )
            except Exception as e:
                print(f"Failed to send notification: {e}")
        
        return JSONResponse({"status": "success", "message": "Заявка отправлена!"})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

# Mount specific routes first
app.include_router(router)

# Serve static files
# We need to get absolute path to avoid issues
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(static_path, "index.html"))

# For detailed view if we want deep linking in future
@app.get("/type/{type_id}")
async def read_type_page(type_id: str):
    return FileResponse(os.path.join(static_path, "index.html"))
