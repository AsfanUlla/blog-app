from fastapi import FastAPI, Depends, HTTPException, status
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
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.gzip import GZipMiddleware
#from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
import os
from os.path import exists as file_exists


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

app.add_event_handler("startup", connect_db)
app.add_event_handler("shutdown", close_db)

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=Config.SESSION_SECRET, https_only=Config.HTTPS_ONLY)
app.add_middleware(GZipMiddleware, minimum_size=256)
#if Config.ENV != "LOCAL":
#    app.add_middleware(HTTPSRedirectMiddleware)

app.mount("/static", StaticFiles(directory="templates/static"), name="static")

app.add_exception_handler(RediectException, redirect)
app.add_middleware(CurrentHost)

@app.get("/robots.txt", response_class=FileResponse)
async def get_robots_txt():
    return  os.getcwd() + "/templates/robots.txt"

# Propeller SW.JS
# @app.get("/sw.js", response_class=FileResponse)
# async def propeller_sw():
#     return  os.getcwd() + "/sw.js"

@app.get("/openapi.json")
async def get_open_api_endpoint(payload: dict = Depends(verify_token)):
    if not payload[0]["is_su_admin"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    return JSONResponse(get_openapi(title="BlogAPI", version="1", routes=app.routes))

@app.get("/docs")
async def get_documentation(payload: dict = Depends(verify_token)):
    if not payload[0]["is_su_admin"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    return get_swagger_ui_html(openapi_url="/openapi.json", title="blog-docs")

@app.get("/.well-known/{file_name}", response_class=FileResponse)
async def get_well_known_file(file_name: str):
    file_path = os.getcwd() + "/.well-known/" + file_name
    if file_exists(file_path):
        return file_path
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not Found")

app.include_router(editor_router, tags=["editor"], prefix="/editor", dependencies=[Depends(verify_token)])
app.include_router(admin_router, tags=["admin"], prefix="/admin")
app.include_router(article_router, tags=["articles"], prefix="")
