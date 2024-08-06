# -*- coding: cp1251 -*-
import config_reader
from config_reader import config

import logging # ���������� ��� �������� ����� #logging.error(msg!!!, exc_info=True)
import asyncio # ���������� ��� ������������ ����������������
import aiogram #import aiogram # ������ ��� API Telegram Bot 
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

logging.basicConfig(level=logging.INFO) ########   ��������� ������   #####
bot = aiogram.Bot(token=config.bot_token.get_secret_value()) # ������ ����
disp = aiogram.Dispatcher() # ���������
flag_empty_drivers = [True]*config_reader.queue_drivers # �������� ��� ������� c����� �� *config_reader.queue_drivers
current_cout_query = [0]*config_reader.queue_drivers # ���������� ������� � ������� �������
#------------------------------------------------------------------------------------------------------------------------

async def check_query(): # �������� ����������� ������� 
    for flag in flag_empty_drivers:
        if(flag == True):
            return flag
        

async def check_place_query(): # �������� ����� � ������� 
    return 0;
        

@disp.message(Command("start")) # ������ ���� 
async def cmd_random(message: aiogram.types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(aiogram.types.InlineKeyboardButton(
        text="������ �������",
        callback_data="take_queue")
    )
    await message.answer(
        "���� ��� ������� ���� ������ ������� �� �������, ����� ������ �������, ����� ������ �����",
        reply_markup=builder.as_markup()
    )
    
@disp.callback_query(aiogram.F.data == "take_queue") # �������� �������
async def send_waiting_queusy(callback: aiogram.types.CallbackQuery):
    if (not check_query):
        await callback.message.answer(str("�� ����� �� ������� "))
    else:
        task_check_place_query = asyncio.create_task(check_place_query())
        await callback.message.answer(str(f"���� ����� � �������: {await task_check_place_query}"))

        
     
#--------------------------------------------------------------------



# ������ �������� �������� ����� ��������
async def main():
    await disp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    



########   ��������� ������   #####
# logger = logging.getLogger(__name__); # ��� ����� � �������
# logger.setLevel(logging.INFO); # LVL ��� ��������� � ������� (������� �����������)

# loggerHandler = logging.FileHandler(f'{__name__}.log'); # ��������� ����������� ��� logger
# loggerFormat = logging.Formatter("%(filename)s | %(asctime)s | %(levelname)s | %(message)s"); # ��������� ��������������

# loggerHandler.setFormatter(loggerFormat); # ���������� �������������� � �����������
# logger.addHandler(loggerHandler); # ���������� ����������� � �������
###################################