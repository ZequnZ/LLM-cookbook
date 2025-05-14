import asyncio
import os

from agents import (
    Agent,
    Runner,
    enable_verbose_stdout_logging,
    set_default_openai_client,
    set_tracing_disabled,
)
from dotenv import load_dotenv
from openai import OpenAIError

from llm_cookbook.utils.get_client import async_openai_client

# Load environment variables
load_dotenv(override=True)

# Disable tracing since we're using Azure OpenAI
set_tracing_disabled(disabled=True)

# Enables verbose logging to stdout. This is useful for debugging.
enable_verbose_stdout_logging()

# Set the default OpenAI client for the Agents SDK
set_default_openai_client(async_openai_client, False)


async def main():
    try:
        # Configure the agent with Azure OpenAI
        agent = Agent(
            name="Assistant",
            instructions="You are a helpful assistant",
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        )

        result = await Runner.run(
            agent, "Write a haiku about recursion in programming."
        )
        print(result.final_output)

    except OpenAIError as e:
        print(f"OpenAI API Error: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
