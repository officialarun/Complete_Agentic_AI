
# MCP (Model Context Protocol) - Notes

## What is MCP?

MCP (Model Context Protocol) is an open protocol that standardizes communication between LLM applications and external tools/resources.

It acts like a **USB-C for AI applications**, allowing models to interact with tools, databases, APIs, files, etc., through a common interface.

---

# MCP Architecture

```text
LLM Application (Client)
            ↓
       MCP Client
            ↓
      MCP Transport
            ↓
       MCP Server
            ↓
   Tools / Resources
```

---

# MCP Components

## 1. MCP Client

* Lives inside the AI application (LangGraph, Claude Desktop, Cursor, etc.)
* Discovers available tools from servers.
* Sends tool invocation requests.
* Receives tool outputs.

Example:

```python
client = MultiServerMCPClient({...})
tools = await client.get_tools()
```

---

## 2. MCP Server

Exposes capabilities to the model.

Can provide:

* Tools
* Resources
* Prompts

Example:

```python
mcp = FastMCP("Math")
```

---

## 3. Tools

Functions that the model can execute.

Example:

```python
@mcp.tool()
def add(a:int,b:int):
    return a+b
```

Flow:

```text
LLM
 ↓
Tool Call
 ↓
MCP Server
 ↓
Tool Result
```

---

# Transport in MCP

Transport defines **how client and server communicate**.

MCP defines **what messages look like**, while transport defines **how they travel**.

---

## A) stdio Transport

```python
mcp.run(transport="stdio")
```

Communication:

```text
stdin <----JSON RPC----> stdout
```

Client launches server as a subprocess.

Example:

```python
{
    "command":"python",
    "args":["mathserver.py"],
    "transport":"stdio"
}
```

### Use Cases

* Local tools
* Claude Desktop
* Cursor
* Fast local communication

### Important

Do NOT use:

```python
print(...)
```

because stdout is used by MCP.

Instead:

```python
print(..., file=sys.stderr)
```

---

## B) streamable-http Transport

```python
{
    "url":"http://localhost:8000/mcp",
    "transport":"streamable-http"
}
```

Communication:

```text
HTTP Request
      ↓
Remote MCP Server
```

### Use Cases

* Remote tools
* Cloud deployment
* Shared services

---

# FastMCP

FastMCP is a high-level framework for building MCP servers.

Example:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")
```

Expose tools:

```python
@mcp.tool()
def multiply(a:int,b:int):
    return a*b
```

Run server:

```python
mcp.run(transport="stdio")
```

---

# LangGraph + MCP Integration

```python
client = MultiServerMCPClient({...})

tools = await client.get_tools()

agent = create_react_agent(
    model=model,
    tools=tools
)
```

Flow:

```text
LLM
 ↓
Tool Discovery
 ↓
Tool Call
 ↓
MCP Server
 ↓
Tool Output
 ↓
Final Answer
```

---

# Important Observation About Tool Calling

LLMs may perform **speculative planning**.

Example:

```text
Question:
(5+10)*12
```

Model may generate:

```text
add(5,10)
multiply(15,12)
```

without waiting for `add()` result.

This is called:

### Parallel Tool Planning / Speculative Tool Planning

---

# create_react_agent Limitation

`create_react_agent()` does NOT guarantee:

```text
tool1
 ↓
wait
 ↓
tool2
```

Instead:

```text
LLM
 ↓
Emit multiple tool calls
 ↓
Execute all tool calls
```

---

# Sequential Tool Execution

To enforce:

```text
Tool1
 ↓
Wait
 ↓
Tool2
```

build a custom LangGraph workflow:

```text
LLM Node
    ↓
Execute ONLY first tool
    ↓
Append ToolMessage
    ↓
LLM Node
```

---

# Debugging Tool Calls

Inspect full message history:

```python
for msg in response["messages"]:
    print(msg)
```

Useful message types:

* HumanMessage
* AIMessage
* ToolMessage
* SystemMessage

---

# Tool Calls in AIMessage

```python
AIMessage(
    tool_calls=[
        ...
    ]
)
```

Tool outputs:

```python
ToolMessage(...)
```

Presence of `ToolMessage` proves that the tool actually executed.

---

# Good Tools for Testing Agents

Avoid easy arithmetic because models know the answers.

Better tools:

* Random secret generators
* UUID generators
* SHA256 hashing
* Current timestamps
* Stateful memory tools

These force the model to actually use tools.

---

# Key Takeaways

1. MCP standardizes tool communication.
2. Transport defines how messages travel.
3. FastMCP simplifies server creation.
4. LangGraph can consume MCP tools directly.
5. LLMs often plan multiple tool calls ahead.
6. `create_react_agent()` does not guarantee sequential execution.
7. Custom LangGraph workflows can enforce strict tool sequencing.
