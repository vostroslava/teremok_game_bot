from repositories.user_repository import UserRepository
from models.user import UserContact
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_contact(self, contact: UserContact) -> None:
        """Register or update user contact info"""
        await self.user_repo.save_contact(contact)
        
    async def get_contact(self, user_id: int) -> UserContact | None:
        return await self.user_repo.get_contact(user_id)

    async def has_contact(self, user_id: int) -> bool:
        return await self.user_repo.has_contact(user_id)

    async def submit_lead(self, name: str, contact: str, message: str) -> None:
        # Leads logic for legacy form
        await self.user_repo.save_lead(0, f"{name} | {contact}", message)

    async def update_lead_status(self, user_id: int, status: str, notes: str = None) -> None:
        await self.user_repo.update_status(user_id, status, notes)
