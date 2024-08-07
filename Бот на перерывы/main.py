# -*- coding: cp1251 -*-
from email import message
from gc import callbacks
import config_reader
from config_reader import config

import logging # ���������� ��� �������� ����� #logging.error(msg!!!, exc_info=True)
import asyncio # ���������� ��� ������������ ����������������
import aiogram #import aiogram # ������ ��� API Telegram Bot 
from aiogram import F, Router
from aiogram.filters.command import Command
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton


logging.basicConfig(level=logging.INFO) ########   ��������� ������   #####
bot = aiogram.Bot(token=config.bot_token.get_secret_value()) # ������ ����
disp = aiogram.Dispatcher() # ���������
flag_empty_drivers = [[True]]*config_reader.queue_drivers # �������� ��� ������� c����� �� *config_reader.queue_drivers
current_cout_query = [[]]*config_reader.queue_drivers # ���������� ������� � ������� �������
#------------------------------------------------------------------------------------------------------------------------

class breakFastState(StatesGroup): # ����� ��������� 
    waiting_to_queue = State() #1 �������� ��������� � �������
    waiting_to_free_queue = State() #2 ����� ������� � �Ĩ� ������������ �������
    waiting_to_solution = State() #3 ������� �� ������ ������� 
    breakfast = State() #4 �������
    

async def set_query(id): # ������� ������� ������� 
    print(current_cout_query[0].__len__)
    current_cout_query.append(id)
    for i in current_cout_query:
            print(i)
    

async def check_query(): # �������� ����������� ������� 
    for flag in flag_empty_drivers:
        if(flag == True):
            return flag
        

async def check_place_query(): # �������� ����� � ������� 
    return 0;
        

@disp.message(Command("reboot")) #���������� ����
async def cmd_reboot(message: Message, state: FSMContext):
    await state.set_state(None) # �������� ���������
    await message.answer( "��� �����������")


@disp.message(StateFilter(None), Command("start")) #1 ������ ������ ���� ��������� ���� #2 ���� #3
async def cmd_start(message: Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="������ �������",
        callback_data="waiting_to_free_queue")
    )
    await state.set_state(breakFastState.waiting_to_queue) #1 �������� ��������� � �������
    await message.answer(
        "���� ��� ������� ���� ������ ������� �� �������, ����� ������ �������, ����� �� ������",
        reply_markup=builder.as_markup()
    )

    
@disp.callback_query(F.data == "waiting_to_queue") #1 �������� ������� ������� ��������� ���� #2 ���� #3
async def new_start(callback: CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="������ �������",
        callback_data="waiting_to_free_queue")
    )
    await state.set_state(breakFastState.waiting_to_queue) # �������� �������
    await callback.message.answer(
        "����� �������� ������ �������, ����� �� ������",
        reply_markup=builder.as_markup()
    )
    await callback.answer() # ����������� ��������� �� ����������


@disp.callback_query(breakFastState.waiting_to_queue, F.data == "waiting_to_free_queue") #2 ���������� ����� ������� ����� ���� � ��������� �������
async def waiting_to_free_queue(callback: CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="��������� ����� � �������",
        callback_data="check_place_query")
    )
    builder.add(InlineKeyboardButton(
        text="����� �� �������",
        callback_data="waiting_to_queue",
        )
    )
    #await set_query(message.from_user.id) # ������ ������� ������� �������
    await state.set_state(breakFastState.waiting_to_free_queue) #2 ����� ������� � �Ĩ� ������������ �������
    await callback.message.answer("�����-�� �����", 
                                  reply_markup=builder.as_markup()
                                  )
    await callback.answer() # ����������� ��������� �� ����������
    


@disp.callback_query(breakFastState.waiting_to_free_queue, F.data == "waiting_to_queue") #3 ���������� ������� �������� # ������� �� ������ ������� 
async def waiting_to_solution(callback: CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="����� �� �������",
        callback_data="breakfast")
    )
    builder.add(InlineKeyboardButton(
        text="����� �� �������",
        callback_data="waiting_to_queue")
    )
    await check_query() # ����� �������
    await state.set_state(breakFastState.waiting_to_solution)
    

@disp.callback_query(breakFastState.waiting_to_free_queue, F.data == "waiting_to_queue") #4 �������
async def breakfast(callback: CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="��������� � ��������",
        callback_data="waiting_to_queue")
    )
    await state.set_state(breakFastState.breakfast)

# @disp.callback_query(F.data == "waiting_to_free_queue") # �������� �������
# async def send_waiting_queusy(callback: CallbackQuery):
#     await set_query(callback.message.from_user.id);
#     if (check_query):
#         await callback.message.answer(str(f"�� ����� �� �������! ��� id: {callback.message.from_user.id}"))     
#     else:
#         task_check_place_query = asyncio.create_task(check_place_query())
#         await callback.message.answer(str(f"���� ����� � �������: {await task_check_place_query}"))

        
     
#--------------------------------------------------------------------



# ������ �������� ��������  ����� �������� (����� ���������� �� ����� �����) // Polling, ��� �����, � ��� �������, ��� ������� ���������� ������ ������������ ���������� ������� � ������� ��� �������� ������� ����� ����. 
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
###################################�