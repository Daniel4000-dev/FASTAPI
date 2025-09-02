from multiprocessing import synchronize
import os
from fastapi import FastAPI, Response, status, Body, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models, schemas, utils
from .database import engine, get_db
from dotenv import load_dotenv
from .routes import post, users, auth

models.Base.metadata.create_all(bind=engine)
# Load variables from .env file
load_dotenv()

app = FastAPI()

# Connect to existing database
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASS")

max_retries = 5
retry_delay = 2  # start with 2 seconds

for attempt in range(max_retries):   
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            cursor_factory=RealDictCursor
        )
        cursor = conn.cursor() 
        print("Database connection was successful!")
        break # exit loop on success
    except Exception as error:
        print(f"Attempt {attempt + 1} of {max_retries} failed: {error}")
        if attempt < max_retries - 1:
            time.sleep(retry_delay)
            retry_delay *= 2 # Exponential backoff
        else:
            print("Maximum retries reached. Exiting.")
            raise
    
my_posts = [
    {"title": "First Post", "content": "This is the content of the first post.", "id": 1},
    {"title": "Second Post", "content": "This is the content of the second post.", "id": 2}
            ]

def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p
        
def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i


app.include_router(post.router)
app.include_router(users.router)
app.include_router(auth.router)

@app.get("/", response_model=schemas.PostResponse)
def root():
    return {"message": "Welcome to my api"}
