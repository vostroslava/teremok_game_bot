from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class User(BaseModel):
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    joined_at: Optional[datetime] = None

class UserContact(BaseModel):
    user_id: int
    name: str
    role: str
    company: Optional[str] = None
    team_size: str
    phone: str
    telegram_username: Optional[str] = None
    product: str = "teremok"
    status: str = "new"
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Admin(BaseModel):
    user_id: int
    username: Optional[str] = None
    role: str = "admin"
    added_at: Optional[datetime] = None

class WebAdmin(BaseModel):
    id: Optional[int] = None
    username: str
    salt: Optional[str] = None # Internal use
    password_hash: Optional[str] = None # Internal use
    created_at: Optional[datetime] = None
