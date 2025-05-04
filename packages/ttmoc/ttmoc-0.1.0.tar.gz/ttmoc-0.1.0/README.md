# Who-Next

A LLM-powered "org chart" Q&A tool that provides natural language queries over organizational data.

## Overview

Who-Next allows users to ask natural language questions about the organizational structure, such as:
- How many FTEs total are under a specific person?
- Who are the peers of a given employee?
- List all managers in a specific team
- Find people with a specific title in a department
- Track changes in the organization

## Project Structure

The project is organized into the following components:

### [Pipeline](./pipeline)
Python script for retrieving organizational data from Microsoft Graph API, calculating derived fields, and exporting to CSV.

### [Database](./db)
Storage solution for the organizational data, supporting efficient queries and tracking changes over time.

### [REST API](./api)
Service that handles natural language queries and returns structured data responses.

### [MCP Server](./mcp_server)
Wrapper for the REST API service that handles authentication and token management.

### [Web UI](./ui)
Clean chat interface for interacting with the Q&A service.

## Development Roadmap

- **MVP**: Pipeline + Database
- **V1**: REST API + MCP Server
- **V2**: Web UI

## Getting Started

Each component has its own README with specific setup instructions. To start working with the project:

1. Clone this repository
2. Set up the pipeline component to extract organizational data
3. Set up the database component to store the data
4. Follow the individual component READMEs for further setup instructions

## Architecture

```
+------------------+     +--------------+     +------------+
| Azure AD /       |     |              |     |            |
| Microsoft Graph  |---->|   Pipeline   |---->|  Database  |
+------------------+     +--------------+     +------------+
                                                    |
                                                    v
                                         +-------------------+
                                         |     REST API      |
                                         +-------------------+
                                                |     |
                                                |     |
                                                v     v
                                    +---------+           +-----------------+
                                    |   UI    |           |   MCP Server    |
                                    +---------+           +-----------------+
```

### Data Flow

1. **Source**: Organizational data is stored in Azure Active Directory and retrieved via Microsoft Graph API
2. **Pipeline**: A daily scheduled process extracts and processes this data:
   - Filters relevant users (Microsoft emails, non-empty job titles, no hyphens in email)
   - Calculates derived fields (is_manager, org_size)
   - Exports to CSV format
3. **Database**: Stores the processed data for efficient querying
4. **REST API**: Retrieves data from the database and processes natural language queries into structured responses
5. **MCP Server**: Receives data from the REST API and handles authentication using Azure credentials
6. **UI**: Receives data from the REST API and provides a clean chat interface for users to interact with the system