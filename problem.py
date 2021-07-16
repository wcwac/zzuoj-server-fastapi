import json
from typing import Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from pymysql.cursors import Cursor

import database
import utils

probRouter = APIRouter(tags=["题目相关"])


class UpdateProblemData(BaseModel):
    id: int
    title: str
    content: str
    input: str
    output: str
    enable: str


class CreateProblemData(BaseModel):
    title: str
    content: str
    input: str
    output: str
    enable: str


@probRouter.get("/zzuoj-problem/problem/cnt", name="题目数量查询")
async def probcnt():
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    cur.execute(
        "SELECT count(*) FROM prob_problem WHERE enable = 1"
    )
    result = cur.fetchall()
    return {"code": 1, "data": result[0][0]}


@probRouter.get("/zzuoj-problem/admin/problem/cnt", name="题目数量查询(包含隐藏题目)")
async def probcntadmin(
        token_data: Dict = Depends(utils.check_jwt_token)
):
    if json.loads(token_data["sub"])["role"] == 0:
        return {"code": -1, "msg": "403"}
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    cur.execute(
        "SELECT count(*) FROM prob_problem"
    )
    result = cur.fetchall()
    return {"code": 1, "data": result[0][0]}


@probRouter.get("/zzuoj-problem/problem/show", name="题目列表查询")
async def problist(pos: int, limit: int):
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    cur.execute(
        "SELECT id, title, ac_count, all_count FROM prob_problem "
        "WHERE enable = 1 ORDER BY id LIMIT %s OFFSET %s",
        (limit, pos)
    )
    result = cur.fetchall()
    return {"code": 1, "data": result}


@probRouter.get("/zzuoj-problem/admin/problem/show", name="题目列表查询(包含隐藏题目)")
async def problistadmin(
        pos: int, limit: int,
        token_data: Dict = Depends(utils.check_jwt_token)
):
    if json.loads(token_data["sub"])["role"] == 0:
        return {"code": -1, "msg": "403"}
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    cur.execute(
        "SELECT id, title, ac_count, all_count, enable FROM prob_problem "
        "ORDER BY id LIMIT %s OFFSET %s",
        (limit, pos)
    )
    result = cur.fetchall()
    return {"code": 1, "data": result}


@probRouter.get("/zzuoj-problem/problem/get", name="题目信息查询")
async def probdetail(pid: int):
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    cur.execute(
        "SELECT title, content, input, output FROM prob_problem "
        "WHERE id = %s AND enable = 1",
        pid
    )
    result = cur.fetchall()
    if len(result):
        return {"code": 1, "data": result[0]}
    else:
        return {"code": -1, "msg": "404"}


@probRouter.get("/zzuoj-problem/admin/problem/get", name="题目信息查询(包含隐藏)")
async def probdetailadmin(
        pid: int,
        token_data: Dict = Depends(utils.check_jwt_token)
):
    if json.loads(token_data["sub"])["role"] == 0:
        return {"code": -1, "msg": "403"}
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    cur.execute(
        "SELECT title, content, input, output, enable FROM prob_problem "
        "WHERE id = %s",
        pid
    )
    result = cur.fetchall()
    if len(result):
        return {"code": 1, "data": result[0]}
    else:
        return {"code": -1, "msg": "404"}


@probRouter.get("/zzuoj-problem/problem/data", name="题目样例查询")
async def probdata(pid: int):
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    cur.execute(
        "SELECT input, output FROM prob_data "
        "WHERE probid = %s AND visible = 1 ORDER BY dataid",
        pid
    )
    result = cur.fetchall()
    return {"code": 1, "data": result}


@probRouter.get("/zzuoj-problem/admin/problem/data", name="题目样例查询(包含隐藏)")
async def probdataadmin(
        pid: int,
        token_data: Dict = Depends(utils.check_jwt_token)
):
    if json.loads(token_data["sub"])["role"] == 0:
        return {"code": -1, "msg": "403"}
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    cur.execute(
        "SELECT input, output, visible FROM prob_data "
        "WHERE probid = %s ORDER BY dataid",
        pid
    )
    result = cur.fetchall()
    return {"code": 1, "data": result}


@probRouter.post("/zzuoj-problem/admin/problem/update", name="题目修改")
async def probupdate(
        data: UpdateProblemData,
        token_data: Dict = Depends(utils.check_jwt_token)
):
    if json.loads(token_data["sub"])["role"] == 0:
        return {"code": -1, "msg": "403"}
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    try:
        cur.execute(
            "UPDATE prob_problem SET title = %s, content = %s, input = %s, output = %s, enable = %s "
            "WHERE id = %s",
            (data.title, data.content, data.input, data.output, data.enable, data.id)
        )
        con.commit()
        return {"code": 1, "data": "执行成功"}
    except:
        return {"code": -1, "msg": "执行失败"}


@probRouter.post("/zzuoj-problem/admin/problem/add", name="题目添加")
async def procreate(
        data: CreateProblemData,
        token_data: Dict = Depends(utils.check_jwt_token)
):
    if json.loads(token_data["sub"])["role"] == 0:
        return {"code": -1, "msg": "403"}
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    try:
        cur.execute(
            "INSERT INTO prob_problem(title, content, input, output, enable) "
            "VALUES (%s, %s, %s, %s, %s) ",
            (data.title, data.content, data.input, data.output, data.enable)
        )
        con.commit()
        return {"code": 1, "data": "执行成功"}
    except:
        return {"code": -1, "msg": "执行失败"}


@probRouter.get("/zzuoj-problem/admin/problem/delete", name="题目删除")
async def probdataadmin(
        problemId: int,
        token_data: Dict = Depends(utils.check_jwt_token)
):
    if json.loads(token_data["sub"])["role"] == 0:
        return {"code": -1, "msg": "403"}
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    try:
        cur.execute(
            "DELETE FROM prob_problem WHERE id = %s",
            problemId
        )
        con.commit()
        return {"code": 1, "data": "删除成功"}
    except:
        con.rollback()
        return {"code": 1, "data": "删除失败"}
