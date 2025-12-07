"""
Google Sheets Integration via Apps Script Webhook
Simple HTTP POST to Google Apps Script - no auth required
"""
import json
import logging
import httpx
from typing import Union, List, Optional
from .config import settings

logger = logging.getLogger(__name__)


async def send_to_sheets(data: Union[dict, List[dict]]) -> bool:
    """
    Send data to Google Sheets via webhook
    Accepts single dict or list of dicts (batch)
    """
    webhook_url = settings.GOOGLE_SHEETS_WEBHOOK_URL
    
    if not webhook_url:
        return False
    
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            response = await client.post(
                webhook_url,
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                count = len(data) if isinstance(data, list) else 1
                logger.info(f"Sent to Google Sheets: {count} items")
                return True
            else:
                logger.error(f"Google Sheets webhook error: {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"Google Sheets webhook failed: {e}")
        return False


async def export_lead_to_sheets(lead: dict) -> bool:
    """Export a lead to Google Sheets"""
    if not settings.GOOGLE_SHEETS_ENABLED:
        return False
    
    data = {
        "type": "lead",
        "name": lead.get("name", ""),
        "role": lead.get("role", ""),
        "company": lead.get("company", ""),
        "phone": lead.get("phone", ""),
        "telegram": lead.get("telegram_username", ""),
        "team_size": lead.get("team_size", ""),
        "user_id": str(lead.get("user_id", "")),
        "status": lead.get("status", "new")
    }
    
    return await send_to_sheets(data)


async def export_test_to_sheets(test: dict, lead: Optional[dict] = None) -> bool:
    """Export a test result to Google Sheets"""
    if not settings.GOOGLE_SHEETS_ENABLED:
        return False
    
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
    
    data = {
        "type": "test",
        "name": lead.get("name", "") if lead else test.get("name", ""),
        "role": lead.get("role", "") if lead else test.get("role", ""),
        "company": lead.get("company", "") if lead else test.get("company", ""),
        "phone": lead.get("phone", "") if lead else test.get("phone", ""),
        "result_type": test.get("result_type", ""),
        "scores": scores_str,
        "product": test.get("product", "teremok"),
        "user_id": str(test.get("user_id", ""))
    }
    
    return await send_to_sheets(data)


# Legacy compatibility - these do nothing now, export happens via webhook
def get_sheets_client():
    return None


class GoogleSheetsClient:
    def full_export_leads(self, leads): pass
    def full_export_tests(self, tests): pass
