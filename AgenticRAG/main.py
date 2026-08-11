# main.py
import os
from crewai import Crew, Process
from crewai import LLM
from dotenv import load_dotenv

from rag_agent import get_retriever_agent, get_responder_agent
from tasks import retrieval_task, answering_task

# Load env variables
load_dotenv()
groq_key = os.getenv("GROQ_KEY")

# Create Groq LLM
groq_llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=groq_key,
    temperature=0.2
)

# Simple text file acting as "knowledge base"
def load_knowledge():
    knowledge_path = os.path.join(os.path.dirname(__file__), "knowledge.md")
    with open(knowledge_path, "r") as f:
        return f.read()

from tools import TextTool

knowledge_text = load_knowledge()
knowledge_tool = TextTool(content=knowledge_text)

# Create agents
retriever = get_retriever_agent(groq_llm, knowledge_tool)
responder = get_responder_agent(groq_llm)

# Provide user query
query = "Explain what this knowledge base contains and Summarize it."

# Create tasks
task1 = retrieval_task(retriever, query)
task2 = answering_task(responder, query)

# Create Crew
crew = Crew(
    agents=[retriever, responder],
    tasks=[task1, task2],
    process=Process.sequential,
    verbose=True
)

# Run pipeline
result = crew.kickoff()     
print("\nFINAL ANSWER:\n", result)