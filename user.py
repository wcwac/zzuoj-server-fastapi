import json
from typing import Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from pymysql.cursors import Cursor

import database
import utils

userRouter = APIRouter(tags=["用户相关"])


class RegData(BaseModel):
    email: str
    password: str
    school: str
    userId: str
    username: str


class LoginData(BaseModel):
    password: str
    username: str


class UpdateData(BaseModel):
    level: int
    enable: int
    email: str
    number: str
    username: str


@userRouter.post("/zzuoj-user/user/login", name="登录")
async def login(data: LoginData):
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    cur.execute(
        "SELECT username,level,editnews,edituser,editgroup,editprob "
        "FROM user_user,sys_usergroup WHERE username = %s AND password = %s"
        , (data.username, utils.saltMD5(data.password)))
    result = cur.fetchall()
    if len(result) != 0:
        jwtdata = {"username": result[0][0], "role": result[0][1], "newsAdmin": result[0][2],
                   "userAdmin": result[0][3], "groupAdmin": result[0][4], "probAdmin": result[0][5]}
        cur.execute(
            "UPDATE user_user SET logintime = %s WHERE username = %s"
            , (utils.gettime(), data.username))
        con.commit()
        return {"code": 1, "data": utils.createjwt(jwtdata)}
        # return {"code": 1, "msg": {result[0][0]}}
    else:
        return {"code": -1, "msg": "错误的用户名或密码"}


@userRouter.post("/zzuoj-user/user/registry", name="注册")
async def signin(data: RegData):
    now = utils.gettime()
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    try:
        cur.execute(
            "INSERT INTO user_user(username, password, name, regtime, logintime, school, number, email, level) "
            "VALUES(%s,%s,'',%s,%s,%s,%s,%s,0)",
            (data.username, utils.saltMD5(data.password), now,
             now, data.school, data.userId, data.email)
        )
        con.commit()
        return {"code": 1, "data": "注册成功"}
    except:
        con.rollback()
        return {"code": -1, "msg": "注册失败"}


@userRouter.get("/zzuoj-user/user/get", name="用户信息查询")
async def userdetail(username: str):
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    cur.execute(
        "SELECT username,number,email,school,regtime FROM user_user WHERE username = %s",
        username
    )
    result = cur.fetchall()
    if len(result) > 0:
        return {"code": 1, "data": {
            "username": result[0][0],
            "userId": result[0][1],
            "email": result[0][2],
            "school": result[0][3],
            "regTime": result[0][4],
            "submit": 0,
            "solved": 0
        }}
    return {"code": -1, "msg": "查询失败"}


@userRouter.get("/zzuoj-user/admin/user/cnt", name="用户数量查询")
async def probcntadmin(
        token_data: Dict = Depends(utils.check_jwt_token)
):
    if json.loads(token_data["sub"])["role"] == 0:
        return {"code": -1, "msg": "403"}
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    cur.execute(
        "SELECT count(*) FROM user_user"
    )
    result = cur.fetchall()
    return {"code": 1, "data": result[0][0]}


@userRouter.get("/zzuoj-user/admin/user/show", name="用户列表查询")
async def problistadmin(
        pos: int = 1, limit: int = 8,
        search: str = '',
        token_data: Dict = Depends(utils.check_jwt_token)
):
    if json.loads(token_data["sub"])["role"] == 0:
        return {"code": -1, "msg": "403"}
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    cur.execute(
        "SELECT username, number, email, enable, level FROM user_user "
        "WHERE username LIKE %s ORDER BY number LIMIT %s OFFSET %s",
        ('%' + search + '%', limit, pos - 1)
    )
    result = cur.fetchall()
    return {"code": 1, "data": result}


@userRouter.post("/zzuoj-user/admin/user/update", name="用户信息修改")
async def updateuser(data: UpdateData):
    now = utils.gettime()
    con = database.pool.connection()
    cur: Cursor = con.cursor()
    try:
        cur.execute(
            "UPDATE user_user SET number = %s,email = %s, enable = %s, level = %s "
            "WHERE username = %s",
            (data.number, data.email, data.enable, data.level, data.username)
        )
        con.commit()
        return {"code": 1, "data": "修改成功"}
    except:
        con.rollback()
        return {"code": -1, "msg": "修改失败"}
