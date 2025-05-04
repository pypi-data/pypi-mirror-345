#!/usr/bin/env python3
import os
import json
import asyncio
import subprocess
from mcp.client.client import Client
from mcp.client.transport.stdio import StdioClientTransport

async def run_example():
    """
    Example of connecting to the who-next MCP server from a Python client.
    This simulates how Claude or another MCP client would connect to our server.
    """
    # Start the MCP server as a subprocess
    server_process = subprocess.Popen(
        ["python", "main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    
    # Create an MCP client connected to the server via stdio
    transport = StdioClientTransport(server_process.stdout, server_process.stdin)
    client = Client()
    
    try:
        # Connect and initialize
        await client.connect(transport)
        await client.initialize()
        
        # List all available tools
        tools = await client.list_tools()
        print("Available tools:")
        for tool in tools.tools:
            print(f"- {tool.name}: {tool.description}")
        print()
        
        # Example 1: Look up employee by name
        print("\n=== Example 1: Look up employee by name ===")
        result = await client.call_tool(
            name="lookup_employee",
            arguments={"name_or_alias": "John"}
        )
        print(result.content)
        
        # Example 2: Get direct reports
        print("\n=== Example 2: Get direct reports ===")
        result = await client.call_tool(
            name="lookup_direct_reports",
            arguments={"alias": "john.doe"}
        )
        print(result.content)
        
        # Example 3: Find employees by criteria
        print("\n=== Example 3: Find employees by criteria ===")
        result = await client.call_tool(
            name="find_employees",
            arguments={
                "title": "Software Engineer",
                "is_manager": True
            }
        )
        print(result.content)
        
        # Example 4: Get span of control
        print("\n=== Example 4: Get span of control ===")
        result = await client.call_tool(
            name="get_span_of_control",
            arguments={"alias": "john.doe"}
        )
        print(result.content)
        
        # Example 5: Get org depth
        print("\n=== Example 5: Get org depth ===")
        result = await client.call_tool(
            name="get_org_depth",
            arguments={"alias": "john.doe"}
        )
        print(result.content)
        
        # Example 6: Count all reports
        print("\n=== Example 6: Count all reports ===")
        result = await client.call_tool(
            name="count_all_reports",
            arguments={
                "alias": "john.doe",
                "title": "Software Engineer"
            }
        )
        print(result.content)
        
        # Example 7: Count employees by criteria
        print("\n=== Example 7: Count employees by criteria ===")
        result = await client.call_tool(
            name="count_employees",
            arguments={
                "title": "Software Engineer",
                "is_manager": True
            }
        )
        print(result.content)
        
    finally:
        # Clean up
        await client.close()
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    asyncio.run(run_example()) 