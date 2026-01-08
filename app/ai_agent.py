from pydantic_ai import Agent
from app.schemas import ScoreResponse
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize the agent. 
# You can customize the model parameter, e.g. "openai:gpt-4o" or just rely on default/env vars.
# For now, we assume the user has configured the model via env vars or default behavior.
model = OpenRouterModel(
    model_name="google/gemini-2.5-flash-lite",
    provider=OpenRouterProvider(
        api_key=os.getenv("OPENROUTER_API_KEY")
    )
)
scoring_agent = Agent(
    model=model,
    output_type=ScoreResponse,
    system_prompt=(
        "You are an expert Python code reviewer and grader. "
        "Your task is to evaluate a submitted Python script based on specific criteria provided. "
        "You must return a JSON object with a 'score' (0-100), 'feedback' (string), and 'reasoning' (optional string). "
        "Be fair, constructive, and strictly follow the criteria. "
        "If the code fails to run or has syntax errors, give a low score and explain why."
    ),
)

async def score_submission(code_content: str, criteria: str) -> ScoreResponse:
    prompt = f"### Criteria:\n{criteria}\n\n### Submitted Code:\n```python\n{code_content}\n```"
    result = await scoring_agent.run(prompt)
    print(f"DEBUG: Result Type: {type(result)}")
    print(f"DEBUG: Result Dir: {dir(result)}")
    try:
        return result.output
    except AttributeError:
        raise ValueError(f"Result attributes: {dir(result)}")
