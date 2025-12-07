from fastapi import FastAPI, APIRouter, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from core.texts import TYPES_DATA, get_types_for_api
from core.database import save_lead, has_contact, get_contact, save_contact, save_test_result
from core.config import settings
from core.telegram_checks import is_subscribed_to_required_channel
from core.logic import calculate_result, DIAGNOSTIC_QUESTIONS
import os
import logging
import aiosqlite

logger = logging.getLogger(__name__)

app = FastAPI()
router = APIRouter()

# Jinja2 templates for new app pages
templates_path = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_path)

# Bot instance for notifications (will be set from main.py)
bot_instance = None

def set_bot(bot):
    global bot_instance
    bot_instance = bot

# API Endpoint to get types (legacy, for compatibility)
@router.get("/api/types")
async def get_types():
    # Convert dataclasses to dicts
    return {k: v.__dict__ for k, v in TYPES_DATA.items()}

# API Endpoint to get Teremok types with full info
@router.get("/api/teremok/types")
async def get_teremok_types():
    """Return all Teremok types with full descriptions for UI"""
    from core.texts import get_types_for_api
    return {"types": get_types_for_api()}

# API Endpoint to get Teremok test questions
@router.get("/api/teremok/questions")
async def get_teremok_questions():
    """Return all diagnostic questions for Teremok test"""
    questions = []
    for q in DIAGNOSTIC_QUESTIONS:
        questions.append({
            "id": q.id,
            "text": q.text,
            "options": [{"text": opt["text"], "index": i} for i, opt in enumerate(q.options)]
        })
    return {"questions": questions, "total": len(questions)}

# ==== NEW: Check subscription endpoint ====
@router.get("/api/check-subscription")
async def check_subscription(user_id: int):
    """
    Проверяет подписку пользователя на обязательный канал и наличие контактов
    
    Query params:
        user_id: Telegram user_id
    
    Returns:
        subscribed: bool - подписан ли на канал
        has_contact: bool - оставлены ли контакты ранее
        channel_username: str - username канала
    """
    if not bot_instance:
        return JSONResponse({"subscribed": False, "has_contact": False, "error": "Bot not initialized"})
    
    # Проверяем подписку на канал
    is_subscribed = await is_subscribed_to_required_channel(bot_instance, user_id)
    
    # Проверяем наличие контактов в БД
    user_has_contact = await has_contact(user_id)
    
    return JSONResponse({
        "subscribed": is_subscribed,
        "has_contact": user_has_contact,
        "channel_username": settings.REQUIRED_CHANNEL_USERNAME
    })

# ==== NEW: Save contacts endpoint ====
@router.post("/api/contacts")
async def save_user_contacts(request: Request):
    """
    Сохранение контактных данных пользователя и отправка уведомления менеджеру
    
    Expected JSON:
        {
            "user_id": int,
            "name": str,
            "role": str,
            "company": str,
            "team_size": str,
            "phone": str,
            "username": str (optional),
            "product": str (optional, default "teremok")
        }
    """
    try:
        data = await request.json()
        user_id = data['user_id']
        product = data.get('product', 'teremok')
        
        await save_contact(
            user_id=user_id,
            name=data['name'],
            role=data['role'],
            company=data.get('company', ''),
            team_size=data['team_size'],
            phone=data['phone'],
            telegram_username=data.get('username')
        )
        
        logger.info(f"Contacts saved for user {user_id}")
        
        # Отправляем короткое уведомление менеджеру
        if bot_instance and settings.MANAGER_CHAT_ID:
            try:
                await bot_instance.send_message(
                    chat_id=settings.MANAGER_CHAT_ID,
                    text="📬 <b>Новая заявка!</b>\n\nИспользуйте /leads чтобы посмотреть детали.",
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Failed to send notification: {e}")
        
        # Экспорт в Google Sheets
        try:
            from core.google_sheets import export_lead_to_sheets
            await export_lead_to_sheets({
                "user_id": user_id,
                "name": data['name'],
                "role": data['role'],
                "company": data.get('company', ''),
                "team_size": data['team_size'],
                "phone": data['phone'],
                "telegram_username": data.get('username')
            })
        except Exception as e:
            logger.error(f"Failed to export lead to sheets: {e}")
        
        return JSONResponse({
            "status": "success", 
            "message": "Контакты сохранены"
        })
        
    except Exception as e:
        logger.error(f"Failed to save contacts: {e}")
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500
        )


async def send_contact_notification_to_manager(bot, user_id: int, data: dict, product: str = "teremok"):
    """
    Отправляет первое уведомление менеджеру о новом лиде (контакты)
    """
    product_emoji = "🐭" if product == "teremok" else "⚙️"
    product_name = "Теремок" if product == "teremok" else "Формула команды"
    
    tg_username = data.get('username') or 'не указан'
    tg_link = f"@{tg_username}" if tg_username != 'не указан' else 'не указан'
    
    message = (
        f"{product_emoji} <b>Новая заявка ({product_name})</b>\n\n"
        f"👤 <b>Имя:</b> {data.get('name', 'Н/Д')}\n"
        f"💼 <b>Роль:</b> {data.get('role', 'Н/Д')}\n"
        f"🏢 <b>Компания:</b> {data.get('company', 'Н/Д')}\n"
        f"👥 <b>Размер команды:</b> {data.get('team_size', 'Н/Д')}\n"
        f"📞 <b>Телефон:</b> {data.get('phone', 'Н/Д')}\n"
        f"💬 <b>Telegram:</b> {tg_link}\n"
        f"🆔 <b>user_id:</b> <code>{user_id}</code>\n\n"
        f"📝 <i>Пользователь заполнил контактную форму</i>"
    )
    
    try:
        await bot.send_message(
            chat_id=settings.MANAGER_CHAT_ID,
            text=message,
            parse_mode="HTML"
        )
        logger.info(f"Contact notification sent to manager for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to send contact notification to manager: {e}")

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
        test_id = 0
        try:
            test_id = await save_test_result(
                user_id=user_id, 
                result_type=result_type, 
                answers=answers,
                scores=result.get('scores', {}),
                product='teremok'
            )
            logger.info(f"Test result saved for user {user_id}: {result_type} (ID: {test_id})")
        except Exception as e:
            logger.error(f"Failed to save test result: {e}")
        
        # Получаем контакты (если есть)
        contact = await get_contact(user_id)
        
        # Отправляем уведомление менеджеру только если включено
        if settings.SEND_NOTIFICATIONS and bot_instance and settings.MANAGER_CHAT_ID:
            await send_test_notification_to_manager(
                bot=bot_instance,
                user_id=user_id,
                contact=contact,
                result_type=result_type,
                answers=answers
            )
        
        # Экспорт в Google Sheets
        try:
            # We add test_id just in case, though google sheets logic might not use it yet
            from core.google_sheets import export_test_to_sheets
            await export_test_to_sheets(
                test={"user_id": user_id, "result_type": result_type, "scores": result.get('scores', {}), "product": "teremok", "test_id": test_id},
                lead=contact
            )
        except Exception as e:
            logger.error(f"Failed to export test to sheets: {e}")
        
        return JSONResponse({
            "status": "success",
            "result_id": test_id,
        })
        
    except Exception as e:
        logger.error(f"Error in submit_test_results: {e}")
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500
        )

@router.get("/app/teremok/result/{result_id}", response_class=HTMLResponse)
async def teremok_result_page(request: Request, result_id: int):
    """Страница результата теста"""
    try:
        # Fetch result from DB
        # We need a new detailed getter or just generic query
        # Since we don't have get_test_result_by_id in db yet, let's look at available methods
        # Or add a quick one right here or in db
        async with aiosqlite.connect(settings.DB_NAME) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM test_results WHERE id = ?", (result_id,)) as cursor:
                row = await cursor.fetchone()
                
        if not row:
            return HTMLResponse("<h1>Результат не найден</h1>", status_code=404)
            
        result = dict(row)
        
        # Get detailed type info
        type_info = TYPES_DATA.get(result['result_type'])
        if not type_info:
            # Fallback for unknown type
            type_info = TYPES_DATA.get("bird") 
            
        # Parse scores if stored as string
        scores = result['scores']
        if isinstance(scores, str):
            try:
                import json
                scores = json.loads(scores)
            except:
                scores = {}
                
        # Get types data for the chart
        all_types = get_types_for_api()
        
        return templates.TemplateResponse("teremok/result.html", {
            "request": request,
            "result": result,
            "type_info": type_info,
            "scores": scores,
            "all_types": all_types
        })
    except Exception as e:
        logger.error(f"Error loading result page: {e}")
        return HTMLResponse(f"<h1>Ошибка загрузки результата</h1><p>{str(e)}</p>", status_code=500)
        


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
        tg_username = contact.get('telegram_username') or 'не указан'
        tg_link = f"@{tg_username}" if tg_username != 'не указан' else 'не указан'
        contact_info = (
            f"👤 <b>Имя:</b> {contact.get('name', 'Н/Д')}\n"
            f"💼 <b>Роль:</b> {contact.get('role', 'Н/Д')}\n"
            f"🏢 <b>Компания:</b> {contact.get('company', 'Н/Д')}\n"
            f"👥 <b>Размер команды:</b> {contact.get('team_size', 'Н/Д')}\n"
            f"📞 <b>Телефон:</b> {contact.get('phone', 'Н/Д')}\n"
            f"💬 <b>Telegram:</b> {tg_link}\n"
        )
    else:
        contact_info = "📢 <b>Подписан на канал, контакты не оставлены</b>\n"
    
    # Формируем сообщение
    message = (
        f"🎯 <b>Пользователь прошёл тест «Теремок»</b>\n\n"
        f"{contact_info}"
        f"🆔 <b>user_id:</b> <code>{user_id}</code>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>Результаты теста:</b>\n\n"
    )
    
    if type_info:
        message += (
            f"{type_info.emoji} <b>Типаж:</b> {type_info.name_ru}\n\n"
            f"<b>Описание:</b>\n{type_info.short_desc}\n\n"
        )
        
        # Добавляем маркеры если есть
        if type_info.markers:
            markers_text = "\n".join([f"• {m}" for m in type_info.markers[:5]])
            message += f"<b>Ключевые маркеры:</b>\n{markers_text}\n\n"
    else:
        message += f"<b>Типаж:</b> {result_type}\n\n"
    
    try:
        await bot.send_message(
            chat_id=settings.MANAGER_CHAT_ID,
            text=message,
            parse_mode="HTML"
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

# ==== NEW: App Page Routes (Jinja2 templates) ====

# Hub
@app.get("/app/hub")
async def app_hub(request: Request):
    return templates.TemplateResponse("hub.html", {"request": request})

# Teremok section
@app.get("/app/teremok/overview")
async def teremok_overview(request: Request):
    return templates.TemplateResponse("teremok/overview.html", {"request": request})

@app.get("/app/teremok/self_test")
async def teremok_self_test(request: Request):
    return templates.TemplateResponse("teremok/self_test.html", {"request": request})

@app.get("/app/teremok/types_overview")
async def teremok_types_overview(request: Request):
    return templates.TemplateResponse("teremok/types_overview.html", {"request": request})

@app.get("/app/teremok/cases")
async def teremok_cases(request: Request):
    return templates.TemplateResponse("teremok/cases.html", {"request": request})

# ==== NEW: Formula Module Routes ====

# API: Get questions
@router.get("/api/formula/questions")
async def get_formula_questions():
    from core.formula_logic import FORMULA_QUESTIONS, FORMULA_OPTIONS
    questions = [
        {
            "id": q.id,
            "text": q.text,
            "options": FORMULA_OPTIONS
        }
        for q in FORMULA_QUESTIONS
    ]
    return {"questions": questions, "total": len(questions)}


# ===== FORMULA (RSP) MODULE =====

@app.get("/api/formula/rsp/questions")
async def get_formula_rsp_questions():
    """Get questions for Formula RSP test"""
    from core.formula_rsp_questions import FORMULA_RSP_QUESTIONS
    return JSONResponse({"questions": FORMULA_RSP_QUESTIONS})

@app.post("/api/formula/rsp/submit")
async def submit_formula_rsp_results(request: Request):
    try:
        data = await request.json()
        user_id = data.get('user_id')
        # employee_name/role might not be sent if we skipped form (subscribed user)
        # So we try to get them, but don't force save_contact if they are missing
        
        name = data.get('employee_name')
        role = data.get('employee_role')
        answers = data.get('answers') 
        
        if not user_id or not answers:
             # Random ID for guest flow if missing
             if not user_id: 
                 import random
                 user_id = random.randint(1000000, 9999999)
        
        # Ensure contact exists (Guest or Subscribed)
        from core.database import has_contact, save_contact, get_contact
        
        user_has_contact = await has_contact(user_id)
        
        # If we have explicit Name/Role in payload (from Form), update/save contact
        if name and role:
             await save_contact(
                user_id=user_id,
                name=name,
                role=role,
                company="", # We might not catch company in this payload if simplified form
                team_size="",
                phone="",
                telegram_username=None,
                product="formula_rsp"
            )
        elif not user_has_contact:
            # No contact and no payload -> Create guest
             await save_contact(
                user_id=user_id,
                name="Guest User",
                role="Guest",
                company="",
                team_size="",
                phone="",
                telegram_username=None,
                product="formula_rsp"
            )

        # Calculate result
        from core.formula_rsp_logic import compute_formula_rsp
        result = compute_formula_rsp(answers)
        
        # Save to DB (New table)
        from core.database import save_formula_rsp_result
        
        test_id = await save_formula_rsp_result(
            user_id=user_id,
            primary_code=result.primary_code,
            primary_name=result.primary_name,
            scores=result.scores,
            answers=answers
        )
        
        logger.info(f"Formula RSP result saved for {user_id}: {result.primary_code} (ID: {test_id})")
        
        # Export to Google Sheets
        contact = await get_contact(user_id)
        try:
            from core.google_sheets import export_test_to_sheets
            # Adapt export function to handle RSP structure
            # We'll pass scores dict directly
            await export_test_to_sheets(
                test={
                    "user_id": user_id, 
                    "result_type": result.primary_name,
                    "scores": result.scores,
                    "product": "formula_rsp",
                    "test_id": test_id,
                    "name": name,
                    "role": role 
                },
                lead=contact
            )
        except Exception as e:
            logger.error(f"Failed to export Formula RSP to sheets: {e}")

        # Return result
        return JSONResponse({
            "status": "success",
            "result": {
                "id": test_id,
                "primary_code": result.primary_code,
                "primary_name": result.primary_name,
                "secondary_codes": result.secondary_codes,
                "scores": result.scores,
                "description": result.description,
                "recommendations": result.recommendations,
                "emoji": result.emoji
            }
        })

    except Exception as e:
        logger.error(f"Error in submit_formula_rsp_results: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@app.get("/app/formula/self_test", response_class=HTMLResponse)
async def formula_self_test_page(request: Request):
    """Main page for Formula RSP test"""
    return templates.TemplateResponse("formula/rsp_test.html", {"request": request})

@app.get("/app/formula/info", response_class=HTMLResponse)
async def formula_info_page(request: Request):
    """Info page redirected to test or separate info"""
    # For now, let's keep it as separate info page or redirect to test?
    # User asked for /app/formula/info as optional, but let's make it render a simple info page 
    # OR reuse the one we had but adapted. 
    # Actually, let's redirect to rsp_test as the landing for now if simpler
    return templates.TemplateResponse("formula/rsp_test.html", {"request": request})




@app.get("/app/formula/overview", response_class=HTMLResponse)
async def formula_overview_page(request: Request):
    return templates.TemplateResponse("formula/overview.html", {"request": request})

@app.get("/app/formula")
async def formula_root_redirect(request: Request):
    return RedirectResponse(url="/app/formula/overview")



@app.get("/app/formula/types", response_class=HTMLResponse)
async def formula_types_page(request: Request):
    return templates.TemplateResponse("formula/types.html", {"request": request})

@app.get("/app/formula/situations", response_class=HTMLResponse)
async def formula_situations_page(request: Request):
    return templates.TemplateResponse("formula/situations.html", {"request": request})

@app.get("/app/formula/result/{test_id}")
async def formula_result_page(request: Request, test_id: int):
    try:
        async with aiosqlite.connect(settings.DB_NAME) as db:
            db.row_factory = aiosqlite.Row
            # Use formula_rsp_results table
            async with db.execute("SELECT * FROM formula_rsp_results WHERE id = ?", (test_id,)) as cursor:
                row = await cursor.fetchone()
        
        if not row:
            return HTMLResponse("<h1>Результат не найден</h1>", status_code=404)
            
        row_dict = dict(row)
        
        # Get detailed type info from RSP types
        from core.formula_rsp_types import get_rsp_type, FORMULA_RSP_TYPES
        
        # primary_type_code field from DB
        type_code = row_dict['primary_type_code']
        type_info = get_rsp_type(type_code)
        
        if not type_info:
            # Fallback
            type_info = get_rsp_type("result")
             
        # Parse scores
        import json
        try:
             scores = json.loads(row_dict['scores']) if isinstance(row_dict['scores'], str) else row_dict['scores']
        except:
             scores = {}
             
        # All types for chart
        all_types = list(FORMULA_RSP_TYPES.values())
             
        return templates.TemplateResponse("formula/result.html", {
            "request": request,
            "type_info": type_info,
            "scores": scores,
            "all_types": all_types
        })
            
    except Exception as e:
        logger.error(f"Error loading Formula result page: {e}")
        return HTMLResponse(f"<h1>Ошибка загрузки</h1><p>{e}</p>", status_code=500)


# Formula section placeholders (kept or redirected)
@app.get("/app/formula/team_quiz")
async def formula_team_quiz(request: Request):
    return RedirectResponse(url="/app/formula/self_test")

@app.get("/app/formula/matrix")
async def formula_matrix(request: Request):
    return templates.TemplateResponse("formula/matrix.html", {"request": request})

@app.get("/app/formula/mistakes")
async def formula_mistakes(request: Request):
    return templates.TemplateResponse("formula/mistakes.html", {"request": request})

# Channel
@app.get("/app/channel")
async def app_channel(request: Request):
    return templates.TemplateResponse("channel.html", {"request": request})

# Mount specific routes first
app.include_router(router)

# Include admin routes
from web.admin_routes import router as admin_router
app.include_router(admin_router)

# Serve static files
# We need to get absolute path to avoid issues
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

from fastapi.responses import RedirectResponse

@app.get("/")
async def read_root():
    """Redirect root to main hub"""
    return RedirectResponse(url="/app/hub")


