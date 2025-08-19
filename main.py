from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette import status
from models import Base
from database import engine
from routers.auth import router as auth_router
from routers.todos import router as todo_router
from routers.users import router as user_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root(request: Request):
    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(auth_router)
app.include_router(todo_router)
app.include_router(user_router)


