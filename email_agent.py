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
@function_tool
def send_email(subject: str, html_body: str) -> Dict[str, str]:
    try:
        """ Send out an email with the given subject and HTML body to all sales prospects """
        sg = sendgrid.SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
        from_email = Email("edengebeta210@gmail.com")  # Change to your verified sender
        to_email = To("eden.alemayehu@a2sv.org")       # Change to your recipient
        content = Content("text/html", html_body)
        mail = Mail(from_email, to_email, subject, content).get()
        response = sg.client.mail.send.post(request_body=mail)
        print("STATUS:", response.status_code, flush=True)
        print("BODY:", response.body, flush=True)
        return {"status": "success", "code": response.status_code}
    except Exception as e:
        err_body = getattr(e, "body", str(e))
        print("SENDGRID ERROR:", err_body, flush=True)
        return {"status": "error", "detail": str(err_body)}
INSTRUCTIONS = """
You are provided with a detailed report. Use your tool to send an email, converting the report into
a clean, well presented HTML email with an appropriate subject line.
"""

email_agent = Agent(name="Email Agent", instructions=INSTRUCTIONS, tools=[send_email], model=anthropic_model)