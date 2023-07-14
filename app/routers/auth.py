from fastapi import status, HTTPException, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import models, schemas, utils, Oauth2
from ..database import get_db

router = APIRouter(tags= ['Authentication'])

@router.post('/login', response_model=schemas.Token)
def login(user_credential: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email==user_credential.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials")
    
    if not utils.verify(user_credential.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials")
 #create token
 # return token
    access_token = Oauth2.create_access_token(data = {"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}