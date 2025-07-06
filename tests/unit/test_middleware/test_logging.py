"""
Unit tests for LoggingMiddleware.
"""

import pytest
import logging
from unittest.mock import AsyncMock, patch
from datetime import datetime

from lmcp.middleware.logging import LoggingMiddleware
from lmcp.types import MiddlewareContext


class TestLoggingMiddleware:
    """Test LoggingMiddleware class."""
    
    def test_init_default_config(self):
        """Test middleware initialization with default config."""
        middleware = LoggingMiddleware()
        
        assert middleware.level == logging.INFO
        assert middleware.log_requests is True
        assert middleware.log_responses is True
        assert middleware.log_errors is True
        assert middleware.log_timing is True
        assert middleware.max_content_length == 1000
    
    def test_init_custom_config(self):
        """Test middleware initialization with custom config."""
        config = {
            "level": "DEBUG",
            "log_requests": False,
            "log_responses": True,
            "log_errors": False,
            "log_timing": False,
            "max_content_length": 500
        }
        
        middleware = LoggingMiddleware(config)
        
        assert middleware.level == logging.DEBUG
        assert middleware.log_requests is False
        assert middleware.log_responses is True
        assert middleware.log_errors is False
        assert middleware.log_timing is False
        assert middleware.max_content_length == 500
    
    @pytest.mark.asyncio
    async def test_process_request_with_logging(self):
        """Test request processing with logging enabled."""
        middleware = LoggingMiddleware({"log_requests": True, "log_timing": True})
        
        context = MiddlewareContext(
            request_id="test-123",
            operation="test_op",
            client_info={},
            server_info={},
            metadata={}
        )
        
        request = {"method": "test", "params": {"arg": "value"}}
        next_handler = AsyncMock(return_value={"result": "success"})
        
        with patch.object(middleware.logger, 'log') as mock_log:
            result = await middleware.process_request(context, request, next_handler)
            
            # Check that request was logged
            assert mock_log.call_count >= 1
            assert any("Request" in str(call.args) for call in mock_log.call_args_list)
            
            # Check that timing was logged
            assert any("completed" in str(call.args) for call in mock_log.call_args_list)
            
            # Check that start time was stored
            assert "start_time" in context.metadata
            
            assert result == {"result": "success"}
    
    @pytest.mark.asyncio
    async def test_process_request_without_logging(self):
        """Test request processing with logging disabled."""
        middleware = LoggingMiddleware({"log_requests": False, "log_timing": False})
        
        context = MiddlewareContext(
            request_id="test-123",
            operation="test_op",
            client_info={},
            server_info={},
            metadata={}
        )
        
        request = {"method": "test"}
        next_handler = AsyncMock(return_value={"result": "success"})
        
        with patch.object(middleware.logger, 'log') as mock_log:
            result = await middleware.process_request(context, request, next_handler)
            
            # Should not log request
            assert not any("Request" in str(call.args) for call in mock_log.call_args_list)
            
            assert result == {"result": "success"}
    
    @pytest.mark.asyncio
    async def test_process_response_with_logging(self):
        """Test response processing with logging enabled."""
        middleware = LoggingMiddleware({"log_responses": True})
        
        context = MiddlewareContext(
            request_id="test-123",
            operation="test_op",
            client_info={},
            server_info={},
            metadata={}
        )
        
        response = {"result": {"data": "value"}}
        
        with patch.object(middleware.logger, 'log') as mock_log:
            result = await middleware.process_response(context, response)
            
            # Check that response was logged
            assert mock_log.call_count >= 1
            assert any("Response" in str(call.args) for call in mock_log.call_args_list)
            
            assert result == response
    
    @pytest.mark.asyncio
    async def test_process_response_without_logging(self):
        """Test response processing with logging disabled."""
        middleware = LoggingMiddleware({"log_responses": False})
        
        context = MiddlewareContext(
            request_id="test-123",
            operation="test_op",
            client_info={},
            server_info={},
            metadata={}
        )
        
        response = {"result": {"data": "value"}}
        
        with patch.object(middleware.logger, 'log') as mock_log:
            result = await middleware.process_response(context, response)
            
            # Should not log response
            assert mock_log.call_count == 0
            
            assert result == response
    
    @pytest.mark.asyncio
    async def test_process_error_with_logging(self):
        """Test error processing with logging enabled."""
        middleware = LoggingMiddleware({"log_errors": True})
        
        context = MiddlewareContext(
            request_id="test-123",
            operation="test_op",
            client_info={},
            server_info={},
            metadata={}
        )
        
        error = ValueError("Test error")
        
        with patch.object(middleware.logger, 'error') as mock_error:
            result = await middleware.process_error(context, error)
            
            # Check that error was logged
            mock_error.assert_called_once()
            assert "Error" in str(mock_error.call_args)
            
            # Should return None (don't handle the error)
            assert result is None
    
    @pytest.mark.asyncio
    async def test_process_error_without_logging(self):
        """Test error processing with logging disabled."""
        middleware = LoggingMiddleware({"log_errors": False})
        
        context = MiddlewareContext(
            request_id="test-123",
            operation="test_op",
            client_info={},
            server_info={},
            metadata={}
        )
        
        error = ValueError("Test error")
        
        with patch.object(middleware.logger, 'error') as mock_error:
            result = await middleware.process_error(context, error)
            
            # Should not log error
            mock_error.assert_not_called()
            
            assert result is None
    
    def test_format_request(self):
        """Test request formatting for logging."""
        middleware = LoggingMiddleware()
        
        context = MiddlewareContext(
            request_id="test-123456789",
            operation="test_op",
            client_info={},
            server_info={},
            metadata={}
        )
        
        request = {
            "method": "tools/call",
            "params": {"name": "test", "args": {"a": 1, "b": 2}}
        }
        
        formatted = middleware._format_request(context, request)
        
        assert "op=test_op" in formatted
        assert "id=test-123" in formatted  # Truncated ID
        assert "method=tools/call" in formatted
        assert "params=" in formatted
    
    def test_format_request_long_content(self):
        """Test request formatting with long content."""
        middleware = LoggingMiddleware({"max_content_length": 10})
        
        context = MiddlewareContext(
            request_id="test-123",
            operation="test_op",
            client_info={},
            server_info={},
            metadata={}
        )
        
        request = {
            "params": {"data": "a" * 100}  # Long data
        }
        
        formatted = middleware._format_request(context, request)
        
        assert "..." in formatted  # Should be truncated
    
    def test_format_response(self):
        """Test response formatting for logging."""
        middleware = LoggingMiddleware()
        
        context = MiddlewareContext(
            request_id="test-123456789",
            operation="test_op",
            client_info={},
            server_info={},
            metadata={}
        )
        
        response = {
            "result": {"data": "value"},
            "id": "test-123"
        }
        
        formatted = middleware._format_response(context, response)
        
        assert "id=test-123" in formatted
        assert "result=" in formatted
    
    def test_format_response_with_error(self):
        """Test response formatting with error."""
        middleware = LoggingMiddleware()
        
        context = MiddlewareContext(
            request_id="test-123",
            operation="test_op",
            client_info={},
            server_info={},
            metadata={}
        )
        
        response = {
            "error": {"code": -32000, "message": "Server error"},
            "id": "test-123"
        }
        
        formatted = middleware._format_response(context, response)
        
        assert "id=test-123" in formatted
        assert "error=" in formatted
        assert "Server error" in formatted
    
    def test_format_error(self):
        """Test error formatting for logging."""
        middleware = LoggingMiddleware()
        
        context = MiddlewareContext(
            request_id="test-123456789",
            operation="test_op",
            client_info={},
            server_info={},
            metadata={}
        )
        
        error = ValueError("Test error message")
        
        formatted = middleware._format_error(context, error)
        
        assert "id=test-123" in formatted
        assert "type=ValueError" in formatted
        assert "msg=Test error message" in formatted