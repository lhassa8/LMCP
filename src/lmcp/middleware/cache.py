"""
Cache Middleware

Provides caching functionality for requests and responses.
"""

import asyncio
import hashlib
import json
import time
from typing import Any, Dict, Optional, Callable, Awaitable

from .base import Middleware
from ..types import MiddlewareContext


class CacheMiddleware(Middleware):
    """Middleware for caching requests and responses."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.ttl = self.config.get("ttl", 300)  # 5 minutes default
        self.max_size = self.config.get("max_size", 1000)
        self.cache_reads = self.config.get("cache_reads", True)
        self.cache_writes = self.config.get("cache_writes", False)
        
        # In-memory cache
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, float] = {}
        self._lock = asyncio.Lock()
    
    async def process_request(
        self, 
        context: MiddlewareContext, 
        request: Dict[str, Any],
        next_handler: Callable[[MiddlewareContext, Dict[str, Any]], Awaitable[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Process request with caching."""
        # Check if this request should be cached
        if not self._should_cache_request(context, request):
            return await next_handler(context, request)
        
        # Generate cache key
        cache_key = self._generate_cache_key(context, request)
        
        # Check cache
        cached_response = await self._get_from_cache(cache_key)
        if cached_response is not None:
            context.metadata["cache_hit"] = True
            return cached_response
        
        # Call next handler
        response = await next_handler(context, request)
        
        # Cache the response
        await self._put_in_cache(cache_key, response)
        context.metadata["cache_hit"] = False
        
        return response
    
    async def process_response(
        self, 
        context: MiddlewareContext, 
        response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process response (no additional caching needed here)."""
        return response
    
    def _should_cache_request(self, context: MiddlewareContext, request: Dict[str, Any]) -> bool:
        """Determine if a request should be cached."""
        # Only cache read operations by default
        if not self.cache_reads:
            return False
        
        # Don't cache write operations unless explicitly enabled
        method = request.get("method", "")
        if method.lower() in ("create", "update", "delete", "write") and not self.cache_writes:
            return False
        
        # Check for cache control headers
        if context.metadata.get("no_cache", False):
            return False
        
        return True
    
    def _generate_cache_key(self, context: MiddlewareContext, request: Dict[str, Any]) -> str:
        """Generate a cache key for the request."""
        # Create a hash of the request
        request_str = json.dumps(request, sort_keys=True)
        
        # Include relevant context
        context_parts = [
            context.operation,
            str(context.server_info),
            str(context.client_info)
        ]
        
        full_str = request_str + "|" + "|".join(context_parts)
        return hashlib.md5(full_str.encode()).hexdigest()
    
    async def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a value from cache."""
        async with self._lock:
            if key not in self._cache:
                return None
            
            # Check if expired
            cache_entry = self._cache[key]
            if time.time() - cache_entry["timestamp"] > self.ttl:
                del self._cache[key]
                del self._access_times[key]
                return None
            
            # Update access time
            self._access_times[key] = time.time()
            
            return cache_entry["data"]
    
    async def _put_in_cache(self, key: str, data: Dict[str, Any]) -> None:
        """Put a value in cache."""
        async with self._lock:
            # Check cache size and evict if needed
            if len(self._cache) >= self.max_size:
                await self._evict_lru()
            
            # Store in cache
            self._cache[key] = {
                "data": data,
                "timestamp": time.time()
            }
            self._access_times[key] = time.time()
    
    async def _evict_lru(self) -> None:
        """Evict least recently used items."""
        if not self._access_times:
            return
        
        # Find the least recently used key
        lru_key = min(self._access_times, key=self._access_times.get)
        
        # Remove from cache
        del self._cache[lru_key]
        del self._access_times[lru_key]
    
    async def clear_cache(self) -> None:
        """Clear the entire cache."""
        async with self._lock:
            self._cache.clear()
            self._access_times.clear()
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        async with self._lock:
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "ttl": self.ttl,
                "oldest_entry": min(
                    (entry["timestamp"] for entry in self._cache.values()), 
                    default=None
                ),
                "newest_entry": max(
                    (entry["timestamp"] for entry in self._cache.values()), 
                    default=None
                )
            }