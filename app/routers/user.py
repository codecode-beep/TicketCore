from .. import models, schemas, utils
from sqlalchemy.orm import Session
from fastapi import FastAPI, status, HTTPException, Depends, APIRouter
from ..database import get_db
 
router=APIRouter(
    
    prefix="/users",
    tags=['Users']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate ,db: Session = Depends(get_db)):
    user.password= utils.hash(user.password)
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user