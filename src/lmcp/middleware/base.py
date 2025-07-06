"""
Base Middleware Interface

Defines the interface for all LMCP middleware.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable, Awaitable

from ..types import MiddlewareContext


class Middleware(ABC):
    """Abstract base class for middleware."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
    
    @abstractmethod
    async def process_request(
        self, 
        context: MiddlewareContext, 
        request: Dict[str, Any],
        next_handler: Callable[[MiddlewareContext, Dict[str, Any]], Awaitable[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Process a request before it's sent to the server.
        
        Args:
            context: The middleware context
            request: The request data
            next_handler: The next handler in the chain
            
        Returns:
            The processed response
        """
        pass
    
    @abstractmethod
    async def process_response(
        self, 
        context: MiddlewareContext, 
        response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a response after it's received from the server.
        
        Args:
            context: The middleware context
            response: The response data
            
        Returns:
            The processed response
        """
        pass
    
    async def process_error(
        self, 
        context: MiddlewareContext, 
        error: Exception
    ) -> Optional[Dict[str, Any]]:
        """
        Process an error that occurred during request/response handling.
        
        Args:
            context: The middleware context
            error: The error that occurred
            
        Returns:
            Optional response to return instead of raising the error
        """
        return None
    
    async def initialize(self) -> None:
        """Initialize the middleware."""
        pass
    
    async def shutdown(self) -> None:
        """Shutdown the middleware."""
        pass


class MiddlewareChain:
    """Manages a chain of middleware."""
    
    def __init__(self):
        self._middleware: list[Middleware] = []
    
    def add_middleware(self, middleware: Middleware) -> None:
        """Add middleware to the chain."""
        self._middleware.append(middleware)
    
    def remove_middleware(self, middleware: Middleware) -> None:
        """Remove middleware from the chain."""
        if middleware in self._middleware:
            self._middleware.remove(middleware)
    
    async def process_request(
        self, 
        context: MiddlewareContext, 
        request: Dict[str, Any],
        final_handler: Callable[[MiddlewareContext, Dict[str, Any]], Awaitable[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Process a request through the middleware chain."""
        if not self._middleware:
            return await final_handler(context, request)
        
        # Create a chain of handlers
        async def create_handler(index: int) -> Callable[[MiddlewareContext, Dict[str, Any]], Awaitable[Dict[str, Any]]]:
            if index >= len(self._middleware):
                return final_handler
            
            middleware = self._middleware[index]
            next_handler = await create_handler(index + 1)
            
            async def handler(ctx: MiddlewareContext, req: Dict[str, Any]) -> Dict[str, Any]:
                try:
                    response = await middleware.process_request(ctx, req, next_handler)
                    return await middleware.process_response(ctx, response)
                except Exception as e:
                    error_response = await middleware.process_error(ctx, e)
                    if error_response is not None:
                        return error_response
                    raise
            
            return handler
        
        handler = await create_handler(0)
        return await handler(context, request)
    
    async def initialize_all(self) -> None:
        """Initialize all middleware in the chain."""
        for middleware in self._middleware:
            await middleware.initialize()
    
    async def shutdown_all(self) -> None:
        """Shutdown all middleware in the chain."""
        for middleware in reversed(self._middleware):
            await middleware.shutdown()
    
    def __len__(self) -> int:
        """Get the number of middleware in the chain."""
        return len(self._middleware)
    
    def __iter__(self):
        """Iterate over middleware in the chain."""
        return iter(self._middleware)