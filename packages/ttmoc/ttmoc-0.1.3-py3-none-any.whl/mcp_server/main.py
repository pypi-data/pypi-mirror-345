#!/usr/bin/env python3
import os
import asyncio
import json
import logging
import requests
import sys
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, UUID4
from mcp.server.fastmcp import FastMCP
from azure.identity import AzureCliCredential, ChainedTokenCredential, InteractiveBrowserCredential
from .token_manager import TokenManager, create_default_credential

# Configure logging to output to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Default API URL - can be overridden with environment variable
DEFAULT_API_URL = "http://localhost:8000"
API_URL = os.getenv("WHO_NEXT_API_URL", DEFAULT_API_URL)

# Print startup message to stderr so it doesn't interfere with MCP protocol
print("Starting Who-Next MCP Server...", file=sys.stderr)
print(f"Connecting to API at: {API_URL}", file=sys.stderr)

# AAD Configuration
AAD_TENANT_ID = os.getenv("AAD_TENANT_ID")
ALLOW_DEV_TOKEN = os.getenv("ALLOW_DEV_TOKEN", "false").lower() == "true"

# Initialize Azure credentials and token manager
try:
    credential = create_default_credential(tenant_id=AAD_TENANT_ID)
    token_manager = TokenManager(
        credential=credential,
        scope="https://graph.microsoft.com/.default",
        allow_dev_token=ALLOW_DEV_TOKEN
    )
    print("Token manager initialized successfully", file=sys.stderr)
except Exception as e:
    print(f"Error initializing token manager: {str(e)}", file=sys.stderr)
    if ALLOW_DEV_TOKEN:
        print("Continuing with dev token support enabled", file=sys.stderr)
    else:
        print("Authentication is required and dev token is not allowed. Exiting.", file=sys.stderr)
        sys.exit(1)

try:
    # Initialize FastMCP server
    mcp = FastMCP("who-next")
    print("MCP server initialized successfully", file=sys.stderr)
except Exception as e:
    print(f"Error initializing MCP server: {str(e)}", file=sys.stderr)
    sys.exit(1)

# Helper function for making API requests
async def make_api_request(method: str, endpoint: str, params: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Dict:
    """Make a request to the REST API with error handling."""
    url = f"{API_URL}{endpoint}"
    
    try:
        # Get a fresh token for each request
        token = await token_manager.get_valid_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.request(
            method=method,
            url=url,
            params=params,
            json=json_data,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_message = f"API request failed: {str(e)}"
        if hasattr(e, 'response') and e.response:
            error_message += f" Response: {e.response.text}"
        logger.error(error_message)
        return {"error": error_message}

# Helper function to format employee data consistently
def format_employee(emp: Dict) -> Dict:
    """Format employee data consistently across all tools."""
    return emp

# Tool implementations

@mcp.tool()
async def lookup_employee_by_name_or_alias(
    name_or_alias: str = Field(..., description="Employee display name or email alias to search for"),
    exact_match: bool = Field(False, description="Whether to use exact matching (when not searching for exact alias match)")
) -> List[Dict]:
    """Look up employees by display name or alias. Uses a smarter lookup strategy:
    1. First tries to find an exact match on alias
    2. If no exact match on alias, then searches both alias and display name
    
    Returns:
        A formatted list of employees with the following fields for each:
        - Name: The employee's display name
        - Alias: Email alias
        - Title: Job title
        - Office: Office location
        - Cost Center: Department/cost center
        - Manager Alias: Email alias of the employee's manager
        - Is Manager: Whether the employee is a manager (True/False)
        - Org Size: Size of the employee's organization
        - Org Level: Level in the organization hierarchy
        - Management Chain: List of managers in the employee's management chain
    """
    params = {
        "name_or_alias": name_or_alias,
        "exact_match": exact_match,
        "limit": 100  # Fixed limit of 100
    }
    
    result = await make_api_request("GET", "/api/employee", params=params)
    
    if "error" in result:
        return f"Error looking up employee: {result['error']}"
    
    employees = result.get("employees", [])
    if not employees:
        return f"No employees found matching '{name_or_alias}'."
    
    formatted_employees = []
    for emp in employees:
        formatted_employees.append(format_employee(emp))
    
    return formatted_employees

@mcp.tool()
async def lookup_direct_reports(
    alias: str = Field(..., description="Email alias of the manager"),
    limit: int = Field(10, description="Maximum number of results to return")
) -> List[Dict]:
    """Get direct reports for an employee.
    
    Returns:
        A formatted list of direct reports with the following fields for each:
        - Name: The employee's display name
        - Alias: Email alias
        - Title: Job title
        - Office: Office location
        - Cost Center: Department/cost center
        - Manager Alias: Email alias of the employee's manager
        - Is Manager: Whether the employee is a manager (True/False)
        - Org Size: Size of the employee's organization
        - Org Level: Level in the organization hierarchy
        - Management Chain: List of managers in the employee's management chain
    """
    params = {
        "alias": alias,
        "limit": min(limit, 500)
    }
    
    result = await make_api_request("GET", "/api/direct_reports", params=params)
    
    if "error" in result:
        return f"Error looking up direct reports: {result['error']}"
    
    reports = result.get("direct_reports", [])
    if not reports:
        return f"No direct reports found for {alias}."
    
    formatted_reports = []
    for emp in reports:
        formatted_reports.append(format_employee(emp))
    
    return formatted_reports

@mcp.tool()
async def find_all_reports_by_alias(
    alias: str = Field(..., description="Email alias of the manager"),
    limit: int = Field(10, description="Maximum number of results to return"),
    name: Optional[str] = Field(None, description="Filter by employee display name"),
    title: Optional[str] = Field(None, description="Filter by job title"),
    cost_center: Optional[str] = Field(None, description="Filter by department/cost center"), 
    office: Optional[str] = Field(None, description="Filter by office location"),
    is_manager: Optional[bool] = Field(None, description="Filter by manager status")
) -> List[Dict]:
    """Get all reports (direct and indirect) for an employee (by its alias) with optional filtering.
    Note this will usually return a lot of results, so it's recommended to use limit to limit the number of results.
    And it's not recommended to use this api to get the list for counting, use count_ apis.
    
    Returns:
        A formatted list of all reports (direct and indirect) with the following fields for each:
        - Name: The employee's display name
        - Alias: Email alias
        - Title: Job title
        - Office: Office location
        - Cost Center: Department/cost center
        - Manager Alias: Email alias of the employee's manager
        - Is Manager: Whether the employee is a manager (True/False)
        - Org Size: Size of the employee's organization
        - Org Level: Level in the organization hierarchy
        - Management Chain: List of managers in the employee's management chain
    """
    params = {
        "alias": alias,
        "limit": min(limit, 500)
    }
    
    # Create request body with matching API field names
    json_data = {}
    if name:
        json_data["name"] = name
    if title:
        json_data["title"] = title
    if cost_center:
        # Match the API's expected field name
        json_data["cost_center"] = cost_center
    if office:
        json_data["office"] = office
    if is_manager is not None:
        json_data["is_manager"] = is_manager
    
    result = await make_api_request("POST", "/api/all_reports", params=params, json_data=json_data if json_data else None)
    
    if "error" in result:
        return f"Error looking up all reports: {result['error']}"
    
    reports = result.get("reports", [])
    if not reports:
        return f"No reports found for {alias} with the specified criteria."
    
    formatted_reports = []
    for emp in reports:
        formatted_reports.append(format_employee(emp))
    
    return formatted_reports

@mcp.tool()
async def find_employees(
    name: Optional[str] = Field(None, description="Filter by employee display name"),
    title: Optional[str] = Field(None, description="Filter by job title"),
    cost_center: Optional[str] = Field(None, description="Filter by department/cost center"),
    office: Optional[str] = Field(None, description="Filter by office location"),
    is_manager: Optional[bool] = Field(None, description="Filter by manager status"),
    exact_match: bool = Field(False, description="Whether to use exact matching for criteria"),
    limit: int = Field(10, description="Maximum number of results to return")
) -> List[Dict]:
    """Find employees across the entire organization by criteria.
    Note this will usually return a lot of results, so it's recommended to use limit to limit the number of results.
    And it's not recommended to use this api to get the list for counting, use count_ apis.
    
    Returns:
        A formatted list of employees matching the criteria with the following fields for each:
        - Name: The employee's display name
        - Alias: Email alias
        - Title: Job title
        - Office: Office location
        - Cost Center: Department/cost center
        - Manager Alias: Email alias of the employee's manager
        - Is Manager: Whether the employee is a manager (True/False)
        - Org Size: Size of the employee's organization
        - Org Level: Level in the organization hierarchy
        - Management Chain: List of managers in the employee's management chain
    """
    if not any([name, title, cost_center, office, is_manager is not None]):
        return "Error: At least one search criterion must be provided"
    
    params = {
        "limit": min(limit, 500),
        "exact_match": exact_match
    }
    
    # Create request body using API field names
    json_data = {}
    if name:
        json_data["name"] = name
    if title:
        json_data["title"] = title
    if cost_center:
        # Match the API's expected field name
        json_data["cost_center"] = cost_center
    if office:
        json_data["office"] = office
    if is_manager is not None:
        json_data["is_manager"] = is_manager
    
    result = await make_api_request("POST", "/api/find", params=params, json_data=json_data)
    
    if "error" in result:
        return f"Error finding employees: {result['error']}"
    
    employees = result.get("employees", [])
    if not employees:
        return "No employees found matching your criteria."
    
    formatted_employees = []
    for emp in employees:
        formatted_employees.append(format_employee(emp))
    
    return formatted_employees

@mcp.tool()
async def get_span_of_control_by_alias(
    alias: str = Field(..., description="Alias of the employee")
) -> Dict:
    """Get span of control metrics for an employee (by its alias), span of control describes on average how many employees a manager has in the organization (managed by this employee)..
    
    Returns:
        Span of control metrics including:
        - Is Manager: Whether the employee is a manager (True/False)
        - Total Employees: Total number of employees in the organization
        - Total Managers: Total number of managers in the organization
        - Span of Control: Ratio of total employees to total managers
    """
    params = {
        "alias": alias
    }
    
    result = await make_api_request("GET", "/api/span_of_control", params=params)
    
    if "error" in result:
        return f"Error getting span of control: {result['error']}"
    
    is_manager = result.get("is_manager", False)
    total_employees = result.get("total_employees", 0)
    total_managers = result.get("total_managers", 0)
    span_of_control = result.get("span_of_control", 0.0)
    
    if not is_manager:
        return f"{alias} is not a manager. Span of control: 0"
    
    return {
        "Is Manager": is_manager,
        "Total Employees": total_employees,
        "Total Managers": total_managers,
        "Span of Control": span_of_control
    }

@mcp.tool()
async def get_org_depth_by_alias(
    alias: str = Field(..., description="Alias of the employee")
) -> Dict:
    """Get organizational depth metrics for an employee (by its alias).
    
    Returns:
        Organizational depth metrics including:
        - Maximum Org Level: Highest organization level in the employee's organization
        - Minimum Org Level: Lowest organization level in the employee's organization
        - Organization Depth: Overall depth of the organization (difference between max and min)
    """
    params = {
        "alias": alias
    }
    
    result = await make_api_request("GET", "/api/org_depth", params=params)
    
    if "error" in result:
        return f"Error getting organizational depth: {result['error']}"
    
    max_org_level = result.get("max_org_level", 0)
    min_org_level = result.get("min_org_level", 0)
    org_depth = result.get("org_depth", 0)
    
    return {
        "Maximum Org Level": max_org_level,
        "Minimum Org Level": min_org_level,
        "Organization Depth": org_depth
    }

@mcp.tool()
async def count_all_reports_by_alias(
    alias: str = Field(..., description="Email alias of the manager"),
    name: Optional[str] = Field(None, description="Filter by employee display name"),
    title: Optional[str] = Field(None, description="Filter by job title"),
    cost_center: Optional[str] = Field(None, description="Filter by department/cost center"), 
    office: Optional[str] = Field(None, description="Filter by office location"),
    is_manager: Optional[bool] = Field(None, description="Filter by manager status")
) -> int:
    """Count all reports (direct and indirect) for an employee by it's alias with optional filtering. 
    
    Returns:
        The total count of reports matching the specified criteria.
    """
    # Create request body with matching API field names
    json_data = {}
    if name:
        json_data["name"] = name
    if title:
        json_data["title"] = title
    if cost_center:
        # Match the API's expected field name
        json_data["cost_center"] = cost_center
    if office:
        json_data["office"] = office
    if is_manager is not None:
        json_data["is_manager"] = is_manager
    
    params = {
        "alias": alias
    }
    
    result = await make_api_request("POST", "/api/count_all_reports", params=params, json_data=json_data if json_data else None)
    
    if "error" in result:
        return f"Error counting all reports: {result['error']}"
    
    count = result.get("count", 0)
    
    if count == 0:
        return f"No reports found for {alias} with the specified criteria."
    
    return count

@mcp.tool()
async def count_employees(
    name: Optional[str] = Field(None, description="Filter by employee display name"),
    title: Optional[str] = Field(None, description="Filter by job title"),
    cost_center: Optional[str] = Field(None, description="Filter by department/cost center"),
    office: Optional[str] = Field(None, description="Filter by office location"),
    is_manager: Optional[bool] = Field(None, description="Filter by manager status"),
    exact_match: bool = Field(False, description="Whether to use exact matching for criteria")
) -> int:
    """Count employees by criteria across the entire organization.
    
    Returns:
        The total count of employees matching the specified criteria.
    """
    if not any([name, title, cost_center, office, is_manager is not None]):
        return "Error: At least one search criterion must be provided"
    
    params = {
        "exact_match": exact_match
    }
    
    # Create request body using API field names
    json_data = {}
    if name:
        json_data["name"] = name
    if title:
        json_data["title"] = title
    if cost_center:
        # Match the API's expected field name
        json_data["cost_center"] = cost_center
    if office:
        json_data["office"] = office
    if is_manager is not None:
        json_data["is_manager"] = is_manager
    
    result = await make_api_request("POST", "/api/count_employees", params=params, json_data=json_data)
    
    if "error" in result:
        return f"Error counting employees: {result['error']}"
    
    count = result.get("count", 0)
    
    if count == 0:
        return "No employees found matching your criteria."
    
    return count

def initialize_server():
    """Initialize the server components. This should be called after environment variables are set."""
    global mcp, token_manager
    
    # Print startup message to stderr so it doesn't interfere with MCP protocol
    print("Starting Who-Next MCP Server...", file=sys.stderr)
    print(f"Connecting to API at: {API_URL}", file=sys.stderr)
    
    try:
        credential = create_default_credential(tenant_id=AAD_TENANT_ID)
        token_manager = TokenManager(
            credential=credential,
            scope="https://graph.microsoft.com/.default",
            allow_dev_token=ALLOW_DEV_TOKEN
        )
        print("Token manager initialized successfully", file=sys.stderr)
    except Exception as e:
        print(f"Error initializing token manager: {str(e)}", file=sys.stderr)
        if ALLOW_DEV_TOKEN:
            print("Continuing with dev token support enabled", file=sys.stderr)
        else:
            print("Authentication is required and dev token is not allowed. Exiting.", file=sys.stderr)
            sys.exit(1)

    try:
        # Initialize FastMCP server
        mcp = FastMCP("who-next")
        
        # Register all tool functions with the MCP server
        mcp.tool()(lookup_employee)
        mcp.tool()(lookup_direct_reports)
        mcp.tool()(lookup_all_reports)
        mcp.tool()(find_employees)
        mcp.tool()(get_span_of_control)
        mcp.tool()(get_org_depth)
        mcp.tool()(count_all_reports)
        mcp.tool()(count_employees)
        
        print("MCP server initialized successfully", file=sys.stderr)
    except Exception as e:
        print(f"Error initializing MCP server: {str(e)}", file=sys.stderr)
        sys.exit(1)
        
    return mcp



# Run the server
if __name__ == "__main__":
    print("Starting MCP server with stdio transport...", file=sys.stderr)
    try:
        mcp.run()
        print("MCP server started successfully", file=sys.stderr)
    except Exception as e:
        print(f"Error starting MCP server: {str(e)}", file=sys.stderr)
        sys.exit(1) 