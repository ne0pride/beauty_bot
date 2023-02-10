from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import os
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InputFile, InputMedia
from config_reader import config


storage = MemoryStorage()

class Test_one(StatesGroup):
    color_eyes = State()

bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher(bot, storage=storage)
