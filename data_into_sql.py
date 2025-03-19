import os
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
import math

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

#     url = Column(String, nullable=True)
#     ingredients = Column(JSON, nullable=True) 

def handle_nan(value):
    if isinstance(value, float) and math.isnan(value):
        return None
    return value

def insert_recipes_from_json(file_path: str):
    with open(file_path, 'r') as f:
        data = json.load(f)

    db = SessionLocal()

    for key, recipe_data in data.items():
        recipe = Recipe(
            cuisine=recipe_data.get('cuisine'),
            title=recipe_data.get('title'),
            rating=handle_nan(recipe_data.get('rating')),
            prep_time=handle_nan(recipe_data.get('prep_time')),
            cook_time=handle_nan(recipe_data.get('cook_time')),
            total_time=handle_nan(recipe_data.get('total_time')),
            description=recipe_data.get('description'),
            nutrients=recipe_data.get('nutrients'),  
            serves=recipe_data.get('serves')
        )
        db.add(recipe)
    
    db.commit()
    db.close()

insert_recipes_from_json('US_recipes.json')