from fastapi import APIRouter, Body, HTTPException, status, Header, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.encoders import jsonable_encoder
from common.utils import templates, strip_tags
from common.views import MongoInterface, PyObjectId, CommonMethods
from common.db import collections
from config import Config
from datetime import datetime
from typing import Optional
from bson import ObjectId


router = APIRouter()


@router.get("/about", response_class=HTMLResponse)
async def about_contact(request: Request):
    return templates.TemplateResponse(
        "components/about.html", 
        await CommonMethods.prep_templates(
            request=request,
            title="About/Contact",
            site_about=Config.SITE_ABOUT.get(request.state.site_name, Config.defaults["about"])
        )
    )


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
        query["hosts"] = request.state.current_domain

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

    return templates.TemplateResponse(
        "components/home.html", 
        await CommonMethods.prep_templates(
            request=request,
            articles=articles,
            recent_articles=await CommonMethods.recent_articles(request),
            next_page=next_url,
            previous_page=prev_url
        )
    )


@router.get("/{article_slug}", response_class=HTMLResponse)
async def article(article_slug, request: Request):
    article_slug = str(article_slug)
    query = dict(
        slug=article_slug,
        is_suspended=False,
        published=True
        )
    if Config.ENV != 'LOCAL':
        query["hosts"] = request.state.current_domain
    article = await MongoInterface.find_or_404(
        collection_name=collections["articles"],
        query=query,
        exclude=dict(
            _id=0,
            cd=0
        ),
        error_message="Article not found"
    )

    published_date = None
    if article.get("published_date"):
        published_date = article["published_date"].date().isoformat()

    author = None
    if article.get("author_id"):
        author = await MongoInterface.find_or_none(
            collection_name=collections["users"],
            query=dict(
                _id=ObjectId(article["author_id"])
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
            title=article["title"],
            data=article["article_data"],
            page_keywords=article["tags"],
            tags=article["tags"],
            author=author,
            published_date=published_date,
            recent_articles=await CommonMethods.recent_articles(request)
        )
    )
