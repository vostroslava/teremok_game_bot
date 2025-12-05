from fastapi import FastAPI, APIRouter, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from core.texts import TYPES_DATA
from core.database import save_lead
from core.config import settings
import os

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

# API Endpoint to submit lead/contact
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
        
        # Send to admin if bot is available
        if bot_instance and settings.ADMIN_ID:
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
                    chat_id=settings.ADMIN_ID,
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
