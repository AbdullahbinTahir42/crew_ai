from crewai import Crew, Task, Agent, LLM, Process
from typing import List
from crewai.project import crew, agent, task, CrewBase
from crewai.tools import BaseTool
from duckduckgo_search import DDGS
import yaml
from pydantic import BaseModel, Field

# Import your custom tools (save the previous artifact as 'custom_tools.py')
from custom_tools import (
    CustomScrapeWebsiteTool, 
    CustomDirectoryReadToolWithDefault, 
    CustomFileReadTool, 
    CustomFileWriterTool,
    EnhancedDDGTool
)

class SimpleDDGTool(BaseTool):
    name: str = "DuckDuckGo Search"
    description: str = "Performs a simple web search using DuckDuckGo."

    def _run(self, query: str) -> str:
        with DDGS() as ddg:
            results = ddg.text(query, max_results=3)
            return "\n".join([r["title"] + " - " + r["href"] for r in results])

llm = LLM(
    model="gemini/gemini-1.5-flash",
    temperature=0.7
)

class Content(BaseModel):
    content_type: str = Field(..., description="The type of content to be created (e.g., blog post, social media post, video)")                         
    topic: str = Field(..., description="The topic of the content")
    target_audience: str = Field(..., description="The target audience for the content")
    tags: List[str] = Field(..., description="Tags to be used for the content")
    content: str = Field(..., description="The content itself")

@CrewBase
class TheMarketingAgent():
    config_agents_path = "config/agents.yaml"
    config_tasks_path = "config/tasks.yaml"

    def __init__(self):
        with open(self.config_agents_path, "r") as f:
            self.agents_config = yaml.safe_load(f)
        with open(self.config_tasks_path, "r") as f:
            self.tasks_config = yaml.safe_load(f)

    @agent
    def head_of_marketing(self) -> Agent:
        return Agent(
            config=self.agents_config['marketing_head'], # type: ignore
            tools=[
                EnhancedDDGTool(),
                CustomScrapeWebsiteTool(), 
                CustomDirectoryReadToolWithDefault(),
                CustomFileReadTool(),
                CustomFileWriterTool()
            ],
            verbose=True,
            reasoning=True,
            llm=llm,
            inject_date=True,
            allow_delegation=True,
            max_rpm=1
        )
    
    @agent
    def content_creator_for_social_media(self) -> Agent:
        return Agent(
            config=self.agents_config['content_creator_for_social_media'], # type: ignore
            tools=[
                EnhancedDDGTool(),
                CustomScrapeWebsiteTool(),
                CustomDirectoryReadToolWithDefault(),
                CustomFileReadTool(),
                CustomFileWriterTool()
            ],
            verbose=True,
            llm=llm,
            inject_date=True,
            max_iter=30,
            allow_delegation=True,
            max_rpm=1
        )

    @agent
    def content_creator_for_blogs(self) -> Agent:
        return Agent(
            config=self.agents_config['content_creator_for_blogs'], # type: ignore
            tools=[
                EnhancedDDGTool(),
                CustomScrapeWebsiteTool(),
                CustomDirectoryReadToolWithDefault(),
                CustomFileReadTool(),
                CustomFileWriterTool()
            ],
            verbose=True,
            llm=llm,
            inject_date=True,
            max_iter=30,
            allow_delegation=True,
            max_rpm=1
        )

    @agent
    def seo_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['seo_specialist'], # type: ignore
            tools=[
                EnhancedDDGTool(),
                CustomScrapeWebsiteTool(),
                CustomDirectoryReadToolWithDefault(),
                CustomFileReadTool(),
                CustomFileWriterTool()
            ],
            verbose=True,
            llm=llm,
            inject_date=True,
            max_iter=30,
            allow_delegation=True,
            max_rpm=1
        )
    
    # Tasks
    @task
    def market_research(self) -> Task:
        return Task(
            config=self.tasks_config['market_research'], # type: ignore
            agent=self.head_of_marketing(),
        )
    
    @task
    def prepare_marketing_strategy(self) -> Task:
        return Task(
            config=self.tasks_config['prepare_marketing_strategy'], # type: ignore
            agent=self.head_of_marketing()
        )

    @task
    def create_content_calendar(self) -> Task:
        return Task(
            config=self.tasks_config['create_content_calendar'], # type: ignore
            agent=self.content_creator_for_social_media()
        )

    @task
    def prepare_post_drafts(self) -> Task:
        return Task(
            config=self.tasks_config['prepare_post_drafts'], # type: ignore 
            agent=self.content_creator_for_social_media(),
            output_json=Content
        )

    @task
    def prepare_scripts_for_reels(self) -> Task:
        return Task(
            config=self.tasks_config['prepare_scripts_for_reels'], # type: ignore
            agent=self.content_creator_for_social_media(),
            output_json=Content
        )

    @task
    def content_research_for_blogs(self) -> Task:
        return Task(
            config=self.tasks_config['content_research_for_blogs'], # type: ignore
            agent=self.content_creator_for_blogs()
        )

    @task
    def draft_blogs(self) -> Task:
        return Task(
            config=self.tasks_config['draft_blogs'], # type: ignore
            agent=self.content_creator_for_blogs(),
            output_json=Content
        )

    @task
    def seo_optimization(self) -> Task:
        return Task(
            config=self.tasks_config['seo_optimization'], # type: ignore
            agent=self.seo_specialist(),
            output_json=Content
        )
    
    @crew
    def marketingCrew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            planning=True,
            planning_llm=llm,
            max_rpm=1
        )

if __name__ == "__main__":
    from datetime import datetime

    inputs = {
        "product_name": "AI Powered Excel Automation Tool",
        "target_audience": "Small and Medium Enterprises (SMEs)",
        "product_description": "A tool that automates repetitive tasks in Excel using AI, saving time and reducing errors.",
        "budget": "Rs. 50,000",
        "current_date": datetime.now().strftime("%Y-%m-%d"),
    }
    crew = TheMarketingAgent()
    crew.marketingCrew().kickoff(inputs=inputs)
    print("Marketing Crew has been kicked off successfully!")