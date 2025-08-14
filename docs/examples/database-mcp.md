# Database MCP Integration with MySQL

In this example, we'll set up ToolFront as an MCP server to query MySQL databases directly from Claude Desktop, Cursor, or any MCP enabled application. MCP enables seamless database access from your AI development environment.

## 1. Install ToolFront with MySQL support.

```bash
pip install "toolfront[mysql]"
```

## 2. Configure MCP server in your application settings.

```json linenums="1"
{
  "mcpServers": {
    "toolfront-mysql": {
      "command": "uvx",
      "args": [
        "toolfront[mysql]", 
        "mysql://user:password@localhost:3306/ecommerce"
      ]
    }
  }
}
```

## 3. Query your MySQL database directly from your MCP client

```
User: What are our top 3 product categories by sales volume?

Claude: I'll query your MySQL database to get the top product categories by sales volume.

[ToolFront executes SQL query]

# Returns a list of categories
>>> ["Electronics", "Clothing", "Home & Garden"]

Your top 3 product categories by sales volume are:
1. Electronics - highest volume
2. Clothing - second highest  
3. Home & Garden - third highest
```

!!! tip "MCP Integration"
    MCP servers enable direct database access from AI applications without switching contexts. Perfect for data analysis, reporting, and business intelligence workflows.