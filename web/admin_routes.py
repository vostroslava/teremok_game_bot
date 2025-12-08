"""
Web Admin Panel Routes
Protected by ADMIN_PANEL_SECRET
"""
from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from core.config import settings
from core.texts import TYPES_DATA
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from services.user_service import UserService
import os
import logging

logger = logging.getLogger(__name__)

from core.dependencies import user_repo, auth_service, user_service, test_service

logger = logging.getLogger(__name__)

# Dependecy Injection (Module Level for simplicity)
# user_repo = UserRepository()
# auth_service = AuthService(user_repo)
# user_service = UserService(user_repo)

router = APIRouter(prefix="/app/admin", tags=["admin"])

# Templates
templates_path = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_path)

# ===== AUTH MIDDLEWARE =====

import secrets

# ===== AUTH MIDDLEWARE =====

async def verify_admin_auth(request: Request) -> bool:
    """Check if request has valid session or legacy key"""
    # 1. Check session token
    token = request.cookies.get("admin_session")
    if token:
        user = await auth_service.get_user_from_token(token)
        if user:
            return True
            
    # 2. Legacy: Check query param or cookie key
    key = request.query_params.get("key")
    if key and key == settings.ADMIN_PANEL_SECRET:
        return True
    
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



# ===== LOGIN/LOGOUT =====

@router.get("/login")
async def login_page(request: Request):
    """Admin login page"""
    if await verify_admin_auth(request):
        return RedirectResponse(url="/app/admin/dashboard", status_code=303)
    return templates.TemplateResponse("admin/login.html", {"request": request})

@router.post("/login")
async def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handle login submission"""
    if await auth_service.verify_password(username, password):
        # Create session
        token = await auth_service.create_session(username)
        
        response = RedirectResponse(url="/app/admin/dashboard", status_code=303)
        response.set_cookie("admin_session", token, max_age=86400*7, httponly=True, samesite="lax")
        return response
        
    return templates.TemplateResponse("admin/login.html", {
        "request": request, 
        "error": "Неверный логин или пароль"
    })

@router.get("/logout")
async def logout(request: Request):
    """Logout"""
    response = RedirectResponse(url="/app/admin/login", status_code=303)
    response.delete_cookie("admin_session")
    response.delete_cookie("admin_key")
    return response

# ===== DASHBOARD =====

# ===== DASHBOARD =====

# Helper
def serialize_record(record):
    """Convert asyncpg record to dict and serialize types"""
    data = dict(record)
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = value.strftime("%Y-%m-%d %H:%M:%S")
    return data

@router.get("")
@router.get("/dashboard")
async def admin_dashboard(request: Request, key: str = None):
    # ... (auth check)
    try:
        if not await verify_admin_auth(request):
            return RedirectResponse(url="/app/admin/login", status_code=303)
        
        logger.info(f"Admin dashboard accessed from {request.client.host}")
        
        # Get stats
        stats = await user_service.get_statistics()
        daily_stats = await user_service.get_daily_statistics()
        
        # Get recent activity
        recent_leads = await user_service.get_recent_leads_full(limit=5)
        recent_leads = [serialize_record(l) for l in recent_leads]
        
        recent_tests = await test_service.get_recent_tests_full(limit=5)
        
        # Enrich tests
        recent_tests_enriched = []
        for t in recent_tests:
            test_dict = serialize_record(t)
            type_info = TYPES_DATA.get(test_dict.get('result_type'))
            if type_info:
                test_dict['type_emoji'] = type_info.emoji
                test_dict['type_name'] = type_info.name_ru
            else:
                test_dict['type_emoji'] = "❓"
                test_dict['type_name'] = test_dict.get('result_type')
            recent_tests_enriched.append(test_dict)

        return templates.TemplateResponse("admin/dashboard.html", {
            "request": request,
            "stats": stats,
            "recent_leads": recent_leads,
            "recent_tests": recent_tests_enriched,
            "chart_labels": daily_stats['labels'],
            "chart_leads": daily_stats['leads'],
            "chart_tests": daily_stats['tests'],
            "key": key or request.query_params.get("key") or request.cookies.get("admin_key")
        })
    except Exception as e:
        logger.error(f"Error in admin_dashboard: {e}", exc_info=True)
        return HTMLResponse(content=f"<h1>Error</h1><pre>{e}</pre>", status_code=500)

    if key:
        response.set_cookie("admin_key", key, max_age=86400*7, httponly=True)
    return response

# ... LEADS ...
@router.get("/leads")
async def admin_leads(request: Request, 
                      status: str = "all",
                      search: str = "",
                      days: str = None,
                      sort_by: str = "created_at",
                      sort_order: str = "desc",
                      key: str = None):
    """Leads management page"""
    if not await verify_admin_auth(request):
        return get_access_denied_response(request)
    
    logger.info(f"Admin leads accessed, status={status}, search={search}")
    
    # Safely parse days
    days_val = int(days) if days and days.isdigit() else None

    leads = await user_service.get_all_leads_full(
        limit=200,
        status=status if status != "all" else None,
        search=search if search else None,
        days=days_val,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Serialize
    leads = [serialize_record(l) for l in leads]
    
    return templates.TemplateResponse("admin/leads.html", {
        "request": request,
        "leads": leads,
        "current_status": status,
        "current_search": search,
        "current_days": days,
        "current_sort_by": sort_by,
        "current_sort_order": sort_order,
        "key": key or request.query_params.get("key") or request.cookies.get("admin_key")
    })

# ... TESTS ...
@router.get("/tests")
async def admin_tests(request: Request,
                      product: str = "all",
                      result_type: str = "all",
                      days: str = None,
                      sort_by: str = "created_at",
                      sort_order: str = "desc",
                      key: str = None):
    """Test results management page"""
    if not await verify_admin_auth(request):
        return get_access_denied_response(request)
    
    logger.info(f"Admin tests accessed, product={product}, result_type={result_type}")
    
    # Safely parse days
    days_val = int(days) if days and days.isdigit() else None

    tests = await test_service.get_all_tests_full(
        limit=200,
        product=product if product != "all" else None,
        result_type=result_type if result_type != "all" else None,
        days=days_val,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Add type info and serialize
    tests_enriched = []
    for t in tests:
        test_dict = serialize_record(t)
        type_info = TYPES_DATA.get(test_dict.get('result_type'))
        if type_info:
            test_dict['type_emoji'] = type_info.emoji
            test_dict['type_name'] = type_info.name_ru
        tests_enriched.append(test_dict)
    
    # Get all available types
    all_types = [{"id": t.id, "name": t.name_ru, "emoji": t.emoji} 
                 for t in TYPES_DATA.values()]
    
    return templates.TemplateResponse("admin/tests.html", {
        "request": request,
        "tests": tests_enriched,
        "all_types": all_types,
        "current_product": product,
        "current_type": result_type,
        "current_days": days,
        "current_sort_by": sort_by,
        "current_sort_order": sort_order,
        "key": key or request.query_params.get("key") or request.cookies.get("admin_key")
    })
# ... REST OF FILE ...

# ===== SETTINGS =====

@router.get("/settings")
async def admin_settings(request: Request, key: str = None):
    """Settings page (read-only)"""
    if not await verify_admin_auth(request):
        return get_access_denied_response(request)
    
    config = {
        "REQUIRED_CHANNEL_USERNAME": settings.REQUIRED_CHANNEL_USERNAME,
        "MANAGER_CHAT_ID": str(settings.MANAGER_CHAT_ID),
        "WEB_APP_URL": settings.WEB_APP_URL,
        "GOOGLE_SHEETS_ENABLED": settings.GOOGLE_SHEETS_ENABLED,
        "GOOGLE_SHEETS_WEBHOOK_URL": settings.GOOGLE_SHEETS_WEBHOOK_URL[:30] + "..." if settings.GOOGLE_SHEETS_WEBHOOK_URL else "-",
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
    if not await verify_admin_auth(request):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    
    data = await request.json()
    status = data.get("status", "new")
    notes = data.get("notes")
    
    await user_service.update_lead_status(user_id, status, notes)
    logger.info(f"Lead {user_id} status updated to {status}")
    
    return JSONResponse({"status": "ok"})

@router.post("/api/export/leads")
async def export_leads_to_sheets(request: Request):
    """Export all leads to Google Sheets"""
    if not await verify_admin_auth(request):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    
    if not settings.GOOGLE_SHEETS_ENABLED:
        return JSONResponse({"error": "Google Sheets интеграция отключена"}, status_code=400)
    
    try:
        from core.google_sheets import send_to_sheets
        
        leads = await user_service.get_all_leads_full(limit=10000)
        # Convert to dicts
        leads = [dict(l) for l in leads]
        
        # Prepare all data first
        all_data = []
        for lead in leads:
            all_data.append({
                "type": "lead",
                "name": lead.get("name", ""),
                "role": lead.get("role", ""),
                "company": lead.get("company", ""),
                "phone": lead.get("phone", ""),
                "telegram": lead.get("telegram_username", ""),
                "team_size": lead.get("team_size", ""),
                "user_id": str(lead.get("user_id", "")),
                "status": lead.get("status", "new")
            })
            
        # Send in batches of 50
        BATCH_SIZE = 50
        sent_count = 0
        
        for i in range(0, len(all_data), BATCH_SIZE):
            batch = all_data[i:i + BATCH_SIZE]
            if await send_to_sheets(batch):
                sent_count += len(batch)
        
        logger.info(f"Full leads export completed: {sent_count}/{len(leads)} leads")
        return JSONResponse({"status": "ok", "count": sent_count})
    except Exception as e:
        logger.error(f"Export leads failed: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@router.post("/api/export/tests")
async def export_tests_to_sheets(request: Request):
    """Export all tests to Google Sheets"""
    if not await verify_admin_auth(request):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    
    if not settings.GOOGLE_SHEETS_ENABLED:
        return JSONResponse({"error": "Google Sheets интеграция отключена"}, status_code=400)
    
    try:
        from core.google_sheets import send_to_sheets
        import json
        
        tests = await test_service.get_all_tests_full(limit=10000)
        # Convert to dicts
        tests = [dict(t) for t in tests]
        
        all_data = []
        for test in tests:
            # Parse scores
            scores_str = ""
            if test.get("scores"):
                try:
                    scores = test["scores"]
                    if isinstance(scores, str):
                        scores = json.loads(scores)
                    scores_str = ", ".join([f"{k}: {v}" for k, v in scores.items()])
                except:
                    scores_str = str(test.get("scores", ""))

            all_data.append({
                "type": "test",
                "name": test.get("name", ""),
                "role": test.get("role", ""),
                "company": test.get("company", ""),
                "phone": test.get("phone", ""),
                "result_type": test.get("result_type", ""),
                "scores": scores_str,
                "product": test.get("product", "teremok"),
                "user_id": str(test.get("user_id", ""))
            })
            
        # Send in batches
        BATCH_SIZE = 50
        sent_count = 0
        
        for i in range(0, len(all_data), BATCH_SIZE):
            batch = all_data[i:i + BATCH_SIZE]
            if await send_to_sheets(batch):
                sent_count += len(batch)
        
        logger.info(f"Full tests export completed: {sent_count}/{len(tests)} tests")
        return JSONResponse({"status": "ok", "count": sent_count})
    except Exception as e:
        logger.error(f"Export tests failed: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)
