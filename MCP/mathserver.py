import random
import hashlib
from mcp.server.fastmcp import FastMCP

mcp=FastMCP("Math")

@mcp.tool()
def add(a:int,b:int)->int:
    """_summary_
    Add to numbers
    """
    print("the call is inside add function")
    return a+b

@mcp.tool()
def multiple(a:int,b:int)-> int:
    """Multiply two numbers"""
    print("the call is inside multiple function")
    return a*b

@mcp.tool()
def secret_number() -> int:
    """Returns a secret random integer that only this tool knows."""
    num = random.randint(10000, 99999)
    print(f"Generated: {num}")
    return num


@mcp.tool()
def sha256_text(text: str) -> str:
    """Returns SHA256 hash."""
    return hashlib.sha256(text.encode()).hexdigest()

#The transport="stdio" argument tells the server to:

#Use standard input/output (stdin and stdout) to receive and respond to tool function calls

if __name__=="__main__":
    mcp.run(transport="stdio")