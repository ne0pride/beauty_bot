import asyncio
import aioschedule as schedule
import time
import psycopg2
from aiogram.types import InputFile, InputMedia
import datetime
import requests
import csv
import json
from config_reader import config

conn = psycopg2.connect(dbname=config.db_name.get_secret_value(), user=config.db_user.get_secret_value(),
                        password=config.db_password.get_secret_value(), host=config.db_host.get_secret_value())
cur = conn.cursor()


async def send_m():
    cur.execute("SELECT question, buttons FROM messages WHERE id_message = 2")
    question = [i for i in cur.fetchall()[0]]
    # btn = cur.fetchall()[1]
    # moves = cur.fetchall()[2]
    bot_token = '942186676:AAHrk6OuLMDrbdBr4b9IipO7KzGtUfERSL0'
    # Create the inline keyboard
    btns = []
    count = 0
    for i in str(question[1]).split(','):
        btn = {
            'text': str(i.strip()),
            'callback_data': 'tk' + str(i.strip())[:5] + str(count)
        }
        btns.append(btn)
        count+=1
    print(btns)
    if len(btns)>1:
        keyboard = {
            'inline_keyboard': [btns]
        }
    else:
        keyboard = {
            'inline_keyboard': [btns]
        }
    photo = {
        'photo': 'https://example.com/photo.jpg'
    }
    res = requests.post(
        'https://api.telegram.org/bot{}/sendMessage'.format(bot_token),
        data={
            'chat_id': '641113946',
            'text': question[0],
            'reply_markup': json.dumps(keyboard),
            'photo': json.dumps(photo)
        }
    )
    #
    # # Create the photo
    # phot = {
    #     'photo': 'https://im.wampi.ru/2023/02/16/start.jpg'
    # }
    # photo_res = InputFile('make_for_blue_eays.JPG')
    # # Send the message with the inline keyboard and photo
    # print('fff')
    # res = requests.post(
    #     'https://api.telegram.org/bot{}/sendPhoto'.format(bot_token),
    #     data={
    #         'chat_id': '641113946',
    #         'photo': photo_res,
    #         'caption': question[0],
    #         'reply_markup': json.dumps(keyboard),
    #     }
    # )
    print(res.text)


#
#
# async def send_chat():
#     try:
#         message = 'Присоединяйся к боту и проходи тест!'
#         cur.execute("SELECT chat_id, chastota, last_m FROM chats")
#         chats = cur.fetchall()
#         for i in chats:
#             print(1)
#             try:
#                 print(2)
#                 if (i[2] + datetime.timedelta(days=i[1])) < datetime.date.today():
#                     print(3)
#                     url = f"https://api.telegram.org/bot{config.bot_token.get_secret_value()}/sendMessage?chat_id={i[0]}&parse_mode=html&text={message}&reply_markup=%7B%0D%0A++%22inline_keyboard%22%3A+%5B%0D%0A++++%5B%0D%0A++++++%7B%0D%0A++++++++%22text%22%3A+%22%D0%A5%D0%BE%D1%87%D1%83%21%22%2C%0D%0A++++++++%22url%22%3A+%22https%3A%2F%2Ft.me%2FPsy_howareyou_bot%22%0D%0A++++++%7D%0D%0A++++%5D%0D%0A++%5D%0D%0A%7D"
#                     params = {
#                         "chat_id": i[0],
#                         "text": message,
#                     }
#                     results = requests.get(url, params=params)
#                     cur.execute(
#                         "UPDATE chats "
#                         "SET last_m = '{}'"
#                         "WHERE chat_id = '{}'".format(datetime.date.today(), str(i[0]), ))
#                     conn.commit()
#             except:
#                 continue
#         await asyncio.sleep(1)
#     except:
#         print('error in send')
#         conn.rollback()
#
#
# async def send_ls():
#     try:
#         message = 'Привет, как ты?\n\n' \
#                   'Позади еще одна неделя и пришло время на минуту остановиться и поделиться своими ощущениями!\n\n' \
#                   'Готов пройти тест прямо сейчас?'
#         cur.execute("SELECT id, tg_id FROM users")
#         chats = cur.fetchall()
#         print(chats)
#         for i in chats:
#             try:
#                 print(i)
#                 cur.execute("SELECT last_r FROM users_information WHERE user_id = '{}'".format(i[0]))
#                 last = cur.fetchone()
#                 if (last[0] + datetime.timedelta(days=6)) < datetime.date.today():
#                     url = f"https://api.telegram.org/bot{config.bot_token.get_secret_value()}/sendMessage?chat_id={i[1]}&parse_mode=html&text={message}"
#                     params = {
#                         "chat_id": i[1],
#                         "text": message,
#                     }
#                     results = requests.get(url, params=params)
#                     cur.execute(
#                         "UPDATE users_information "
#                         "SET last_r = '{}'"
#                         "WHERE user_id = '{}'".format(datetime.date.today(), str(i[0]), ))
#                     conn.commit()
#             except:
#                 continue
#         await asyncio.sleep(1)
#     except:
#         print('error in send')
#         conn.rollback()


# scheduler = schedule.Scheduler()
# scheduler.every(1).seconds.do(send_m)
#
#
# # Run the event loop
# while True:
#     loop = asyncio.get_event_loop()
#     loop.run_forever()

# # schedule.every().day.at("12:00").do(send_chat)
schedule.every(1).seconds.do(send_m)

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        asyncio.run(send_m())
    except KeyboardInterrupt:
        pass
