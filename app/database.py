from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "postgresql://neondb_owner:npg_HV38xYkqWdmL@ep-cool-smoke-b5n1trh4-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"  

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()