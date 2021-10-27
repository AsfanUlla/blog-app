from fastapi import APIRouter, Body, HTTPException, status, Depends
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from admin.models import AddUserSchema, UserLoginSchema, AddHostSchema
from common.models import SchemalessResponse, EmailSchema
from fastapi.encoders import jsonable_encoder
from common.views import MongoInterface
from common.utils import get_password_hash, verify_password, create_access_token, verify_token, templates
from datetime import timedelta, datetime
from common.db import collections
from starlette.requests import Request

router = APIRouter()


@router.get('/login', response_class=HTMLResponse)
async def login_page(request: Request):
    html_content = dict(
        request=request,
        site_header=request.state.current_host,
        title="Login"
    )
    return templates.TemplateResponse("components/login.html", html_content)


@router.post('/login', response_model=SchemalessResponse)
async def user_login(request: Request, login: UserLoginSchema):
    user = await MongoInterface.find_or_404(
        collections['users'],
        query=dict(
            email=login.user_email
        ),
        exclude=dict(
            passwd=1
        ),
        error_message="Illegal User"
    )
    if not verify_password(login.passwd, user['passwd']):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Password")
    user_token = await create_access_token(
        data=dict(
            user_id=str(user['_id'])
        ),
        expires_delta=timedelta(days=5)
    )

    request.session['token'] = user_token

    response = SchemalessResponse(
        data=dict(
            success=True
        ),
        message="user logged in"
    )
    return JSONResponse(jsonable_encoder(response))


@router.get('/logout', response_class=RedirectResponse, status_code=302)
async def user_logout(request: Request):
    request.session.clear()
    return str(request.base_url) + 'admin/login'
    

@router.post("/register", response_model=SchemalessResponse)
async def add_user(user: AddUserSchema, payload: dict = Depends(verify_token)):
    if not payload[0]["is_su_admin"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    user_doc = await MongoInterface.find_or_none(
        collections['users'],
        query=dict(
            email=user.email
        ), exclude=dict(
            _id=1
        )
    )
    if user_doc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exist")
    user.passwd = get_password_hash(user.passwd)
    post_obj = jsonable_encoder(user)
    user_add = await MongoInterface.insert_one(collections['users'], post_obj)
    response = SchemalessResponse(
        data=dict(
            success=True
        ),
        message="user created successfully"
    )
    return JSONResponse(jsonable_encoder(response))


@router.post("/add_host", response_model=SchemalessResponse)
async def add_host(_host: AddHostSchema, payload: dict = Depends(verify_token)):
    if not payload[0]["is_su_admin"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    _host.host = str(_host.host).strip("/")
    host_doc = await MongoInterface.find_or_none(
            collection_name=collections['hosts'],
            query=dict(
                host=_host.host
            ),
            exclude=dict(
                _id=1
            )
        )
    _host = jsonable_encoder(_host)
    if host_doc:
        update_host = await MongoInterface.update_doc(
            collection_name=collections["hosts"],
            query=dict(
                _id=host_doc["_id"]
            ),
            update_data=_host,
            q_type='set'
        )
        message = "Host updated"
    else:
        add_host = await MongoInterface.insert_one(
            collection_name=collections["hosts"],
            post_obj=_host
        )
        message = "Host added"
    response = SchemalessResponse(
        data=dict(
            success=True
        ),
        message=message
    )
    return JSONResponse(jsonable_encoder(response))


@router.get("", response_class=HTMLResponse)
async def admin(request: Request, payload: dict = Depends(verify_token)):
    if not payload[0]["is_su_admin"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    users = await MongoInterface.find_all(
        collection_name=collections['users'],
        exclude=dict(
            passwd=0
        )
    )

    hosts = await MongoInterface.find_all(
        collection_name=collections["hosts"]
    )

    html_content = dict(
        request=request,
        site_header=request.state.current_host,
        title="Admin",
        users=users,
        hosts=hosts
    )
    return templates.TemplateResponse("components/admin.html", html_content)

"""@router.get('/user_verification', response_model=SchemalessResponse)
async def user_verify(verify_user: str):
    user, payload = await verify_token(verify_user, key=Config.JWT_EMAIL_SECRET)
    update_doc = await MongoInterface.update_doc(
        collection_name=collections['users'],
        query=dict(
            _id=ObjectId(payload.get("user_id"))
        ),
        update_data=dict(
            disabled=False,
            is_verified=True,
        ),
        q_type="set"
    )

    response = SchemalessResponse(
        data=dict(
            login_link=Config.HOST_URL+"users/login",
            success=True
        ),
        message="User Verified"
    )

    return JSONResponse(jsonable_encoder(response))"""
