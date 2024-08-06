# -*- coding: cp1251 -*-
import config_reader
from config_reader import config

import logging # библиотека для хранения логов #logging.error(msg!!!, exc_info=True)
import asyncio # библиотека для асинхронного программирования
import aiogram #import aiogram # Каркас для API Telegram Bot 
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

logging.basicConfig(level=logging.INFO) ########   Настройка логера   #####
bot = aiogram.Bot(token=config.bot_token.get_secret_value()) # Объект бота
disp = aiogram.Dispatcher() # Диспетчер
flag_empty_drivers = [True]*config_reader.queue_drivers # Доступна для очередь cписок из *config_reader.queue_drivers
current_cout_query = [0]*config_reader.queue_drivers # Количество человек в каждоый очереди
#------------------------------------------------------------------------------------------------------------------------

async def check_query(): # проверка доступности очереди 
    for flag in flag_empty_drivers:
        if(flag == True):
            return flag
        

async def check_place_query(): # Проверка места в очереди 
    return 0;
        

@disp.message(Command("start")) # Запуск бота 
async def cmd_random(message: aiogram.types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(aiogram.types.InlineKeyboardButton(
        text="Занять очередь",
        callback_data="take_queue")
    )
    await message.answer(
        "Этот бот поможет тебе занять очередь на перерыв, чтобы занять очередь, нажми кнопку внизу",
        reply_markup=builder.as_markup()
    )
    
@disp.callback_query(aiogram.F.data == "take_queue") # Проверка очереди
async def send_waiting_queusy(callback: aiogram.types.CallbackQuery):
    if (not check_query):
        await callback.message.answer(str("Вы вышли на перерыв "))
    else:
        task_check_place_query = asyncio.create_task(check_place_query())
        await callback.message.answer(str(f"Ваше место в очереди: {await task_check_place_query}"))

        
     
#--------------------------------------------------------------------



# Запуск процесса поллинга новых апдейтов
async def main():
    await disp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    



########   Настройка логера   #####
# logger = logging.getLogger(__name__); # Имя файла в логгере
# logger.setLevel(logging.INFO); # LVL для обработки в логгере (Уровень логирования)

# loggerHandler = logging.FileHandler(f'{__name__}.log'); # настройка обработчика для logger
# loggerFormat = logging.Formatter("%(filename)s | %(asctime)s | %(levelname)s | %(message)s"); # настройка форматировщика

# loggerHandler.setFormatter(loggerFormat); # добавление форматировщика к обработчику
# logger.addHandler(loggerHandler); # добавление обработчика к логгеру
###################################