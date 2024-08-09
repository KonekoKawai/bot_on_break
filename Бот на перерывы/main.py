import config_reader
from config_reader import *

#------------------------------------------------------------------------------------------------------------------------

class time(enum.Enum):
    break_time = 900 # Время перерыва в секундах 
    break_time_minuts = 15 # Время перерыва в минутах
    solution_time = 60 # Время на принятия решения по поводу перерыва

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


@disp.message(Command("reboot")) #Перезапуск бота
async def cmd_reboot(message: Message, state: FSMContext):
    await message.delete()
    await state.set_state(None) # ОТЧИЩАЕМ состояния
    await message.answer( "<b>Бот перезапущен</b>", parse_mode=ParseMode.HTML)

@disp.message(Command("start")) #1 Первый запуск бота Запускает либо #2 либо #3
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
        "Нажми на кнопку, чтобы занять очередь ",
        reply_markup=builder.as_markup()
    )
    
    
@disp.callback_query(F.data == "waiting_to_queue") #1 Эмитация первого запуска Запускает либо #2 либо #3
async def new_start(callback: CallbackQuery, state: FSMContext):
    global dic_break_more_XX_minuts # Время на принятие решения --------------------------------------------
    dic_break_more_XX_minuts[callback.from_user.id] = False # Время на принятие решения --------------------------------------------

    
    await callback.message.delete() # Удаления предыдущих инлайнов
    
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
    
    delete_this_message = [] # Список для удаления сообщения
    delete_this_message.clear()
    
    await callback.message.delete() # Удаления предыдущих инлайнов
    
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
        delete_this_message.append(await callback.message.answer(f"Очередь подошла. Чтобы выйти на перерыв, нажмите кнопку в течении ⚠️{time.solution_time.value} секунд⚠️.\nЕсли не нажать на кнопку, вы будете исключены из очереди",
                                      reply_markup=builder.as_markup() ))
        await callback.answer() # Подтвердить получение от телеграмма

        # Время на принятие решения --------------------------------------------------------------------------------------------------
        await asyncio.sleep(time.solution_time.value/2) # Если пользователь за определенное время не вернётся на перерыв, его выкидывает с перерыва
        if(dic_time_solution[callback.from_user.id] == True):
            delete_this_message.append(await callback.message.answer(f"⚠️ У вас осталось меньше {int(time.solution_time.value/2)} секунд на принятие решения ⚠️")
                                       )
            await asyncio.sleep(time.solution_time.value/2) # Если пользователь за определенное время не вернётся на перерыв, его выкидывает с перерыва 
            
            await delete_this_message[len(delete_this_message)-1].delete() # Удаляем последнее сообщение в списке
            delete_this_message.pop() # и выкидываем его из списка
         
            
            if(dic_time_solution[callback.from_user.id] == True): # Время на принятие решения ИСТЕКЛО --------------------------------------------
                await delete_this_message[len(delete_this_message)-1].delete() # Удаляем последний элемент 
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
        await callback.message.delete()

        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text="Уйти на перерыв",
            callback_data="breakfast"),
        )
        
        await state.set_state(breakFastState.waiting_to_solution) #3 РЕШЕНИЕ ПО ПОВОДУ ОЧЕРЕДИ 
        delete_this_message.append(await callback.message.answer(f"Очередь подошла. Чтобы выйти на перерыв, нажмите кнопку в течении ⚠️{time.solution_time.value} секунд⚠️.\nЕсли не нажать на кнопку, вы будете исключены из очереди",
                                      reply_markup=builder.as_markup() )
                                   )   
        await callback.answer() # Подтвердить получение от телеграмма
        
        # Время на принятие решения --------------------------------------------------------------------------------------------------
        await asyncio.sleep(time.solution_time.value/2) # Если пользователь за определенное время не вернётся на перерыв, его выкидывает с перерыва
        
        if(dic_time_solution[callback.from_user.id] == True):
            delete_this_message.append(await callback.message.answer(f"⚠️ У вас осталось меньше {int(time.solution_time.value/2)} секунд на принятие решения ⚠️")
                        )
            await asyncio.sleep(time.solution_time.value/2) # Если пользователь за определенное время не вернётся на перерыв, его выкидывает с перерыва  
            
            await delete_this_message[len(delete_this_message)-1].delete() # Удаляем последнее сообщение в списке
            delete_this_message.pop() # и выкидываем его из списка
            
            if(dic_time_solution[callback.from_user.id] == True): # Время на принятие решения --------------------------------------------
                await delete_this_message[len(delete_this_message)-1].delete() # Удаляем последнее сообщение в списке
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
      

@disp.callback_query(breakFastState.waiting_to_solution, F.data == "breakfast") #4 Перерыв
async def breakfast(callback: CallbackQuery, state: FSMContext):
    global dic_time_solution # Время на принятие решения --------------------------------------------
    dic_time_solution[callback.from_user.id] = False # Время на принятие решения --------------------------------------------
    
    global dic_break_more_XX_minuts # Время на принятие решения --------------------------------------------
    dic_break_more_XX_minuts[callback.from_user.id] = True # ключ: значение | id пользователя: опоздал ли он на перерыв 
    
    delete_this_message = [] # Список для удаления сообщения
    delete_this_message.clear()
    
    await callback.message.delete()
    
    
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Вернуться с перерыва",
        callback_data="waiting_to_queue")
    )
    await state.set_state(breakFastState.breakfast) #4 ПЕРЕРЫВ
    delete_this_message.append(await callback.message.answer(f"Вы на перерыве, чтобы вернуться нажмите на кнопку.\n Если вы будете на перерыве больше {time.break_time_minuts.value} минут, вас автоматически исключит из очереди ⬇️"
                                  , reply_markup=builder.as_markup()))
    await callback.answer() # Подтвердить получение от телеграмма
  
    # Время на принятие решения --------------------------------------------------------------------------------------------------
    await asyncio.sleep(time.break_time.value/3) # Если пользователь за определенное время не вернётся на перерыв, его выкидывает с перерыва 
    
    if(dic_break_more_XX_minuts[callback.from_user.id] == True):
        delete_this_message.append(await callback.message.answer(f"⚠️ У вас осталось меньше {int(time.break_time_minuts.value*2/3)} минут на перерыв  ⚠️")
                                   )
        await asyncio.sleep(time.break_time.value/3) # Если пользователь за определенное время не вернётся на перерыв, его выкидывает с перерыва 
        
        await delete_this_message[len(delete_this_message)-1].delete() # Удаляем послений элемент 
        delete_this_message.pop() # и удаляем его из списка
        
        if(dic_break_more_XX_minuts[callback.from_user.id] == True):
            
            
            delete_this_message.append(await callback.message.answer(f"⚠️ У вас осталось меньше {int(time.break_time_minuts.value/3)} минут на перерыв  ⚠️")
                                       )
            await asyncio.sleep(time.break_time.value/3) # Если пользователь за определенное время не вернётся на перерыв, его выкидывает с перерыва 
            
            await delete_this_message[len(delete_this_message)-1].delete() # Удаляем послений элемент 
            delete_this_message.pop() # и удаляем его из списка
            
            if(dic_break_more_XX_minuts[callback.from_user.id] == True): # Время на принятие решения --------------------------------------------
                
                await delete_this_message[len(delete_this_message)-1].delete() # Удаляем послений элемент 
                delete_this_message.pop() # и удаляем его из списка
                
                await state.set_state(breakFastState.waiting_to_queue)
                await callback.message.answer("❌ Вы были удалены с перерыва за отуствие более 15 минут ")
                await delet_in_query(callback.from_user.id) # Удаление челвоека из очереди
            
                builder_not_solution = InlineKeyboardBuilder()
                builder_not_solution.add(InlineKeyboardButton(
                            text="Возврат в меню",
                            callback_data="waiting_to_queue")
                            )
                delete_this_message.append(await callback.message.answer(f"Вернитесь в меню, чтобы повторно зайти в очередь",
                                              reply_markup=builder_not_solution.as_markup() )
                )
                await asyncio.sleep(time.break_time)
                if delete_this_message: # Если не пуст
                    await delete_this_message[len(delete_this_message)-1].delete() # Удаляем послений элемент 
                    delete_this_message.pop() # и удаляем его из списка
                
                
    
    

@disp.message() #Любая фраза вне контекста бота
async def any_message(message: Message):
    await message.delete()
    
#--------------------------------------------------------------------

# Запуск процесса поллинга  новых апдейтов (поиск обновлений от новых задач) // Polling, или опрос, – это процесс, при котором клиентский скрипт периодически отправляет запросы к серверу для проверки наличия новой инфы. 
async def main():
    await disp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
