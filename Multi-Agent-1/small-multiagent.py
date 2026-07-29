import os
from crewai import LLM, Agent, Task, Crew
from dotenv import load_dotenv
from crewai_tools import SerperDevTool

load_dotenv()

groq_api_key = os.getenv('GROQ_KEY')

gemini_llm = LLM(
    model='llama-3.3-70b-versatile',
    provider='openai',
    api_key=groq_api_key,
    base_url='https://api.groq.com/openai/v1',
    temperature=0.0  # Lower temperature for more consistent results.
)

# Tool for research
search_tool = SerperDevTool()

# Research Agent
research_agent = Agent(
    role="Research Specialist",
    goal="Collect accurate and useful information from the web related to the topic.",
    backstory="An expert researcher with the ability to find high-quality insights quickly.",
    tools=[search_tool],
    verbose=True,
    llm = gemini_llm,
)

# Writer Agent
writer_agent = Agent(
    role="Content Writer",
    goal="Create a clear and well-structured explanation using provided research.",
    backstory="A skilled writer who converts raw research into polished content.",
    verbose=True,
    llm=gemini_llm,
)

# Research Task
research_task = Task(
    description="Search the web and gather information about: 'How does reinforcement learning work?'",
    expected_output="A detailed but simple bullet-point research summary.",
    agent=None,  # Assigned at runtime
)

# Writing task
writing_task = Task(
    description="Using the research summary, write a final explanation understandable by beginners.",
    expected_output="A polished explanation of reinforcement learning.",
    agent=None,  # Assigned at runtime
)

# Assign agents to tasks
research_task.agent = research_agent
writing_task.agent = writer_agent

# Create the Crew (MAS)
crew = Crew(
    agents=[research_agent, writer_agent],
    tasks=[research_task, writing_task],
    verbose=True,
)

result = crew.kickoff()

final_output = result.raw           # or result.output

with open("final_report.md", "w") as f:
    f.write(final_output)