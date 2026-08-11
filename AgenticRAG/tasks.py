# tasks.py
from crewai import Task

def retrieval_task(retriever_agent, query):
    return Task(
        description=f"Retrieve relevant context for the query: {query}",
        expected_output="Relevant text extracted from the knowledge base.",
        agent=retriever_agent
    )

def answering_task(responder_agent, query):
    return Task(
        description=f"Answer the question using the retrieved context. "
                    f"Question: {query}",
        expected_output="A final answer based only on the provided context.",
        agent=responder_agent
    )