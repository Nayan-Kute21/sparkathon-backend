from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from typing import List, Optional, Dict, Any
import google.generativeai as genai
import os
import json
import asyncio
from dotenv import load_dotenv
import uuid
from datetime import datetime
from pydantic import BaseModel

# LangGraph imports for proper tool management
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import BaseTool
from langchain_core.runnables import RunnableConfig
from typing_extensions import Annotated, TypedDict

load_dotenv()
app = APIRouter()


class MCPState(TypedDict):
    """State for MCP operations using LangGraph"""

    messages: Annotated[List[BaseMessage], lambda x, y: x + y]
    system_context: Dict[str, Any]
    available_tools: List[Dict]
    current_request: str
    iteration: int
    max_iterations: int
    executed_tools: List[Dict]
    session_id: Optional[str]


class WebSocketConnectionManager:
    """Manages WebSocket connections for live MCP operations"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        await self.send_message(
            session_id,
            {
                "type": "connection",
                "status": "connected",
                "session_id": session_id,
                "message": "WebSocket connection established",
            },
        )

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, session_id: str, message: Dict):
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            if websocket.client_state == WebSocketState.CONNECTED:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    print(f"Error sending message to {session_id}: {e}")
                    self.disconnect(session_id)


class MCPClient:
    """Client for communicating with external MCP server"""

    def __init__(self):
        self.server_command = [
            "node",
            "/Users/tanmaydaga/Documents/05 Programming/00 Focus/sparkathon-backend/mcp-server/index.js",
        ]
        self.process = None
        self.request_id = 0

    async def _ensure_server_running(self):
        if self.process is None or self.process.returncode is not None:
            env = os.environ.copy()
            env["API_BASE_URL"] = "http://localhost:8000/api"

            self.process = await asyncio.create_subprocess_exec(
                *self.server_command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )

    async def send_request(self, method: str, params: Optional[Dict] = None) -> Dict:
        await self._ensure_server_running()

        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {},
        }

        request_data = json.dumps(request) + "\n"

        try:
            self.process.stdin.write(request_data.encode())
            await self.process.stdin.drain()

            response_line = await self.process.stdout.readline()
            if not response_line:
                raise Exception("No response from MCP server")

            response_data = json.loads(response_line.decode().strip())

            if "error" in response_data:
                raise Exception(f"MCP Error: {response_data['error']}")

            return response_data.get("result", {})

        except Exception as e:
            print(f"Error communicating with MCP server: {e}")
            if self.process:
                self.process.terminate()
                await self.process.wait()
                self.process = None
            raise e

    async def list_tools(self) -> List[Dict]:
        try:
            result = await self.send_request("tools/list")
            return result.get("tools", [])
        except Exception as e:
            print(f"Error listing tools: {e}")
            return []

    async def call_tool(self, tool_name: str, arguments: Dict) -> Dict:
        try:
            params = {"name": tool_name, "arguments": arguments}
            result = await self.send_request("tools/call", params)
            return result
        except Exception as e:
            print(f"Error calling tool {tool_name}: {e}")
            return {"error": str(e)}

    async def get_system_context(self) -> Dict[str, Any]:
        """Get system context with available operations"""
        return {
            "stores": [],
            "main_stores": [],
            "orders": [],
            "total_counts": {"stores": 0, "main_stores": 0, "orders": 0},
            "context_loaded": False,
            "available_operations": [
                "get_all_stores",
                "get_all_main_stores",
                "get_all_orders",
                "create_store",
                "update_store",
                "delete_store",
                "create_main_store",
                "update_main_store",
                "delete_main_store",
                "create_order",
                "update_order",
                "delete_order",
            ],
        }

    async def get_full_system_context(self) -> Dict[str, Any]:
        """Get full system context - only call when needed"""
        context = await self.get_system_context()
        context["context_loaded"] = True

        try:
            # Get data from all sources
            results = [
                (await self.call_tool("get_all_stores", {}), "stores"),
                (await self.call_tool("get_all_main_stores", {}), "main_stores"),
                (await self.call_tool("get_all_orders", {}), "orders"),
            ]

            for result, key in results:
                if "content" in result and result["content"]:
                    try:
                        data = json.loads(result["content"][0]["text"])
                        entities = data.get(
                            "stores" if key != "orders" else "orders", []
                        )
                        context[key] = entities
                        context["total_counts"][key] = len(entities)
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue

        except Exception as e:
            print(f"Error getting full system context: {e}")
            context["error"] = str(e)

        return context

    async def close(self):
        if self.process:
            self.process.terminate()
            await self.process.wait()
            self.process = None


class MCPToolWrapper(BaseTool, BaseModel):
    """LangChain tool wrapper for MCP tools"""

    name: str
    description: str
    mcp_client: MCPClient
    tool_info: Dict

    def __init__(self, mcp_client: MCPClient, tool_info: Dict, **kwargs):
        # Set the required fields first
        super().__init__(
            name=tool_info["name"],
            description=tool_info["description"],
            mcp_client=mcp_client,
            tool_info=tool_info,
            **kwargs,
        )

    def _run(self, **kwargs) -> str:
        """Synchronous run - not used in async context"""
        raise NotImplementedError("Use async version")

    async def _arun(self, **kwargs) -> str:
        """Execute the MCP tool asynchronously"""
        try:
            result = await self.mcp_client.call_tool(self.tool_info["name"], kwargs)
            return json.dumps(result)
        except Exception as e:
            return f"Error executing {self.tool_info['name']}: {str(e)}"


class LangGraphMCPExecutor:
    """LangGraph-based MCP executor with proper tool management"""

    def __init__(self, api_key: str, websocket_manager: WebSocketConnectionManager):
        self.api_key = api_key
        self.websocket_manager = websocket_manager
        self.mcp_client = MCPClient()
        genai.configure(api_key=api_key)
        self.workflow = None
        self.tools = []

    async def initialize_workflow(self):
        """Initialize LangGraph workflow with MCP tools"""
        mcp_tools = await self.mcp_client.list_tools()
        self.tools = [
            MCPToolWrapper(self.mcp_client, tool_info) for tool_info in mcp_tools
        ]

        workflow = StateGraph(MCPState)

        # Add nodes
        workflow.add_node("initialize", self._initialize_node)
        workflow.add_node("analyze_and_plan", self._analyze_and_plan_node)
        workflow.add_node("execute_tool", self._execute_tool_node)
        workflow.add_node("update_context", self._update_context_node)
        workflow.add_node("finalize", self._finalize_node)

        # Set entry point and edges
        workflow.set_entry_point("initialize")
        workflow.add_edge("initialize", "analyze_and_plan")
        workflow.add_conditional_edges(
            "analyze_and_plan",
            self._should_execute_tool,
            {"execute": "execute_tool", "finish": "finalize"},
        )
        workflow.add_edge("execute_tool", "update_context")
        workflow.add_conditional_edges(
            "update_context",
            self._should_continue,
            {"continue": "analyze_and_plan", "finish": "finalize"},
        )
        workflow.add_edge("finalize", END)

        self.workflow = workflow.compile()

    async def execute_feedback_loop(
        self, session_id: str, initial_request: str, max_iterations: int = 10
    ):
        """Execute feedback loop using LangGraph workflow"""
        try:
            await self._send_workflow_message(
                session_id,
                {
                    "type": "langgraph_workflow_start",
                    "initial_request": initial_request,
                    "max_iterations": max_iterations,
                    "framework": "LangGraph with proper tool management",
                },
            )

            if not self.workflow:
                await self.initialize_workflow()

            initial_state = {
                "messages": [HumanMessage(content=initial_request)],
                "system_context": {},
                "available_tools": [
                    {"name": tool.name, "description": tool.description}
                    for tool in self.tools
                ],
                "current_request": initial_request,
                "iteration": 0,
                "max_iterations": max_iterations,
                "executed_tools": [],
                "session_id": session_id,
            }

            config = RunnableConfig(configurable={"session_id": session_id})
            final_state = await self.workflow.ainvoke(initial_state, config)

            await self._send_workflow_message(
                session_id,
                {
                    "type": "langgraph_workflow_complete",
                    "total_iterations": final_state["iteration"],
                    "tools_executed": len(final_state["executed_tools"]),
                    "successful_tools": sum(
                        1 for t in final_state["executed_tools"] if t["success"]
                    ),
                    "final_state": {
                        "system_context": final_state["system_context"],
                        "executed_tools": final_state["executed_tools"],
                    },
                },
            )

        except Exception as e:
            await self._send_workflow_message(
                session_id,
                {"type": "error", "message": f"LangGraph workflow error: {str(e)}"},
            )
        finally:
            await self.mcp_client.close()

    async def _send_workflow_message(self, session_id: str, message: Dict):
        """Helper method to send workflow messages"""
        await self.websocket_manager.send_message(session_id, message)

    async def _initialize_node(
        self, state: MCPState, config: RunnableConfig
    ) -> MCPState:
        """Initialize the workflow"""
        session_id = state.get("session_id")

        await self._send_workflow_message(
            session_id,
            {
                "type": "workflow_node",
                "node": "initialize",
                "message": "Initializing LangGraph workflow...",
            },
        )

        system_context = await self.mcp_client.get_system_context()
        state["system_context"] = system_context
        state["iteration"] = 0

        await self._send_workflow_message(
            session_id,
            {
                "type": "system_context",
                "available_tools": len(state["available_tools"]),
                "system_summary": system_context.get("total_counts", {}),
            },
        )

        state["messages"].append(
            AIMessage(
                content=f"Workflow initialized. System context loaded with {len(self.tools)} tools available."
            )
        )

        return state

    async def _analyze_and_plan_node(
        self, state: MCPState, config: RunnableConfig
    ) -> MCPState:
        """Analyze current state and plan next action using Gemini"""
        session_id = state.get("session_id")
        state["iteration"] += 1

        await self._send_workflow_message(
            session_id,
            {
                "type": "iteration_start",
                "iteration": state["iteration"],
                "max_iterations": state["max_iterations"],
            },
        )

        await self._send_workflow_message(
            session_id,
            {
                "type": "workflow_node",
                "node": "analyze_and_plan",
                "iteration": state["iteration"],
                "message": "Gemini analyzing current state and planning next action...",
            },
        )

        analysis_prompt = self._create_analysis_prompt(state)

        try:
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            response = model.generate_content(analysis_prompt)
            analysis_content = (
                response.text if response.text else "No analysis generated"
            )

            state["messages"].append(
                AIMessage(
                    content=analysis_content,
                    additional_kwargs={
                        "iteration": state["iteration"],
                        "node": "analyze_and_plan",
                    },
                )
            )

            await self._send_workflow_message(
                session_id,
                {
                    "type": "gemini_analysis",
                    "iteration": state["iteration"],
                    "analysis": analysis_content,
                },
            )

        except Exception as e:
            await self._handle_error(state, session_id, f"Analysis error: {str(e)}")

        return state

    async def _execute_tool_node(
        self, state: MCPState, config: RunnableConfig
    ) -> MCPState:
        """Execute the planned tool"""
        session_id = state.get("session_id")

        await self._send_workflow_message(
            session_id,
            {
                "type": "workflow_node",
                "node": "execute_tool",
                "iteration": state["iteration"],
                "message": "Executing planned tool...",
            },
        )

        last_message = state["messages"][-1]
        tool_call = self._extract_tool_call(last_message.content)

        if tool_call:
            await self._execute_single_tool(state, session_id, tool_call)

        return state

    async def _execute_single_tool(
        self, state: MCPState, session_id: str, tool_call: Dict
    ):
        """Execute a single tool call"""
        await self._send_workflow_message(
            session_id,
            {
                "type": "tool_execution_start",
                "iteration": state["iteration"],
                "tool_name": tool_call["tool_name"],
                "arguments": tool_call["arguments"],
            },
        )

        try:
            tool = next(
                (t for t in self.tools if t.name == tool_call["tool_name"]), None
            )

            if tool:
                result = await tool._arun(**tool_call["arguments"])
                success = "error" not in result.lower()

                execution_record = {
                    "iteration": state["iteration"],
                    "tool_name": tool_call["tool_name"],
                    "arguments": tool_call["arguments"],
                    "result": result,
                    "success": success,
                    "timestamp": datetime.utcnow().isoformat(),
                }

                state["executed_tools"].append(execution_record)
                state["messages"].append(
                    ToolMessage(
                        content=result, tool_call_id=f"tool_{state['iteration']}"
                    )
                )

                await self._send_workflow_message(
                    session_id,
                    {
                        "type": "tool_execution_result",
                        "iteration": state["iteration"],
                        "tool_name": tool_call["tool_name"],
                        "arguments": tool_call["arguments"],
                        "success": success,
                        "result": (
                            json.loads(result) if result.startswith("{") else result
                        ),
                    },
                )

            else:
                await self._handle_error(
                    state, session_id, f"Tool {tool_call['tool_name']} not found"
                )

        except Exception as e:
            await self._handle_error(
                state, session_id, f"Tool execution error: {str(e)}"
            )

    async def _handle_error(self, state: MCPState, session_id: str, error_msg: str):
        """Handle errors consistently"""
        state["messages"].append(AIMessage(content=error_msg))
        await self._send_workflow_message(
            session_id,
            {
                "type": "error",
                "iteration": state["iteration"],
                "message": error_msg,
            },
        )

    async def _update_context_node(
        self, state: MCPState, config: RunnableConfig
    ) -> MCPState:
        """Update system context when necessary"""
        session_id = state.get("session_id")

        await self._send_workflow_message(
            session_id,
            {
                "type": "workflow_node",
                "node": "update_context",
                "iteration": state["iteration"],
                "message": "Checking if context update is needed...",
            },
        )

        try:
            last_executed = (
                state["executed_tools"][-1] if state["executed_tools"] else None
            )

            context_loading_tools = [
                "get_all_stores",
                "get_all_main_stores",
                "get_all_orders",
            ]
            data_modifying_tools = [
                "create_store",
                "update_store",
                "delete_store",
                "create_main_store",
                "update_main_store",
                "delete_main_store",
                "create_order",
                "update_order",
                "delete_order",
            ]

            should_update = False
            update_reason = ""

            if last_executed:
                tool_name = last_executed["tool_name"]

                if tool_name in context_loading_tools:
                    updated_context = await self.mcp_client.get_full_system_context()
                    state["system_context"] = updated_context
                    should_update = True
                    update_reason = f"Context loaded via {tool_name}"

                elif tool_name in data_modifying_tools and state["system_context"].get(
                    "context_loaded", False
                ):
                    updated_context = await self.mcp_client.get_full_system_context()
                    state["system_context"] = updated_context
                    should_update = True
                    update_reason = f"Context refreshed after {tool_name}"

                else:
                    update_reason = f"No context update needed for {tool_name}"

            message_content = f"System context {'updated' if should_update else 'update skipped'}: {update_reason}"
            state["messages"].append(
                AIMessage(
                    content=message_content,
                    additional_kwargs={"node": "update_context"},
                )
            )

            message_type = (
                "system_update" if should_update else "context_update_skipped"
            )
            await self._send_workflow_message(
                session_id,
                {
                    "type": message_type,
                    "iteration": state["iteration"],
                    "reason": update_reason,
                    **(
                        {
                            "updated_context": state["system_context"].get(
                                "total_counts", {}
                            )
                        }
                        if should_update
                        else {}
                    ),
                },
            )

        except Exception as e:
            await self._handle_error(
                state, session_id, f"Context update error: {str(e)}"
            )

        return state

    async def _finalize_node(self, state: MCPState, config: RunnableConfig) -> MCPState:
        """Finalize the workflow with summary"""
        session_id = state.get("session_id")

        await self._send_workflow_message(
            session_id,
            {
                "type": "workflow_node",
                "node": "finalize",
                "iteration": state["iteration"],
                "message": "Generating final summary...",
            },
        )

        summary = await self._generate_summary(state)

        state["messages"].append(
            AIMessage(
                content=summary,
                additional_kwargs={"node": "finalize", "type": "summary"},
            )
        )

        await self._send_workflow_message(
            session_id,
            {
                "type": "feedback_loop_complete",
                "total_iterations": state["iteration"],
                "tools_executed": len(state["executed_tools"]),
                "successful_tools": sum(
                    1 for t in state["executed_tools"] if t["success"]
                ),
                "summary": summary,
            },
        )

        return state

    def _should_execute_tool(self, state: MCPState) -> str:
        """Determine if we should execute a tool or finish"""
        if state["iteration"] >= state["max_iterations"]:
            return "finish"

        last_message = state["messages"][-1]
        if hasattr(last_message, "content"):
            content = last_message.content
            if "EXECUTE:" in content:
                return "execute"
            elif "COMPLETE:" in content:
                return "finish"

        return "execute"

    def _should_continue(self, state: MCPState) -> str:
        """Determine if we should continue iterating or finish"""
        if state["iteration"] >= state["max_iterations"]:
            return "finish"

        if state["executed_tools"]:
            last_execution = state["executed_tools"][-1]
            if last_execution["success"]:
                return "continue"

        return "finish"

    def _create_analysis_prompt(self, state: MCPState) -> str:
        """Create analysis prompt using LangGraph state"""
        prompt_parts = [
            f"ITERATION {state['iteration']} - MCP STORE MANAGEMENT",
            "",
            "You are executing store management operations.",
            "Analyze the current request and decide the next action.",
            "",
            "AVAILABLE MCP TOOLS:",
        ]

        for tool_info in state["available_tools"]:
            prompt_parts.append(f"- {tool_info['name']}: {tool_info['description']}")

        if state["system_context"].get("context_loaded", False):
            prompt_parts.extend(
                [
                    "",
                    "CURRENT SYSTEM STATE:",
                    json.dumps(state["system_context"], indent=2),
                    "",
                ]
            )
        else:
            prompt_parts.extend(
                [
                    "",
                    "SYSTEM CONTEXT: Not loaded yet. Use get_all_stores, get_all_main_stores, or get_all_orders tools if you need current data.",
                    f"Available operations: {', '.join(state['system_context'].get('available_operations', []))}",
                    "",
                ]
            )

        if state["executed_tools"]:
            prompt_parts.extend(
                [
                    "PREVIOUSLY EXECUTED TOOLS:",
                    json.dumps(state["executed_tools"][-3:], indent=2),
                    "",
                ]
            )

        prompt_parts.extend(
            [
                f"CURRENT REQUEST: {state['current_request']}",
                "",
                "INSTRUCTIONS:",
                "1. Analyze the current request",
                "2. If you need current system data, first call get_all_stores, get_all_main_stores, or get_all_orders",
                "3. If you need to execute a tool, respond with exactly ONE tool call:",
                '   EXECUTE: tool_name({"param1": "value1", "param2": "value2"})',
                "4. If no more tools are needed, respond with 'COMPLETE: [explanation]'",
                "5. Always explain your reasoning before the tool call",
                "6. Don't assume system state - call tools to get current data when needed",
                "",
                "Your response:",
            ]
        )

        return "\n".join(prompt_parts)

    def _extract_tool_call(self, response_text: str) -> Optional[Dict]:
        """Extract tool call from response text"""
        lines = response_text.split("\n")

        for line in lines:
            line = line.strip()
            if line.startswith("EXECUTE:"):
                try:
                    tool_part = line.split(":", 1)[1].strip()
                    if "(" in tool_part and ")" in tool_part:
                        tool_name = tool_part.split("(")[0].strip()
                        params_str = tool_part.split("(", 1)[1].rsplit(")", 1)[0]

                        try:
                            params = (
                                json.loads(params_str) if params_str.strip() else {}
                            )
                        except json.JSONDecodeError:
                            params = {}

                        return {"tool_name": tool_name, "arguments": params}
                except Exception as e:
                    print(f"Error parsing tool call: {e}")

        return None

    async def _generate_summary(self, state: MCPState) -> str:
        """Generate final summary using Gemini"""
        summary_prompt = f"""
        Please provide a comprehensive summary of the LangGraph MCP workflow execution.

        INITIAL REQUEST: {state['current_request']}

        EXECUTED TOOLS:
        {json.dumps(state['executed_tools'], indent=2)}

        FINAL SYSTEM STATE:
        {json.dumps(state['system_context'], indent=2)}

        Please summarize:
        1. What was accomplished using LangGraph workflow
        2. Which operations succeeded/failed and why
        3. The overall outcome
        4. System state changes

        Be concise but comprehensive.
        """

        try:
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            response = model.generate_content(summary_prompt)
            return response.text if response.text else "Summary generation failed"
        except Exception as e:
            return f"Error generating summary: {str(e)}"


# Global connection manager
connection_manager = WebSocketConnectionManager()


@app.websocket("/gemini/ws/feedback-loop")
async def websocket_feedback_loop(
    websocket: WebSocket, model: str = "gemini-2.0-flash-exp"
):
    """WebSocket endpoint for LangGraph-based MCP feedback loop execution"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        await websocket.close(code=1008, reason="GEMINI_API_KEY not set in environment")
        return

    session_id = str(uuid.uuid4())
    await connection_manager.connect(websocket, session_id)

    try:
        while True:
            data = await websocket.receive_text()
            request_data = json.loads(data)

            if request_data.get("action") == "start_feedback_loop":
                initial_request = request_data.get("request", "")
                max_iterations = request_data.get("max_iterations", 10)

                if not initial_request:
                    await connection_manager.send_message(
                        session_id, {"type": "error", "message": "Request is required"}
                    )
                    continue

                executor = LangGraphMCPExecutor(api_key, connection_manager)
                await executor.execute_feedback_loop(
                    session_id, initial_request, max_iterations
                )

            elif request_data.get("action") == "stop_feedback_loop":
                await connection_manager.send_message(
                    session_id,
                    {
                        "type": "connection",
                        "message": "LangGraph workflow stopped by user",
                    },
                )
                break

    except WebSocketDisconnect:
        connection_manager.disconnect(session_id)
    except Exception as e:
        await connection_manager.send_message(
            session_id, {"type": "error", "message": f"WebSocket error: {str(e)}"}
        )
        connection_manager.disconnect(session_id)


@app.get("/gemini/mcp-status")
async def get_mcp_status():
    """Get MCP server status and available tools"""
    mcp_client = MCPClient()

    try:
        tools = await mcp_client.list_tools()
        system_context = await mcp_client.get_system_context()

        return {
            "status": "connected",
            "framework": "LangGraph with proper tool management",
            "available_tools": len(tools),
            "tools": [
                {"name": t["name"], "description": t["description"]} for t in tools
            ],
            "system_summary": {
                "total_stores": system_context.get("total_counts", {}).get("stores", 0),
                "total_main_stores": system_context.get("total_counts", {}).get(
                    "main_stores", 0
                ),
                "total_orders": system_context.get("total_counts", {}).get("orders", 0),
            },
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Could not connect to MCP server",
        }
    finally:
        await mcp_client.close()
