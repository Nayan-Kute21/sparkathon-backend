from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.models.user import User, UserCreate, UserUpdate
from app.repository.user_repo import UserRepository
from app.db.dbconnect import get_database

router = APIRouter(prefix="/users", tags=["users"])

def get_user_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> UserRepository:
    return UserRepository(db)

@router.post("/", response_model=User)
async def create_user(
    user_data: UserCreate,
    repository: UserRepository = Depends(get_user_repository)
):
    """Create a new user"""
    # Check if email already exists
    existing_user = await repository.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username already exists
    existing_username = await repository.get_by_username(user_data.username)
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    return await repository.create(user_data)

@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    repository: UserRepository = Depends(get_user_repository)
):
    """Get user by ID"""
    user = await repository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/", response_model=List[User])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    repository: UserRepository = Depends(get_user_repository)
):
    """Get all users with pagination"""
    return await repository.get_all(skip=skip, limit=limit)

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    repository: UserRepository = Depends(get_user_repository)
):
    """Update a user"""
    user = await repository.update(user_id, user_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    repository: UserRepository = Depends(get_user_repository)
):
    """Delete a user"""
    success = await repository.delete(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}