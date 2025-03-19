import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
import math

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
    prep_time: Optional[int]
    cook_time: Optional[int]
    total_time: Optional[int]
    description: Optional[str]
    nutrients: Optional[dict]
    serves: Optional[str]

    class Config:
        orm_mode = True

@app.get("/recipes_info/", response_model=List[RecipeResponse])
async def get_recipes(
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "rating",
    sort_order: str = "desc"
):
    db = SessionLocal()
    
    if sort_order == "asc":
        sort_order = None
    else:
        sort_order = "desc"
    
    recipes = db.query(Recipe).order_by(getattr(Recipe, sort_by).desc() if sort_order == "desc" else getattr(Recipe, sort_by).asc()).all()
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