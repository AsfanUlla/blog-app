from fastapi import APIRouter, File, HTTPException, status, UploadFile, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from common.utils import verify_token, templates
from editor.models import *
from common.models import SchemalessResponse
from common.views import MongoInterface
from common.db import collections
from slugify import slugify
from datetime import datetime, date
import os
import imghdr
from config import Config
from typing import Optional


router = APIRouter()


@router.post("/save", response_model=SchemalessResponse)
async def save_article(request: Request, data: SaveArticle, payload: dict = Depends(verify_token)):
    article_slug = slugify(data.title)
    doc = await MongoInterface.find_or_none(
        collection_name=collections["articles"],
        query=dict(
            slug=article_slug
        ),
        exclude=dict(
            _id=1
        )
    )
    edit = data.edit
    del data.edit
    post_obj = jsonable_encoder(data)
    if edit:
        if doc is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="article not found")
        if data.published:
            post_obj.update(
                dict(
                    published_date = datetime.utcnow()
                )
            )
        update_article = await MongoInterface.update_doc(
            collection_name=collections["articles"],
            query=dict(
                _id=doc["_id"]
            ),
            update_data=post_obj,
            q_type='set'
        )
        message = "article updated successfully"
    else:
        if doc:
            raise HTTPException(status.HTTP_409_CONFLICT, detail="article already exist")
        published_date = None
        if data.published:
            published_date = datetime.utcnow()
        post_obj.update(
            dict(
                is_suspended=False,
                author_id=payload[1].get("user_id"),
                slug=article_slug,
                published_date=published_date
            )
        )
        saved_article = await MongoInterface.insert_one(
            collection_name=collections["articles"],
            post_obj=post_obj
        )
        message = "article saved successfully"

    response = SchemalessResponse(
        data=dict(
            success=True
        ),
        message=message
    )
    return JSONResponse(jsonable_encoder(response))


@router.post("/upload_image")
async def upload_img(img: UploadFile = File(...)):
    img_typ = imghdr.what(img.file)
    if img_typ is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="File type not allowed")
    root_dir = os.getcwd() + "/templates/static/article_files/"
    today_dir = str(date.today())
    try:
        if not os.path.exists(root_dir + today_dir):
            os.mkdir(root_dir + today_dir)
    except Exception as e:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail="Unexpected error occurred")
    filename = img.filename.replace(" ", "-")
    file_path = root_dir + today_dir + "/" + filename
    with open(file_path, 'wb') as f:
        f.write(img.file.read())
        f.close()
    file_url = Config.HOST_URL + "/static/article_files/" + today_dir + "/" + filename
    response = dict(
        success=1,
        file=dict(
            url=file_url
        )
    )
    return JSONResponse(jsonable_encoder(response))


@router.get("", response_class=HTMLResponse)
async def editor(request: Request, article: Optional[str] = None):
    article_doc = None
    if article:
        article_doc = await MongoInterface.find_or_404(
            collection_name=collections["articles"],
            query=dict(
                slug=article
            ),
            exclude=dict(
                is_suspended=0,
                slug=0,
                published_date=0,
                cd=0,
                _id=0
            ),
            error_message="Article not found"
        )
    host_doc = await MongoInterface.find_all(
        collection_name=collections["hosts"],
        query=dict(
            enabled=True
        ),
        exclude=dict(
            _id=False,
            enabled=False
        )
    )
    if not host_doc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Configure hosts first")
    hosts = []
    for host in host_doc:
        hosts.append(host["host"])
    html_content = dict(
        request=request,
        site_header=request.state.current_host,
        title="Editor",
        hosts=hosts,
        article_doc=article_doc
    )
    return templates.TemplateResponse("components/editor.html", html_content)


"""@router.delete("/delete")
async def delete_article():
    return {"success": True}"""
