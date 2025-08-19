from crewai import Crew, Task, Agent, LLM, Process
from typing import List
from crewai.project import crew,agent,task, CrewBase
from crewai.tools import BaseTool
from duckduckgo_search import DDGS
from crewai_tools import ScrapeWebsiteTool, DirectoryReadTool, Fil

class SimpleDDGTool(BaseTool):
    name: str = "DuckDuckGo Search"
    description: str = "Performs a simple web search using DuckDuckGo."

    def _run(self, query: str) -> str:
        with DDGS() as ddg:
            results = ddg.text(query, max_results=3)
            return "\n".join([r["title"] + " - " + r["href"] for r in results])
        

llm = LLM(
    model= "gemini/gemini-2.0-flash",
    temperature=
)
