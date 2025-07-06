"""
Retry Middleware

Provides automatic retry functionality for failed requests.
"""

import asyncio
import logging
import random
from typing import Any, Dict, Optional, Callable, Awaitable, List

from .base import Middleware
from ..types import MiddlewareContext
from ..exceptions import LMCPError, ConnectionError, TimeoutError

logger = logging.getLogger(__name__)


class RetryMiddleware(Middleware):
    """Middleware for automatic request retries."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.max_retries = self.config.get("max_retries", 3)
        self.base_delay = self.config.get("base_delay", 1.0)
        self.max_delay = self.config.get("max_delay", 60.0)
        self.exponential_base = self.config.get("exponential_base", 2.0)
        self.jitter = self.config.get("jitter", True)
        
        # Which exceptions should trigger a retry
        self.retryable_exceptions = self.config.get("retryable_exceptions", [
            ConnectionError,
            TimeoutError,
        ])
        
        # Which HTTP status codes should trigger a retry
        self.retryable_status_codes = self.config.get("retryable_status_codes", [
            502,  # Bad Gateway
            503,  # Service Unavailable
            504,  # Gateway Timeout
        ])
    
    async def process_request(
        self, 
        context: MiddlewareContext, 
        request: Dict[str, Any],
        next_handler: Callable[[MiddlewareContext, Dict[str, Any]], Awaitable[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Process request with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Add attempt info to context
                context.metadata["retry_attempt"] = attempt
                context.metadata["max_retries"] = self.max_retries
                
                if attempt > 0:
                    logger.info(f"Retrying request (attempt {attempt + 1}/{self.max_retries + 1})")
                
                # Call next handler
                response = await next_handler(context, request)
                
                # Check if response indicates a retryable error
                if self._is_retryable_response(response) and attempt < self.max_retries:
                    logger.warning(f"Retryable response received, will retry: {response}")
                    await self._wait_before_retry(attempt)
                    continue
                
                # Success or non-retryable response
                if attempt > 0:
                    logger.info(f"Request succeeded after {attempt + 1} attempts")
                
                return response
                
            except Exception as e:
                last_exception = e
                
                # Check if this exception is retryable
                if not self._is_retryable_exception(e):
                    logger.debug(f"Non-retryable exception: {type(e).__name__}")
                    raise
                
                # Check if we have more retries
                if attempt >= self.max_retries:
                    logger.error(f"Request failed after {attempt + 1} attempts")
                    raise
                
                # Wait before retry
                logger.warning(f"Retryable exception occurred: {e}")
                await self._wait_before_retry(attempt)
        
        # This should not be reached, but just in case
        if last_exception:
            raise last_exception
        
        raise LMCPError("Unexpected error in retry middleware")
    
    async def process_response(
        self, 
        context: MiddlewareContext, 
        response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process response (no retry logic needed here)."""
        return response
    
    def _is_retryable_exception(self, exception: Exception) -> bool:
        """Check if an exception should trigger a retry."""
        for exc_type in self.retryable_exceptions:
            if isinstance(exception, exc_type):
                return True
        return False
    
    def _is_retryable_response(self, response: Dict[str, Any]) -> bool:
        """Check if a response indicates a retryable error."""
        # Check for error responses with retryable status codes
        if "error" in response:
            error = response["error"]
            if isinstance(error, dict):
                code = error.get("code")
                if code in self.retryable_status_codes:
                    return True
        
        return False
    
    async def _wait_before_retry(self, attempt: int) -> None:
        """Wait before retrying with exponential backoff."""
        # Calculate delay with exponential backoff
        delay = self.base_delay * (self.exponential_base ** attempt)
        
        # Apply maximum delay
        delay = min(delay, self.max_delay)
        
        # Add jitter to prevent thundering herd
        if self.jitter:
            delay = delay * (0.5 + random.random() * 0.5)
        
        logger.debug(f"Waiting {delay:.2f} seconds before retry")
        await asyncio.sleep(delay)
    
    async def get_retry_stats(self) -> Dict[str, Any]:
        """Get retry statistics."""
        return {
            "max_retries": self.max_retries,
            "base_delay": self.base_delay,
            "max_delay": self.max_delay,
            "exponential_base": self.exponential_base,
            "jitter": self.jitter,
            "retryable_exceptions": [exc.__name__ for exc in self.retryable_exceptions],
            "retryable_status_codes": self.retryable_status_codes
        }