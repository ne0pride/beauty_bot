from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
import os
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InputFile, InputMedia
# from config_reader import config
import aioschedule
import asyncio
import json
import psycopg2
import bd
import random

global counter_sms
counter_sms = 1

conn = psycopg2.connect(dbname='beautybot', user='postgres',
                        password='c7ym7CYD', host='localhost', port='5432')
cur = conn.cursor()

storage = MemoryStorage()


class Test_one(StatesGroup):
    color_eyes = State()


# кнопки выбора действия
start_test = KeyboardButton(text='Подобрать мне макияж')
consultation = KeyboardButton(text='Записаться на консультацию')
keybd_move = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False).add(
    start_test)

btn_1 = InlineKeyboardMarkup(text='карий', callback_data='c_k')
btn_2 = InlineKeyboardMarkup(text='голубой', callback_data='c_g')
btn_3 = InlineKeyboardMarkup(text='серый', callback_data='c_s')
btn_4 = InlineKeyboardMarkup(text='зеленый', callback_data='c_z')
keybd_test_1 = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(
    btn_1, btn_2, btn_4
)

like = InlineKeyboardMarkup(text='🔥', callback_data='reaction_l')
dislike = InlineKeyboardMarkup(text='🤢', callback_data='reaction_d')
keybd_reaction = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(like, dislike)

yes = InlineKeyboardMarkup(text='Да✅', callback_data='yes')
keybd_yes = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(
    yes
)
yes_advice = InlineKeyboardMarkup(text='Да✅', callback_data='yes_a')
keybd_yes_advice = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(
    yes_advice
)

sub = InlineKeyboardMarkup(text='Подписалась👌', callback_data='sub')
keybd_sub = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(
    sub
)

subadvice = InlineKeyboardMarkup(text='Подписалась👌', callback_data='sub_advice')
keybd_subadvice = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(
    subadvice
)

bot = Bot(token='6032924863:AAEn7AfhJ8H4qbEHYoCaGQcUlwrUuIA4pkI')
dp = Dispatcher(bot, storage=storage)


# функция отправки напоминания
async def send():
    try:
        users_id = await bd.get_users()
        print(users_id)
        global counter_sms
        count_m = await bd.get_count_messages()
        print(count_m)
        print(counter_sms)
        if counter_sms > count_m:
            counter_sms = 1
        cur.execute("SELECT question, buttons, photo FROM messages WHERE id_message = '{}'".format(counter_sms))
        question = [i for i in cur.fetchall()[0]]
        count = 0
        markup = InlineKeyboardMarkup()  # создаём клавиатуру
        markup.row_width = 1  # кол-во кнопок в строке
        for i in str(question[1]).split(','):  # цикл для создания кнопок
            markup.add(InlineKeyboardButton(i.strip(), callback_data='tk' + str(
                i.strip()[:5] + str(count))))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
            count += 1
        for z in users_id:
            try:
                if question[2] != None:
                    photo_res = InputFile(str(question[2]))
                    await bot.send_photo(z, photo=photo_res, caption=question[0], reply_markup=markup)
                else:
                    await bot.send_message(z, question[0], reply_markup=markup)
            except Exception as e:
                print(str(e))
        counter_sms += 1
    except Exception as e:
        print('rlbk in send ' + str(e))


async def send_advice(id=None):
    if id is not None:
        print('===')
        print(id)
        count_a = await bd.get_count_messages()
        cur.execute("SELECT advice FROM advices WHERE id_advice = '{}'".format(random.randrange(1, count_a)))
        advice = cur.fetchone()
        await bot.send_message(id, advice[0])
        await bot.send_message(id, 'Подобрать ещё советик?', reply_markup=keybd_yes_advice)
    else:
        users_id = await bd.get_users()
        count_a = await bd.get_count_messages()
        cur.execute("SELECT advice FROM advices WHERE id_advice = '{}'".format(random.randrange(1, count_a)))
        advice = cur.fetchone()
        for i in users_id:
            try:
                await bot.send_message(i, advice[0])
                await bot.send_message(i, 'Подобрать ещё советик?', reply_markup=keybd_yes_advice)
            except Exception as e:
                print(str(e))


async def scheduler():
    aioschedule.every().day.at("12:30").do(send_advice)
    aioschedule.every().monday.at("12:00").do(send)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    asyncio.create_task(scheduler())


# Клиентская часть
@dp.message_handler(commands='start')
async def command_start(message: types.Message):
    try:
        if (not await bd.user_exists(message.from_user.id)):
            await bd.add_user(message.from_user.id, str(message.from_user.first_name))
            await bd.add_user_info(message.from_user.id)
        photo_res = InputFile('start.PNG')
        await bot.send_photo(message.from_user.id, photo=photo_res,
                             caption='Привет!\nРада знакомству\n Я расскажу тебе все секреты и тонкости макияжа, а еще подберу самые лучшие варианты специально для тебя😊!')
        await bot.send_message(message.from_user.id, 'Для начала нажми кнопку пройти тест и выбери свой цвет глаз.',
                               reply_markup=keybd_move)
    except:
        print(str(Exception))
        await message.reply('Ошибка')


@dp.message_handler(lambda message: message.text == 'Подобрать мне макияж', state=None)
async def start_test(message: types.Message):
    user_channel_status = await bot.get_chat_member(chat_id='@dfgfdw32', user_id=message.from_user.id)
    if user_channel_status["status"] == 'left':
        await bd.sub_unable(message.from_user.id)
    activate = await bd.chek_activate(message.from_user.id)
    if int(activate) == 1:
        await bot.send_message(message.from_user.id, 'Что бы пройти тест ещё раз, подпишитесь на канал:'
                                                     '\n https://t.me/dfgfdw32', reply_markup=keybd_sub)
    elif int(activate) == 0:
        await bd.activate(message.from_user.id)
        await Test_one.color_eyes.set()
        await bot.send_message(message.from_user.id, "Выберите свой цвет глаз", reply_markup=keybd_test_1)
    else:
        await Test_one.color_eyes.set()
        await bot.send_message(message.from_user.id, "Выберите свой цвет глаз", reply_markup=keybd_test_1)


@dp.callback_query_handler(Text(startswith=('c_')), state=Test_one.color_eyes)
async def choose_color(callback_query: types.CallbackQuery, state: FSMContext):
    ans = callback_query.data
    itog = ''
    if ans == 'c_k':
        itog = 'карий'
        await bot.send_message(callback_query.from_user.id,
                               '🌸 Девушкам с карими глазами отлично подойдут яркие оттенки: синий, золотой, фиолетовый, красный')
        await bot.send_message(callback_query.from_user.id,
                               '🌸 Если у тебя светлые волосы, постарайся в макияже делать акцент на глаза. Это сделает твой образ более ярким и запоминающимся ')
        await bot.send_message(callback_query.from_user.id,
                               '🌸 Если тебе нравятся более спокойные цвета, используй: персиковый, сливовый, бежевый, кофейный и т.д')
        photo_res = InputFile('make_for_kar_eays.PNG')
        await bot.send_photo(callback_query.from_user.id, photo=photo_res)
    elif ans == 'c_g':
        itog = 'голубой'
        await bot.send_message(callback_query.from_user.id,
                               '🌸 Девушкам с голубыми глазами отлично подходят светлые тёплые цвета теней:\nзолотой, розовый, персиковый, медный, кофейный и т.д.')
        await bot.send_message(callback_query.from_user.id,
                               '🌸 Если у тебя светлая кожа, добавь в свою косметичку более нежные оттенки, например: \nперсиковый, кремовый, молочный шоколад, или пудровый')
        await bot.send_message(callback_query.from_user.id,
                               '🌸 Если тебе нравятся холодные оттенки, попробуй использовать контрастные цвета: \nфиолетовый, кобальтовый, или ультрамариновый. Следи, чтобы оттенок теней не совпадал с оттенком глаз на 100%')
        photo_res = InputFile('make_for_blue_eays.PNG')
        await bot.send_photo(callback_query.from_user.id, photo=photo_res)
    elif ans == 'c_z':
        itog = 'зеленый'
        await bot.send_message(callback_query.from_user.id,
                               '🌸 Девушкам с зелёными глазами отлично подходят тёплые цвета теней: фиолетовые, бордовые, коричневые, золотые, красные.')
        await bot.send_message(callback_query.from_user.id,
                               '🌸 Старайся избегать ярко-синих и серебристых оттенков — они могут придать глазам уставший вид и лишить их выразительности')
        await bot.send_message(callback_query.from_user.id,
                               '🌸 Попробуй добавить контрастные цвета: например, красные стрелки отлично дополнят твой образ')
        photo_res = InputFile('make_for_green_eays.PNG')
        await bot.send_photo(callback_query.from_user.id, photo=photo_res)
    await bot.send_message(callback_query.from_user.id, 'Как тебе мои бьюти-советы сегодня?',
                           reply_markup=keybd_reaction)
    await bot.send_message(callback_query.from_user.id, 'Пройти тест еще раз?', reply_markup=keybd_yes)
    await state.finish()


@dp.callback_query_handler(Text(startswith=('reaction')))
async def reaction(callback_query: types.CallbackQuery):
    ans = callback_query.data
    print(ans)


@dp.callback_query_handler(Text(startswith=('yes')))
async def btn_yes(callback_query: types.CallbackQuery):
    adv = 0
    print(callback_query.data[-1])
    if callback_query.data[-1] == 'a':
        adv = 1
    activate = await bd.chek_activate(callback_query.from_user.id)
    if adv == 0:
        if int(activate) == 1:
            await bot.send_message(callback_query.from_user.id, 'Что бы пройти тест ещё раз, подпишитесь на канал:'
                                                                '\n https://t.me/dfgfdw32', reply_markup=keybd_sub)
        else:
            await bot.send_message(callback_query.from_user.id, 'Нажмите, чтобы пройти тест', reply_markup=keybd_move)
    else:
        if int(activate) == 1:
            await bot.send_message(callback_query.from_user.id, 'Что бы подобрать еще совет, подпишитесь на канал:'
                                                                '\n https://t.me/dfgfdw32',
                                   reply_markup=keybd_subadvice)
        else:
            print('ent')
            user_channel_status = await bot.get_chat_member(chat_id='@dfgfdw32', user_id=callback_query.from_user.id)
            if user_channel_status["status"] == 'left':
                await bd.sub_unable(callback_query.from_user.id)
            activate = await bd.chek_activate(callback_query.from_user.id)
            print(activate)
            if int(activate) == 1:
                await bot.send_message(callback_query.from_user.id, 'Что бы подобрать еще совет, подпишитесь на канал:'
                                                                    '\n https://t.me/dfgfdw32',
                                       reply_markup=keybd_subadvice)
            else:
                print('защел в совет')
                count_a = await bd.get_count_messages()
                cur.execute("SELECT advice FROM advices WHERE id_advice = '{}'".format(random.randrange(1, count_a)))
                advice = cur.fetchone()
                print(callback_query.from_user.id)
                await bot.send_message(callback_query.from_user.id, advice[0])
                await bot.send_message(callback_query.from_user.id, 'Подобрать ещё советик?',
                                       reply_markup=keybd_yes_advice)


@dp.callback_query_handler(Text(startswith=('sub')))
async def btn_sub(callback_query: types.CallbackQuery):
    adv = 0
    if callback_query.data[-1] == 'e':
        adv = 1
    if adv == 0:
        user_channel_status = await bot.get_chat_member(chat_id='@dfgfdw32', user_id=callback_query.from_user.id)
        if user_channel_status["status"] != 'left':
            await bd.sub(callback_query.from_user.id)
            await bot.send_message(callback_query.from_user.id, 'Нажмите, чтобы пройти тест', reply_markup=keybd_move)
        else:
            await bot.send_message(callback_query.from_user.id, 'Вы не подписались, подпишитесь, и нажмите снова',
                                   reply_markup=keybd_sub)
    else:
        user_channel_status = await bot.get_chat_member(chat_id='@dfgfdw32', user_id=callback_query.from_user.id)
        if user_channel_status["status"] != 'left':
            await bd.sub(callback_query.from_user.id)
            count_a = await bd.get_count_messages()
            cur.execute("SELECT advice FROM advices WHERE id_advice = '{}'".format(random.randrange(1, count_a)))
            advice = cur.fetchone()
            print(callback_query.from_user.id)
            await bot.send_message(callback_query.from_user.id, advice[0])
            await bot.send_message(callback_query.from_user.id, 'Подобрать ещё советик?', reply_markup=keybd_yes_advice)
        else:
            await bot.send_message(callback_query.from_user.id, 'Вы не подписались, подпишитесь, и нажмите снова',
                                   reply_markup=keybd_subadvice)


@dp.callback_query_handler(Text(startswith=('tk')))
async def btn_sub(callback_query: types.CallbackQuery):
    btn = (str(callback_query.data)[2:-1])
    num = (str(callback_query.data)[-1])
    print(btn)
    print(num)
    msg = await bd.get_moves(btn, num)
    print(msg)
    if 'МЕНЕДЖЕРУ' in msg:
        u_id = msg.split(' ')[1].strip()
        await bot.send_message(u_id, 'Свяжись с' + ' https://t.me/' + str(callback_query.from_user.username),
                               reply_markup=keybd_move)
        await bot.send_message(callback_query.from_user.id, 'С тобой свяжется наш менеджер', reply_markup=keybd_move)
    else:
        await bot.send_message(callback_query.from_user.id, msg, reply_markup=keybd_move)


@dp.message_handler(lambda message: message.text == 'Записаться на консультацию')
async def cons(message: types.Message):
    await bot.send_message(5907862004, 'Свяжись с' + ' https://t.me/' + str(message.from_user.username),
                           reply_markup=keybd_move)
    await bot.send_message(message.from_user.id, 'С тобой свяжется наш менеджер', reply_markup=keybd_move)


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
