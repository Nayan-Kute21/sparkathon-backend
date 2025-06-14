# Store Management MCP Server

A Node.js Model Context Protocol (MCP) server that provides tools for interacting with your store management API running on localhost:8000.

## Features

This MCP server provides the following tools for your LLM:

1. **add_item_to_store** - Add a single item to a store
2. **add_multiple_items** - Add multiple items to a store in bulk
3. **update_item_quantity** - Update the quantity of an existing item
4. **get_all_stores** - Retrieve all stores
5. **update_store_conditions** - Update store economic, political, and environmental conditions

## Setup

1. Make sure your API server is running on localhost:8000
2. Install dependencies: `npm install`
3. Start the MCP server: `npm start`

## Usage with LLM

Configure your LLM client to use this MCP server by adding the configuration from `mcp-config.json` to your LLM's MCP settings.

## API Endpoints Supported

- `POST /stores/{store_id}/items/` - Add single item
- `POST /stores/{store_id}/items/bulk/` - Add multiple items
- `PUT /stores/{store_id}/items/{item_name}/quantity/` - Update item quantity
- `GET /stores/` - Get all stores
- `PUT /stores/{store_id}/conditions/` - Update store conditions

## Example Usage

Once connected to your LLM, you can use natural language commands like:

- "Add a new item called 'Apple' with price 2.50 and quantity 100 to store 'store1'"
- "Update the quantity of 'Apple' in store 'store1' to 150"
- "Get all stores"
- "Update the economic condition of store 'store1' to 'good'"
