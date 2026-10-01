from fastapi import FastAPI, status, HTTPException, Depends

from . import models, schemas, utils
from .routers import user, auth, home
from .database import engine,get_db
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)


app= FastAPI(
    title="ticketCore"
)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(home.router)

@app.get("/sqlalchemy")
def test_post(db: Session = Depends(get_db)):
    return {"status":"Sucess"}

