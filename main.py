from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, JSON, and_, or_, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List, Optional, Union
from pydantic import BaseModel
import os

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:123456@localhost:3306/recipe")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Recipe(Base):
    __tablename__ = 'recipes'
    
    id = Column(Integer, primary_key=True, index=True)
    cuisine = Column(String, index=True)
    title = Column(String, index=True)
    rating = Column(Float, nullable=True)
    prep_time = Column(Integer, nullable=True)
    cook_time = Column(Integer, nullable=True)
    total_time = Column(Integer, nullable=True)
    description = Column(Text)
    nutrients = Column(JSON)
    serves = Column(String)

Base.metadata.create_all(bind=engine)

class RecipeResponse(BaseModel):
    id: int
    cuisine: Optional[str]
    title: Optional[str]
    rating: Optional[float]
    total_time: Optional[int]
    serves: Optional[str]

    class Config:
        orm_mode = True

@app.get("/recipes_info/", response_model=List[RecipeResponse])
async def get_recipes(
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "rating",
    sort_order: str = "desc",
    title: Optional[str] = Query(None, min_length=1),
    cuisine: Optional[str] = Query(None, min_length=1)
):
    db = SessionLocal()
    query = db.query(Recipe)

    if title:
        query = query.filter(Recipe.title.ilike(f"%{title}%"))
    if cuisine:
        query = query.filter(Recipe.cuisine.ilike(f"%{cuisine}%"))

    if hasattr(Recipe, sort_by):
        column = getattr(Recipe, sort_by)
        query = query.order_by(column.desc() if sort_order == "desc" else column.asc())

    recipes = query.offset(skip).limit(limit).all()
    
    db.close()
    return recipes

@app.get("/api/recipes", response_model=List[RecipeResponse])
async def get_recipes_paginated(
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(10, ge=1, le=100, description="Number of recipes per page")
):
    db = SessionLocal()
    skip = (page - 1) * limit
    
    query = db.query(Recipe)
    query = query.order_by(Recipe.rating.desc())
    recipes = query.offset(skip).limit(limit).all()
    
    db.close()
    return recipes

def parse_comparison(value: str) -> tuple[float, str]:
    if value.startswith('<='):
        return float(value[2:]), '<='
    elif value.startswith('>='):
        return float(value[2:]), '>='
    elif value.startswith('<'):
        return float(value[1:]), '<'
    elif value.startswith('>'):
        return float(value[1:]), '>'
    else:
        return float(value), '='

@app.get("/api/recipes/search", response_model=List[RecipeResponse])
async def search_recipes(
    calories: Optional[str] = Query(None, description="Filter by calories (e.g., '<=400', '>=300', '=500')"),
    title: Optional[str] = Query(None, description="Search by recipe title (partial match)"),
    cuisine: Optional[str] = Query(None, description="Filter by cuisine"),
    total_time: Optional[str] = Query(None, description="Filter by total time (e.g., '<=60', '>=30', '=45')"),
    rating: Optional[str] = Query(None, description="Filter by rating (e.g., '>=4.5', '<=5.0', '=4.0')")
):
    db = SessionLocal()
    query = db.query(Recipe)

    # Apply filters
    if calories:
        value, operator = parse_comparison(calories)
        if operator == '<=':
            query = query.filter(func.jsonb_extract_path_text(Recipe.nutrients, 'calories').cast(Float) <= value)
        elif operator == '>=':
            query = query.filter(func.jsonb_extract_path_text(Recipe.nutrients, 'calories').cast(Float) >= value)
        elif operator == '<':
            query = query.filter(func.jsonb_extract_path_text(Recipe.nutrients, 'calories').cast(Float) < value)
        elif operator == '>':
            query = query.filter(func.jsonb_extract_path_text(Recipe.nutrients, 'calories').cast(Float) > value)
        else:
            query = query.filter(func.jsonb_extract_path_text(Recipe.nutrients, 'calories').cast(Float) == value)

    if title:
        query = query.filter(Recipe.title.ilike(f"%{title}%"))

    if cuisine:
        query = query.filter(Recipe.cuisine.ilike(f"%{cuisine}%"))

    if total_time:
        value, operator = parse_comparison(total_time)
        if operator == '<=':
            query = query.filter(Recipe.total_time <= value)
        elif operator == '>=':
            query = query.filter(Recipe.total_time >= value)
        elif operator == '<':
            query = query.filter(Recipe.total_time < value)
        elif operator == '>':
            query = query.filter(Recipe.total_time > value)
        else:
            query = query.filter(Recipe.total_time == value)

    if rating:
        value, operator = parse_comparison(rating)
        if operator == '<=':
            query = query.filter(Recipe.rating <= value)
        elif operator == '>=':
            query = query.filter(Recipe.rating >= value)
        elif operator == '<':
            query = query.filter(Recipe.rating < value)
        elif operator == '>':
            query = query.filter(Recipe.rating > value)
        else:
            query = query.filter(Recipe.rating == value)

    recipes = query.all()
    db.close()
    return recipes

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)