from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from common.utils import verify_token
from common.views import RediectException, redirect, CurrentHost
from common.db import close_db, connect_db
from articles.views import router as article_router
from editor.views import router as editor_router
from admin.views import router as admin_router
from starlette.middleware.sessions import SessionMiddleware
from config import Config

app = FastAPI()

app.add_event_handler("startup", connect_db)
app.add_event_handler("shutdown", close_db)

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=Config.SESSION_SECRET, https_only=False)

app.mount("/static", StaticFiles(directory="templates/static"), name="static")

app.add_exception_handler(RediectException, redirect)
app.add_middleware(CurrentHost)

app.include_router(editor_router, tags=["editor"], prefix="/editor", dependencies=[Depends(verify_token)])
app.include_router(admin_router, tags=["users"], prefix="/admin")
app.include_router(article_router, tags=["articles"], prefix="")
