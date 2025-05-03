"""
ExcelJet API Client Exceptions
"""

from typing import Any, Dict, Optional


class ExceljetApiError(Exception):
    """Base exception for all client errors"""
    def __init__(
        self, 
        message: str,
        status_code: Optional[int] = None,
        detail: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)
        
    def __str__(self) -> str:
        if self.status_code:
            return f"{self.message} (Status code: {self.status_code})"
        return self.message


class AuthenticationError(ExceljetApiError):
    """Raised when API key authentication fails"""
    pass


class NodeNotFoundError(ExceljetApiError):
    """Raised when a requested node is not found"""
    pass


class InvalidRequestError(ExceljetApiError):
    """Raised for malformed requests or validation errors"""
    pass


class ApiConnectionError(ExceljetApiError):
    """Raised for network connection errors"""
    pass


class ConflictError(ExceljetApiError):
    """Raised when an operation conflicts with existing resources"""
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = 409,
        detail: Optional[Any] = None,
        conflicting_nodes: Optional[list[int]] = None
    ):
        super().__init__(message, status_code, detail)
        self.conflicting_nodes = conflicting_nodes or [] 