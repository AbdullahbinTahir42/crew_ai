from crewai import Crew, Task, Agent, LLM
from crewai.project import CrewBase, crew, task, agent
from crewai.tools import BaseTool
from duckduckgo_search import DDGS
from dotenv import load_dotenv
import os
import yaml

# Load environment variables
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")  # Make sure your .env has GEMINI_API_KEY

# ----------------------------
# Simple DuckDuckGo Search Tool
# ----------------------------
class SimpleDDGTool(BaseTool):
    name: str = "DuckDuckGo Search"
    description: str = "Performs a simple web search using DuckDuckGo."

    def _run(self, query: str) -> str:
        with DDGS() as ddg:
            results = ddg.text(query, max_results=3)
            return "\n".join([r["title"] + " - " + r["href"] for r in results])

# ----------------------------
# Crew Definition
# ----------------------------
@CrewBase
class Research_and_writing_Crew():
    # Paths
    config_agents_path = "config/agents.yaml"
    config_tasks_path = "config/tasks.yaml"

    # Load YAML configs in __init__
    def __init__(self):
        with open(self.config_agents_path, "r") as f:
            self.config_agents = yaml.safe_load(f)
        with open(self.config_tasks_path, "r") as f:
            self.config_tasks = yaml.safe_load(f)

    @agent
    def researcher_agent(self) -> Agent:
        return Agent(
            config=self.config_agents['researcher_agent'],  # type: ignore
            tools=[SimpleDDGTool()],
            verbose=True
        )

    @agent
    def writer_agent(self) -> Agent:
        return Agent(
            config=self.config_agents['writer_agent'],  # type: ignore
            verbose=True
        )

    @task
    def researcher_task(self) -> Task:
        return Task(
            config=self.config_tasks['researcher_task'],  # type: ignore
            agent=self.researcher_agent(),
        )

    @task
    def writer_task(self) -> Task:
        return Task(
            config=self.config_tasks['writer_task'],  # type: ignore
            agent=self.writer_agent(),
            context=[self.researcher_task()]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.researcher_agent(), self.writer_agent()],
            tasks=[self.researcher_task(), self.writer_task()],
        )


# ----------------------------
# Run the Crew
# ----------------------------
if __name__ == "__main__":
    research_crew = Research_and_writing_Crew()
    topic = input("Enter the research topic: ")
    research_crew.crew().kickoff(inputs={'topic': topic})
