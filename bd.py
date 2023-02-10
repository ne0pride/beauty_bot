import psycopg2
import requests
import asyncio
import datetime
from config_reader import config

conn = psycopg2.connect(dbname=config.db_name.get_secret_value(), user=config.db_user.get_secret_value(),
                        password=config.db_password.get_secret_value(), host=config.db_host.get_secret_value())
cur = conn.cursor()


async def user_exists(user_id):
    try:
        """Проверяем, есть ли юзер в базе"""
        cur.execute("SELECT EXISTS (SELECT * FROM users WHERE tg_id = '{}')".format(user_id))
        return cur.fetchone()[0]
    except Exception:
        conn.rollback()
        print('rlbk user_exists')

async def add_user(user_id, name):
    try:
        cur.execute("SELECT MAX(id) FROM users")
        id = cur.fetchone()
        print(id[0])
        if id[0] == None:
            id = 0
        else:
            id = id[0] + 1
        cur.execute(
            "INSERT INTO users (id,tg_id,name) VALUES ('{}','{}','{}')".format(id, str(user_id), name, ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print('rlbk add_user' + str(e))