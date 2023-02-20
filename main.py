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
from config_reader import config
import aioschedule
import asyncio
import json
import psycopg2
import bd

global counter_sms
counter_sms = 1

conn = psycopg2.connect(dbname=config.db_name.get_secret_value(), user=config.db_user.get_secret_value(),
                        password=config.db_password.get_secret_value(), host=config.db_host.get_secret_value())
cur = conn.cursor()

storage = MemoryStorage()


class Test_one(StatesGroup):
    color_eyes = State()


# кнопки выбора действия
start_test = KeyboardButton(text='Пройти тест')
consultation = KeyboardButton(text='Записаться на консультацию')
keybd_move = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False).add(
    start_test, consultation)

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

sub = InlineKeyboardMarkup(text='Подписалась👌', callback_data='sub')
keybd_sub = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(
    sub
)

bot = Bot(token=config.bot_token.get_secret_value())
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

async def scheduler():
    aioschedule.every(1).minutes.do(send)

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
        photo_res = InputFile('start.JPG')
        await bot.send_photo(message.from_user.id, photo=photo_res, caption='Привет!\n'
                                                                            'Рада знакомству\n'
                                                                            'Я подберу лучшие варианты макияжа специально для тебя и расскажу все тонкости 😊')
        await bot.send_message(message.from_user.id, 'Для начала нажми кнопку пройти тест и выбери свой цвет глаз.',
                               reply_markup=keybd_move)
    except:
        print(str(Exception))
        await message.reply('Ошибка')
        await bot.send_document()


@dp.message_handler(lambda message: message.text == 'Пройти тест', state=None)
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
    elif ans == 'c_g':
        itog = 'голубой'
        await bot.send_message(callback_query.from_user.id,
                               '🌸 Девушкам с голубыми глазами отлично подходят светлые тёплые цвета теней:\nзолотой, розовый, персиковый, медный, кофейный и т.д.')
        await bot.send_message(callback_query.from_user.id,
                               '🌸 Если у тебя светлая кожа, добавь в свою косметичку более нежные оттенки, например: \nперсиковый, кремовый, молочный шоколад, или пудровый')
        await bot.send_message(callback_query.from_user.id,
                               '🌸 Если тебе нравятся холодные оттенки, попробуй использовать контрастные цвета: \nфиолетовый, кобальтовый, или ультрамариновый. Следи, чтобы оттенок теней не совпадал с оттенком глаз на 100%')
        photo_res = InputFile('make_for_blue_eays.JPG')
        await bot.send_photo(callback_query.from_user.id, photo=photo_res)
    elif ans == 'c_z':
        itog = 'зеленый'
        await bot.send_message(callback_query.from_user.id,
                               '🌸 Девушкам с зелёными глазами отлично подходят тёплые цвета теней: фиолетовые, бордовые, коричневые, золотые, красные.')
        await bot.send_message(callback_query.from_user.id,
                               '🌸 Старайся избегать ярко-синих и серебристых оттенков — они могут придать глазам уставший вид и лишить их выразительности')
        await bot.send_message(callback_query.from_user.id,
                               '🌸 Попробуй добавить контрастные цвета: например, красные стрелки отлично дополнят твой образ')
        photo_res = InputFile('make_for_green_eays.JPG')
        await bot.send_photo(callback_query.from_user.id, photo=photo_res)
    await bot.send_message(callback_query.from_user.id, 'Как тебе мои бьюти-советы сегодня?',
                           reply_markup=keybd_reaction)
    await bot.send_message(callback_query.from_user.id, 'Подобрать еще советик?', reply_markup=keybd_yes)
    await state.finish()


@dp.callback_query_handler(Text(startswith=('reaction')))
async def reaction(callback_query: types.CallbackQuery):
    ans = callback_query.data
    print(ans)


@dp.callback_query_handler(Text(startswith=('yes')))
async def btn_yes(callback_query: types.CallbackQuery):
    activate = await bd.chek_activate(callback_query.from_user.id)
    if int(activate) == 1:
        await bot.send_message(callback_query.from_user.id, 'Что бы пройти тест ещё раз, подпишитесь на канал:'
                                                            '\n https://t.me/dfgfdw32', reply_markup=keybd_sub)
    else:
        await bot.send_message(callback_query.from_user.id, 'Нажмите, чтобы пройти тест', reply_markup=keybd_move)


@dp.callback_query_handler(Text(startswith=('sub')))
async def btn_sub(callback_query: types.CallbackQuery):
    user_channel_status = await bot.get_chat_member(chat_id='@dfgfdw32', user_id=callback_query.from_user.id)
    if user_channel_status["status"] != 'left':
        await bd.sub(callback_query.from_user.id)
        await bot.send_message(callback_query.from_user.id, 'Нажмите, чтобы пройти тест', reply_markup=keybd_move)
    else:
        await bot.send_message(callback_query.from_user.id, 'Вы не подписались, подпишитесь, и нажмите снова',
                               reply_markup=keybd_sub)


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


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
