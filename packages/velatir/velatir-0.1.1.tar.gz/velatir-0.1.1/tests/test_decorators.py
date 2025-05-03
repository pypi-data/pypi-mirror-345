import asyncio
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from velatir.models import VelatirResponse
from velatir.decorators import watch
from velatir.exceptions import VelatirWatchDeniedError

# Sample functions to be decorated
async def sample_async_function(param1, param2="default"):
    """This is a sample async function"""
    return f"{param1}-{param2}"

def sample_sync_function(param1, param2="default"):
    """This is a sample sync function"""
    return f"{param1}-{param2}"

@pytest.fixture
def mock_client():
    """Fixture to create a mock client and patch get_client()"""
    client = AsyncMock()
    with patch('velatir.get_client', return_value=client):
        yield client

class TestWatchDecorator:
    
    async def test_async_function_approved_immediately(self, mock_client):
        """Test that an async function runs when immediately approved"""
        # Configure mock response
        response = VelatirResponse(
            request_id="test-id",
            state="approved"
        )
        mock_client.create_watch_request.return_value = response
        
        # Apply decorator
        decorated = watch()(sample_async_function)
        
        # Call function
        result = await decorated("value1", "value2")
        
        # Verify results
        assert result == "value1-value2"
        mock_client.create_watch_request.assert_called_once()
        mock_client.wait_for_approval.assert_not_called()
    
    async def test_async_function_pending_then_approved(self, mock_client):
        """Test that an async function waits when pending, then runs when approved"""
        # Configure mock responses
        pending_response = VelatirResponse(
            request_id="test-id",
            state="pending"
        )
        approved_response = VelatirResponse(
            request_id="test-id",
            state="approved"
        )
        mock_client.create_watch_request.return_value = pending_response
        mock_client.wait_for_approval.return_value = approved_response
        
        # Apply decorator
        decorated = watch()(sample_async_function)
        
        # Call function
        result = await decorated("value1", "value2")
        
        # Verify results
        assert result == "value1-value2"
        mock_client.create_watch_request.assert_called_once()
        mock_client.wait_for_approval.assert_called_once_with(
            request_id="test-id",
            polling_interval=5.0,
            max_attempts=None
        )
    
    async def test_async_function_denied_immediately(self, mock_client):
        """Test that an async function raises exception when denied immediately"""
        # Configure mock response
        response = VelatirResponse(
            request_id="test-id",
            state="denied"
        )
        mock_client.create_watch_request.return_value = response
        
        # Apply decorator
        decorated = watch()(sample_async_function)
        
        # Call function and expect exception
        with pytest.raises(VelatirWatchDeniedError) as excinfo:
            await decorated("value1", "value2")
        
        # Verify results
        assert "test-id" in str(excinfo.value)
        mock_client.create_watch_request.assert_called_once()
        mock_client.wait_for_approval.assert_not_called()
    
    def test_sync_function_approved(self, mock_client):
        """Test that a sync function runs when approved"""
        # Configure mock response
        response = VelatirResponse(
            request_id="test-id", 
            state="approved"
        )
        mock_client.create_watch_request.return_value = response
        
        # Apply decorator
        decorated = watch()(sample_sync_function)
        
        # Call function
        result = decorated("value1", "value2")
        
        # Verify results
        assert result == "value1-value2"
        mock_client.create_watch_request.assert_called_once()