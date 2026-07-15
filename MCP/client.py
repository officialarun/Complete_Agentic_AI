import os
import asyncio
from langchain.agents import create_agent
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent

load_dotenv()

async def main():
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")

    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": ["mathserver.py"],
                "transport": "stdio",
            },
            "weather": {
                "url": "http://localhost:8000/mcp",
                "transport": "streamable-http",
            },
        }
    )

    tools = await client.get_tools()
    model=ChatGroq(model="llama-3.3-70b-versatile")
    agent = create_agent(
    model=model,
    tools=tools
)

    # weather_response=await agent.ainvoke({"messages":[{"role":"user","content":"What is the weather in California"}]})
    # print("Loaded tools:", [tool.name for tool in tools])
    # print("Weather Response:", weather_response["messages"][-1].content)
    # for msg in weather_response["messages"]:
    #     print(type(msg).__name__)
    #     print(msg)
    #     print("=" * 50)
    
    # test for math tool
    # math_response=await agent.ainvoke({"messages":[{"role":"user","content":"Only use availabletools to answer the question.If tools not available or error occurs notify the user about it:What is the result of (5 + 10) * 12"}]})
    math_response = await agent.ainvoke(
    {
        "messages": [
            {
                "role": "system",
                "content": """
                You are a tool-using assistant.

                Rules:
                1. Call only ONE tool at a time.
                2. If a tool call requires argument which depends on output of another tool call, you must first call the first tool and wait for its result before calling the second tool.    
                3. Wait for the tool result before deciding the next action.
                4. Never generate nested tool calls.
                5. If multiple calculations are required, perform them step-by-step.
                """
            },
            {
                "role": "user",
                "content": "Get a secret random integer and then calculate the SHA256 hash of that number."
            }
        ]
    }
)
    print("Math Response:", math_response["messages"][-1].content)
    for msg in math_response["messages"]:
        print(type(msg).__name__)
        print(msg)
        print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())


