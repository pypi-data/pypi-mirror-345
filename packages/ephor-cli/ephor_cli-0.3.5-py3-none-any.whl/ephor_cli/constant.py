import os

API_SERVER_URL = os.getenv("API_SERVER_URL", "https://mcp-hive.ti.trilogy.com/api")
# API_SERVER_URL = os.getenv("API_SERVER_URL", "http://localhost:3000/api")

AGENT_SERVER_URL = os.getenv("AGENT_SERVER_URL", "https://agents.ti.trilogy.com")
# AGENT_SERVER_URL = os.getenv("AGENT_SERVER_URL", "http://localhost:10002")

DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "mcp-hive")
