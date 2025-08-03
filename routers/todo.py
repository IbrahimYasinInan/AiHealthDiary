from fastapi import APIRouter, Depends, Path, HTTPException, Request, Response
from google.ai.generativelanguage_v1 import Content
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from models import Base, Todo
from database import engine, SessionLocal
from typing import Annotated
from routers.auth import get_current_user
from dotenv import load_dotenv
import google.generativeai as ai
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage

router = APIRouter(
    prefix="/todo",
    tags=["Todo"]
)

templates= Jinja2Templates(directory="templates")

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    suggestion: str = Field(min_length=3, max_length=1000)
    priority: int = Field(gt=0, lt=5)
    complete:bool


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency= Annotated[Session, Depends(get_db)]
user_dependency= Annotated[dict, Depends(get_current_user)]

def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie("access_token")
    return redirect_response


def create_todo_with_gemini(todo_string: str):
    load_dotenv()
    ai.cofigure(api_key=os.environ.get('api_key'))
    llm= ChatGoogleGenerativeAI(model="gemini-1.5-pro")
    response= llm.invoke(
        [
            HumanMessage(content="I will provide you with a short note about my health or mood today. What I want you to do is generate a longer, reflective, and empathetic diary entry that elaborates on my condition and provides context, including possible causes or suggestions for improvement."),
            HumanMessage(content=todo_string),
        ]
    )
    return response.content


@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    try:
        user= await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        todos = db.query(Todo).filter(Todo.owner_id == user.get('id')).all()
        return templates.TemplateResponse("todo.html",{"request": request, "todos": todos, "user": user})
    except:
        redirect_to_login()

@router.get("/add-todo-page")
async def render_add_todo_page(request: Request):
    try:
        user= await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse("add-todo.html",{"request": request, "user": user})
    except:
        redirect_to_login()

@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
    try:
        user= await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        todo = db.query(Todo).filter(Todo.id == todo_id).first()
        return templates.TemplateResponse("edit-todo.html",{"request": request, "todo": todo, "user": user})
    except:
        redirect_to_login()

@router.get("/")
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return db.query(Todo).filter(Todo.owner_id == user.get('id')).all()


@router.get("/todo/{todo_id}")
async def read_by_id(user: user_dependency, db:db_dependency,todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    todo= db.query(Todo).filter(Todo.id == todo_id).first(Todo.owner_id == user.get('id')).first()

    if todo is not None:
        return todo
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db:db_dependency, todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    todo = Todo(**todo_request.dict(), owner_id = user.get('id'))
    todo_suggestion = create_todo_with_gemini(todo.suggestion)
    db.add(todo)
    db.commit()

@router.put("/todo/{todo_id}")
async def update_todo(user: user_dependency ,db:db_dependency,
                      todo_request: TodoRequest,
                      todo_id: int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    todo = db.query(Todo).filter(Todo.id==todo_id).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="todo not found")

    todo.title = todo_request.title
    todo.suggestion= todo_request.suggestion
    todo.priority=todo_request.priority
    todo.complete=todo_request.complete

    db.add(todo)
    db.commit()


@router.delete("/todo/{todo_id}")
async def delete_todo(user: user_dependency ,db:db_dependency, todo_id: int=Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    todo= db.query(Todo).filter(todo_id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="todo not found")

    #db.query(Todo).filter(Todo.id == todo_id).delete()
    db.delete(todo)
    db.commit()

