from ..schemas import user
from .. import models, utils
from sqlalchemy.orm import Session
from fastapi import FastAPI, status, HTTPException, Depends, APIRouter
from ..database import get_db
 
router=APIRouter(
    
    prefix="/users",
    tags=['Users']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=user.UserOut)
def create_user(user: user.UserCreate ,db: Session = Depends(get_db)):
    user.password= utils.hash(user.password)
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user