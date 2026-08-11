# rag_agent.py
from crewai import Agent


def get_retriever_agent(llm, knowledge_tool):
    return Agent(
        role="Knowledge Retriever",
        goal="Find and extract the most relevant passages from the knowledge base for a given query.",
        backstory="You are skilled at searching documents and pulling out only the relevant context.",
        tools=[knowledge_tool],
        verbose=True,
        llm=llm,
    )


def get_responder_agent(llm):
    return Agent(
        role="Question Answerer",
        goal="Answer the user's question clearly and accurately using only the retrieved context.",
        backstory="You specialize in turning retrieved context into precise, well-explained answers.",
        verbose=True,
        llm=llm,
    )
