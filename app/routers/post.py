from fastapi import Response,status, HTTPException, Depends, APIRouter
from typing import List, Optional
from sqlalchemy.orm import Session
from .. import models, schemas, Oauth2
from ..database import get_db
from sqlalchemy import func


router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

#get all posts
@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user:int = Depends(Oauth2.get_current_user_), limit: int = 10, skip: int = 0, search:Optional[str]=""):

    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    return posts

#create post
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(post:schemas.PostBase, db: Session = Depends(get_db), current_user:int = Depends(Oauth2.get_current_user_)):#this depecdency  force user to be logged in

    # post_dict = post.dict()
    # post_dict['id']= randrange(0,1000000)
    # my_post.routerend(post_dict)

    # new_post = models.Post(title=post.title, content=post.content, published=post.published)
    print(current_user.email)
    new_post = models.Post(owner_id = current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

#get single post
@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user:int = Depends(Oauth2.get_current_user_)):
    # post = find_id(id)

    desired_post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    if not desired_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail = f"the post with {id} id not found")
        #response.status_code=status.HTTP_404_NOT_FOUND
        #return{"detail" : f"the post with {id} id not found"}
    return desired_post

#delete post
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user:int = Depends(Oauth2.get_current_user_)):
    #find the index in the array
    # index = find_index_post(id)
    post_query = db.query(models.Post).filter(models.Post.id == id)
    
    post_to_delete= post_query.first() 

    if post_to_delete == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail =f"post with id:{id} not found")
    
    if post_to_delete.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"not authorized to perform the action")

    # my_post.pop(index)
    post_query.delete(synchronize_session =False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


#update post
@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id: int , updated_post: schemas.PostBase, db: Session = Depends(get_db), current_user:int = Depends(Oauth2.get_current_user_)):

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()


    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail =f"post with id:{id} not found")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"not authorized to perform the action")
    
    # post_dict = post.dict()
    # post_dict['id']=id
    # my_post[index]= post_dict

    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()

    return post_query.first()