"""
Data models for the Velatir SDK.
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class VelatirResponse(BaseModel):
    """Response from the Velatir API for a watch request."""
    
    request_id: str = Field(alias="requestId")
    state: str = Field(alias="state")

    class Config:
        populate_by_name = True
    
    @property
    def is_approved(self) -> bool:
        """Check if the request is approved."""
        return self.state == "approved"
    
    @property
    def is_denied(self) -> bool:
        """Check if the request is denied."""
        return self.state == "denied"
    
    @property
    def is_pending(self) -> bool:
        """Check if the request is pending."""
        return self.state == "pending"