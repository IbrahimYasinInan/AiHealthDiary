from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette import status
from models import Base
from database import engine
from routers.auth import router as auth_router
from routers.todo import router as todo_router

app = FastAPI()

@app.get("/")
def read_root(request: Request):
    return RedirectResponse(url="/todo/todo-page", status_code=status.HTTP_302_FOUND)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(auth_router)
app.include_router(todo_router)

Base.metadata.create_all(bind=engine)
