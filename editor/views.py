from fastapi import APIRouter, File, HTTPException, status, UploadFile, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from common.utils import verify_token, templates
from editor.models import *
from common.models import SchemalessResponse
from common.views import MongoInterface, PyObjectId, CommonMethods
from common.db import collections
from slugify import slugify
import datetime
import os
import imghdr
from config import Config
from typing import Optional
from bson import ObjectId, objectid


router = APIRouter()

"""
@router.post("/save_article")
async def save_article_v2(
    request: Request,
    post_data: SaveArticle,
    auth: dict = Depends(verify_token)
):
    if not auth[0]["is_su_admin"] and not auth[0]["is_editor"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    doc = None
    if post_data.article_id is not None and objectid.ObjectId.is_valid(post_data.article_id):
        doc = await MongoInterface.find_or_none(
            collection_name=collections["articles"], 
            query=dict(
                _id=ObjectId(post_data.article_id)
            ),
            exclude=dict(
                _id=1,
                slug=1,
                published=1
            )    
        )

    del post_data.article_id

    post_obj = jsonable_encoder(post_data)
       
    post_obj["author_id"]=auth[1].get("user_id")

    if doc:
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
        article_id = await MongoInterface.insert_one(
            collection_name=collections["articles"],
            post_obj=post_obj
        )
        message = "article saved successfully"
    
    response = SchemalessResponse(
        data=dict(
            success=True,
            article_url= request.state.current_host_url + "/editor/preview?article=" + str(article_id)
        ),
        message=message
    )
    return JSONResponse(jsonable_encoder(response))


@router.post("/pub_or_unpub")
async def pub_or_unpub(
    request: Request,
    post_data: PubOrUn,
    auth: dict = Depends(verify_token)
):
    if not auth[0]["is_su_admin"] and not auth[0]["is_editor"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    doc = await MongoInterface.find_or_404(
            collection_name=collections["articles"], 
            query=dict(
                _id=ObjectId(post_data.article_id)
            ),
            exclude=dict(
                _id=1,
                slug=1,
                published=1,
                title = 1
            ),
            error_message="Article not found"
        )

    del post_data.article_id
    post_obj = jsonable_encoder(post_data)
    post_obj["published_date"]=datetime.datetime.utcnow()
    if not doc.get("slug"):
        post_obj["slug"] = slugify(doc["title"])
    update_article = await MongoInterface.update_doc(
        collection_name=collections["articles"],
        query=dict(
            _id=doc["_id"]
        ),
        update_data=post_obj,
        q_type='set'
    )

    response = SchemalessResponse(
        data=dict(
            success=True
        ),
        message="Article Updated sucessfully"
    )
    return JSONResponse(jsonable_encoder(response))"""


@router.post("/save")
async def save_article(
    request: Request,
    data: SaveArticle,
    payload: dict = Depends(verify_token)
    ):
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
    doc = None
    if edit or data.title != "":
        doc = await MongoInterface.find_or_none(
            collection_name=collections["articles"],
            query=query,
            exclude=dict(
                _id=1,
                title=1,
                published=1
            )
        )

    if doc and doc.get("title"):
        if doc.get("title").strip() != data.title.strip():
            xdoc = await MongoInterface.find_or_none(
                collection_name=collections["articles"],
                query=dict(
                    slug=slugify(data.title)
                ),
                exclude=dict(
                    _id=1
                )
            )
            if xdoc:
                raise HTTPException(status.HTTP_409_CONFLICT, detail="Title already exist")



    del data.article_id
    data.title = data.title.strip()
    post_obj = jsonable_encoder(data)
    article_id = None

    if edit:
        if doc is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="article not found")
        if data.published:
            pub = True
            if doc["published"]:
                pub = False
            post_obj = dict(
                slug=slugify(doc["title"]),
                published=pub,
                published_date=datetime.datetime.utcnow()
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
        post_obj.update(
            dict(
                is_suspended=False,
                author_id=payload[1].get("user_id"),
                slug=article_slug
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
            article_url= request.state.current_host_url + "/editor/preview?article=" + str(article_id)
        ),
        message=message
    )
    return JSONResponse(jsonable_encoder(response))


@router.get("/preview", response_class=HTMLResponse)
async def preview_article(request: Request, article: PyObjectId, payload: dict = Depends(verify_token)):
    if not payload[0]["is_su_admin"] and not payload[0]["is_editor"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    article_doc = await MongoInterface.find_or_404(
        collection_name=collections["articles"],
        query=dict(
            _id=ObjectId(article)
        ),
        exclude=dict(
            _id=0,
            cd=0
        ),
        error_message="Article not found"
    )

    published_date = None
    if article_doc.get("published_date"):
        published_date = article_doc["published_date"].date().isoformat()

    author = None
    if article_doc.get("author_id"):
        author = await MongoInterface.find_or_none(
            collection_name=collections["users"],
            query=dict(
                _id=ObjectId(article_doc["author_id"])
            ),
            exclude=dict(
                full_name=1,
                email=1,
                avatar=1,
                about=1,
                social=1
            )
        )
        if author:
            author["avatar"] = author.get("avatar", request.state.current_host_url+"/static/assets/img/default_avatar.jpg")
            author["about"] = author.get("about", None)
            author["social"] = author.get("social", {})
        
    return templates.TemplateResponse(
        "components/article.html",
        await CommonMethods.prep_templates(
            request=request,
            title=article_doc["title"],
            data=article_doc["article_data"],
            page_keywords=article_doc["tags"],
            pub=article_doc.get("published", False),
            author=author,
            published_date=published_date,
            editor_url=request.state.current_host_url + "/editor?article=" + str(article),
            preview=True
        )
    )


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


@router.post("/discard")
async def article_discard(request: Request, ddel: Discard, payload: dict = Depends(verify_token)):
    if not payload[0]["is_su_admin"] and not payload[0]["is_editor"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    discard = await MongoInterface.delete_one(
        collection_name=collections["articles"],
        query=dict(
            _id=ObjectId(ddel.article_id)
        )
    )
    response = SchemalessResponse(
        data=dict(
            success=True,
            redirect_url= request.state.current_host_url + "/editor"
        ),
        message="Article deleted"
    )
    return JSONResponse(jsonable_encoder(response))


@router.get("", response_class=HTMLResponse)
async def editor(request: Request, article: Optional[PyObjectId] = None, payload: dict = Depends(verify_token)):
    if not payload[0]["is_su_admin"] and not payload[0]["is_editor"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    article_doc = None
    preview_url = ""
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
        preview_url = request.state.current_host_url + "/editor/preview?article=" + str(article)
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

    mqyery = dict(
        author_id=payload[1]["user_id"]
    )
    if payload[0]["is_su_admin"]:
        mqyery = {}

    my_bl = await MongoInterface.find_all(
        collection_name=collections["articles"],
        query=mqyery,
        exclude=dict(
            _id=1,
            title=1,
            published=1,
            hosts=1,
            is_suspended=1,
            published_date=1
        ),
        sort=[('_id', -1)]
    )

    my_blogs=[]
    if my_bl:
        for bl in my_bl:
            
            if bl.get("published_date") and type(bl.get("published_date")) == datetime.datetime:
                bl["published_date"] = bl["published_date"].date().isoformat()
            else:
                bl["published_date"] = "NA"

            
            bl["actions"] = dict(
                editor_url=request.state.current_host_url + "/editor?article=" + str(bl["_id"]),
                preview_url=request.state.current_host_url + "/editor/preview?article=" + str(bl["_id"])
            )
            del bl["_id"]
            my_blogs.append(bl)

    return templates.TemplateResponse(
        "components/editor.html", 
        await CommonMethods.prep_templates(
            request=request,
            title="Editor",
            hosts=hosts,
            article_doc=article_doc,
            preview_url=preview_url,
            my_blogs=my_blogs
        )
    )
