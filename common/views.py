from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status, Request, Response, Depends
from datetime import datetime
from bson import ObjectId, objectid
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from config import Config
from common.db import collections, get_db
from motor.motor_asyncio import AsyncIOMotorDatabase


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return str(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class MongoInterface:

    @staticmethod
    async def insert_one(collection_name, post_obj, exist_query=None, error_message="DOC exists"):
        db = await get_db()
        if exist_query:
            doc_exist = await db[collection_name].find_one(exist_query, {"_id": 1})
            if doc_exist:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error_message)
        post_obj = jsonable_encoder(post_obj)
        post_obj['cd'] = datetime.utcnow()
        doc = await db[collection_name].insert_one(post_obj)
        # doc = await db[collection_name].find_one({"_id": doc.inserted_id})
        return str(doc.inserted_id)

    @staticmethod
    async def find_or_404(collection_name, query, exclude=None, error_message="Item Not Found"):
        db = await get_db()
        doc = await db[collection_name].find_one(query, exclude)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
        return doc

    @staticmethod
    async def find_or_none(collection_name, query, exclude=None, sort=None):
        db = await get_db()
        if sort:
            return await db[collection_name].find_one(query, exclude, sort=sort)
        return await db[collection_name].find_one(query, exclude)

    @staticmethod
    async def find_all(collection_name, query=None, exclude=None, sort=None, list=1000):
        db = await get_db()
        document = []
        if query is None:
            query = {}
        if exclude is None:
            exclude = {}
        exclude.update(dict(
            cd=False
        ))
        if sort:
            doc = await db[collection_name].find(query, exclude, sort=sort).to_list(list)
        else:
            doc = await db[collection_name].find(query, exclude).to_list(list)
        for d in doc:
            for key, item in d.items():
                if type(item) == ObjectId:
                    d[key] = str(item)
            document.append(d)
        return document

    @staticmethod
    async def bulk_update(**kwargs):
        db = await get_db()
        try:
            if kwargs.get("q_type") == "set":
                await db[kwargs.get("collection_name")].bulk_write(
                    [
                        UpdateOne(
                            {
                                '_id': ObjectId(key)
                            },
                            {
                                '$set': values
                            },
                            upsert=True
                        ) for key, values in kwargs.get("data").items()
                    ]
                )
            elif kwargs.get("q_type") == "push":
                await db[kwargs.get("collection_name")].bulk_write(
                    [
                        UpdateOne(
                            {
                                '_id': ObjectId(key)
                            },
                            {
                                '$push': values
                            },
                            upsert=True
                        ) for key, values in kwargs.get("data").items()
                    ]
                )
            else:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid query type")
        except BulkWriteError as bwe:
            raise HTTPException(status_code=bwe.code, detail=str(bwe.details))
        return True

    @staticmethod
    async def update_doc(**kwargs):
        db = await get_db()
        if kwargs.get("q_type") == 'push':
            return await db[kwargs.get("collection_name")].update_one(
                kwargs.get("query"),
                {"$push": kwargs.get("update_data")},
                upsert=True
            )
        elif kwargs.get("q_type") == 'set':
            return await db[kwargs.get("collection_name")].update_one(
                kwargs.get("query"),
                {"$set": kwargs.get("update_data")},
                upsert=True
            )
        else:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid query type")

    @staticmethod
    async def id_pagination(collection_name, query=None, exclude=None, page_size=10, last_id=None, first_id=None):
        db = await get_db()
        if query is None:
            query = {}
        if exclude is None:
            exclude = {}
        exclude.update(dict(
            cd=False
        ))

        sort = [('_id', -1)]

        if objectid.ObjectId.is_valid(first_id):
            queryf = query.copy()
            queryf.update(
                {'_id': {'$gt': ObjectId(first_id)}}
            )
            data = await db[collection_name].find(queryf, exclude, sort=sort).limit(page_size).to_list(page_size)
        elif objectid.ObjectId.is_valid(last_id):
            queryl = query.copy()
            queryl.update(
                {'_id': {'$lt': ObjectId(last_id)}}
            )
            data = await db[collection_name].find(queryl, exclude, sort=sort).limit(page_size).to_list(page_size)
        else:
            data = await db[collection_name].find(query, exclude, sort=sort).limit(page_size).to_list(page_size)

        if not data:
            lt = await db[collection_name].find(query, exclude, sort=sort).limit(page_size).to_list(page_size)
            return lt, None, None

        last_id = data[-1]['_id']
        first_id = data[0]['_id']
        
        return data, first_id, last_id


class RediectException(Exception):
    def __init__(self, path: str, status_code: int):
        self.path = path
        self.status_code = status_code


async def redirect(request: Request, exc: RediectException):
    return RedirectResponse(url=exc.path, status_code=exc.status_code)


"""class CurrentHost(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request.state.current_host = request.base_url.hostname.capitalize()
        request.state.current_host_url = str(request.base_url).strip("/")
        if Config().ENV != "LOCAL":
            MongoInterface.find_or_404(
                collection_name=collections["hosts"], 
                query=dict(
                    host=request.state.current_host_url
                ),
                exclude=dict(
                    _id=1
                ),
                error_message="Unallowed host"
            )
        return await call_next(request)"""

class CurrentHost(BaseHTTPMiddleware):
    async def __call__(self, scope, receive, send) -> None:
        request = Request(scope, receive)
        request.state.current_host = request.base_url.hostname.capitalize()
        request.state.current_host_url = str(request.base_url).strip("/")
        if Config().ENV != "LOCAL":
            await MongoInterface.find_or_404(
                collection_name=collections["hosts"], 
                query=dict(
                    host=request.state.current_host_url
                ),
                exclude=dict(
                    _id=1
                ),
                error_message="Unallowed host"
            )
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        await self.app(scope, receive, send)
