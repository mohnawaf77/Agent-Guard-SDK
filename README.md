# AgentGuard Python SDK

Python SDK for AgentGuard — secure API calls for AI agents without handling real API keys.

## Installation

```bash
pip install agentguard
```

## Quick Start

```python
from agentguard import AgentGuardSession

# Initializes session — prompts for credentials if not found in env vars or config
session = AgentGuardSession()

# Make secure API calls routed through AgentGuard proxy
response = session.post(
    "https://api.tavily.com/search",
    credential_id="your_credential_id",
    json={"query": "hello"}
)
print(response.json())
```
