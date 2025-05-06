# OpenAPI AI

This is a Python library that helps AI agents to connect to, talk to, and consume existing web REST API endpoints built with [OpenAPI standard](https://www.openapis.org/). It does so by generating tools at runtime that can be called by LLM-based agents built with [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) or [Google ADK](https://google.github.io/adk-docs/).

![OpenAPI AI](https://yvkbpmmzjmfqjxusmyop.supabase.co/storage/v1/object/public/github//openapi_ai.png)

## Usage

First, you need to install the package:

```bash
pip install openapi-ai
```

In this example, we will be using [this server](https://github.com/ariadng/metatrader-mcp-server) that is running at localhost.

```python
import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner
from openapi_ai import OpenAPITools

load_dotenv()

async def main():
    tools = OpenAPITools("http://localhost:8000/openapi.json", remove_prefix="/api/v1")

    agent = Agent(
        name="Haiku trading agent",
        instructions="You are a trading assistant. Always answer in haiku form.",
        model="gpt-4o",
        tools=tools.get_openai_tools(),
    )

    result = await Runner.run(agent, "What is my current account info?")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())

"""
Example output:

Real account holds much,  
Balance strong in dollars vast,  
Equity shines bright.  

Leverage set high,  
Profit flows, free margin wide,  
In currency's might.
"""

```

## Use Cases

### 1. Enterprise Automation & Internal Tools Integration

Many companies have internal web tools for things like HR, project tracking, or customer information. Often, these tools have APIs described using the OpenAPI standard. **OpenAPI AI** library can read these descriptions and automatically create Python functions. This allows an AI agent (built with OpenAI or Google agent SDKs) to use these functions to interact with the company's tools, potentially letting users ask for information or perform simple tasks in one place.

### 2. Giving AI Agents Access to Live Information

AI models know a lot, but they don't always have the latest information like current weather, live stock prices, or if a product is in stock right now. If a service provides this live data through an API with an OpenAPI description, **OpenAPI AI** library can generate tools for it. An AI agent can then use these tools to fetch the real-time data when needed, helping it give more current and specific answers.

### 3. Helping AI Agents Interact with External Web Services

Sometimes you might want an AI agent to do something on another website or platform, like adding an issue to GitHub or posting a basic message. If these external services offer an API documented with OpenAPI, **OpenAPI AI** library can create the functions for those actions. An agent using these functions (with the right permissions and authentication) could then perform tasks on those platforms based on user requests.

### 4. Speeding Up AI Agent Development with API Integration

Certain tasks involve multiple steps using different APIs, for example, checking flight availability and then looking for hotels, or getting data from a CRM and sending it to a marketing tool. If the APIs for these steps are described using OpenAPI, **OpenAPI AI** library can generate functions for each one. An AI agent could then potentially manage the sequence of calling these functions to complete the overall task.

### 5. Rapid Prototyping and Development

When building an AI agent that needs to use web APIs, developers typically write code to make the API calls. **OpenAPI AI** library helps automate part of this. By reading an API's OpenAPI specification file, it generates the basic Python functions an agent (using OpenAI or Google SDKs) needs to call that API. This can save development time, letting builders focus more on the agent's core logic rather than writing repetitive API connection code.

### 6. Enabling AI for Legacy Systems

Sometimes, older company systems don't have modern APIs that AI agents can easily use. A common approach is to build a simpler, modern API "wrapper" around the old system and describe this wrapper using OpenAPI. **OpenAPI AI** library can then read the wrapper's OpenAPI description and generate functions for it, providing a way for an AI agent to communicate with the underlying legacy system indirectly.

## Roadmap

![Version 1.0 Roadmap](https://yvkbpmmzjmfqjxusmyop.supabase.co/storage/v1/object/public/profile-pictures//OpenAPI-AI_v1.0.png)

## Project Checklist

- ✅ Generate python functions from OpenAPI server endpoints
- ✅ Integrate Pydantic
- ✅ Generate function tools for OpenAI Agent SDK
- Generate function tools for Google ADK
- Support for endpoints with multiple path parameters
- Authentication

## License

MIT
