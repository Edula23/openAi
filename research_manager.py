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
from email_agent import email_agent
from planner_agent import planner_Agent, WebSearchTool, WebSearchItem, WebSearchPlan
from search_agent import search_agent
from writer_agent import writer_agent, ReportData
load_dotenv(override=True)
anthropic_client = AsyncOpenAI(api_key=os.getenv("ANTHROPIC_API_KEY"), base_url="https://api.anthropic.com/v1/")
anthropic_model = OpenAIChatCompletionsModel(model="claude-sonnet-5", openai_client=anthropic_client)
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"] 

class ResearchManager:
    async def run(self, query: str):
        """ Run the deep research process, yielding the status updates and the final report """
        trace_id = gen_trace_id()
        print(f"Research trace: https://platform.openai.com/traces/{trace_id}")
        yield f"View trace: https://platform.openai.com/traces/{trace_id}"
        print("Starting research...")
        search_plan = await self.plan_searches(query)
        yield "Searches planned, starting to search..."
        search_results = await self.perform_searches(search_plan)
        yield "Searches complete, writing email"
        report = await self.write_report(query, search_results)
        yield "Report written, sending email..."
        await self.send_email(report)
        yield "Email sent, research complete"
        yield report.markdown_report
    async def plan_searches(self, query: str):
        """ Use the planner_Agent to plan which searches to run for the query """
        print("Planning searches...")
        result = await Runner.run(planner_Agent, f"Query: {query}")
        print(f"Will perform{len(result.final_output.searches)} searches")
        return result.final_output
    async def perform_searches(self, search_plan: WebSearchPlan):
        """ Call search() for each item in the search plan"""
        print("Searching...")
        num_completed = 0
        tasks = [asyncio.create_task(self.search(item)) for item in search_plan.searches]
        results = await asyncio.gather(*tasks)
        print("Finished searching")
        return results


    async def search(self, item: WebSearchItem):
        """ Use the search agent to run a web search for each item in the search plan """
        input = "Search terms: {item.query}\nReason for searching: {item.reason}"
        result = await Runner.run(search_agent, input)
        return result.final_output
    async def write_report(self, query: str, search_results: list[str]):
        """ Use the writer agent to write a report based on the search results """
        print("Thinking about report...")
        input = f"Original query: {query}\nSummarized search results: {search_results}"
        result = await Runner.run(writer_agent, input)
        print("Finished writing report")
        return result.final_output


    async def send_email(self, report: ReportData):
        """ Use the email agent to send an email with the report """
        print("Writing email...")
        result = await Runner.run(email_agent, report.markdown_report)
        print("Email sent")
        return report