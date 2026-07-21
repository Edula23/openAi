import os
import gradio as gr
from dotenv import load_dotenv
from research_manager import ResearchManager

load_dotenv(override=True)


async def run(query: str):
    async for chunk in ResearchManager().run(query):
        yield chunk


# UI to chat & to generate
with gr.Blocks(theme=gr.themes.Default(primary_hue="sky")) as ui:
    gr.Markdown("# Deep Research")
    query = gr.Textbox(label="What topic would you like to research?")
    run_button = gr.Button(value="Run", variant="primary")
    report = gr.Markdown(label="Report")

    run_button.click(fn=run, inputs=query, outputs=report)
    query.submit(fn=run, inputs=query, outputs=report)

ui.launch(
    server_name="0.0.0.0",
    server_port=int(os.environ.get("PORT", 7860)),
    inbrowser=True)