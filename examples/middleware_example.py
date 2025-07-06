"""
Middleware Example

Demonstrates how to use LMCP middleware for logging, caching, retries, and metrics.
"""

import asyncio
import logging
from lmcp import connect, ConnectionConfig
from lmcp.middleware import LoggingMiddleware, CacheMiddleware, RetryMiddleware, MetricsMiddleware
from lmcp.advanced import Pipeline


async def basic_middleware_example():
    """Example using individual middleware components."""
    print("🔧 Basic Middleware Example")
    print("=" * 50)
    
    # Configure connection with custom config
    config = ConnectionConfig(
        uri="stdio://mcp-server-filesystem",
        timeout=30.0,
        max_retries=3
    )
    
    # Create client with middleware (this would be integrated in a real implementation)
    async with connect("stdio://mcp-server-filesystem") as client:
        print(f"✅ Connected to: {client.server_info.name}")
        
        # Simulate some operations
        try:
            tools = await client.list_tools()
            print(f"🔧 Found {len(tools)} tools")
            
            # Try to call a tool
            result = await client.tools.list_files(path=".")
            print(f"📁 Listed files: {len(result.content) if hasattr(result.content, '__len__') else 'N/A'}")
            
        except Exception as e:
            print(f"❌ Error: {e}")


async def pipeline_example():
    """Example using the Pipeline with multiple middleware."""
    print("\n🚰 Pipeline Middleware Example")
    print("=" * 50)
    
    # This is a conceptual example - the Pipeline class would need to be implemented
    # to integrate with the middleware system
    
    try:
        # Create pipeline with multiple middleware
        async with Pipeline() as pipeline:
            # Add middleware in order
            pipeline.add_middleware(LoggingMiddleware({
                "level": "INFO",
                "log_requests": True,
                "log_responses": True,
                "log_timing": True
            }))
            
            pipeline.add_middleware(CacheMiddleware({
                "ttl": 300,  # 5 minutes
                "max_size": 100
            }))
            
            pipeline.add_middleware(RetryMiddleware({
                "max_retries": 3,
                "base_delay": 1.0,
                "exponential_base": 2.0
            }))
            
            pipeline.add_middleware(MetricsMiddleware({
                "collect_timing": True,
                "collect_counters": True,
                "collect_errors": True
            }))
            
            # Add servers to pipeline
            pipeline.add_server("stdio://mcp-server-filesystem")
            pipeline.add_server("stdio://mcp-server-git")
            
            print("📊 Pipeline configured with:")
            print("  - Logging middleware")
            print("  - Cache middleware (5min TTL)")
            print("  - Retry middleware (3 attempts)")
            print("  - Metrics middleware")
            print("  - 2 MCP servers")
            
            # Execute operations in parallel
            print("\n🔄 Executing parallel operations...")
            
            operations = [
                ("filesystem.list_files", {"path": "."}),
                ("filesystem.read_file", {"path": "README.md"}),
                ("git.get_status", {}),
                ("git.get_branch", {})
            ]
            
            # This would execute the operations through the middleware chain
            print("📋 Operations queued:")
            for op_name, op_args in operations:
                print(f"  - {op_name}: {op_args}")
            
            # Simulate results
            print("\n✅ Operations completed")
            print("📈 Middleware benefits:")
            print("  - All requests/responses logged")
            print("  - Repeated requests cached")
            print("  - Failed requests retried automatically")
            print("  - Performance metrics collected")
            
    except Exception as e:
        print(f"❌ Pipeline error: {e}")


async def middleware_configuration_example():
    """Example showing different middleware configurations."""
    print("\n⚙️ Middleware Configuration Examples")
    print("=" * 50)
    
    # Logging middleware configurations
    print("📝 Logging Middleware Options:")
    
    # Basic logging
    basic_logging = LoggingMiddleware({
        "level": "INFO",
        "log_requests": True,
        "log_responses": True
    })
    print("  - Basic: INFO level, requests & responses")
    
    # Verbose logging
    verbose_logging = LoggingMiddleware({
        "level": "DEBUG", 
        "log_requests": True,
        "log_responses": True,
        "log_errors": True,
        "log_timing": True,
        "max_content_length": 500
    })
    print("  - Verbose: DEBUG level, all logging enabled")
    
    # Cache middleware configurations
    print("\n💾 Cache Middleware Options:")
    
    # Short-term cache
    short_cache = CacheMiddleware({
        "ttl": 60,  # 1 minute
        "max_size": 50,
        "cache_reads": True,
        "cache_writes": False
    })
    print("  - Short-term: 1min TTL, read-only")
    
    # Long-term cache
    long_cache = CacheMiddleware({
        "ttl": 3600,  # 1 hour
        "max_size": 1000,
        "cache_reads": True,
        "cache_writes": True
    })
    print("  - Long-term: 1hr TTL, read/write")
    
    # Retry middleware configurations
    print("\n🔄 Retry Middleware Options:")
    
    # Conservative retry
    conservative_retry = RetryMiddleware({
        "max_retries": 2,
        "base_delay": 0.5,
        "max_delay": 5.0,
        "jitter": True
    })
    print("  - Conservative: 2 retries, short delays")
    
    # Aggressive retry
    aggressive_retry = RetryMiddleware({
        "max_retries": 5,
        "base_delay": 2.0,
        "max_delay": 30.0,
        "exponential_base": 2.5
    })
    print("  - Aggressive: 5 retries, exponential backoff")
    
    # Metrics middleware configurations
    print("\n📊 Metrics Middleware Options:")
    
    # Basic metrics
    basic_metrics = MetricsMiddleware({
        "collect_timing": True,
        "collect_counters": True,
        "collect_errors": False
    })
    print("  - Basic: timing & counters only")
    
    # Full metrics
    full_metrics = MetricsMiddleware({
        "collect_timing": True,
        "collect_counters": True,
        "collect_errors": True,
        "max_history": 10000
    })
    print("  - Full: all metrics, large history")
    
    print("\n💡 Middleware can be combined and configured based on your needs!")


async def main():
    """Run all middleware examples."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    print("🎭 LMCP Middleware Examples")
    print("=" * 50)
    print("This example demonstrates the powerful middleware system in LMCP.")
    print("Middleware allows you to add cross-cutting concerns like logging,")
    print("caching, retries, and metrics without changing your core logic.")
    print()
    
    try:
        await basic_middleware_example()
        await pipeline_example()
        await middleware_configuration_example()
        
        print("\n🎉 All middleware examples completed!")
        print("\n💭 Key Takeaways:")
        print("  - Middleware provides powerful cross-cutting functionality")
        print("  - Easy to configure and combine different middleware")
        print("  - Pipelines enable sophisticated request processing")
        print("  - Great for production deployments with monitoring needs")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())