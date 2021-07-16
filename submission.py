import json
from typing import Dict, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from pymysql.cursors import Cursor

import database
import utils

submRouter = APIRouter(tags=["提交相关"])


class SubmitCodeData(BaseModel):
    valid: int
    problemId: str
    language: str
    inDate: str
    code: str


@submRouter.post("/zzuoj-submission/submission/submit", name="提交代码")
async def submitcode(
        data: SubmitCodeData,
        token_data: Dict = Depends(utils.check_jwt_token)
):
    now = utils.gettime()
    username = json.loads(token_data["sub"])["username"]
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    try:
        print(data.problemId, username, data.code, now, data.language)
        print("INSERT INTO subm_submission(probid, username, code, submittime, langid) "
              "VALUES(%s,%s,%s,%s,%s)" %
              (data.problemId, username, data.code, now, data.language))
        cur.execute(
            "INSERT INTO subm_submission(probid, username, code, submittime, langid) "
            "VALUES(%s,%s,%s,%s,%s)",
            (data.problemId, username, data.code, now, data.language)
        )

        con.commit()
        return {"code": 1, "data": "提交成功"}
    except:
        return {"code": -1, "msg": "sql error"}


# async def submitcnt():
#     con = database.pool.connection()
#     cur: Cursor = con.cursor()
#     cur.execute(
#         "SELECT count(*) FROM subm_submission"
#     )
#     result = cur.fetchall()
#     return {"code": 1, "data": result[0][0]}


@submRouter.get("/zzuoj-submission/submission/cnt", name="提交数量查询")
async def submitcnt(
        pos: int = 0,
        limit: int = 8,
        uid: Optional[str] = Query("", max_length=20, regex="^[A-Za-z0-9]*$"),
        pid: Optional[str] = Query("", max_length=10, regex="^[0-9]*$"),
        langid: Optional[str] = Query("", max_length=10, regex="^[0-9]*$")
):
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    sql = "SELECT COUNT(*) \
    FROM subm_submission WHERE TRUE "
    if pid != "":
        sql = sql + "AND prob_problem.id = %s " % pid
    if uid != "":
        sql = sql + "AND username = '%s' " % uid
    if langid != "":
        sql = sql + "AND langid = %s " % langid
    sql = sql + "ORDER BY id DESC LIMIT %s OFFSET %s"
    cur.execute(sql, (limit, pos))
    result = cur.fetchall()
    return {"code": 1, "data": result[0][0]}


@submRouter.get("/zzuoj-submission/submission/show", name="提交列表查询")
async def submitlist(
        pos: int,
        limit: int,
        uid: Optional[str] = Query("", max_length=20, regex="^[A-Za-z0-9]*$"),
        pid: Optional[str] = Query("", max_length=10, regex="^[0-9]*$"),
        langid: Optional[str] = Query("", max_length=10, regex="^[0-9]*$")
):
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    sql = "SELECT subm_submission.id, title, username, submittime, status, lang, timeuse, memuse \
    FROM subm_submission,sys_status,sys_language,prob_problem \
    WHERE subm_submission.langid=sys_language.id \
    AND subm_submission.statusid=sys_status.id \
    AND subm_submission.probid=prob_problem.id "
    if pid != "":
        sql = sql + "AND prob_problem.id = %s " % pid
    if uid != "":
        sql = sql + "AND username = '%s' " % uid
    if langid != "":
        sql = sql + "AND langid = %s " % langid
    sql = sql + "ORDER BY id DESC LIMIT %s OFFSET %s"
    cur.execute(sql, (limit, pos))
    result = cur.fetchall()
    if len(result):
        return {"code": 1, "data": result}
    else:
        return {"code": -1, "msg": "404"}
