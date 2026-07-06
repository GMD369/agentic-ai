from smolagents import CodeAgent, InferenceClientModel

# Initialize a model (using Hugging Face Inference API)
model = InferenceClientModel(model_id="Qwen/Qwen2.5-Coder-32B-Instruct")

# Create an agent with no tools
agent = CodeAgent(tools=[], model=model)

# Run the agent with a task
result = agent.run("Calculate the sum of numbers from 1 to 10")
print(result)