﻿import config_reader
from config_reader import *

#------------------------------------------------------------------------------------------------------------------------

class time(enum.Enum):
    break_time = 12 # СЕК Время перерыва 
    break_time_minuts = 15 # МИН Время перерыва 
    solution_time = 10 # СЕК Время на принятия решения по поводу перерыва

class breakFastState(StatesGroup): # Класс состояний 
    waiting_to_queue = State() #1 ОЖИДАНИЕ ВХОЖДЕНИЯ В ОЧЕРЕДЬ
    waiting_to_free_queue = State() #2 ЗАНЯЛ ОЧЕРЕДЬ И ЖДЁТ ОСВОБОЖДЕНИЯ ОЧЕРЕДИ
    waiting_to_solution = State() #3 РЕШЕНИЕ ПО ПОВОДУ ОЧЕРЕДИ 
    breakfast = State() #4 ПЕРЕРЫВ
   

async def set_query(user_id): # функция занятия очереди 
    global current_cout_query
    current_cout_query.sort(key=lambda arr: len(arr)) # Самая первая очередь, самая короткая 
    current_cout_query[0].append(user_id)
    #mess = bot.send_message(chat_id="@BlaTestKonekoKawai_Bot", text=f"Вы {current_cout_query[0][len(current_cout_query[0])-1]} в очереди!")
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
    
    for x in current_cout_query:
        print(f"Выведем значения очереди: {x}")
        
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
    
    for x in current_cout_query:
        print(f"Очередь после удаления: {x}")


async def time_loop(dic_id_place, user_id, time_sec, callback: CallbackQuery) -> bool: # Функция для нормальной работы таймера
    i = 0
    while i < time_sec:
        if(i==time_sec/2):
            delete_this_message = await callback.message.answer(f"⚠️ Прошла половина времени ⚠️.\nУ вас осталось - {int(time_sec/2)} секунд")
        if(dic_id_place[user_id]==False):
            if(i>=time_sec/2):
                try:
                    await delete_this_message.delete()
                except:
                    pass
            return False
        await asyncio.sleep(1)
        i=i+1
        
            
    if(i>=time_sec/2):
        try:
            await delete_this_message.delete()
        except:
            pass
    return True

@disp.message(Command("reboot")) #Перезапуск бота
async def cmd_reboot(message: Message, state: FSMContext):
    try:
        await message.delete()
    except:
        pass
    await state.set_state(None) # ОТЧИЩАЕМ состояния
    await message.answer( "<b>Бот перезапущен</b>", parse_mode=ParseMode.HTML)

@disp.message(Command("start")) #1 Первый запуск бота Запускает либо #2 либо #3
async def cmd_start(message: Message, state: FSMContext):
    try:
        await message.delete()
    except:
        pass
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Занять очередь",
        callback_data="waiting_to_free_queue")
    )
    await delet_in_query(message.from_user.id) # Удаление челововека из очереди
    await state.set_state(breakFastState.waiting_to_queue) #1 ОЖИДАНИЕ ВХОЖДЕНИЯ В ОЧЕРЕДЬ
    await message.answer(
        "Нажми на кнопку, чтобы занять очередь ",
        reply_markup=builder.as_markup()
    )
    
    
@disp.callback_query(F.data == "waiting_to_queue") #1 Эмитация первого запуска Запускает либо #2 либо #3
async def new_start(callback: CallbackQuery, state: FSMContext):
    global dic_break_more_XX_minuts # Время на принятие решения --------------------------------------------
    dic_break_more_XX_minuts[callback.from_user.id] = False # Время на принятие решения --------------------------------------------
    
    try:
        await callback.message.delete()
    except:
        pass
    
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
    global dic_time_solution # Время на принятие решения --------------------------------------------
    dic_time_solution[callback.from_user.id] = True # Время на принятие решения --------------------------------------------
    
    try:
        await callback.message.delete()
    except:
        pass
    
    await set_query(callback.from_user.id) # человек с id занимает очередь 
    await state.set_state(breakFastState.waiting_to_free_queue) #2 ЗАНЯЛ ОЧЕРЕДЬ И ЖДЁТ ОСВОБОЖДЕНИЯ ОЧЕРЕДИ
    
    if(check_query(callback.from_user.id)): # Если очередь подошла
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text="Уйти на перерыв",
            callback_data="breakfast"),
        )
        
        await state.set_state(breakFastState.waiting_to_solution) #3 РЕШЕНИЕ ПО ПОВОДУ ОЧЕРЕДИ 
        #
        delete_this_message = await callback.message.answer(f"Очередь подошла. Чтобы выйти на перерыв, нажмите кнопку в течении ⚠️{time.solution_time.value} секунд⚠️.\nЕсли не нажать на кнопку, вы будете исключены из очереди",
                                      reply_markup=builder.as_markup() )
        await callback.answer() # Подтвердить получение от телеграмма
        
        # Время на принятие решения --------------------------------------------------------------------------------------------------

        if(await time_loop(dic_id_place=dic_time_solution, user_id=callback.from_user.id, callback=callback, time_sec=time.solution_time.value)):
            try:
               await delete_this_message.delete() # Удаляем последнее сообщение в списке        
            except:
                pass
            delete_this_message.pop() # и выкидываем его из списка
            
            await state.set_state(breakFastState.waiting_to_queue)
            await delet_in_query(callback.from_user.id) # Удаление челвоека из очереди
            
            builder_not_solution = InlineKeyboardBuilder()
            builder_not_solution.add(InlineKeyboardButton(
                    text="Возврат в меню",
                    callback_data="waiting_to_queue")
                    )
            await callback.message.answer(f"❌ Вы не успели принять решение и были исключены из очереди ❌\n Вернитесь в меню, чтобы зайти в очередь",
                                          reply_markup=builder_not_solution.as_markup() )    
            
    else:
        await callback.message.answer("Очередь занята, ожидайте своей очереди. Вам придёт уведомление")
        await callback.answer() # Подтвердить получение от телеграмма
        
        await asyncio.create_task(check_query_1(callback.from_user.id)) # ждём выполнения check_query_1
        try:
            await callback.message.delete()
        except:
            pass

        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text="Уйти на перерыв",
            callback_data="breakfast"),
        )
        
        await state.set_state(breakFastState.waiting_to_solution) #3 РЕШЕНИЕ ПО ПОВОДУ ОЧЕРЕДИ 
        delete_this_message = await callback.message.answer(f"Очередь подошла. Чтобы выйти на перерыв, нажмите кнопку в течении ⚠️{time.solution_time.value} секунд⚠️.\nЕсли не нажать на кнопку, вы будете исключены из очереди",
                                      reply_markup=builder.as_markup() )   
        await callback.answer() # Подтвердить получение от телеграмма
        
        # Время на принятие решения --------------------------------------------------------------------------------------------------

        if(await time_loop(dic_id_place=dic_time_solution, user_id=callback.from_user.id, callback=callback, time_sec=time.solution_time.value)):
            try:
                    await delete_this_message.delete() # Удаляем последнее сообщение в списке    
            except:
                pass
            
            await state.set_state(breakFastState.waiting_to_queue)
            await delet_in_query(callback.from_user.id) # Удаление челвоека из очереди
            
            builder_not_solution = InlineKeyboardBuilder()
            builder_not_solution.add(InlineKeyboardButton(
                    text="Возврат в меню",
                    callback_data="waiting_to_queue")
                    )
            await callback.message.answer(f"❌ Вы не успели принять решение и были исключены из очереди ❌\n Вернитесь в меню, чтобы зайти в очередь",
                                          reply_markup=builder_not_solution.as_markup() )  
           

@disp.callback_query(breakFastState.waiting_to_solution, F.data == "breakfast") #4 Перерыв
async def breakfast(callback: CallbackQuery, state: FSMContext):
    global dic_time_solution # Время на принятие решения --------------------------------------------
    dic_time_solution[callback.from_user.id] = False # Время на принятие решения --------------------------------------------
    
    global dic_break_more_XX_minuts # Время на принятие решения --------------------------------------------
    dic_break_more_XX_minuts[callback.from_user.id] = True # ключ: значение | id пользователя: опоздал ли он на перерыв 
    
    try:
        await callback.message.delete()
    except:
        pass
    
    
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Вернуться с перерыва",
        callback_data="waiting_to_queue")
    )
    await state.set_state(breakFastState.breakfast) #4 ПЕРЕРЫВ
    delete_this_message = await callback.message.answer(f"Вы на перерыве, чтобы вернуться нажмите на кнопку.\n Если вы будете на перерыве больше {time.break_time_minuts.value} минут, вас автоматически исключит из очереди ⬇️"
                                  , reply_markup=builder.as_markup())
    await callback.answer() # Подтвердить получение от телеграмма
  
    # Время на принятие решения --------------------------------------------------------------------------------------------------
    if(await time_loop(dic_id_place=dic_break_more_XX_minuts, user_id=callback.from_user.id, callback=callback, time_sec=time.break_time.value)):
        try:
            await delete_this_message.delete() # Удаляем последнее сообщение в списке    
        except:
            pass
        
        await state.set_state(breakFastState.waiting_to_queue)
        await delet_in_query(callback.from_user.id) # Удаление челвоека из очереди
            
        builder_not_solution = InlineKeyboardBuilder()
        builder_not_solution.add(InlineKeyboardButton(
                            text="Возврат в меню",
                            callback_data="waiting_to_queue")
                            )
        await callback.message.answer(f"❌ Вы были удалены с перерыва за отуствие более 15 минут ❌\nВернитесь в меню, чтобы повторно зайти в очередь",
                                              reply_markup=builder_not_solution.as_markup() )   
    
    
    
    

@disp.message() #Любая фраза вне контекста бота
async def any_message(message: Message):
    await message.delete()
    
#--------------------------------------------------------------------

# Запуск процесса поллинга  новых апдейтов (поиск обновлений от новых задач) // Polling, или опрос, – это процесс, при котором клиентский скрипт периодически отправляет запросы к серверу для проверки наличия новой инфы. 
async def main():
    await disp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
