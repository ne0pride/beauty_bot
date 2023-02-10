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
import bd

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
    btn_1, btn_2, btn_3, btn_4
)

like = InlineKeyboardMarkup(text='🔥', callback_data='reaction_l')
dislike = InlineKeyboardMarkup(text='🤢', callback_data='reaction_d')
keybd_reaction = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(like, dislike)

bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher(bot, storage=storage)


# Клиентская часть
@dp.message_handler(commands='start')
async def command_start(message: types.Message):
    try:
        if (not await bd.user_exists(message.from_user.id)):
            await bd.add_user(message.from_user.id, str(message.from_user.first_name))
        await bot.send_message(message.from_user.id, 'Привет! Это бот “Beauty for you”', reply_markup=keybd_move)
    except:
        await message.reply('Ошибка')


@dp.message_handler(lambda message: message.text == 'Пройти тест', state=None)
async def keywords(message: types.Message):
    await Test_one.color_eyes.set()
    await bot.send_message(message.from_user.id, "Выберите свой цвет глаз", reply_markup=keybd_test_1)


@dp.callback_query_handler(Text(startswith=('c_')), state=Test_one.color_eyes)
async def choose_color(callback_query: types.CallbackQuery, state: FSMContext):
    ans = callback_query.data
    itog = ''
    if ans == 'c_k':
        itog = 'карий'
        await bot.send_message(callback_query.from_user.id, 'Совет для кариглазых')
    elif ans == 'c_g':
        itog = 'голубой'
        await bot.send_message(callback_query.from_user.id, 'Совет для голубоглазых')
    elif ans == 'c_s':
        itog = 'серый'
        await bot.send_message(callback_query.from_user.id, 'Совет для сероглазых')
    elif ans == 'c_z':
        itog = 'зеленый'
        await bot.send_message(callback_query.from_user.id, 'Совет для зелёноглазых')
    await bot.send_message(callback_query.from_user.id, 'Как вам совет?', reply_markup=keybd_reaction)
    await bot.send_message(callback_query.from_user.id, 'Подобрать еще советик?', reply_markup=keybd_move)
    await state.finish()


@dp.callback_query_handler(Text(startswith=('reaction')))
async def reaction(callback_query: types.CallbackQuery):
    ans = callback_query.data
    print(ans)


executor.start_polling(dp, skip_updates=True)
