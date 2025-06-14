#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import axios from "axios";

const API_BASE_URL = "http://localhost:8000/api";

// Severity levels enum
const SeverityLevel = {
  LOW: "low",
  MEDIUM: "medium",
  HIGH: "high",
  CRITICAL: "critical",
};

class StoreManagementServer {
  constructor() {
    this.server = new Server(
      {
        name: "store-management-server",
        version: "0.1.0",
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
  }

  setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: "create_store",
            description: "Create a new store",
            inputSchema: {
              type: "object",
              properties: {
                store_name: {
                  type: "string",
                  description: "Name of the store",
                },
                store_address: { type: "string", description: "Store address" },
                store_phone: {
                  type: "string",
                  description: "Store contact number",
                },
                store_email: { type: "string", description: "Store email" },
                owner_name: { type: "string", description: "Store owner name" },
                store_type: {
                  type: "string",
                  description: "Type of store",
                  default: "General",
                },
                items: {
                  type: "array",
                  description: "Initial items for the store",
                  items: {
                    type: "object",
                    properties: {
                      item_name: {
                        type: "string",
                        description: "Name of the item",
                      },
                      current_quantity: {
                        type: "number",
                        minimum: 0,
                        description: "Current quantity in stock",
                      },
                      max_quantity: {
                        type: "number",
                        minimum: 1,
                        description: "Maximum quantity capacity",
                      },
                      unit: {
                        type: "string",
                        description: "Unit of measurement",
                        default: "pcs",
                      },
                      price: {
                        type: "number",
                        minimum: 0,
                        description: "Price per unit",
                      },
                      category: {
                        type: "string",
                        description: "Item category",
                      },
                    },
                    required: ["item_name", "current_quantity", "max_quantity"],
                  },
                  default: [],
                },
                economic_conditions: {
                  type: "string",
                  enum: ["low", "medium", "high", "critical"],
                  description:
                    "Current economic conditions affecting the store",
                },
                economic_notes: {
                  type: "string",
                  description: "Additional notes about economic conditions",
                },
                political_instability: {
                  type: "string",
                  enum: ["low", "medium", "high", "critical"],
                  description: "Level of political instability in the area",
                },
                political_notes: {
                  type: "string",
                  description: "Additional notes about political situation",
                },
                environmental_issues: {
                  type: "string",
                  enum: ["low", "medium", "high", "critical"],
                  description: "Environmental issues affecting the store",
                },
                environmental_notes: {
                  type: "string",
                  description: "Additional notes about environmental issues",
                },
              },
              required: ["store_name", "store_address", "owner_name"],
            },
          },
          {
            name: "add_item_to_store",
            description: "Add a single item to a store",
            inputSchema: {
              type: "object",
              properties: {
                store_id: {
                  type: "string",
                  description: "The ID of the store to add the item to",
                },
                item: {
                  type: "object",
                  description: "The item to add",
                  properties: {
                    item_name: {
                      type: "string",
                      description: "Name of the item",
                    },
                    current_quantity: {
                      type: "number",
                      minimum: 0,
                      description: "Current quantity in stock",
                    },
                    max_quantity: {
                      type: "number",
                      minimum: 1,
                      description: "Maximum quantity capacity",
                    },
                    unit: {
                      type: "string",
                      description: "Unit of measurement",
                      default: "pcs",
                    },
                    price: {
                      type: "number",
                      minimum: 0,
                      description: "Price per unit",
                    },
                    category: { type: "string", description: "Item category" },
                  },
                  required: ["item_name", "current_quantity", "max_quantity"],
                },
              },
              required: ["store_id", "item"],
            },
          },
          {
            name: "add_multiple_items",
            description: "Add multiple items to a store",
            inputSchema: {
              type: "object",
              properties: {
                store_id: {
                  type: "string",
                  description: "The ID of the store to add items to",
                },
                items: {
                  type: "array",
                  description: "Array of items to add",
                  items: {
                    type: "object",
                    properties: {
                      item_name: {
                        type: "string",
                        description: "Name of the item",
                      },
                      current_quantity: {
                        type: "number",
                        minimum: 0,
                        description: "Current quantity in stock",
                      },
                      max_quantity: {
                        type: "number",
                        minimum: 1,
                        description: "Maximum quantity capacity",
                      },
                      unit: {
                        type: "string",
                        description: "Unit of measurement",
                        default: "pcs",
                      },
                      price: {
                        type: "number",
                        minimum: 0,
                        description: "Price per unit",
                      },
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
            description: "Update the quantity of an item in a store",
            inputSchema: {
              type: "object",
              properties: {
                store_id: {
                  type: "string",
                  description: "The ID of the store",
                },
                item_name: {
                  type: "string",
                  description: "The name of the item to update",
                },
                new_quantity: {
                  type: "number",
                  minimum: 0,
                  description: "The new current quantity for the item",
                },
              },
              required: ["store_id", "item_name", "new_quantity"],
            },
          },
          {
            name: "get_all_stores",
            description: "Get all stores",
            inputSchema: {
              type: "object",
              properties: {},
            },
          },
          {
            name: "get_store_by_id",
            description: "Get a specific store by ID",
            inputSchema: {
              type: "object",
              properties: {
                store_id: {
                  type: "string",
                  description: "The ID of the store to retrieve",
                },
              },
              required: ["store_id"],
            },
          },
          {
            name: "update_store",
            description: "Update store information",
            inputSchema: {
              type: "object",
              properties: {
                store_id: {
                  type: "string",
                  description: "The ID of the store to update",
                },
                store_data: {
                  type: "object",
                  description: "The store data to update",
                  properties: {
                    store_name: {
                      type: "string",
                      description: "Name of the store",
                    },
                    store_address: {
                      type: "string",
                      description: "Store address",
                    },
                    store_phone: {
                      type: "string",
                      description: "Store contact number",
                    },
                    store_email: { type: "string", description: "Store email" },
                    owner_name: {
                      type: "string",
                      description: "Store owner name",
                    },
                    store_type: {
                      type: "string",
                      description: "Type of store",
                    },
                    is_active: { type: "boolean", description: "Store status" },
                    items: {
                      type: "array",
                      description: "List of store items",
                      items: {
                        type: "object",
                        properties: {
                          item_name: {
                            type: "string",
                            description: "Name of the item",
                          },
                          current_quantity: {
                            type: "number",
                            minimum: 0,
                            description: "Current quantity in stock",
                          },
                          max_quantity: {
                            type: "number",
                            minimum: 1,
                            description: "Maximum quantity capacity",
                          },
                          unit: {
                            type: "string",
                            description: "Unit of measurement",
                          },
                          price: {
                            type: "number",
                            minimum: 0,
                            description: "Price per unit",
                          },
                          category: {
                            type: "string",
                            description: "Item category",
                          },
                        },
                      },
                    },
                    economic_conditions: {
                      type: "string",
                      enum: ["low", "medium", "high", "critical"],
                      description:
                        "Current economic conditions affecting the store",
                    },
                    economic_notes: {
                      type: "string",
                      description: "Additional notes about economic conditions",
                    },
                    political_instability: {
                      type: "string",
                      enum: ["low", "medium", "high", "critical"],
                      description: "Level of political instability in the area",
                    },
                    political_notes: {
                      type: "string",
                      description: "Additional notes about political situation",
                    },
                    environmental_issues: {
                      type: "string",
                      enum: ["low", "medium", "high", "critical"],
                      description: "Environmental issues affecting the store",
                    },
                    environmental_notes: {
                      type: "string",
                      description:
                        "Additional notes about environmental issues",
                    },
                  },
                },
              },
              required: ["store_id", "store_data"],
            },
          },
          {
            name: "update_store_conditions",
            description:
              "Update store economic, political, and environmental conditions",
            inputSchema: {
              type: "object",
              properties: {
                store_id: {
                  type: "string",
                  description: "The ID of the store to update",
                },
                conditions: {
                  type: "object",
                  description: "The conditions to update",
                  properties: {
                    economic_conditions: {
                      type: "string",
                      enum: ["low", "medium", "high", "critical"],
                      description:
                        "Current economic conditions affecting the store",
                    },
                    economic_notes: {
                      type: "string",
                      description: "Additional notes about economic conditions",
                    },
                    political_instability: {
                      type: "string",
                      enum: ["low", "medium", "high", "critical"],
                      description: "Level of political instability in the area",
                    },
                    political_notes: {
                      type: "string",
                      description: "Additional notes about political situation",
                    },
                    environmental_issues: {
                      type: "string",
                      enum: ["low", "medium", "high", "critical"],
                      description: "Environmental issues affecting the store",
                    },
                    environmental_notes: {
                      type: "string",
                      description:
                        "Additional notes about environmental issues",
                    },
                  },
                },
              },
              required: ["store_id", "conditions"],
            },
          },
        ],
      };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case "create_store":
            return await this.createStore(args);

          case "add_item_to_store":
            return await this.addItemToStore(args.store_id, args.item);

          case "add_multiple_items":
            return await this.addMultipleItems(args.store_id, args.items);

          case "update_item_quantity":
            return await this.updateItemQuantity(
              args.store_id,
              args.item_name,
              args.new_quantity
            );

          case "get_all_stores":
            return await this.getAllStores();

          case "get_store_by_id":
            return await this.getStoreById(args.store_id);

          case "update_store":
            return await this.updateStore(args.store_id, args.store_data);

          case "update_store_conditions":
            return await this.updateStoreConditions(
              args.store_id,
              args.conditions
            );

          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: "text",
              text: `Error: ${error.message}`,
            },
          ],
        };
      }
    });
  }

  async createStore(storeData) {
    try {
      const response = await axios.post(`${API_BASE_URL}/stores/`, storeData);
      return {
        content: [
          {
            type: "text",
            text: `Successfully created store "${
              storeData.store_name
            }". Store ID: ${response.data.id || response.data._id}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(
        `Failed to create store: ${
          error.response?.data?.detail || error.message
        }`
      );
    }
  }

  async addItemToStore(storeId, item) {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/stores/${storeId}/items/`,
        item
      );
      return {
        content: [
          {
            type: "text",
            text: `Successfully added item "${item.item_name}" to store ${storeId}. Response: ${response.data.message}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(
        `Failed to add item: ${error.response?.data?.detail || error.message}`
      );
    }
  }

  async addMultipleItems(storeId, items) {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/stores/${storeId}/items/bulk/`,
        items
      );
      return {
        content: [
          {
            type: "text",
            text: `Successfully added ${items.length} items to store ${storeId}. Response: ${response.data.message}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(
        `Failed to add items: ${error.response?.data?.detail || error.message}`
      );
    }
  }

  async updateItemQuantity(storeId, itemName, newQuantity) {
    try {
      const response = await axios.put(
        `${API_BASE_URL}/stores/${storeId}/items/${itemName}/quantity/`,
        null,
        {
          params: { new_quantity: newQuantity },
        }
      );
      return {
        content: [
          {
            type: "text",
            text: `Successfully updated quantity of "${itemName}" in store ${storeId} to ${newQuantity}. Response: ${response.data.message}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(
        `Failed to update item quantity: ${
          error.response?.data?.detail || error.message
        }`
      );
    }
  }

  async getAllStores() {
    try {
      const response = await axios.get(`${API_BASE_URL}/stores/`);
      return {
        content: [
          {
            type: "text",
            text: `Retrieved all stores:\n${JSON.stringify(
              response.data.stores || response.data,
              null,
              2
            )}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(
        `Failed to get stores: ${error.response?.data?.detail || error.message}`
      );
    }
  }

  async getStoreById(storeId) {
    try {
      const response = await axios.get(`${API_BASE_URL}/stores/${storeId}`);
      return {
        content: [
          {
            type: "text",
            text: `Retrieved store ${storeId}:\n${JSON.stringify(
              response.data,
              null,
              2
            )}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(
        `Failed to get store: ${error.response?.data?.detail || error.message}`
      );
    }
  }

  async updateStore(storeId, storeData) {
    try {
      const response = await axios.put(
        `${API_BASE_URL}/stores/${storeId}`,
        storeData
      );
      return {
        content: [
          {
            type: "text",
            text: `Successfully updated store ${storeId}. Response: ${response.data.message}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(
        `Failed to update store: ${
          error.response?.data?.detail || error.message
        }`
      );
    }
  }

  async updateStoreConditions(storeId, conditions) {
    try {
      const response = await axios.put(
        `${API_BASE_URL}/stores/${storeId}/conditions/`,
        conditions
      );
      return {
        content: [
          {
            type: "text",
            text: `Successfully updated conditions for store ${storeId}. Response: ${response.data.message}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(
        `Failed to update store conditions: ${
          error.response?.data?.detail || error.message
        }`
      );
    }
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("Store Management MCP server running on stdio");
  }
}

const server = new StoreManagementServer();
server.run().catch(console.error);
