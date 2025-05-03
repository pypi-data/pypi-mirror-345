# MySQL MCP Server Documentation

## Overview
This repository contains the MySQL database configuration for the MCP (Model Context Protocol) server. This MCP server handles data fetching from the connected database.

## Prerequisites
- Python 3.10 or above
- pip or uv package installer
- mysql-connector-python

## Installation Steps
1. Install the MCP package using either pip or uv package installer. The MCP package version should be 1.6.0 or higher with the CLI components included.
2. Install the required MySQL connector package. This package is essential as it establishes the connection between your MCP server and the MySQL database, enabling data querying capabilities.
3. Set up your environment variables by creating a .env file in your project directory. This file should contain your database connection details including host, username, password, and database name.
4. After completing the installation and configuration, you can start the server and connect it to any MCP client for use. The server will handle database operations through the configured MySQL connection.
For detailed setup instructions and additional configuration options, refer to the official MCP Python SDK documentation.

## Environment Variables
Required environment variables for database connection:
- `DB_HOST` - Database host address
- `DB_USER` - Database username
- `DB_PASSWORD` - Database password
- `DB_NAME` - Target database name
