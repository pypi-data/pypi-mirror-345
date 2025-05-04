#!/usr/bin/env python3
import os
import json
from main import get_mcp_client

def print_json(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2))

def run_examples():
    # Initialize the MCP client
    client = get_mcp_client()
    print(f"Connected to API at {client.api_url}")
    
    # Example 1: Look up employee by name
    print("\n=== Example 1: Look up employee by name ===")
    result = client.lookup_employee(name_or_alias="John")
    print_json(result)
    
    # Example 2: Look up employee by exact alias
    print("\n=== Example 2: Look up employee by exact alias ===")
    result = client.lookup_employee(name_or_alias="john.doe", exact_match=True)
    print_json(result)
    
    # Example 3: Get direct reports
    print("\n=== Example 3: Get direct reports ===")
    result = client.lookup_direct_reports(alias="john.doe")
    print_json(result)
    
    # Example 4: Get all reports with filtering
    print("\n=== Example 4: Get all reports with filtering ===")
    result = client.lookup_all_reports(
        alias="john.doe",
        title="Software Engineer",
        is_manager=False
    )
    print_json(result)
    
    # Example 5: Find employees by criteria
    print("\n=== Example 5: Find employees by criteria ===")
    result = client.find_employees(
        office="Seattle",
        title="Program Manager"
    )
    print_json(result)
    
    # Example 6: Get span of control
    print("\n=== Example 6: Get span of control ===")
    result = client.get_span_of_control(alias="john.doe")
    print_json(result)
    
    # Example 7: Get org depth
    print("\n=== Example 7: Get org depth ===")
    result = client.get_org_depth(alias="john.doe")
    print_json(result)

    # Example 8: Count all reports with filtering
    print("\n=== Example 8: Count all reports with filtering ===")
    result = client.count_all_reports(
        alias="john.doe",
        title="Software Engineer",
        is_manager=False
    )
    print_json(result)
    
    # Example 9: Count employees by criteria
    print("\n=== Example 9: Count employees by criteria ===")
    result = client.count_employees(
        office="Seattle",
        title="Program Manager"
    )
    print_json(result)

if __name__ == "__main__":
    try:
        run_examples()
    except Exception as e:
        print(f"Error: {str(e)}") 