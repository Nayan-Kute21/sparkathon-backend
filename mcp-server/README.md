# Store Management MCP Server

A Node.js Model Context Protocol (MCP) server that provides tools for interacting with your store management API running on localhost:8000.

## Features

This MCP server provides the following tools for your LLM:

### Store Management Tools

1. **create_store** - Create a new store (now requires latitude/longitude)
2. **get_store** - Get store information by ID
3. **get_all_stores** - Get all stores
4. **delete_store** - Delete a store by ID
5. **add_item_to_store** - Add a single item to a store
6. **add_multiple_items_to_store** - Add multiple items to a store in bulk
7. **update_item_quantity** - Update the quantity of an existing item
8. **update_store_conditions** - Update store economic, political, and environmental conditions

### Main Store Management Tools

9. **create_main_store** - Create a central warehouse
10. **get_main_store** - Get main store information
11. **get_all_main_stores** - Get all main stores
12. **add_item_to_main_store** - Add items to main store inventory

### Order Management Tools

13. **create_order** - Create order from store to main store
14. **get_order** - Get order details by ID
15. **get_all_orders** - Get all orders
16. **update_order_status** - Update order status
17. **process_order** - Process order and update inventory

## NEW: Gemini AI Integration

The FastAPI server now includes Gemini AI endpoints that work with MCP context:

### Gemini Endpoints

- `POST /api/gemini/chat` - Chat with Gemini AI with MCP store context
- `POST /api/gemini/store-analysis` - Get AI analysis of your store system
- `GET /api/gemini/mcp-tools` - Get information about available MCP tools

### Environment Variables

Add to your `.env` file:

```
GEMINI_API_KEY=your_gemini_api_key_here
MONGO_URI=your_mongodb_connection_string
```

## Setup

1. Make sure your API server is running on localhost:8000
2. Install dependencies: `npm install`
3. Install Python dependencies: `pipenv install`
4. Start the FastAPI server: `pipenv run uvicorn app.main:app --reload`
5. Start the MCP server: `npm start`

## Usage with LLM

Configure your LLM client to use this MCP server by adding the configuration from `mcp-config.json` to your LLM's MCP settings.

## API Endpoints Supported

### Store Management

- `POST /api/stores/` - Create store (requires latitude/longitude)
- `GET /api/stores/` - Get all stores
- `GET /api/stores/{id}` - Get store by ID
- `DELETE /api/stores/{id}` - Delete store
- `POST /api/stores/{id}/items/` - Add single item
- `POST /api/stores/{id}/items/bulk/` - Add multiple items
- `PUT /api/stores/{id}/items/{name}/quantity/` - Update item quantity
- `PUT /api/stores/{id}/conditions/` - Update store conditions

### Main Store Management

- `POST /api/mainstore/` - Create main store
- `GET /api/mainstore/` - Get all main stores
- `GET /api/mainstore/{id}` - Get main store by ID
- `POST /api/mainstore/{id}/items/` - Add items to main store

### Order Management

- `POST /api/orders/` - Create order
- `GET /api/orders/` - Get all orders
- `GET /api/orders/{id}` - Get order by ID
- `PUT /api/orders/{id}/status/` - Update order status
- `POST /api/orders/{id}/process/` - Process order

### Gemini AI Integration

- `POST /api/gemini/chat` - Chat with Gemini AI with store context
- `POST /api/gemini/store-analysis` - Get AI analysis of store system
- `GET /api/gemini/mcp-tools` - Get MCP tools information

## Example Usage

Once connected to your LLM, you can use natural language commands like:

- "Create a new store called 'Downtown Market' at coordinates 40.7128, -74.0060"
- "Add 100 apples to store xyz123"
- "Update the economic condition of store abc456 to 'critical'"
- "Get AI analysis of my store performance"
- "Chat with Gemini about inventory optimization strategies"

## Recent Updates

- ✅ Added latitude/longitude support for store locations
- ✅ Added delete store functionality
- ✅ Integrated Gemini AI for intelligent store analysis
- ✅ Added MCP context awareness to AI responses
- ✅ Support for store performance analytics
