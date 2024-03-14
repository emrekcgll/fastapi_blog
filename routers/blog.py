from fastapi import APIRouter, Depends, HTTPException, status

from typing import Annotated

from pydantic import BaseModel
from database import SessionLocal
from sqlalchemy.orm import Session
from models import Blogs
from routers.auth import get_current_user

router = APIRouter(prefix="/blog", tags=["blog"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependecy = Annotated[dict, Depends(get_current_user)]


class CreateBlogScheme(BaseModel):
    title: str
    content: str


@router.get("/")
def get_all(db: db_dependency):
    return db.query(Blogs).all()


@router.get("/{id}")
def get_all(db: db_dependency, id: int):
    value = db.query(Blogs).filter(Blogs.id == id).first()
    if value is not None:
        return value
    raise HTTPException(status_code=404, detail="Blog not found!")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create(user: user_dependecy, db: db_dependency, scheme: CreateBlogScheme):
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Authentication Failed!")
    value = Blogs(**scheme.model_dump(), is_active=True,
                  author=user.get("id"),)
    db.add(value)
    db.commit()
