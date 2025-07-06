"""
Logging Middleware

Provides request/response logging functionality.
"""

import logging
import time
from typing import Any, Dict, Optional, Callable, Awaitable

from .base import Middleware
from ..types import MiddlewareContext, LogLevel

logger = logging.getLogger(__name__)


class LoggingMiddleware(Middleware):
    """Middleware for logging requests and responses."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.level = getattr(logging, self.config.get("level", "INFO"))
        self.log_requests = self.config.get("log_requests", True)
        self.log_responses = self.config.get("log_responses", True)
        self.log_errors = self.config.get("log_errors", True)
        self.log_timing = self.config.get("log_timing", True)
        self.max_content_length = self.config.get("max_content_length", 1000)
        
        # Create dedicated logger
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(self.level)
    
    async def process_request(
        self, 
        context: MiddlewareContext, 
        request: Dict[str, Any],
        next_handler: Callable[[MiddlewareContext, Dict[str, Any]], Awaitable[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Process and log the request."""
        start_time = time.time()
        
        # Log request
        if self.log_requests:
            request_info = self._format_request(context, request)
            self.logger.log(self.level, f"→ Request: {request_info}")
        
        # Store start time in context
        context.metadata["start_time"] = start_time
        
        # Call next handler
        response = await next_handler(context, request)
        
        # Log timing
        if self.log_timing:
            duration = time.time() - start_time
            self.logger.log(self.level, f"⏱ Request completed in {duration:.3f}s")
        
        return response
    
    async def process_response(
        self, 
        context: MiddlewareContext, 
        response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process and log the response."""
        if self.log_responses:
            response_info = self._format_response(context, response)
            self.logger.log(self.level, f"← Response: {response_info}")
        
        return response
    
    async def process_error(
        self, 
        context: MiddlewareContext, 
        error: Exception
    ) -> Optional[Dict[str, Any]]:
        """Process and log errors."""
        if self.log_errors:
            error_info = self._format_error(context, error)
            self.logger.error(f"✗ Error: {error_info}")
        
        return None  # Don't handle the error, just log it
    
    def _format_request(self, context: MiddlewareContext, request: Dict[str, Any]) -> str:
        """Format request for logging."""
        parts = []
        
        # Add operation
        if context.operation:
            parts.append(f"op={context.operation}")
        
        # Add request ID
        if context.request_id:
            parts.append(f"id={context.request_id[:8]}")
        
        # Add method if available
        if "method" in request:
            parts.append(f"method={request['method']}")
        
        # Add truncated params/content
        if "params" in request:
            params_str = str(request["params"])
            if len(params_str) > self.max_content_length:
                params_str = params_str[:self.max_content_length] + "..."
            parts.append(f"params={params_str}")
        
        return " ".join(parts)
    
    def _format_response(self, context: MiddlewareContext, response: Dict[str, Any]) -> str:
        """Format response for logging."""
        parts = []
        
        # Add request ID
        if context.request_id:
            parts.append(f"id={context.request_id[:8]}")
        
        # Add result info
        if "result" in response:
            result_str = str(response["result"])
            if len(result_str) > self.max_content_length:
                result_str = result_str[:self.max_content_length] + "..."
            parts.append(f"result={result_str}")
        
        # Add error info
        if "error" in response:
            error_str = str(response["error"])
            if len(error_str) > self.max_content_length:
                error_str = error_str[:self.max_content_length] + "..."
            parts.append(f"error={error_str}")
        
        return " ".join(parts)
    
    def _format_error(self, context: MiddlewareContext, error: Exception) -> str:
        """Format error for logging."""
        parts = []
        
        # Add request ID
        if context.request_id:
            parts.append(f"id={context.request_id[:8]}")
        
        # Add error type and message
        parts.append(f"type={type(error).__name__}")
        parts.append(f"msg={str(error)}")
        
        return " ".join(parts)