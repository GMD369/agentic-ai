from smolagents import CodeAgent, InferenceClientModel, WebSearchTool

model = InferenceClientModel(model_id="Qwen/Qwen2.5-Coder-32B-Instruct")
agent = CodeAgent(tools=[WebSearchTool()], model=model, stream_outputs=True)

result = agent.run("What's the temprature in Paris today?")
print(result)