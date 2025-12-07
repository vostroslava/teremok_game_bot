import secrets
import hashlib
from repositories.user_repository import UserRepository
from models.user import WebAdmin

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def verify_password(self, username: str, password: str) -> bool:
        """Verify admin credentials"""
        admin = await self.user_repo.get_web_admin_by_username(username)
        if not admin:
            return False
        
        input_hash = hashlib.sha256((password + admin.salt).encode()).hexdigest()
        return input_hash == admin.password_hash

    async def create_session(self, username: str) -> str:
        """Create new session and return token"""
        token = secrets.token_hex(32)
        await self.user_repo.set_session_token(username, token)
        return token

    async def get_user_from_token(self, token: str) -> str | None:
        """Get username from valid token"""
        admin = await self.user_repo.get_web_admin_by_token(token)
        return admin.username if admin else None

    async def register_admin(self, username: str, password: str) -> None:
        """Register new admin"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        
        admin = WebAdmin(
            username=username,
            password_hash=password_hash,
            salt=salt
        )
        await self.user_repo.create_web_admin(admin)
