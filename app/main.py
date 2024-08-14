from fastapi import FastAPI, status, Response, HTTPException,Depends
from fastapi import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models 
from .database import engine,SessionLocal,get_db
from .schemas import PostBase,PostCreate,Post,UserCreate,UserOut
from typing import List, Optional
from passlib.context import CryptContext
from . import utility,schemas
from .routers import post,user,auth,vote
from fastapi.middleware.cors import CORSMiddleware

# models.Base.metadata.create_all(bind=engine)


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)