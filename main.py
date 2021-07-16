from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import database
from news import newsRouter
from problem import probRouter
from submission import submRouter
from system import sysRouter
from user import userRouter

app = FastAPI()
app.include_router(sysRouter)
app.include_router(userRouter)
app.include_router(newsRouter)
app.include_router(probRouter)
app.include_router(submRouter)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.get("/")
# async def root():
#     con = database.pool.connection()
#     cur = con.cursor()
#     sql = "SELECT * FROM student;"
#     cur.execute(sql)
#     return {"message": cur.fetchall()}
#
#
# @app.get("/{id}/{name}")
# async def test(id, name):
#     con = database.pool.connection()
#     cur = con.cursor()
#     sql = "insert into student(id, name) VALUES({},'{}');".format(id, name)
#     try:
#         cur.execute(sql)
#         con.commit()
#         return {"hello": 0}
#     except:
#         con.rollback()
#         return {"hello": -1}


@app.on_event("startup")
async def startup():
    print("Connecting...")
    if database.pool is None:
        database.init_mysql()
    print("Successful.")


@app.on_event("shutdown")
async def shutdown():
    print("Closing...")
    database.pool.close()
    print("Successful.")


if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", reload=True)
