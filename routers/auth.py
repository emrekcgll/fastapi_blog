from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from pydantic import BaseModel, EmailStr
from database import SessionLocal
from sqlalchemy.orm import Session
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from decouple import config

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = config("secret")
ALGORITHM = config("algorithm")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class CreateUserScheme(BaseModel):
    email: EmailStr
    username: str
    name: str
    surname: str
    password: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/login')


@router.post("/create_user", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, scheme: CreateUserScheme):
    model = Users(email=scheme.email,
                  username=scheme.username,
                  name=scheme.name,
                  surname=scheme.surname,
                  hashed_password=bcrypt_context.hash(scheme.password),
                  role=scheme.role,
                  is_active=True)
    db.add(model)
    db.commit()


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    expires = datetime.utcnow() + expires_delta
    encode = {"sub": username, "id": user_id, "role": role, "exp": expires}
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/login", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return "Failed Authentication!"
    token = create_access_token(
        user.username, user.id, user.role, timedelta(hours=24))
    return {"access_token": token, "token_type": "bearer"}


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        id: int = payload.get("id")
        role: str = payload.get("role")
        if username is None or id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user!")
        return {"username": username, "id": id, "role": role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user!")
