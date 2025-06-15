from fastapi import FastAPI
from dotenv import load_dotenv
from app.db.dbconnect import connect_to_mongo, close_mongo_connection
from app.api.store import app as store_router
from app.api.mainstore import app as mainstore_router
load_dotenv()

app = FastAPI(title="Store Management API", version="1.0.0")

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
@app.get("/")
async def root():
    return {"message": "Store Management API with MongoDB"}