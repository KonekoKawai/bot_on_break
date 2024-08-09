
################################### ПОДКЛЮЧАЕМ БИБЛИОТЕКИ ###################################

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

import enum
import logging # библиотека для хранения логов #logging.error(msg!!!, exc_info=True)
import asyncio # библиотека для асинхронного программирования
from asyncio import Future
import aiogram #import aiogram # Каркас для API Telegram Bot 
from aiogram import F, Router
from aiogram.filters.command import Command
from aiogram.filters import Command, StateFilter, BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, user
from aiogram.enums import ParseMode

#############################################################################################

########   Настройка логера   #####

logging.basicConfig(level=logging.INFO) 
   
# logger = logging.getLogger(__name__); # Имя файла в логгере
# logger.setLevel(logging.INFO); # LVL для обработки в логгере (Уровень логирования)

# loggerHandler = logging.FileHandler(f'{__name__}.log'); # настройка обработчика для logger
# loggerFormat = logging.Formatter("%(filename)s | %(asctime)s | %(levelname)s | %(message)s"); # настройка форматировщика

# loggerHandler.setFormatter(loggerFormat); # добавление форматировщика к обработчику
# logger.addHandler(loggerHandler); # добавление обработчика к логгеру


#############################################################################################

#Для токена
class Settings(BaseSettings):
    bot_token: SecretStr
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


config = Settings()

#Количество очередей и человек в ней 
queue_drivers = 2;
queue_client = 2;


bot = aiogram.Bot(token=config.bot_token.get_secret_value()) # Объект бота
disp = aiogram.Dispatcher() # Диспетчер

dic_break_more_XX_minuts = {} # Словарь для определения задержки на перерыве больше 15 минут  # Время на принятие решения --------------------------------------------
dic_time_solution = {} # Словарь для определения задержки при принятии решения Время на принятие решения --------------------------------------------


flag_empty_drivers = [[True]]*queue_drivers # Доступна для очередь cписок из *config_reader.queue_drivers

current_cout_query = [] ## Количество человек в каждоый очереди Количество очередей config_reader.queue_drivers
for i in range(queue_drivers):
    current_cout_query.append([] * queue_drivers)