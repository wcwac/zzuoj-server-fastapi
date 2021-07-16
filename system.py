from fastapi import APIRouter
from pymysql.cursors import Cursor

import database

sysRouter = APIRouter(tags=["系统相关"])


@sysRouter.get("/zzuoj-system/languages/get", name="支持语言查询")
async def getlang():
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    cur.execute(
        "SELECT id,lang FROM sys_language"
    )
    result = cur.fetchall()
    return {"code": 1, "data": result}


@sysRouter.get("/zzuoj-file/help/get", name="帮助信息查询")
async def getlang():
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    cur.execute(
        "SELECT title,content FROM sys_help ORDER BY id DESC LIMIT 1"
    )
    result = cur.fetchall()
    if len(result):
        return {"code": 1, "data": result[0]}
    else:
        return {"code": -1, "msg": "404"}


@sysRouter.get("/zzuoj-file/help/get", name="帮助信息查询")
async def getlang():
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    cur.execute(
        "SELECT title,content FROM sys_help ORDER BY id DESC LIMIT 1"
    )
    result = cur.fetchall()
    if len(result):
        return {"code": 1, "data": result[0]}
    else:
        return {"code": -1, "msg": "404"}
