from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from dotenv import load_dotenv

from db import engine
from db import get_db

from models import Base

app = FastAPI(title="Wikipedia Summarizer API")

load_dotenv()

@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# @app.post("/users")
# def create_user(name: str, db: Session = Depends(get_db)) -> dict:
#     user = User(name=name)
#     db.add(user)
#     db.commit()
#     db.refresh(user)
#     return {"id": user.id, "name": user.name}


# @app.get("/users")
# def list_users(db: Session = Depends(get_db)) -> list[dict]:
#     users = db.scalars(select(User).order_by(User.id)).all()
#     return [{"id": u.id, "name": u.name} for u in users]
