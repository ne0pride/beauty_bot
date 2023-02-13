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


# Клиентская часть
@dp.message_handler(commands='start')
async def command_start(message: types.Message):
    try:
        if (not await bd.user_exists(message.from_user.id)):
            await bd.add_user(message.from_user.id, str(message.from_user.first_name))
        photo_res = InputFile('start.JPG')
        await bot.send_photo(message.from_user.id, photo=photo_res, caption='Привет!\n'
                                                                            'Рада знакомству\n'
                                                                            'Я подберу лучшие варианты макияжа специально для тебя и расскажу все тонкости 😊')
        await bot.send_message(message.from_user.id, 'Для начала нажми кнопку пройти тест и выбери свой цвет глаз.',
                               reply_markup=keybd_move)
    except:
        print(str(Exception))
        await message.reply('Ошибка')


@dp.message_handler(lambda message: message.text == 'Пройти тест', state=None)
async def keywords(message: types.Message):
    # сделать проверку на первое прохождение, не давать пройти второй раз если не подписан на канал
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
    await bot.send_message(callback_query.from_user.id, 'Подобрать еще советик?', reply_markup=keybd_yes)
    await state.finish()


@dp.callback_query_handler(Text(startswith=('reaction')))
async def reaction(callback_query: types.CallbackQuery):
    ans = callback_query.data
    print(ans)


@dp.callback_query_handler(Text(startswith=('yes')))
async def btn_yes(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id,
                           'Что бы получить еще один совет, подпишись на канал\n https://t.me/dfgfdw32',
                           reply_markup=keybd_sub)


@dp.callback_query_handler(Text(startswith=('sub')))
async def btn_sub(callback_query: types.CallbackQuery):
    user_channel_status = await bot.get_chat_member(chat_id='@dfgfdw32', user_id=callback_query.from_user.id)
    if user_channel_status["status"] != 'left':
        await bot.send_message(callback_query.from_user.id, 'Нажмите, чтобы пройти тест', reply_markup=keybd_move)
    else:
        await bot.send_message(callback_query.from_user.id, 'Вы не подписались, подпишитесь, и нажмите снова',
                               reply_markup=keybd_sub)


executor.start_polling(dp, skip_updates=True)
