from fastapi import FastAPI, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import database, models, schemas, utils, oauth2

router=APIRouter(tags=['Home'])

@router.get("/home")
def home(db: Session = Depends(database.get_db),get_current_user: int = Depends(oauth2.get_current_user)):
    print(get_current_user)
    return {"message": "Welcome to the home page!"}