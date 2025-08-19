from crewai import Crew, Task, Agent, LLM, Process
from typing import List
from crewai.project import crew,agent,task, CrewBase
from crewai.tools import BaseTool
from duckduckgo_search import DDGS
from crewai_tools import ScrapeWebsiteTool, DirectoryReadTool, FileReadTool,FileWriterTool
import yaml
from pydantic import BaseModel, Field

class SimpleDDGTool(BaseTool):
    name: str = "DuckDuckGo Search"
    description: str = "Performs a simple web search using DuckDuckGo."

    def _run(self, query: str) -> str:
        with DDGS() as ddg:
            results = ddg.text(query, max_results=3)
            return "\n".join([r["title"] + " - " + r["href"] for r in results])
        

llm = LLM(
    model= "gemini/gemini-2.0-flash",
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

    # Load YAML configs in __init__
    def __init__(self):
        with open(self.config_agents_path, "r") as f:
            self.config_agents = yaml.safe_load(f)
        with open(self.config_tasks_path, "r") as f:
            self.config_tasks = yaml.safe_load(f)

    @agent
    def head_of_marketing(self) -> Agent:
        return Agent(
            config=self.config_agents['marketing_head'],  # type: ignore
            tools=[
                   SimpleDDGTool(),
                   ScrapeWebsiteTool(), 
                   DirectoryReadTool('resources/drafts'),
                   FileReadTool(),
                   FileWriterTool()
                   ],
            verbose=True,
            reasoning=True, # This agent can reason about its actions means think before responding
            llm=llm,
            inject_date=True, # current date will be injected
            allow_delegation=True, #this agent can give tasks to another agent
            max_rpm=3
        )
    
    @agent
    def content_creator_for_social_media(self) -> Agent:
        return Agent(
            config=self.config_agents['content_creator_for_social_media'],  # type: ignore
            tools=[
                SimpleDDGTool(),
                ScrapeWebsiteTool(),
                DirectoryReadTool('resources/drafts'),
                FileReadTool(),
                FileWriterTool()
            ],
            verbose=True,
            llm=llm,
            inject_date=True,  # current date will be injected
            max_iter=30,
            allow_delegation=True,  # this agent can give tasks to another agent
            max_rpm=3
        )
    @agent
    def content_creator_for_blogs(self) -> Agent:
        return Agent(
            config=self.config_agents['content_creator_for_blogs'],  # type: ignore
            tools=[
                SimpleDDGTool(),
                ScrapeWebsiteTool(),
                DirectoryReadTool('resources/drafts'),
                FileReadTool(),
                FileWriterTool()
            ],
            verbose=True,
            llm=llm,
            inject_date=True,  # current date will be injected
            max_iter=30,
            allow_delegation=True,  # this agent can give tasks to another agent
            max_rpm=3
        )

    @agent
    def seo_specialist(self) -> Agent:
        return Agent(
            config=self.config_agents['seo_specialist'],  # type: ignore
            tools=[
                SimpleDDGTool(),
                ScrapeWebsiteTool(),
                DirectoryReadTool('resources/drafts'),
                FileReadTool(),
                FileWriterTool()
            ],
            verbose=True,
            llm=llm,
            inject_date=True,  # current date will be injected
            max_iter=30,
            allow_delegation=True,  # this agent can give tasks to another agent
            max_rpm=3
        )
    
    #Tasks

    @task
    def market_research(self) -> Task:
        return Task(
            config=self.config_tasks['market_research'],  # type: ignore
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
            config=self.tasks_config['prepare_post_drafts'],# type: ignore
            agent=self.content_creator_for_social_media(),
            output_json=Content
        )

    @task
    def prepare_scripts_for_reels(self) -> Task:
        return Task(
            config=self.tasks_config['prepare_scripts_for_reels'],# type: ignore
            agent=self.content_creator_for_social_media(),
            output_json=Content
        )

    @task
    def content_research_for_blogs(self) -> Task:
        return Task(
            config=self.tasks_config['content_research_for_blogs'],# type: ignore
            agent=self.content_creator_for_blogs()
        )

    @task
    def draft_blogs(self) -> Task:
        return Task(
            config=self.tasks_config['draft_blogs'],# type: ignore
            agent=self.content_creator_for_blogs(),
            output_json=Content
        )

    @task
    def seo_optimization(self) -> Task:
        return Task(
            config=self.tasks_config['seo_optimization'],# type: ignore
            agent=self.seo_specialist(),
            output_json=Content
        )