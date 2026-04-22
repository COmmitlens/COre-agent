import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# Load environment variables
load_dotenv()

# Initialize Azure OpenAI client
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("ENDPOINT_URL"),
    api_version="2025-01-01-preview",
    azure_deployment="gpt-4o-mini",
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    streaming=True,
)


# Generate response from GPT + store
async def generate_response(prompt: str) -> str:
    try:
        # Invoke the LLM with the prompt
        response = await llm.ainvoke(prompt)
        return response.content

    except Exception as e:
        raise Exception(f"Error generating response: {str(e)}")


# Generate streaming response with system and user prompts
async def generate_streaming_response(system_prompt: str, user_prompt: str):
    """
    Generate a streaming response from the LLM.

    Args:
        system_prompt: The system message to set context
        user_prompt: The user's input prompt

    Yields:
        Chunks of the LLM response as they're generated
    """
    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        async for chunk in llm.astream(messages):
            if chunk.content:
                yield chunk.content

    except Exception as e:
        raise Exception(f"Error generating streaming response: {str(e)}")


async def classify_query_intent(user_query: str) -> str:

    try:
        system_prompt = """You are an intent classification assistant for a Git analytics tool.
Your task is to classify a user's query into exactly one of the following intent categories:

- code_explanation: The user wants an explanation of code changes, diffs, file contents, or what a commit does.
- get_commits_by_author_and_date: The user wants to find or list commits filtered by a specific author and/or date range also in query it will be given user email.
- get_recent_commits: The user wants to see the latest or most recent commits in a repository.

Rules:
- Respond with ONLY the intent label — no explanation, no punctuation, no extra text.
- Choose the single best matching intent.
- If unsure, default to get_recent_commits."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Classify the intent of this query: {user_query}"),
        ]

        response = await llm.ainvoke(messages)
        intent = response.content.strip()

        valid_intents = {
            "code_explanation",
            "get_commits_by_author_and_date",
            "get_recent_commits",
        }
        print(f"Classified intent: {intent}")
        if intent not in valid_intents:
            intent = "get_recent_commits"

        return intent

    except Exception as e:
        raise Exception(f"Error classifying query intent: {str(e)}")
