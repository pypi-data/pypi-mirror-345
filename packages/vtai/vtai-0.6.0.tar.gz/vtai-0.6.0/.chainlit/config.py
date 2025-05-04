import os
from pathlib import Path

from vtai.integrations.mcp.browser_mcp import browser_mcp_manager

# Load browser MCP configuration
browser_mcp_manager.load_default_config()

# Get browser MCP initialization script
mcp_browser_script = browser_mcp_manager.get_initialization_script()

# Update Chainlit configuration
css = """
.mcp-browser-container {
	width: 100%;
	height: 300px;
	border: 1px solid #e0e0e0;
	border-radius: 8px;
	margin-bottom: 1rem;
	overflow: hidden;
	background-color: #f5f5f5;
}
"""

# Add browser MCP initialization script to Chainlit
head_html = mcp_browser_script
