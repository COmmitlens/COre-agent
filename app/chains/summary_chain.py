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
