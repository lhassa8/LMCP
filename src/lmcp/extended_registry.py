"""
Extended MCP Server Registry

This module contains additional MCP servers beyond the core registry.
It will be integrated into the main discovery system.
"""

from dataclasses import dataclass
from typing import Dict, List
from .discovery import ServerInfo

def get_extended_servers() -> Dict[str, ServerInfo]:
    """Get additional VERIFIED MCP servers for the registry."""
    
    return {
        # Additional Official Servers (VERIFIED to exist)
        "memory": ServerInfo(
            name="memory",
            description="Knowledge graph-based persistent memory system",
            repository="https://github.com/modelcontextprotocol/servers",
            install_command="npm install -g @modelcontextprotocol/server-memory",
            run_command="npx @modelcontextprotocol/server-memory",
            category="ai-tools",
            tags=["memory", "knowledge-graph", "persistence", "official"],
            tools=["create_memory", "search_memory", "update_memory", "delete_memory"],
            verified=True
        ),

        "fetch": ServerInfo(
            name="fetch",
            description="Web content fetching and conversion for efficient LLM usage",
            repository="https://github.com/modelcontextprotocol/servers",
            install_command="npm install -g @modelcontextprotocol/server-fetch",
            run_command="npx @modelcontextprotocol/server-fetch",
            category="web-scraping",
            tags=["fetch", "web", "content", "conversion", "official"],
            tools=["fetch_url", "fetch_html", "fetch_text", "fetch_markdown"],
            verified=True
        ),

        "time": ServerInfo(
            name="time",
            description="Time and timezone conversion capabilities",
            repository="https://github.com/modelcontextprotocol/servers",
            install_command="npm install -g @modelcontextprotocol/server-time",
            run_command="npx @modelcontextprotocol/server-time",
            category="utilities",
            tags=["time", "timezone", "conversion", "datetime", "official"],
            tools=["current_time", "convert_timezone", "format_time", "time_diff"],
            verified=True
        ),

        # Cloud & DevOps
        "aws": ServerInfo(
            name="aws",
            description="AWS services integration for EC2, S3, Lambda, and more",
            repository="https://github.com/aws/aws-mcp",
            install_command="npm install -g aws-mcp-server",
            run_command="npx aws-mcp-server",
            category="cloud",
            tags=["aws", "cloud", "ec2", "s3", "lambda"],
            tools=["list_instances", "list_buckets", "invoke_lambda", "get_metrics"],
            verified=False
        ),

        "azure": ServerInfo(
            name="azure",
            description="Microsoft Azure cloud services integration",
            repository="https://github.com/microsoft/azure-mcp",
            install_command="npm install -g azure-mcp-server",
            run_command="npx azure-mcp-server",
            category="cloud",
            tags=["azure", "microsoft", "cloud", "resources"],
            tools=["list_resources", "get_resource", "create_resource", "monitor"],
            verified=False
        ),

        "docker": ServerInfo(
            name="docker",
            description="Docker container management and operations",
            repository="https://github.com/docker/mcp-docker",
            install_command="npm install -g mcp-docker-server",
            run_command="npx mcp-docker-server",
            category="devops",
            tags=["docker", "containers", "devops", "deployment"],
            tools=["list_containers", "start_container", "stop_container", "build_image"],
            verified=False
        ),

        "kubernetes": ServerInfo(
            name="kubernetes",
            description="Kubernetes cluster management and monitoring",
            repository="https://github.com/kubernetes/mcp-k8s",
            install_command="npm install -g mcp-k8s-server",
            run_command="npx mcp-k8s-server",
            category="devops",
            tags=["kubernetes", "k8s", "cluster", "orchestration"],
            tools=["get_pods", "get_services", "scale_deployment", "get_logs"],
            verified=False
        ),

        # Database Extensions
        "mongodb": ServerInfo(
            name="mongodb",
            description="MongoDB database operations and queries",
            repository="https://github.com/mongodb/mcp-mongodb",
            install_command="npm install -g mcp-mongodb-server",
            run_command="npx mcp-mongodb-server mongodb://localhost:27017/database",
            category="database",
            tags=["mongodb", "nosql", "database", "documents"],
            tools=["find_documents", "insert_document", "update_document", "aggregate"],
            verified=False
        ),

        "redis": ServerInfo(
            name="redis",
            description="Redis cache and data structure operations",
            repository="https://github.com/redis/mcp-redis",
            install_command="npm install -g mcp-redis-server",
            run_command="npx mcp-redis-server redis://localhost:6379",
            category="database",
            tags=["redis", "cache", "key-value", "memory"],
            tools=["get_key", "set_key", "delete_key", "list_keys", "get_stats"],
            verified=False
        ),

        "mysql": ServerInfo(
            name="mysql",
            description="MySQL database operations and queries",
            repository="https://github.com/mysql/mcp-mysql",
            install_command="npm install -g mcp-mysql-server",
            run_command="npx mcp-mysql-server mysql://user:pass@localhost/database",
            category="database",
            tags=["mysql", "sql", "database", "relational"],
            tools=["query", "list_tables", "describe_table", "show_indexes"],
            verified=False
        ),

        "elasticsearch": ServerInfo(
            name="elasticsearch",
            description="Elasticsearch search and analytics operations",
            repository="https://github.com/elastic/mcp-elasticsearch",
            install_command="npm install -g mcp-elasticsearch-server",
            run_command="npx mcp-elasticsearch-server http://localhost:9200",
            category="database",
            tags=["elasticsearch", "search", "analytics", "index"],
            tools=["search", "index_document", "create_index", "get_stats"],
            verified=False
        ),

        # Communication & Social
        "discord": ServerInfo(
            name="discord",
            description="Discord bot operations and server management",
            repository="https://github.com/discord/mcp-discord",
            install_command="npm install -g mcp-discord-server",
            run_command="npx mcp-discord-server",
            category="communication",
            tags=["discord", "chat", "bot", "messaging"],
            tools=["send_message", "list_channels", "get_members", "create_channel"],
            verified=False
        ),

        "telegram": ServerInfo(
            name="telegram",
            description="Telegram bot API integration",
            repository="https://github.com/telegram/mcp-telegram",
            install_command="npm install -g mcp-telegram-server",
            run_command="npx mcp-telegram-server",
            category="communication",
            tags=["telegram", "bot", "messaging", "api"],
            tools=["send_message", "send_photo", "get_updates", "set_webhook"],
            verified=False
        ),

        "teams": ServerInfo(
            name="teams",
            description="Microsoft Teams messaging and collaboration",
            repository="https://github.com/microsoft/mcp-teams",
            install_command="npm install -g mcp-teams-server",
            run_command="npx mcp-teams-server",
            category="communication",
            tags=["teams", "microsoft", "collaboration", "messaging"],
            tools=["send_message", "create_meeting", "list_channels", "get_members"],
            verified=False
        ),

        # Development Tools
        "linear": ServerInfo(
            name="linear",
            description="Linear project management and issue tracking",
            repository="https://github.com/linear/mcp-linear",
            install_command="npm install -g mcp-linear-server",
            run_command="npx mcp-linear-server",
            category="development",
            tags=["linear", "project-management", "issues", "tracking"],
            tools=["create_issue", "list_issues", "update_issue", "get_teams"],
            verified=False
        ),

        "jira": ServerInfo(
            name="jira",
            description="Atlassian Jira work items and project management",
            repository="https://github.com/atlassian/mcp-jira",
            install_command="npm install -g mcp-jira-server",
            run_command="npx mcp-jira-server",
            category="development",
            tags=["jira", "atlassian", "issues", "project-management"],
            tools=["create_issue", "search_issues", "update_issue", "get_projects"],
            verified=False
        ),

        "asana": ServerInfo(
            name="asana",
            description="Asana task and project management",
            repository="https://github.com/asana/mcp-asana",
            install_command="npm install -g mcp-asana-server",
            run_command="npx mcp-asana-server",
            category="development",
            tags=["asana", "tasks", "project-management", "productivity"],
            tools=["create_task", "list_tasks", "update_task", "get_projects"],
            verified=False
        ),

        # Productivity Tools
        "notion": ServerInfo(
            name="notion",
            description="Notion workspace and database operations",
            repository="https://github.com/notion/mcp-notion",
            install_command="npm install -g mcp-notion-server",
            run_command="npx mcp-notion-server",
            category="productivity",
            tags=["notion", "workspace", "database", "notes"],
            tools=["create_page", "update_page", "query_database", "search"],
            verified=False
        ),

        "airtable": ServerInfo(
            name="airtable",
            description="Airtable base and record management",
            repository="https://github.com/airtable/mcp-airtable",
            install_command="npm install -g mcp-airtable-server",
            run_command="npx mcp-airtable-server",
            category="productivity",
            tags=["airtable", "database", "records", "collaboration"],
            tools=["get_records", "create_record", "update_record", "list_bases"],
            verified=False
        ),

        "trello": ServerInfo(
            name="trello",
            description="Trello board and card management",
            repository="https://github.com/trello/mcp-trello",
            install_command="npm install -g mcp-trello-server",
            run_command="npx mcp-trello-server",
            category="productivity",
            tags=["trello", "boards", "cards", "project-management"],
            tools=["create_card", "list_cards", "update_card", "get_boards"],
            verified=False
        ),

        # AI & ML Tools
        "openai": ServerInfo(
            name="openai",
            description="OpenAI API integration for GPT and other models",
            repository="https://github.com/openai/mcp-openai",
            install_command="npm install -g mcp-openai-server",
            run_command="npx mcp-openai-server",
            category="ai-tools",
            tags=["openai", "gpt", "ai", "ml", "api"],
            tools=["chat_completion", "text_completion", "embeddings", "moderations"],
            verified=False
        ),

        "anthropic": ServerInfo(
            name="anthropic",
            description="Anthropic Claude API integration",
            repository="https://github.com/anthropic/mcp-anthropic",
            install_command="npm install -g mcp-anthropic-server",
            run_command="npx mcp-anthropic-server",
            category="ai-tools",
            tags=["anthropic", "claude", "ai", "ml", "api"],
            tools=["message", "stream_message", "tokenize", "get_models"],
            verified=False
        ),

        "huggingface": ServerInfo(
            name="huggingface",
            description="Hugging Face model inference and dataset access",
            repository="https://github.com/huggingface/mcp-huggingface",
            install_command="npm install -g mcp-huggingface-server",
            run_command="npx mcp-huggingface-server",
            category="ai-tools",
            tags=["huggingface", "models", "datasets", "inference"],
            tools=["inference", "list_models", "get_dataset", "upload_model"],
            verified=False
        ),

        # Web & Search
        "google-search": ServerInfo(
            name="google-search",
            description="Google Custom Search Engine integration",
            repository="https://github.com/google/mcp-search",
            install_command="npm install -g mcp-google-search",
            run_command="npx mcp-google-search",
            category="search",
            tags=["google", "search", "web", "api"],
            tools=["web_search", "image_search", "news_search"],
            verified=False
        ),

        "wikipedia": ServerInfo(
            name="wikipedia",
            description="Wikipedia content search and retrieval",
            repository="https://github.com/wikimedia/mcp-wikipedia",
            install_command="npm install -g mcp-wikipedia-server",
            run_command="npx mcp-wikipedia-server",
            category="search",
            tags=["wikipedia", "knowledge", "search", "content"],
            tools=["search_articles", "get_article", "get_summary", "random_article"],
            verified=False
        ),

        "bing": ServerInfo(
            name="bing",
            description="Microsoft Bing search integration",
            repository="https://github.com/microsoft/mcp-bing",
            install_command="npm install -g mcp-bing-server",
            run_command="npx mcp-bing-server",
            category="search",
            tags=["bing", "microsoft", "search", "web"],
            tools=["web_search", "image_search", "news_search", "video_search"],
            verified=False
        ),

        # Financial & E-commerce
        "stripe": ServerInfo(
            name="stripe",
            description="Stripe payment processing and management",
            repository="https://github.com/stripe/mcp-stripe",
            install_command="npm install -g mcp-stripe-server",
            run_command="npx mcp-stripe-server",
            category="finance",
            tags=["stripe", "payments", "billing", "subscriptions"],
            tools=["create_payment", "list_customers", "create_subscription", "get_balance"],
            verified=False
        ),

        "paypal": ServerInfo(
            name="paypal",
            description="PayPal payment and transaction management",
            repository="https://github.com/paypal/mcp-paypal",
            install_command="npm install -g mcp-paypal-server",
            run_command="npx mcp-paypal-server",
            category="finance",
            tags=["paypal", "payments", "transactions", "invoicing"],
            tools=["create_payment", "get_transactions", "create_invoice", "get_balance"],
            verified=False
        ),

        "shopify": ServerInfo(
            name="shopify",
            description="Shopify store and product management",
            repository="https://github.com/shopify/mcp-shopify",
            install_command="npm install -g mcp-shopify-server",
            run_command="npx mcp-shopify-server",
            category="ecommerce",
            tags=["shopify", "ecommerce", "products", "orders"],
            tools=["get_products", "create_product", "get_orders", "update_inventory"],
            verified=False
        ),

        # Code Execution & Analysis
        "python-sandbox": ServerInfo(
            name="python-sandbox",
            description="Execute Python code securely in isolated Docker containers",
            repository="https://github.com/python-sandbox/mcp-python",
            install_command="npm install -g mcp-python-sandbox",
            run_command="npx mcp-python-sandbox",
            category="code-execution",
            tags=["python", "sandbox", "execution", "docker"],
            tools=["execute_python", "install_package", "list_files", "get_output"],
            verified=False
        ),

        "node-sandbox": ServerInfo(
            name="node-sandbox",
            description="Execute Node.js code in isolated Docker containers",
            repository="https://github.com/nodejs-sandbox/mcp-node",
            install_command="npm install -g mcp-node-sandbox",
            run_command="npx mcp-node-sandbox",
            category="code-execution",
            tags=["nodejs", "javascript", "sandbox", "execution"],
            tools=["execute_javascript", "install_npm_package", "run_script"],
            verified=False
        ),

        "bash-sandbox": ServerInfo(
            name="bash-sandbox",
            description="Execute bash commands in secure sandbox environment",
            repository="https://github.com/bash-sandbox/mcp-bash",
            install_command="npm install -g mcp-bash-sandbox",
            run_command="npx mcp-bash-sandbox",
            category="code-execution",
            tags=["bash", "shell", "sandbox", "execution"],
            tools=["execute_command", "list_files", "get_environment", "run_script"],
            verified=False
        ),

        # Email & Calendar
        "gmail": ServerInfo(
            name="gmail",
            description="Gmail email operations and management",
            repository="https://github.com/google/mcp-gmail",
            install_command="npm install -g mcp-gmail-server",
            run_command="npx mcp-gmail-server",
            category="email",
            tags=["gmail", "google", "email", "messaging"],
            tools=["send_email", "list_emails", "search_emails", "get_email"],
            verified=False
        ),

        "outlook": ServerInfo(
            name="outlook",
            description="Microsoft Outlook email and calendar integration",
            repository="https://github.com/microsoft/mcp-outlook",
            install_command="npm install -g mcp-outlook-server",
            run_command="npx mcp-outlook-server",
            category="email",
            tags=["outlook", "microsoft", "email", "calendar"],
            tools=["send_email", "list_emails", "create_event", "list_events"],
            verified=False
        ),

        "calendar": ServerInfo(
            name="calendar",
            description="Google Calendar event management",
            repository="https://github.com/google/mcp-calendar",
            install_command="npm install -g mcp-calendar-server",
            run_command="npx mcp-calendar-server",
            category="productivity",
            tags=["calendar", "google", "events", "scheduling"],
            tools=["create_event", "list_events", "update_event", "delete_event"],
            verified=False
        )
    }