# CRM Integration with GPT-4o

In this example, we'll analyze HubSpot CRM data (contacts, deals, pipeline, campaigns) using natural language queries. GPT-4o's excellent tool calling capabilities make it ideal for API integrations requiring multiple endpoint coordination.

## 1. Export your OpenAI and HubSpot API keys.

```bash
export OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>
export HUBSPOT_API_KEY=<YOUR_HUBSPOT_API_KEY>
```

## 2. Connect to HubSpot and analyze your CRM data.

```python linenums="1"
from toolfront import API

# Connect to HubSpot API
api = API(
    "https://api.hubapi.com/api-catalog-public/v1/apis/crm/v3/objects",
    model="openai:gpt-4o",
    headers={"Authorization": f"Bearer {os.getenv('HUBSPOT_API_KEY')}"}
)

# Get contact emails from high-value deals for follow-up
high_value_contacts: list[str] = api.ask(
    "Get email addresses of contacts associated with deals over $10,000 that closed in the last 30 days"
)

print(f"Found {len(high_value_contacts)} high-value customers")
print("Contact emails:", high_value_contacts[:3])  # Show first 3

>>> Found 12 high-value customers
>>> Contact emails: ['john.doe@techcorp.com', 'sarah.smith@innovate.io', 'mike.jones@startup.co']
```

!!! tip "API Integration"
    Use specific type hints like `list[str]` to get clean, structured data from complex API responses. GPT-4o excels at coordinating multiple API endpoints for comprehensive analysis.