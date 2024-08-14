from fastapi import FastAPI, status, Response, HTTPException,Depends,APIRouter
from fastapi import Body
from random import randrange
from sqlalchemy.orm import Session
from .. import models 
from ..database import engine,SessionLocal,get_db
from ..schemas import PostBase,PostCreate,Post,PostOut
from typing import List, Optional
from . import oauth2
from sqlalchemy import func


router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

@router.get("/", status_code=status.HTTP_200_OK,response_model=List[PostOut])
async def get_posts(db: Session = Depends(get_db),current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # # Execute a query
    # cursor.execute("SELECT * FROM posts")
    # # Retrieve query results
    # records = cursor.fetchall()
    # print(records)
    records =  db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return records

@router.post("/", status_code=status.HTTP_201_CREATED,response_model=Post)
async def create_posts(new_post: PostCreate,db: Session = Depends(get_db),get_current_user : int = Depends(oauth2.get_current_user)):
    # cursor.execute("INSERT INTO posts (title,content,published) VALUES (%s,%s,%s) RETURNING *",(new_post.title,new_post.content,new_post.published))
    # new_post = cursor.fetchall()
    # conn.commit()
    new_post = models.Post(owner_id=get_current_user.id,**new_post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/{id}",response_model=Post)
def get_post(id: int, response: Response,db: Session = Depends(get_db),get_current_user : int = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ID not found")
    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_posts(id: int,db: Session = Depends(get_db),get_current_user : int = Depends(oauth2.get_current_user) ):
    
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ID not found")
    if post.owner_id != get_current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    post_query.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", status_code=status.HTTP_200_OK,response_model=Post)
def update_posts(id: int, updated_post: PostCreate,db: Session = Depends(get_db),get_current_user : int = Depends(oauth2.get_current_user)):
    # cursor.execute("""UPDATE posts SET title = %s,content = %s,published = %s WHERE id = %s returning * """,(updated_post.title,updated_post.content,updated_post.published,str(id)))
    # post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()
    
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ID not found")
     # Prepare the update dictionary
    if post.owner_id != get_current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
        
    post_query.update(updated_post.model_dump(),synchronize_session=False)
    
    db.commit()

    return post_query.first()
