import json
from typing import Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from pymysql.cursors import Cursor

import database
import utils

newsRouter = APIRouter(tags=["公告相关"])


class UpdateNewsData(BaseModel):
    newsid: int
    title: str
    content: str


class CreateNewsData(BaseModel):
    title: str
    content: str


@newsRouter.get("/zzuoj-file/news/cnt", name="公告数量查询")
async def newscnt():
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    cur.execute(
        "SELECT count(*) FROM news_news"
    )
    result = cur.fetchall()
    return {"code": 1, "data": result[0][0]}


@newsRouter.get("/zzuoj-file/news/show", name="公告列表查询")
async def newslist(pos: int, limit: int):
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    cur.execute(
        "SELECT id, title, author, time FROM news_news "
        "ORDER BY id DESC LIMIT %s OFFSET %s ",
        (limit, pos)
    )
    result = cur.fetchall()
    return {"code": 1, "data": result}


@newsRouter.get("/zzuoj-file/news/get", name="公告详情查询")
async def newsdetail(id: int):
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    cur.execute(
        "SELECT title,content FROM news_news WHERE id = %s",
        id
    )
    result = cur.fetchall()
    if len(result):
        return {"code": 1, "data": result[0]}
    else:
        return {"code": -1, "msg": "404"}


@newsRouter.post("/zzuoj-file/admin/news/update", name="公告更新")
async def newsupdate(
        data: UpdateNewsData,
        token_data: Dict = Depends(utils.check_jwt_token)
):
    role = json.loads(token_data["sub"])["role"]
    if role == 0:
        return {"code": -1, "msg": "未授权"}
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    try:
        cur.execute(
            "UPDATE news_news SET title=%s,content=%s WHERE id=%s",
            (data.title, data.content, data.newsid)
        )
        con.commit()
        return {"code": 1, "data": "修改成功"}
    except:
        con.rollback()
        return {"code": -1, "msg": "失败"}


@newsRouter.post("/zzuoj-file/admin/news/add", name="创建新公告")
async def newscreate(
        data: CreateNewsData,
        token_data: Dict = Depends(utils.check_jwt_token)
):
    now = utils.gettime()
    role = json.loads(token_data["sub"])["role"]
    username = json.loads(token_data["sub"])["username"]
    if role == 0:
        return {"code": -1, "msg": "未授权"}
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    try:
        cur.execute(
            "INSERT INTO news_news(title,content, author, time) VALUES (%s,%s,%s,%s)",
            (data.title, data.content, username, now)
        )
        con.commit()
        return {"code": 1, "data": "修改成功"}
    except Exception as e:
        con.rollback()
        print(e)
        return {"code": -1, "msg": "失败"}


@newsRouter.get("/zzuoj-file/admin/news/delete", name="公告删除")
async def probdataadmin(
        id: int,
        token_data: Dict = Depends(utils.check_jwt_token)
):
    if json.loads(token_data["sub"])["role"] == 0:
        return {"code": -1, "msg": "403"}
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    try:

        cur.execute(
            "DELETE FROM news_news WHERE id = %s",
            id
        )
        con.commit()
        return {"code": 1, "data": "删除成功"}
    except:
        con.rollback()
        return {"code": 1, "data": "删除失败"}
