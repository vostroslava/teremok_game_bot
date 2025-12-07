from repositories.user_repository import UserRepository
from repositories.test_repository import TestRepository
from services.user_service import UserService
from services.test_service import TestService
from services.auth_service import AuthService
from services.notification_service import NotificationService

# Repositories
user_repo = UserRepository()
test_repo = TestRepository()

# Services
user_service = UserService(user_repo)
test_service = TestService(test_repo)
auth_service = AuthService(user_repo)
notification_service = NotificationService()
