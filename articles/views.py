from fastapi import APIRouter, Body, HTTPException, status, Header, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.encoders import jsonable_encoder
from common.utils import templates, strip_tags, recent_articles
from common.views import MongoInterface, PyObjectId
from common.db import collections
from config import Config
from datetime import datetime
from typing import Optional
from bson import ObjectId


router = APIRouter()


@router.get("/about", response_class=HTMLResponse)
async def about_contact(request: Request):
    html_content = dict(
        request=request,
        site_header=request.state.current_host,
        title="About/Contact",
        page_desc="Latest technology blogs for beginners and learners"
    )

    return templates.TemplateResponse("components/about.html", html_content)


@router.get("/", response_class=HTMLResponse)
async def all_blogs(
    request: Request, 
    previous_page: Optional[PyObjectId] = None, 
    next_page: Optional[PyObjectId] = None, 
    search: Optional[str] = None
):

    query = dict(
        is_suspended=False,
        published=True
    )
    if Config.ENV != 'LOCAL':
        query["hosts"] = request.state.current_host_url

    articles_doc, first_id, last_id = await MongoInterface.id_pagination(
        collection_name=collections["articles"],
        query=query,
        last_id=next_page,
        first_id=previous_page,
        page_size=9,
        search=search
    )
    
    articles = []
    if articles_doc:
        for article in articles_doc:
            if article["published_date"]:
                published_date = article["published_date"].date().isoformat()

            adata = dict(
                title=article["title"],
                published_date=published_date,
                article_url=request.state.current_host_url + "/" + article["slug"],
                tags=article["tags"]
            )

            article_text = ""

            for block in article["article_data"]["blocks"]:
                if block["type"] == "paragraph":
                    article_text = block["data"]["text"]
                    article_text = article_text[:400] + ' ...'
                    break

            adata["article_text"] = article_text

            """if article["author_id"]:
                author = await MongoInterface.find_or_none(
                    collection_name=collections["users"],
                    query=dict(
                        _id=ObjectId(article["author_id"])
                    ),
                    exclude=dict(
                        full_name=1,
                        email=1,
                        avatar=1,
                        about=1
                    )
                )
                if author:
                    if not author.get("avatar"):
                        author["avatar"] = request.state.current_host_url+"/static/assets/img/default_avatar.jpg"
                    if not author.get("about"):
                        author["about"] = "shy"
                    adata.update(author)"""

            articles.append(adata)

    next_url = None
    prev_url = None

    if last_id:
        next_url = request.state.current_host_url + "?next_page=" + str(last_id)

    if first_id:
        prev_url =  request.state.current_host_url + "?previous_page=" + str(first_id)

    html_content = dict(
        request=request,
        site_header=request.state.current_host,
        title=request.state.current_host,
        articles=articles,
        recent_articles=await recent_articles(request),
        next_page=next_url,
        previous_page=prev_url,
        page_desc="Latest technology blogs for beginners and learners"
    )

    return templates.TemplateResponse("components/home.html", html_content)


"""@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    query = dict(
        is_suspended=False,
        published=True,
        featured=True
    )
    if Config.ENV != 'LOCAL':
        query["hosts"] = request.state.current_host_url
    featured_article = await MongoInterface.find_all(
        collection_name=collections["articles"],
        query=query,
        sort=[('_id', -1)],
        list=3
    )

    if not featured_article:
        del query['featured']
        featured_article = await MongoInterface.find_all(
            collection_name=collections["articles"],
            query=query,
            sort=[('_id', -1)],
            list=3
        )

    articles = []
    if featured_article:
        for article in featured_article:
            if article["published_date"]:
                published_date = str(article["published_date"].date().isoformat()).replace('-', '.')

            adata = dict(
                title=article["title"],
                published_date=published_date,
                article_url=request.state.current_host_url + "/" + article["slug"],
                tags=article["tags"]
            )

            article_text = ""

            for block in article["article_data"]["blocks"]:
                if block["type"] == "paragraph":
                    article_text = block["data"]["text"]
                    article_text = article_text[:240] + ' ...'
                    break

            adata["article_text"] = strip_tags(article_text)

            if article["author_id"]:
                author = await MongoInterface.find_or_none(
                    collection_name=collections["users"],
                    query=dict(
                        _id=ObjectId(article["author_id"])
                    ),
                    exclude=dict(
                        full_name=1,
                        email=1,
                        avatar=1,
                        about=1
                    )
                )
                if author:
                    if not author.get("avatar"):
                        author["avatar"] = request.state.current_host_url+"/static/assets/img/default_avatar.jpg"
                    if not author.get("about"):
                        author["about"] = "shy"
                    adata.update(author)
            
            articles.append(adata)

    html_content = dict(
        request=request,
        site_header=request.state.current_host,
        title=request.state.current_host,
        page_desc="Latest technology blogs for beginners and learners",
        featured=articles
    )
    return templates.TemplateResponse("components/home.html", html_content)"""


@router.get("/{article_slug}", response_class=HTMLResponse)
async def article(article_slug, request: Request):
    article_slug = str(article_slug)
    query = dict(
        slug=article_slug,
        is_suspended=False,
        published=True
        )
    if Config.ENV != 'LOCAL':
        query["hosts"] = request.state.current_host_url
    article = await MongoInterface.find_or_404(
        collection_name=collections["articles"],
        query=query,
        exclude=dict(
            _id=0,
            cd=0
        ),
        error_message="Article not found"
    )

    author = None
    """if article.get("author_id"):
        author = await MongoInterface.find_or_none(
            collection_name=collections["users"],
            query=dict(
                _id=ObjectId(article["author_id"])
            ),
            exclude=dict(
                full_name=1,
                email=1,
                avatar=1,
                about=1
            )
        )
        if author:
            if not author.get("avatar"):
                author["avatar"] = request.state.current_host_url+"/static/assets/img/default_avatar.jpg"
            if not author.get("about"):
                author["about"] = "shy" """

    html_content = dict(
        request=request,
        site_header=request.state.current_host,
        title=article["title"],
        data=article["article_data"],
        tags=article["tags"],
        author=author,
        recent_articles=await recent_articles(request),
    )
    return templates.TemplateResponse("components/article.html", html_content)
