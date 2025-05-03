"""
Exceptions for the Velatir SDK.
"""

class VelatirError(Exception):
    """Base exception for all Velatir errors."""
    pass

class VelatirAPIError(VelatirError):
    """Exception raised when the Velatir API returns an error."""
    
    def __init__(
        self, 
        message: str, 
        code: str = None, 
        http_status: int = None, 
        http_body: str = None
    ):
        self.message = message
        self.code = code
        self.http_status = http_status
        self.http_body = http_body
        super().__init__(self.message)

class VelatirTimeoutError(VelatirError):
    """Exception raised when a request times out."""
    pass

class VelatirWatchDeniedError(VelatirError):
    """Exception raised when a watch request is denied."""
    
    def __init__(self, request_id: str):
        self.request_id = request_id
        message = f"Function execution denied by Velatir (request_id: {request_id})"
        super().__init__(message)