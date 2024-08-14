from fastapi import FastAPI, status, Response, HTTPException,Depends,APIRouter
from fastapi import Body
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from random import randrange
from sqlalchemy.orm import Session
from .. import models 
from ..database import engine,SessionLocal,get_db
from ..schemas import PostBase,PostCreate,Post,Userlogin,Token
from typing import List
from .. import utility
from . import oauth2

router = APIRouter(
    tags = ["Authentication"]
)

@router.post("/login",status_code=status.HTTP_200_OK, response_model=Token)
def login(user_credentials:OAuth2PasswordRequestForm=Depends(),db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="User not found")
    
    if not utility.verify(user_credentials.password,user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid Credentails")
    
    #create a token 
    #return token
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
    