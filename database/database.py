import os
from dotenv import load_dotenv
import pymysql, pymysql.cursors


class Database:
    def __init__(self, sql: str | None = None):
        load_dotenv()
        self.conn = pymysql.connect(
            host=os.environ.get("HOST"),
            user=os.environ.get("USER"),
            password=os.environ.get("DATABASE_PASSWORD"),
            db=os.environ.get("DB_NAME"),
            charset="utf8",
        )
        self.cur = self.conn.cursor(pymysql.cursors.DictCursor)
        self.sql = sql

    def __del__(self):
        self.conn.commit()
        self.conn.close()

    def execute(self, sql: str | None = None, params: tuple | None = None):
        if sql == None:
            sql = self.sql
        self.cur.execute(sql, params)
        return self.cur.fetchall()
