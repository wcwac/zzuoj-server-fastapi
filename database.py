import pymysql
from dbutils.pooled_db import PooledDB

pool: PooledDB

pool = None


def init_mysql():
    global pool
    pool = PooledDB(
        pymysql,
        maxconnections=50,
        host='localhost',
        user='root',
        port=3306,
        passwd='yY139411.',
        db='mydb',
        use_unicode=True)
