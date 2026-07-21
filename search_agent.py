from agents import Agent, WebSearchTool, trace, Runner, function_tool, gen_trace_id
from agents.model_settings import ModelSettings
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import asyncio
import sendgrid
import os
import httpx
from openai import AsyncOpenAI
from sendgrid.helpers.mail import Mail, Email, To, Content
from typing import Dict
from agents import OpenAIChatCompletionsModel, function_tool
from IPython.display import display, Markdown
load_dotenv(override=True)
anthropic_client = AsyncOpenAI(api_key=os.getenv("ANTHROPIC_API_KEY"), base_url="https://api.anthropic.com/v1/")
anthropic_model = OpenAIChatCompletionsModel(model="claude-sonnet-5", openai_client=anthropic_client)
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"] 

INSTRUCTIONS = "You are a research assistant. Given a search term, you search the web for that term and \
produce a concise summary of the results. The summary must 2-3 paragraphs and less than 300 \
words. Capture the main points. Write succinctly, no need to have complete sentences or good \
grammar. This will be consumed by someone synthesizing a report, so it's vital you capture the \
essence and ignore any fluff. Do not include any additional commentary other than the summary itself."

@function_tool
async def web_search(query: str) -> str:
    """Search the web for the given query and return a summary of what was found."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-5",
                "max_tokens": 1000,
                "messages": [
                    {"role": "user", "content": query}
                ],
                "tools": [
                    {"type": "web_search_20260209", "name": "web_search", "max_uses": 3}
                ],
            },
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()

    # data["content"] is a list of blocks: text, server_tool_use, web_search_tool_result
    # Just pull out the text blocks — that's Claude's synthesized answer with citations woven in
    text_parts = [
        block["text"] for block in data["content"] if block.get("type") == "text"
    ]
    return "\n".join(text_parts)
search_agent = Agent(
    name="Search agent",
    instructions=INSTRUCTIONS,
    tools=[web_search],
    model=anthropic_model,
    model_settings=ModelSettings(tool_choice="required"),
)