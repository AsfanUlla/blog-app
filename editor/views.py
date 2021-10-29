from fastapi import APIRouter, File, HTTPException, status, UploadFile, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from common.utils import verify_token, templates
from editor.models import *
from common.models import SchemalessResponse
from common.views import MongoInterface, PyObjectId
from common.db import collections
from slugify import slugify
import datetime
import os
import imghdr
from config import Config
from typing import Optional
from bson import ObjectId


router = APIRouter()


@router.post("/save")
async def save_article(request: Request, data: SaveArticle, payload: dict = Depends(verify_token)):
    if not payload[0]["is_su_admin"] and not payload[0]["is_editor"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    article_slug = slugify(data.title)
    edit = data.edit
    del data.edit

    query = dict(
        slug=article_slug
    )
    if edit:
        query = dict(
            _id=ObjectId(data.article_id)
        )
    
    doc = await MongoInterface.find_or_none(
        collection_name=collections["articles"],
        query=query,
        exclude=dict(
            _id=1
        )
    )

    del data.article_id
    post_obj = jsonable_encoder(data)
    article_id = None

    if edit:
        if doc is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="article not found")
        if data.published:
            post_obj.update(
                dict(
                    published_date = datetime.datetime.utcnow()
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
        article_id = doc["_id"]
        message = "article updated successfully"
    else:
        if doc:
            raise HTTPException(status.HTTP_409_CONFLICT, detail="article already exist")
        published_date = None
        if data.published:
            published_date = datetime.datetime.utcnow()
        post_obj.update(
            dict(
                is_suspended=False,
                author_id=payload[1].get("user_id"),
                slug=article_slug,
                published_date=published_date
            )
        )
        article_id = await MongoInterface.insert_one(
            collection_name=collections["articles"],
            post_obj=post_obj
        )
        message = "article saved successfully"

    response = SchemalessResponse(
        data=dict(
            success=True,
            article_id=str(article_id)
        ),
        message=message
    )
    return JSONResponse(jsonable_encoder(response))


@router.post("/upload_image")
async def upload_img(request: Request, img: UploadFile = File(...), payload: dict = Depends(verify_token)):
    if not payload[0]["is_su_admin"] and not payload[0]["is_editor"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    img_typ = imghdr.what(img.file)
    if img_typ is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="File type not allowed")
    root_dir = os.getcwd() + "/templates/static/article_files/"
    today_dir = str(datetime.date.today())
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
    file_url = request.state.current_host_url + "/static/article_files/" + today_dir + "/" + filename
    response = dict(
        success=1,
        file=dict(
            url=file_url
        )
    )
    return JSONResponse(jsonable_encoder(response))


@router.get("", response_class=HTMLResponse)
async def editor(request: Request, article: Optional[PyObjectId] = None, payload: dict = Depends(verify_token)):
    if not payload[0]["is_su_admin"] and not payload[0]["is_editor"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    article_doc = None
    if article:
        article_doc = await MongoInterface.find_or_404(
            collection_name=collections["articles"],
            query=dict(
                _id=ObjectId(article)
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
