# AWS Bedrock

## Setup

Configure AWS credentials through the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html) or export as environment variables:

```bash
export AWS_ACCESS_KEY_ID=<YOUR_AWS_ACCESS_KEY_ID>
export AWS_SECRET_ACCESS_KEY=<YOUR_AWS_SECRET_ACCESS_KEY>
export AWS_DEFAULT_REGION=<YOUR_AWS_REGION>
```

## Examples


```python
from toolfront import Database

db = Database("postgresql://user:pass@host/db")

# Claude 3.5 Sonnet via Bedrock
result = db.ask(..., model="bedrock:anthropic.claude-3-5-sonnet-20241022-v2:0")
```


!!! tip "AWS Bedrock Model Names"
    Always specify a Bedrock model with the `bedrock:` prefix.