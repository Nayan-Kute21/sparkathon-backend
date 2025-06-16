#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ListPromptsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import fetch from "node-fetch";

// API configuration
const API_BASE_URL = process.env.API_BASE_URL || "http://localhost:8000/api";

class StoreManagementServer {
  constructor() {
    this.server = new Server(
      {
        name: "store-management-server",
        version: "1.0.0",
      },
      {
        capabilities: {
          tools: {},
          resources: {},
          prompts: {},
        },
      }
    );

    this.setupToolHandlers();
  }

  setupToolHandlers() {
    // Handle resources/list requests (return empty for now)
    this.server.setRequestHandler(ListResourcesRequestSchema, async () => {
      return {
        resources: [],
      };
    });

    // Handle prompts/list requests (return empty for now)
    this.server.setRequestHandler(ListPromptsRequestSchema, async () => {
      return {
        prompts: [],
      };
    });

    // List all available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          // Store Management Tools
          {
            name: "create_store",
            description: "Create a new individual store",
            inputSchema: {
              type: "object",
              properties: {
                store_name: {
                  type: "string",
                  description: "Name of the store",
                },
                store_address: { type: "string", description: "Store address" },
                owner_name: { type: "string", description: "Store owner name" },
                store_phone: {
                  type: "string",
                  description: "Store phone number (optional)",
                },
                store_email: {
                  type: "string",
                  description: "Store email (optional)",
                },
                store_type: {
                  type: "string",
                  description: "Type of store (optional)",
                },
                economic_conditions: {
                  type: "string",
                  enum: ["low", "medium", "high", "critical"],
                  description: "Economic conditions level",
                },
                economic_notes: {
                  type: "string",
                  description: "Economic notes",
                },
                political_instability: {
                  type: "string",
                  enum: ["low", "medium", "high", "critical"],
                  description: "Political instability level",
                },
                political_notes: {
                  type: "string",
                  description: "Political notes",
                },
                environmental_issues: {
                  type: "string",
                  enum: ["low", "medium", "high", "critical"],
                  description: "Environmental issues level",
                },
                environmental_notes: {
                  type: "string",
                  description: "Environmental notes",
                },
              },
              required: ["store_name", "store_address", "owner_name"],
            },
          },
          {
            name: "get_store",
            description: "Get individual store information by ID",
            inputSchema: {
              type: "object",
              properties: {
                store_id: {
                  type: "string",
                  description: "Store ID to retrieve",
                },
              },
              required: ["store_id"],
            },
          },
          {
            name: "get_all_stores",
            description: "Get all individual stores",
            inputSchema: {
              type: "object",
              properties: {},
            },
          },
          {
            name: "add_item_to_store",
            description: "Add an item to an individual store",
            inputSchema: {
              type: "object",
              properties: {
                store_id: { type: "string", description: "Store ID" },
                item_name: { type: "string", description: "Name of the item" },
                current_quantity: {
                  type: "integer",
                  description: "Current quantity",
                },
                max_quantity: {
                  type: "integer",
                  description: "Maximum capacity",
                },
                unit: { type: "string", description: "Unit of measurement" },
                price: { type: "number", description: "Price per unit" },
                category: { type: "string", description: "Item category" },
              },
              required: [
                "store_id",
                "item_name",
                "current_quantity",
                "max_quantity",
              ],
            },
          },
          {
            name: "add_multiple_items_to_store",
            description: "Add multiple items to an individual store",
            inputSchema: {
              type: "object",
              properties: {
                store_id: { type: "string", description: "Store ID" },
                items: {
                  type: "array",
                  description: "List of items to add",
                  items: {
                    type: "object",
                    properties: {
                      item_name: {
                        type: "string",
                        description: "Name of the item",
                      },
                      current_quantity: {
                        type: "integer",
                        description: "Current quantity",
                      },
                      max_quantity: {
                        type: "integer",
                        description: "Maximum capacity",
                      },
                      unit: {
                        type: "string",
                        description: "Unit of measurement",
                      },
                      price: { type: "number", description: "Price per unit" },
                      category: {
                        type: "string",
                        description: "Item category",
                      },
                    },
                    required: ["item_name", "current_quantity", "max_quantity"],
                  },
                },
              },
              required: ["store_id", "items"],
            },
          },
          {
            name: "update_item_quantity",
            description: "Update item quantity in an individual store",
            inputSchema: {
              type: "object",
              properties: {
                store_id: { type: "string", description: "Store ID" },
                item_name: { type: "string", description: "Item name" },
                new_quantity: { type: "integer", description: "New quantity" },
              },
              required: ["store_id", "item_name", "new_quantity"],
            },
          },
          {
            name: "update_store_conditions",
            description:
              "Update store economic, political, and environmental conditions",
            inputSchema: {
              type: "object",
              properties: {
                store_id: { type: "string", description: "Store ID" },
                economic_conditions: {
                  type: "string",
                  enum: ["low", "medium", "high", "critical"],
                  description: "Economic conditions level",
                },
                economic_notes: {
                  type: "string",
                  description: "Economic notes",
                },
                political_instability: {
                  type: "string",
                  enum: ["low", "medium", "high", "critical"],
                  description: "Political instability level",
                },
                political_notes: {
                  type: "string",
                  description: "Political notes",
                },
                environmental_issues: {
                  type: "string",
                  enum: ["low", "medium", "high", "critical"],
                  description: "Environmental issues level",
                },
                environmental_notes: {
                  type: "string",
                  description: "Environmental notes",
                },
              },
              required: ["store_id"],
            },
          },

          // Main Store Management Tools
          {
            name: "create_main_store",
            description: "Create a new main store (central warehouse)",
            inputSchema: {
              type: "object",
              properties: {
                name: { type: "string", description: "Name of the main store" },
                location: {
                  type: "string",
                  description: "Location of the main store",
                },
                manager: { type: "string", description: "Manager name" },
                economic_conditions: {
                  type: "string",
                  enum: ["low", "medium", "high", "critical"],
                  description: "Economic conditions level",
                },
                economic_notes: {
                  type: "string",
                  description: "Economic notes",
                },
                political_instability: {
                  type: "string",
                  enum: ["low", "medium", "high", "critical"],
                  description: "Political instability level",
                },
                political_notes: {
                  type: "string",
                  description: "Political notes",
                },
                environmental_issues: {
                  type: "string",
                  enum: ["low", "medium", "high", "critical"],
                  description: "Environmental issues level",
                },
                environmental_notes: {
                  type: "string",
                  description: "Environmental notes",
                },
              },
              required: ["name", "location", "manager"],
            },
          },
          {
            name: "get_main_store",
            description: "Get main store information by ID",
            inputSchema: {
              type: "object",
              properties: {
                store_id: { type: "string", description: "Main store ID" },
              },
              required: ["store_id"],
            },
          },
          {
            name: "get_all_main_stores",
            description: "Get all main stores",
            inputSchema: {
              type: "object",
              properties: {},
            },
          },
          {
            name: "add_item_to_main_store",
            description: "Add item to main store inventory",
            inputSchema: {
              type: "object",
              properties: {
                store_id: { type: "string", description: "Main store ID" },
                item_name: { type: "string", description: "Name of the item" },
                current_quantity: {
                  type: "integer",
                  description: "Current quantity",
                },
                max_quantity: {
                  type: "integer",
                  description: "Maximum capacity",
                },
                unit: { type: "string", description: "Unit of measurement" },
                price: { type: "number", description: "Price per unit" },
                category: { type: "string", description: "Item category" },
              },
              required: [
                "store_id",
                "item_name",
                "current_quantity",
                "max_quantity",
              ],
            },
          },

          // Order Management Tools
          {
            name: "create_order",
            description: "Create a new order from a store to a main store",
            inputSchema: {
              type: "object",
              properties: {
                store_id: {
                  type: "string",
                  description: "ID of the store placing the order",
                },
                store_name: {
                  type: "string",
                  description: "Name of the store",
                },
                main_store_id: {
                  type: "string",
                  description: "ID of the main store",
                },
                items: {
                  type: "array",
                  description: "List of items to order",
                  items: {
                    type: "object",
                    properties: {
                      item_name: { type: "string", description: "Item name" },
                      quantity: {
                        type: "integer",
                        description: "Quantity to order",
                      },
                      unit: {
                        type: "string",
                        description: "Unit of measurement",
                      },
                      price: { type: "number", description: "Price per unit" },
                      category: {
                        type: "string",
                        description: "Item category",
                      },
                    },
                    required: ["item_name", "quantity"],
                  },
                },
                notes: { type: "string", description: "Additional notes" },
              },
              required: ["store_id", "store_name", "main_store_id", "items"],
            },
          },
          {
            name: "get_all_orders",
            description: "Get all orders in the system",
            inputSchema: {
              type: "object",
              properties: {},
            },
          },
          {
            name: "get_order",
            description: "Get order by ID",
            inputSchema: {
              type: "object",
              properties: {
                order_id: { type: "string", description: "Order ID" },
              },
              required: ["order_id"],
            },
          },
          {
            name: "update_order_status",
            description: "Update order status",
            inputSchema: {
              type: "object",
              properties: {
                order_id: { type: "string", description: "Order ID" },
                status: {
                  type: "string",
                  enum: [
                    "pending",
                    "processing",
                    "shipped",
                    "delivered",
                    "cancelled",
                  ],
                  description: "New order status",
                },
                notes: { type: "string", description: "Additional notes" },
              },
              required: ["order_id"],
            },
          },
          {
            name: "process_order",
            description: "Process an order and update inventory",
            inputSchema: {
              type: "object",
              properties: {
                order_id: { type: "string", description: "Order ID to process" },
              },
              required: ["order_id"],
            },
          },
        ],
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        let response;

        // Check if FastAPI server is running
        try {
          const healthCheck = await fetch(`http://localhost:8000/`, {
            method: "GET",
            timeout: 5000,
          });
          if (!healthCheck.ok) {
            throw new Error("FastAPI server not responding");
          }
        } catch (error) {
          return {
            content: [
              {
                type: "text",
                text: `Error: Cannot connect to FastAPI server at http://localhost:8000. Please ensure the server is running with: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`,
              },
            ],
            isError: true,
          };
        }

        switch (name) {
          // Store Management - Using correct API endpoints
          case "create_store":
            response = await this.callAPI("/stores/", "POST", args);
            break;

          case "get_store":
            response = await this.callAPI(`/stores/${args.store_id}`, "GET");
            break;

          case "get_all_stores":
            response = await this.callAPI("/stores/", "GET");
            break;

          case "add_item_to_store":
            const { store_id, ...itemData } = args;
            response = await this.callAPI(
              `/stores/${store_id}/items/`,
              "POST",
              itemData
            );
            break;

          case "add_multiple_items_to_store":
            response = await this.callAPI(
              `/stores/${args.store_id}/items/bulk/`,
              "POST",
              args.items
            );
            break;

          case "update_item_quantity":
            response = await this.callAPI(
              `/stores/${args.store_id}/items/${args.item_name}/quantity/`,
              "PUT",
              null,
              {
                new_quantity: args.new_quantity,
              }
            );
            break;

          case "update_store_conditions":
            const { store_id: storeId, ...conditions } = args;
            response = await this.callAPI(
              `/stores/${storeId}/conditions/`,
              "PUT",
              conditions
            );
            break;

          // Main Store Management
          case "create_main_store":
            response = await this.callAPI("/mainstore/", "POST", args);
            break;

          case "get_main_store":
            response = await this.callAPI(`/mainstore/${args.store_id}`, "GET");
            break;

          case "get_all_main_stores":
            response = await this.callAPI("/mainstore/", "GET");
            break;

          case "add_item_to_main_store":
            const { store_id: mainStoreId, ...mainItemData } = args;
            response = await this.callAPI(
              `/mainstore/${mainStoreId}/items/`,
              "POST",
              mainItemData
            );
            break;

          // Order Management
          case "create_order":
            response = await this.callAPI("/orders/", "POST", args);
            break;

          case "get_all_orders":
            response = await this.callAPI("/orders/", "GET");
            break;

          case "get_order":
            response = await this.callAPI(`/orders/${args.order_id}`, "GET");
            break;

          case "update_order_status":
            const { order_id, ...statusData } = args;
            response = await this.callAPI(
              `/orders/${order_id}/status/`,
              "PUT",
              statusData
            );
            break;

          case "process_order":
            response = await this.callAPI(
              `/orders/${args.order_id}/process/`,
              "POST",
              {}
            );
            break;

          default:
            throw new Error(`Unknown tool: ${name}`);
        }

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(response, null, 2),
            },
          ],
        };
      } catch (error) {
        console.error(`Error in tool ${name}:`, error.message);
        return {
          content: [
            {
              type: "text",
              text: `Error: ${error.message}`,
            },
          ],
          isError: true,
        };
      }
    });
  }

  async callAPI(endpoint, method = "GET", body = null, queryParams = null) {
    let url = `${API_BASE_URL}${endpoint}`;

    // Add query parameters if provided
    if (queryParams && method === "PUT" && endpoint.includes("/quantity/")) {
      // For quantity updates, we need to pass new_quantity as query param
      const params = new URLSearchParams(queryParams);
      url += `?${params.toString()}`;
    }

    const options = {
      method,
      headers: {
        "Content-Type": "application/json",
      },
      timeout: 30000,
    };

    if (body && method !== "GET") {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API Error (${response.status}): ${errorText}`);
    }

    return await response.json();
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("Store Management MCP server running on stdio");
  }
}

const server = new StoreManagementServer();
server.run().catch(console.error);
