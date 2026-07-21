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
INSTRUCTIONS = (
    "You are a senior researcher tasked with writing a cohesive report for a research query. "
    "You will be provided with the original query, and some initial research done by a research assistant.\n"
    "You first come up with an outline for the report that describes the structure and "
    "flow of the report. Then, generate the report and return that as your final output.\n"
    "The final output should be in markdown format, and it should be lengthy and detailed. Aim "
    "for 3-10 pages of content, at least 1800 words."
)

class ReportData(BaseModel):
    short_summary: str
    """A short 2-3 sentence summary of the findings."""

    markdown_report: str
    """The final report."""

    follow_up_questions: list[str]
    """Suggested topics to research further."""

writer_agent = Agent(
    name="WriterAgent",
    instructions=INSTRUCTIONS,
    model=anthropic_model,
    output_type=ReportData,
)