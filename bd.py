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
        cur.execute("SELECT EXISTS (SELECT * FROM users WHERE tg_id = '{}')".format(str(user_id)))
        return cur.fetchone()[0]
    except Exception:
        conn.rollback()
        print('rlbk user_exists')


async def add_user(user_id, name):
    try:
        cur.execute("SELECT MAX(id) FROM users")
        id = cur.fetchone()
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


async def activate(user_id):
    try:
        cur.execute(
            "SELECT a.id FROM users as a, users_info as b WHERE a.tg_id = '{}'".format(str(user_id)))
        id = cur.fetchone()
        cur.execute(
            "UPDATE users_info "
            "SET activate = '1'"
            "WHERE user_id = '{}'".format(id[0], ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print('rlbk activate' + str(e))


async def chek_activate(user_id):
    try:
        cur.execute(
            "SELECT a.id FROM users as a WHERE a.tg_id = '{}'".format(str(user_id)))
        id = cur.fetchone()
        if id[0] != None:
            cur.execute("SELECT activate FROM users_info WHERE user_id = '{}'".format(id[0]))
            activ = cur.fetchone()
            activat = int(activ[0])
            print(activat)
            return activat

    except Exception as e:
        conn.rollback()
        print('rlbk chek activate' + str(e))

async def add_user_info(user_id):
    try:
        cur.execute(
            "SELECT a.id FROM users as a WHERE a.tg_id = '{}'".format(str(user_id)))
        id = cur.fetchone()
        print(id)
        cur.execute(
            "INSERT INTO users_info (user_id, activate) VALUES ('{}','{}')".format(id[0], 0,))
        conn.commit()


    except Exception as e:
        conn.rollback()
        print('rlbk add user inf' + str(e))

async def sub(user_id):
    try:
        cur.execute(
            "SELECT a.id FROM users as a WHERE a.tg_id = '{}'".format(str(user_id)))
        id = cur.fetchone()
        cur.execute(
            "UPDATE users_info "
            "SET activate = '2'"
            "WHERE user_id = '{}'".format(id[0], ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print('rlbk sub' + str(e))

async def sub_unable(user_id):
    try:
        cur.execute(
            "SELECT a.id FROM users as a WHERE a.tg_id = '{}'".format(str(user_id)))
        id = cur.fetchone()
        cur.execute(
            "UPDATE users_info "
            "SET activate = '1'"
            "WHERE user_id = '{}'".format(id[0], ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print('rlbk sub' + str(e))

async def get_moves(btn,num):
    cur.execute(
        "SELECT moves FROM messages WHERE position('{}' in buttons) > 0".format(
            btn))
    moves = cur.fetchone()[0]
    # print(moves)
    msgs = (str(moves).split("/\\"))
    msg = (msgs[int(num)].strip())
    return msg
    # moves = str(*moves).split("/\\")
    # print(moves[int(num)])