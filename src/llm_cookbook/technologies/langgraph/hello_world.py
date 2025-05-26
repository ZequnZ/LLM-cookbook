import os
from typing import Annotated

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from llm_cookbook.utils.tool_creation import create_tool, registry

# Load environment variables
load_dotenv(override=True)

llm = AzureChatOpenAI(
    model="gpt-4.1", api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)


# Tool parameter
class SearchStockPrice(BaseModel):
    name: str = Field(..., description="Search query for Stock name")


# Create tool function
@create_tool(
    name="search_stock_price",
    description="Search stock price from the database",
    parameters_model=SearchStockPrice,
)
def search_stock_price(name: str) -> str | int:
    """Implementation of stock price search functionality"""
    if name in ["AAPL", "TSM"]:
        return 100
    else:
        return f"Stock {name} is not in our database."


# Create a state type that includes a list of messages
class State(TypedDict):
    messages: Annotated[list, add_messages]


# Create a node
def call_model(state: State) -> State:
    return {
        "messages": [
            llm.invoke(state["messages"], tools=registry.list_tools_by_schema())
        ]
    }


def route_tools(
    state: State,
):
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route to the end.
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END


def call_tool_search_stock_price(state: State) -> State:
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route to the end.
    """
    for tool_call in state["messages"][-1].tool_calls:
        if tool_call["name"] == "search_stock_price":
            tool_args = tool_call["args"]
            result = search_stock_price(**tool_args)
            tool_response_message = {
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": str(result),
            }
    return {"messages": [tool_response_message]}


# Register the tool
registry.register(search_stock_price)

# Create a graph
graph = StateGraph(State)

graph.add_node("call_model", call_model)
graph.add_node("tools", call_tool_search_stock_price)

graph.add_edge(START, "call_model")
graph.add_conditional_edges(
    "call_model",
    route_tools,
    {
        "tools": "tools",
        END: END,
    },
)
graph.add_edge("tools", "call_model")
graph_complete = graph.compile()

if __name__ == "__main__":
    sys_prompt = "You are a helpful assistant that is able to privide info about stocks"
    input_ = "what is the stock price of AAPL?"

    message_stack = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": input_},
    ]
    result = graph_complete.invoke({"messages": message_stack})
    print(result["messages"][-1].content)
