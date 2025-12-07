"""
Google Sheets Integration Module
Exports leads and test results to Google Sheets
"""
import json
import logging
from typing import Optional, List
from .config import settings

logger = logging.getLogger(__name__)

# Singleton client instance
_sheets_client = None

class GoogleSheetsClient:
    """Client for Google Sheets API operations"""
    
    def __init__(self, creds_json: str, leads_sheet_id: str, tests_sheet_id: str):
        try:
            import gspread
            from google.oauth2.service_account import Credentials
        except ImportError:
            logger.error("gspread or google-auth not installed. Run: pip install gspread google-auth")
            raise ImportError("Required packages not installed")
        
        # Parse credentials
        creds_info = json.loads(creds_json)
        
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = Credentials.from_service_account_info(creds_info, scopes=scopes)
        self.gc = gspread.authorize(credentials)
        
        self.leads_sheet_id = leads_sheet_id
        self.tests_sheet_id = tests_sheet_id
        
        logger.info("Google Sheets client initialized successfully")
    
    def _get_leads_sheet(self):
        """Get the leads worksheet"""
        spreadsheet = self.gc.open_by_key(self.leads_sheet_id)
        return spreadsheet.sheet1
    
    def _get_tests_sheet(self):
        """Get the tests worksheet"""
        spreadsheet = self.gc.open_by_key(self.tests_sheet_id)
        return spreadsheet.sheet1
    
    def append_lead(self, lead: dict) -> bool:
        """Append a single lead row to the sheet"""
        try:
            sheet = self._get_leads_sheet()
            
            row = [
                lead.get('created_at', '')[:19] if lead.get('created_at') else '',
                'webapp',  # source
                lead.get('name', ''),
                lead.get('role', ''),
                lead.get('company', ''),
                lead.get('team_size', ''),
                lead.get('phone', ''),
                lead.get('telegram_username', ''),
                str(lead.get('user_id', '')),
                lead.get('status', 'new'),
                lead.get('notes', '')
            ]
            
            sheet.append_row(row)
            logger.info(f"Lead appended to Google Sheets: {lead.get('name')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to append lead to Google Sheets: {e}")
            return False
    
    def append_test_result(self, test: dict, lead: Optional[dict] = None) -> bool:
        """Append a single test result row to the sheet"""
        try:
            sheet = self._get_tests_sheet()
            
            # Parse scores if present
            scores_str = ''
            if test.get('scores'):
                try:
                    if isinstance(test['scores'], str):
                        scores = json.loads(test['scores'])
                    else:
                        scores = test['scores']
                    scores_str = ', '.join([f"{k}: {v}" for k, v in scores.items()])
                except:
                    scores_str = str(test.get('scores', ''))
            
            row = [
                test.get('created_at', '')[:19] if test.get('created_at') else '',
                test.get('product', 'teremok'),
                lead.get('name', '') if lead else test.get('name', ''),
                lead.get('role', '') if lead else test.get('role', ''),
                lead.get('company', '') if lead else test.get('company', ''),
                lead.get('team_size', '') if lead else test.get('team_size', ''),
                lead.get('phone', '') if lead else test.get('phone', ''),
                lead.get('telegram_username', '') if lead else test.get('telegram_username', ''),
                str(test.get('user_id', '')),
                test.get('result_type', ''),
                scores_str
            ]
            
            sheet.append_row(row)
            logger.info(f"Test result appended to Google Sheets: {test.get('result_type')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to append test result to Google Sheets: {e}")
            return False
    
    def full_export_leads(self, leads: List[dict]) -> bool:
        """Export all leads to the sheet (clears existing data)"""
        try:
            sheet = self._get_leads_sheet()
            
            # Clear and add headers
            sheet.clear()
            headers = [
                'Дата', 'Источник', 'Имя', 'Роль', 'Компания', 
                'Размер команды', 'Телефон', 'Telegram', 'User ID',
                'Статус', 'Примечание'
            ]
            sheet.append_row(headers)
            
            # Add all leads
            for lead in leads:
                row = [
                    lead.get('created_at', '')[:19] if lead.get('created_at') else '',
                    'webapp',
                    lead.get('name', ''),
                    lead.get('role', ''),
                    lead.get('company', ''),
                    lead.get('team_size', ''),
                    lead.get('phone', ''),
                    lead.get('telegram_username', ''),
                    str(lead.get('user_id', '')),
                    lead.get('status', 'new'),
                    lead.get('notes', '')
                ]
                sheet.append_row(row)
            
            logger.info(f"Full leads export completed: {len(leads)} leads")
            return True
            
        except Exception as e:
            logger.error(f"Full leads export failed: {e}")
            return False
    
    def full_export_tests(self, tests: List[dict]) -> bool:
        """Export all test results to the sheet (clears existing data)"""
        try:
            sheet = self._get_tests_sheet()
            
            # Clear and add headers
            sheet.clear()
            headers = [
                'Дата', 'Продукт', 'Имя', 'Роль', 'Компания',
                'Размер команды', 'Телефон', 'Telegram', 'User ID',
                'Типаж', 'Баллы'
            ]
            sheet.append_row(headers)
            
            # Add all tests
            for test in tests:
                scores_str = ''
                if test.get('scores') or test.get('test_scores'):
                    try:
                        scores = test.get('scores') or test.get('test_scores')
                        if isinstance(scores, str):
                            scores = json.loads(scores)
                        scores_str = ', '.join([f"{k}: {v}" for k, v in scores.items()])
                    except:
                        scores_str = str(test.get('scores', ''))
                
                row = [
                    test.get('created_at', '')[:19] if test.get('created_at') else '',
                    test.get('product', 'teremok'),
                    test.get('name', ''),
                    test.get('role', ''),
                    test.get('company', ''),
                    test.get('team_size', ''),
                    test.get('phone', ''),
                    test.get('telegram_username', ''),
                    str(test.get('user_id', '')),
                    test.get('result_type', ''),
                    scores_str
                ]
                sheet.append_row(row)
            
            logger.info(f"Full tests export completed: {len(tests)} tests")
            return True
            
        except Exception as e:
            logger.error(f"Full tests export failed: {e}")
            return False


def get_sheets_client() -> Optional[GoogleSheetsClient]:
    """Get or create the Google Sheets client singleton"""
    global _sheets_client
    
    if not settings.GOOGLE_SHEETS_ENABLED:
        return None
    
    if _sheets_client is not None:
        return _sheets_client
    
    if not settings.GOOGLE_SERVICE_ACCOUNT_JSON:
        logger.warning("GOOGLE_SERVICE_ACCOUNT_JSON not configured")
        return None
    
    if not settings.GOOGLE_SHEETS_LEADS_ID or not settings.GOOGLE_SHEETS_TESTS_ID:
        logger.warning("Google Sheets IDs not configured")
        return None
    
    try:
        _sheets_client = GoogleSheetsClient(
            creds_json=settings.GOOGLE_SERVICE_ACCOUNT_JSON,
            leads_sheet_id=settings.GOOGLE_SHEETS_LEADS_ID,
            tests_sheet_id=settings.GOOGLE_SHEETS_TESTS_ID
        )
        return _sheets_client
    except Exception as e:
        logger.error(f"Failed to initialize Google Sheets client: {e}")
        return None


async def export_lead_to_sheets(lead: dict) -> bool:
    """Helper function to export a single lead"""
    client = get_sheets_client()
    if client:
        return client.append_lead(lead)
    return False


async def export_test_to_sheets(test: dict, lead: Optional[dict] = None) -> bool:
    """Helper function to export a single test result"""
    client = get_sheets_client()
    if client:
        return client.append_test_result(test, lead)
    return False
