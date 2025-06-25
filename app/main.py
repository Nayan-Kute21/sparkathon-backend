from contextlib import asynccontextmanager
from fastapi import FastAPI
from .api.item_api import router as items_router
from .api.user_api import router as users_router
from .api.cart_api import router as cart_router
from .api.order_api import router as orders_router
from .db.dbconnect import connect_to_mongo, close_mongo_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="Sparkathon Backend", 
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(items_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(cart_router, prefix="/api/v1")
app.include_router(orders_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Sparkathon Backend API"}