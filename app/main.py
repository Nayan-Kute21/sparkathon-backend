from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from app.db.dbconnect import connect_to_mongo, close_mongo_connection
from app.api.store import app as store_router
from app.api.mainstore import app as mainstore_router
from app.api.gemini import app as gemini_router
from fastapi.middleware.cors import CORSMiddleware
import os

load_dotenv()

app = FastAPI(title="Store Management API with Live MCP Integration", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Connect to database on startup"""
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    await close_mongo_connection()


# Include routers
app.include_router(store_router, prefix="/api", tags=["stores"])
app.include_router(mainstore_router, prefix="/api", tags=["mainstore"])
app.include_router(gemini_router, prefix="/api", tags=["gemini"])


@app.get("/")
async def root():
    return {"message": "Store Management API with MongoDB and Live MCP Integration"}


@app.get("/live", response_class=HTMLResponse)
async def get_live_client():
    """Serve the WebSocket client HTML page"""
    html_file_path = os.path.join(
        os.path.dirname(__file__), "..", "websocket_client.html"
    )

    try:
        with open(html_file_path, "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content, status_code=200)
    except FileNotFoundError:
        return HTMLResponse(
            content="""
            <html>
                <head><title>File Not Found</title></head>
                <body>
                    <h1>WebSocket Client Not Found</h1>
                    <p>The websocket_client.html file was not found.</p>
                    <p>Please make sure the file exists in the project root directory.</p>
                    <p><a href="/docs">Go to API Documentation</a></p>
                </body>
            </html>
            """,
            status_code=404,
        )


@app.get("/client", response_class=HTMLResponse)
async def get_mcp_client():
    """Alternative endpoint for the WebSocket client"""
    return await get_live_client()
