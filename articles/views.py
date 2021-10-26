from fastapi import APIRouter, Body, HTTPException, status, Header, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.encoders import jsonable_encoder
from common.utils import templates
from common.views import MongoInterface, PyObjectId
from common.db import collections
from config import Config
from datetime import datetime
from typing import Optional


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, previous_page: Optional[PyObjectId] = None, next_page: Optional[PyObjectId] = None):
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
        first_id=previous_page
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
                    article_text = article_text[:300] + ' ...'
                    break

            adata["article_text"] = article_text

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
        next_page=next_url,
        previous_page=prev_url
    )

    return templates.TemplateResponse("components/home.html", html_content)


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
    article = await MongoInterface().find_or_404(
        collection_name=collections["articles"],
        query=query,
        exclude=dict(
            _id=0,
            cd=0
        ),
        error_message="Article not found"
    )

    html_content = dict(
        request=request,
        site_header=request.state.current_host,
        title=article["title"],
        data=article["article_data"],
        tags=article["tags"]
    )
    return templates.TemplateResponse("components/article.html", html_content)
