from pydantic import BaseModel, EmailStr

class Post(BaseModel):
    title: str
    content: str
    published: bool = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str 

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str

    class Config:
        from_attributese = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str