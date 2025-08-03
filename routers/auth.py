from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import User
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
from fastapi.templating import Jinja2Templates

router= APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)
templates = Jinja2Templates(directory="templates")

SECRET_KEY = "sensikeninaditeroristorospucocuklariibne6saray"
ALGORITHM= "HS256"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency= Annotated[Session, Depends(get_db)]

bcrypt_content = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer= OAuth2PasswordBearer(tokenUrl="/auth/token")

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str

class token(BaseModel):
    accestoken: str
    token_type:str


def create_acces_token(user_name: str, user_id: int, expires_delta: timedelta):
    payload= {'sub': user_name, 'id': user_id}
    expires= datetime.now(timezone.utc)+expires_delta
    payload.update({'exp': expires})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(username: str, password: str, db):
    user= db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_content.verify(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username= payload.get('sub')
        user_id = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username or Id invalid")
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token is invalid")

@router.get("/login-page")
def render_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register-page")
def render_login_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/")
async def create_user(db:db_dependency, create_user_request: CreateUserRequest):
    user = User(
        username=create_user_request.username,
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password=bcrypt_content.hash(create_user_request.password)
    )
    db.add(user)
    db.commit()

@router.post("/token")

async def login_for_acces_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency):
    user= authenticate_user(form_data.username, form_data.password,db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="incorrect username or password")
    token = create_acces_token(user.username, user.id, timedelta(minutes=60))
    return {"access_token": token, "token_type": "bearer"}
