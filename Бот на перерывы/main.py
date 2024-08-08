import config_reader
from config_reader import config

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

logging.basicConfig(level=logging.INFO) ########   Настройка логера   #####
bot = aiogram.Bot(token=config.bot_token.get_secret_value()) # Объект бота
disp = aiogram.Dispatcher() # Диспетчер

flag_empty_drivers = [[True]]*config_reader.queue_drivers # Доступна для очередь cписок из *config_reader.queue_drivers

current_cout_query = [] ## Количество человек в каждоый очереди Количество очередей config_reader.queue_drivers
for i in range(config_reader.queue_drivers):
    current_cout_query.append([] * config_reader.queue_drivers)
#------------------------------------------------------------------------------------------------------------------------

class breakFastState(StatesGroup): # Класс состояний 
    waiting_to_queue = State() #1 ОЖИДАНИЕ ВХОЖДЕНИЯ В ОЧЕРЕДЬ
    waiting_to_free_queue = State() #2 ЗАНЯЛ ОЧЕРЕДЬ И ЖДЁТ ОСВОБОЖДЕНИЯ ОЧЕРЕДИ
    waiting_to_solution = State() #3 РЕШЕНИЕ ПО ПОВОДУ ОЧЕРЕДИ 
    breakfast = State() #4 ПЕРЕРЫВ
    

async def set_query(user_id): # функция занятия очереди 
    global current_cout_query
    current_cout_query.sort(key=lambda arr: len(arr)) # Самая первая очередь, самая короткая 
    current_cout_query[0].append(user_id)
    current_cout_query.sort(key=lambda arr: len(arr)) # Самая первая очередь, самая короткая 
   

def check_query(user_id) -> bool: # проверка доступности очереди в самом начале 
    global current_cout_query
    for i in range(config_reader.queue_drivers):
        if current_cout_query[i]:
            if (user_id == current_cout_query[i][0]):        
                return True
    return False


async def check_query_1(user_id) -> bool: # проверка доступности очереди асинхронная Если изначально очередь занята
    global current_cout_query
    while True: 
        await asyncio.sleep(0)
        for i in range(config_reader.queue_drivers):
            if current_cout_query[i]:
                if (user_id == current_cout_query[i][0]):        
                    return True
            

async def delet_in_query(user_id): # Удаление из очереди
    global current_cout_query
    # for x in current_cout_query:
    #     print(f"Выведем значения очереди: {x}")
        
    for i in range(config_reader.queue_drivers): # Пройдемся по всем очередям 
        if current_cout_query[i]: # Если список не пуст
            if user_id in current_cout_query[i]:
                current_cout_query[i].remove(user_id)
                if(len(current_cout_query)>0):     
                    current_cout_query.sort(key=lambda arr: len(arr)) # Самая первая очередь, самая короткая 
                    if(len(current_cout_query[len(current_cout_query)-1]) > 1):
                        current_cout_query[0].append(current_cout_query[len(current_cout_query)-1].pop()) # Берём самую длинную очередь и переносим из неё id в самую короткую                 
                break

    current_cout_query.sort(key=lambda arr: len(arr)) # Самая первая очередь, самая короткая        
    # for x in current_cout_query:
    #     print(f"Очередь после удаления: {x}")
    
        
@disp.message(Command("reboot")) #Перезапуск бота
async def cmd_reboot(message: Message, state: FSMContext):
    await message.delete()
    await state.set_state(None) # ОТЧИЩАЕМ состояния
    await message.answer( "<b>Бот перезапущен</b>", parse_mode=ParseMode.HTML)

@disp.message(StateFilter(None), Command("start")) #1 Первый запуск бота Запускает либо #2 либо #3
async def cmd_start(message: Message, state: FSMContext):
    await message.delete()
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Занять очередь",
        callback_data="waiting_to_free_queue")
    )
    await delet_in_query(message.from_user.id) # Удаление челововека из очереди
    await state.set_state(breakFastState.waiting_to_queue) #1 ОЖИДАНИЕ ВХОЖДЕНИЯ В ОЧЕРЕДЬ
    await message.answer(
        "Этот бот поможет тебе занять очередь на перерыв. Нажми на кнопку, чтобы занять очередь ",
        reply_markup=builder.as_markup()
    )
    
    
    
@disp.callback_query(F.data == "waiting_to_queue") #1 Эмитация первого запуска Запускает либо #2 либо #3
async def new_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Занять очередь",
        callback_data="waiting_to_free_queue")
    )
    await delet_in_query(callback.from_user.id) # Удаление челвоека из очереди
    await state.set_state(breakFastState.waiting_to_queue) #1 ОЖИДАНИЕ ВХОЖДЕНИЯ В ОЧЕРЕДЬ
    await callback.message.answer(
        "Чтобы нажми на кнопку, повторно занять очередь",
        reply_markup=builder.as_markup()
    )
    await callback.answer() # Подтвердить получение от телеграмма
   

@disp.callback_query(breakFastState.waiting_to_queue, F.data == "waiting_to_free_queue") #2 Обработчки ЗАНЯЛ ОЧЕРЕДЬ После шага с ожиданием очереди
async def waiting_to_free_queue(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await set_query(callback.from_user.id) # человек с id занимает очередь 
    await state.set_state(breakFastState.waiting_to_free_queue) #2 ЗАНЯЛ ОЧЕРЕДЬ И ЖДЁТ ОСВОБОЖДЕНИЯ ОЧЕРЕДИ
    if(check_query(callback.from_user.id)): # Если очередь подошла
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text="Уйти на перерыв",
            callback_data="breakfast"),
        )
        builder.add(InlineKeyboardButton(
            text="Выйти из очереди",
            callback_data="waiting_to_queue")
        )
        builder.adjust(1)
        await state.set_state(breakFastState.waiting_to_solution) #3 РЕШЕНИЕ ПО ПОВОДУ ОЧЕРЕДИ 
        await callback.message.answer(f"⬇️ Очередь подошла, выбери действие ⬇️", reply_markup=builder.as_markup() )
        await callback.answer() # Подтвердить получение от телеграмма

       
    else:
        await callback.message.answer("Очередь занята, ожидайте своей очереди. Вам придёт уведомление")
        await callback.answer() # Подтвердить получение от телеграмма

        await asyncio.create_task(check_query_1(callback.from_user.id)) # ждём выполнения check_query_1
        await callback.message.delete()

        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text="Уйти на перерыв",
            callback_data="breakfast"),
        )
        builder.add(InlineKeyboardButton(
            text="Выйти из очереди",
            callback_data="waiting_to_queue")
        )
        builder.adjust(1)
        await state.set_state(breakFastState.waiting_to_solution) #3 РЕШЕНИЕ ПО ПОВОДУ ОЧЕРЕДИ 
        await callback.message.answer(f"⬇️ Очередь подошла, выбери действие ⬇️", reply_markup=builder.as_markup() )
        await callback.answer() # Подтвердить получение от телеграмма
      

@disp.callback_query(breakFastState.waiting_to_solution, F.data == "breakfast") #4 Перерыв
async def breakfast(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Вернуться с перерыва",
        callback_data="waiting_to_queue")
    )
    await state.set_state(breakFastState.breakfast) #4 ПЕРЕРЫВ
    
    await callback.message.answer("Вы на перерыве, чтобы вернуться нажмите на кнопку ⬇️", 
                                  reply_markup=builder.as_markup()
                                  )
    await callback.answer() # Подтвердить получение от телеграмма
    
     
#--------------------------------------------------------------------

# Запуск процесса поллинга  новых апдейтов (поиск обновлений от новых задач) // Polling, или опрос, – это процесс, при котором клиентский скрипт периодически отправляет запросы к серверу для проверки наличия новой инфы. 
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
