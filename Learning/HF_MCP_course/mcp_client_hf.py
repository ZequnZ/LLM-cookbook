"""HF MCP client"""

import asyncio
import os

from huggingface_hub import MCPClient


async def main():
    async with MCPClient(
        model="Qwen/Qwen2.5-72B-Instruct",
        provider="novita",
        api_key=os.getenv("HUGGINGFACE_API_TOKEN"),
    ) as client:
        await client.add_mcp_server(
            type="http",
            url="https://zequnz-mcp-learning.hf.space/gradio_api/mcp/",
            terminate_on_close=True,
        )
        # ref: https://github.com/huggingface/huggingface_hub/blob/v0.34.4/src/huggingface_hub/inference/_mcp/mcp_client.py#L236
        async for result in client.process_single_turn_with_tools(
            [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that can answer questions and help with tasks.",
                },
                {
                    "role": "user",
                    "content": "Analyze the following text: {the weather is amazing, like you}",
                },
            ]
        ):
            if hasattr(result, "choices"):
                stream_output = result.choices[0]
                print(f"Num of choice: {len(result.choices)}")
                print(f"Role: {stream_output.delta.role}")
                print(f"Content: {stream_output.delta.content}")
                print(f"Tool calls: {stream_output.delta.tool_calls}")
                print("-" * 30)
            else:
                print(result)


if __name__ == "__main__":
    asyncio.run(main())
