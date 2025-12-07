"""
Web Admin Panel Routes
Protected by ADMIN_PANEL_SECRET
"""
from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from core.config import settings
from core import database as db
from core.texts import TYPES_DATA
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/app/admin", tags=["admin"])

# Templates
templates_path = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_path)

# ===== AUTH MIDDLEWARE =====

def verify_admin_key(request: Request) -> bool:
    """Check if request has valid admin key"""
    # Check query param
    key = request.query_params.get("key")
    if key and key == settings.ADMIN_PANEL_SECRET:
        return True
    
    # Check cookie
    cookie_key = request.cookies.get("admin_key")
    if cookie_key and cookie_key == settings.ADMIN_PANEL_SECRET:
        return True
    
    return False

def get_access_denied_response(request: Request) -> HTMLResponse:
    """Return access denied page"""
    html = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Доступ запрещён</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
            }
            .box {
                text-align: center;
                padding: 40px;
                background: rgba(255,255,255,0.1);
                border-radius: 16px;
                max-width: 400px;
            }
            h1 { font-size: 3rem; margin: 0 0 16px; }
            p { color: rgba(255,255,255,0.7); }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>🔒</h1>
            <h2>Доступ только для администрации</h2>
            <p>Используйте ссылку из бота для входа в админ-панель.</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=403)

# ===== DASHBOARD =====

@router.get("")
@router.get("/")
async def admin_dashboard(request: Request, key: str = None):
    """Main admin dashboard"""
    if not verify_admin_key(request):
        return get_access_denied_response(request)
    
    logger.info(f"Admin dashboard accessed from {request.client.host}")
    
    # Get stats
    stats = await db.get_stats()
    recent_leads = await db.get_recent_leads(10)
    recent_tests = await db.get_recent_tests(10)
    
    # Add type info to tests
    for test in recent_tests:
        type_info = TYPES_DATA.get(test.get('result_type'))
        if type_info:
            test['type_emoji'] = type_info.emoji
            test['type_name'] = type_info.name_ru
    
    response = templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "stats": stats,
        "recent_leads": recent_leads,
        "recent_tests": recent_tests,
        "key": key or request.query_params.get("key") or request.cookies.get("admin_key")
    })
    
    # Set cookie if key provided
    if key:
        response.set_cookie("admin_key", key, max_age=86400*7, httponly=True)
    
    return response

# ===== LEADS =====

@router.get("/leads")
async def admin_leads(request: Request, 
                      status: str = "all",
                      search: str = "",
                      days: int = None,
                      key: str = None):
    """Leads management page"""
    if not verify_admin_key(request):
        return get_access_denied_response(request)
    
    logger.info(f"Admin leads accessed, status={status}, search={search}")
    
    leads = await db.get_all_leads_full(
        limit=200,
        status=status if status != "all" else None,
        search=search if search else None,
        days=days
    )
    
    return templates.TemplateResponse("admin/leads.html", {
        "request": request,
        "leads": leads,
        "current_status": status,
        "current_search": search,
        "current_days": days,
        "key": key or request.query_params.get("key") or request.cookies.get("admin_key")
    })

# ===== TESTS =====

@router.get("/tests")
async def admin_tests(request: Request,
                      product: str = "all",
                      result_type: str = "all",
                      days: int = None,
                      key: str = None):
    """Test results management page"""
    if not verify_admin_key(request):
        return get_access_denied_response(request)
    
    logger.info(f"Admin tests accessed, product={product}, result_type={result_type}")
    
    tests = await db.get_all_tests_full(
        limit=200,
        product=product if product != "all" else None,
        result_type=result_type if result_type != "all" else None,
        days=days
    )
    
    # Add type info
    for test in tests:
        type_info = TYPES_DATA.get(test.get('result_type'))
        if type_info:
            test['type_emoji'] = type_info.emoji
            test['type_name'] = type_info.name_ru
    
    # Get all available types
    all_types = [{"id": t.id, "name": t.name_ru, "emoji": t.emoji} 
                 for t in TYPES_DATA.values()]
    
    return templates.TemplateResponse("admin/tests.html", {
        "request": request,
        "tests": tests,
        "all_types": all_types,
        "current_product": product,
        "current_type": result_type,
        "current_days": days,
        "key": key or request.query_params.get("key") or request.cookies.get("admin_key")
    })

# ===== SETTINGS =====

@router.get("/settings")
async def admin_settings(request: Request, key: str = None):
    """Settings page (read-only)"""
    if not verify_admin_key(request):
        return get_access_denied_response(request)
    
    config = {
        "REQUIRED_CHANNEL_USERNAME": settings.REQUIRED_CHANNEL_USERNAME,
        "MANAGER_CHAT_ID": str(settings.MANAGER_CHAT_ID),
        "WEB_APP_URL": settings.WEB_APP_URL,
        "GOOGLE_SHEETS_ENABLED": settings.GOOGLE_SHEETS_ENABLED,
        "GOOGLE_SHEETS_LEADS_ID": settings.GOOGLE_SHEETS_LEADS_ID[:20] + "..." if settings.GOOGLE_SHEETS_LEADS_ID else "-",
        "GOOGLE_SHEETS_TESTS_ID": settings.GOOGLE_SHEETS_TESTS_ID[:20] + "..." if settings.GOOGLE_SHEETS_TESTS_ID else "-",
        "CHECK_SUBSCRIPTION_ENABLED": settings.CHECK_SUBSCRIPTION_ENABLED,
    }
    
    return templates.TemplateResponse("admin/settings.html", {
        "request": request,
        "config": config,
        "key": key or request.query_params.get("key") or request.cookies.get("admin_key")
    })

# ===== API ENDPOINTS =====

@router.post("/api/lead/{user_id}/status")
async def update_lead_status(request: Request, user_id: int):
    """Update lead status and notes"""
    if not verify_admin_key(request):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    
    data = await request.json()
    status = data.get("status", "new")
    notes = data.get("notes")
    
    await db.update_lead_status(user_id, status, notes)
    logger.info(f"Lead {user_id} status updated to {status}")
    
    return JSONResponse({"status": "ok"})

@router.post("/api/export/leads")
async def export_leads_to_sheets(request: Request):
    """Export all leads to Google Sheets"""
    if not verify_admin_key(request):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    
    if not settings.GOOGLE_SHEETS_ENABLED:
        return JSONResponse({"error": "Google Sheets интеграция отключена"}, status_code=400)
    
    try:
        from core.google_sheets import get_sheets_client
        client = get_sheets_client()
        if not client:
            return JSONResponse({"error": "Google Sheets не настроен"}, status_code=400)
        
        leads = await db.get_all_leads_full(limit=10000)
        client.full_export_leads(leads)
        
        logger.info(f"Full leads export completed: {len(leads)} leads")
        return JSONResponse({"status": "ok", "count": len(leads)})
    except Exception as e:
        logger.error(f"Export leads failed: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@router.post("/api/export/tests")
async def export_tests_to_sheets(request: Request):
    """Export all tests to Google Sheets"""
    if not verify_admin_key(request):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    
    if not settings.GOOGLE_SHEETS_ENABLED:
        return JSONResponse({"error": "Google Sheets интеграция отключена"}, status_code=400)
    
    try:
        from core.google_sheets import get_sheets_client
        client = get_sheets_client()
        if not client:
            return JSONResponse({"error": "Google Sheets не настроен"}, status_code=400)
        
        tests = await db.get_all_tests_full(limit=10000)
        client.full_export_tests(tests)
        
        logger.info(f"Full tests export completed: {len(tests)} tests")
        return JSONResponse({"status": "ok", "count": len(tests)})
    except Exception as e:
        logger.error(f"Export tests failed: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)
