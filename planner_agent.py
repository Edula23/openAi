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

HOW_MANY_SEARCHES = 2
INSTRUCTIONS = f"You are a helpful research assistant. Given a user query, come up with a set of web searches to perform to best answer the query. Output {HOW_MANY_SEARCHES} terms to query for."

class WebSearchItem(BaseModel):
    reason: str = Field(description="Your reasoning for why this search is important to the query.")
    query: str = Field(description="The search term to use for the web search.")

class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="A list of web searches to perform to best answer the query.")

planner_Agent = Agent(
    name="Planner agent",
    instructions=INSTRUCTIONS,
    model=anthropic_model,
    output_type=WebSearchPlan,
    
)