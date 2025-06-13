from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
# client = AsyncIOMotorClient(MONGO_URI)
# db = client.mydatabase

@app.get("/")
async def root():
    return {"message": "FastAPI with MongoDB"}
