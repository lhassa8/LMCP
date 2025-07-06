"""
Metrics Middleware

Provides metrics collection and monitoring functionality.
"""

import time
from typing import Any, Dict, Optional, Callable, Awaitable, List
from datetime import datetime
from collections import defaultdict, deque

from .base import Middleware
from ..types import MiddlewareContext, MetricsData


class MetricsMiddleware(Middleware):
    """Middleware for collecting metrics."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.collect_timing = self.config.get("collect_timing", True)
        self.collect_counters = self.config.get("collect_counters", True)
        self.collect_errors = self.config.get("collect_errors", True)
        self.max_history = self.config.get("max_history", 1000)
        
        # Metrics storage
        self._counters: Dict[str, int] = defaultdict(int)
        self._timing_history: deque = deque(maxlen=self.max_history)
        self._error_history: deque = deque(maxlen=self.max_history)
        self._request_history: deque = deque(maxlen=self.max_history)
        
        # Aggregated metrics
        self._total_requests = 0
        self._total_errors = 0
        self._total_duration = 0.0
    
    async def process_request(
        self, 
        context: MiddlewareContext, 
        request: Dict[str, Any],
        next_handler: Callable[[MiddlewareContext, Dict[str, Any]], Awaitable[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Process request and collect metrics."""
        start_time = time.time()
        
        # Count the request
        if self.collect_counters:
            self._counters["requests.total"] += 1
            self._counters[f"requests.{context.operation}"] += 1
            self._total_requests += 1
        
        # Store start time
        context.metadata["metrics_start_time"] = start_time
        
        try:
            # Call next handler
            response = await next_handler(context, request)
            
            # Record success metrics
            if self.collect_counters:
                self._counters["requests.success"] += 1
                self._counters[f"requests.{context.operation}.success"] += 1
            
            return response
            
        except Exception as e:
            # Record error metrics
            if self.collect_errors:
                self._record_error(context, e)
            
            raise
        
        finally:
            # Record timing
            if self.collect_timing:
                self._record_timing(context, start_time)
    
    async def process_response(
        self, 
        context: MiddlewareContext, 
        response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process response and record final metrics."""
        # Check for error responses
        if "error" in response and self.collect_errors:
            error_info = response["error"]
            self._record_response_error(context, error_info)
        
        # Record response size if available
        if self.collect_counters:
            response_size = len(str(response))
            self._counters["response.bytes"] += response_size
        
        return response
    
    async def process_error(
        self, 
        context: MiddlewareContext, 
        error: Exception
    ) -> Optional[Dict[str, Any]]:
        """Process and record error metrics."""
        if self.collect_errors:
            self._record_error(context, error)
        
        return None  # Don't handle the error, just record it
    
    def _record_timing(self, context: MiddlewareContext, start_time: float) -> None:
        """Record timing metrics."""
        duration = time.time() - start_time
        
        # Update aggregated metrics
        self._total_duration += duration
        
        # Store in history
        timing_data = MetricsData(
            name="request.duration",
            value=duration,
            timestamp=datetime.now(),
            labels={
                "operation": context.operation,
                "request_id": context.request_id
            }
        )
        self._timing_history.append(timing_data)
        
        # Update counters
        self._counters["timing.total_duration"] = self._total_duration
        self._counters["timing.avg_duration"] = self._total_duration / max(self._total_requests, 1)
    
    def _record_error(self, context: MiddlewareContext, error: Exception) -> None:
        """Record error metrics."""
        self._total_errors += 1
        
        # Update counters
        self._counters["errors.total"] += 1
        self._counters[f"errors.{type(error).__name__}"] += 1
        self._counters[f"errors.{context.operation}"] += 1
        
        # Store in history
        error_data = MetricsData(
            name="request.error",
            value=1,
            timestamp=datetime.now(),
            labels={
                "operation": context.operation,
                "request_id": context.request_id,
                "error_type": type(error).__name__,
                "error_message": str(error)
            }
        )
        self._error_history.append(error_data)
    
    def _record_response_error(self, context: MiddlewareContext, error_info: Any) -> None:
        """Record response error metrics."""
        self._total_errors += 1
        
        # Update counters
        self._counters["errors.response"] += 1
        
        if isinstance(error_info, dict):
            error_code = error_info.get("code", "unknown")
            self._counters[f"errors.code.{error_code}"] += 1
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        return {
            "counters": dict(self._counters),
            "totals": {
                "requests": self._total_requests,
                "errors": self._total_errors,
                "duration": self._total_duration,
                "avg_duration": self._total_duration / max(self._total_requests, 1),
                "error_rate": self._total_errors / max(self._total_requests, 1)
            },
            "history": {
                "timing": list(self._timing_history),
                "errors": list(self._error_history),
                "requests": list(self._request_history)
            }
        }
    
    async def get_summary(self) -> Dict[str, Any]:
        """Get a summary of key metrics."""
        if self._total_requests == 0:
            return {
                "total_requests": 0,
                "total_errors": 0,
                "error_rate": 0.0,
                "avg_duration": 0.0
            }
        
        return {
            "total_requests": self._total_requests,
            "total_errors": self._total_errors,
            "error_rate": self._total_errors / self._total_requests,
            "avg_duration": self._total_duration / self._total_requests,
            "requests_per_second": self._calculate_rps(),
            "p95_duration": self._calculate_percentile(0.95),
            "p99_duration": self._calculate_percentile(0.99)
        }
    
    def _calculate_rps(self) -> float:
        """Calculate requests per second."""
        if len(self._timing_history) < 2:
            return 0.0
        
        # Use the time span of recent requests
        recent_requests = list(self._timing_history)[-100:]  # Last 100 requests
        if len(recent_requests) < 2:
            return 0.0
        
        time_span = (recent_requests[-1].timestamp - recent_requests[0].timestamp).total_seconds()
        if time_span <= 0:
            return 0.0
        
        return len(recent_requests) / time_span
    
    def _calculate_percentile(self, percentile: float) -> float:
        """Calculate duration percentile."""
        if not self._timing_history:
            return 0.0
        
        durations = [metric.value for metric in self._timing_history]
        durations.sort()
        
        index = int(len(durations) * percentile)
        return durations[min(index, len(durations) - 1)]
    
    async def reset_metrics(self) -> None:
        """Reset all metrics."""
        self._counters.clear()
        self._timing_history.clear()
        self._error_history.clear()
        self._request_history.clear()
        
        self._total_requests = 0
        self._total_errors = 0
        self._total_duration = 0.0