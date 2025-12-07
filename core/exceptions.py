class AppError(Exception):
    """Base application exception"""
    pass

class RepositoryError(AppError):
    """Database/Repository errors"""
    pass

class ServiceError(AppError):
    """Business logic errors"""
    pass

class AuthError(ServiceError):
    """Authentication errors"""
    pass

class ValidationError(ServiceError):
    """Data validation errors"""
    pass

class NotFoundError(ServiceError):
    """Resource not found"""
    pass
