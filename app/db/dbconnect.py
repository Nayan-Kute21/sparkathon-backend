from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None

database = Database()

async def get_database() -> AsyncIOMotorDatabase:
    return database.database

async def connect_to_mongo():
    """Create database connection"""
    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://nayankishorkute21:weakpassword@cluster1.qki4o.mongodb.net/?retryWrites=true&w=majority&appName=cluster1")
    database.client = AsyncIOMotorClient(MONGO_URI)
    database.database = database.client.store_database
    
    # Test the connection
    try:
        await database.client.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")

async def close_mongo_connection():
    """Close database connection"""
    if database.client:
        database.client.close()
        print("Disconnected from MongoDB!")