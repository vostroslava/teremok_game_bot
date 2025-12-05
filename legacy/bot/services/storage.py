import json
import os
from datetime import datetime
import logging

DATA_DIR = "data"
LEADS_FILE = os.path.join(DATA_DIR, "leads.json")

logger = logging.getLogger(__name__)

def ensure_data_dir():
    """Создает директорию data, если её нет."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def save_lead(data: dict):
    """Сохраняет лид в JSON файл."""
    ensure_data_dir()
    
    lead_entry = {
        "timestamp": datetime.now().isoformat(),
        **data
    }
    
    leads = []
    if os.path.exists(LEADS_FILE):
        try:
            with open(LEADS_FILE, "r", encoding="utf-8") as f:
                leads = json.load(f)
        except json.JSONDecodeError:
            logger.error("Ошибка чтения файла лидов. Создается новый.")
            leads = []
            
    leads.append(lead_entry)
    
    with open(LEADS_FILE, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=4)
    
    logger.info(f"Лид сохранен: {data.get('email')}")
