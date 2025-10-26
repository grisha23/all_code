import logging
import random
import asyncio
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота (получите у @BotFather)
BOT_TOKEN = "8294607564:AAF85XpskAJ2axXTLu6aypf-Vygx_rqtuIY"

# Временная база данных в памяти
db = {
    'users': {}
}

# Символы для игровых автоматов
SLOT_SYMBOLS = ["🍒", "🍋", "🍊", "🍇", "🔔", "💎", "7️⃣"]

# Инициализация пользователя
def init_user(user_id, username):
    if user_id not in db['users']:
        db['users'][user_id] = {
            'username': username,
            'balance': 1000  # Стандартный начальный баланс
        }

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    init_user(user_id, username)
    
    # Создаем кнопку "Старт"
    keyboard = [[KeyboardButton("🚀 Старт")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🎮 Добро пожаловать в игровой бот!\n\n"
        "Нажмите кнопку ниже, чтобы начать играть!",
        reply_markup=reply_markup
    )

# Главное меню
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = db['users'][user_id]
    
    balance = user_data['balance']
    
    # Клавиатура главного меню
    keyboard = [
        ["🎰 Бандит", "🎡 Рулетка"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        f"🏠 *Главное меню*\n\n"
        f"💵 Баланс: *{balance} монет*\n\n"
        f"Выберите игру:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Меню выбора ставки для Бандита
async def bandit_bet_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = db['users'][user_id]
    
    keyboard = [
        ["50 🎰", "100 🎰", "200 🎰"],
        ["500 🎰", "💵 Своя ставка", "🔙 Назад"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # Сохраняем текущее меню в контексте
    context.user_data['current_menu'] = 'bandit'
    
    await update.message.reply_text(
        f"🎰 *ИГРОВЫЕ АВТОМАТЫ*\n\n"
        f"💵 Ваш баланс: *{user_data['balance']} монет*\n"
        f"Выберите ставку или введите свою:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Меню выбора ставки для Рулетки
async def roulette_bet_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = db['users'][user_id]
    
    keyboard = [
        ["50 🎡", "100 🎡", "200 🎡"],
        ["500 🎡", "💵 Своя ставка", "🔙 Назад"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # Сохраняем текущее меню в контексте
    context.user_data['current_menu'] = 'roulette'
    
    await update.message.reply_text(
        f"🎡 *РУЛЕТКА*\n\n"
        f"💵 Ваш баланс: *{user_data['balance']} монет*\n"
        f"Выберите ставку или введите свою:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Меню выбора цвета для Рулетки после выбора ставки
async def roulette_color_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, bet_amount):
    user_id = update.effective_user.id
    user_data = db['users'][user_id]
    
    # Сохраняем ставку в контексте пользователя
    context.user_data['roulette_bet'] = bet_amount
    
    keyboard = [
        ["🔴 Красный", "⚫ Черный"],
        ["🟢 Зеленый", "🔙 Назад"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        f"🎡 *РУЛЕТКА*\n\n"
        f"💰 Ваша ставка: *{bet_amount} монет*\n"
        f"💵 Ваш баланс: *{user_data['balance']} монет*\n\n"
        f"Выберите цвет:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Обработка своей ставки
async def handle_custom_bet(update: Update, context: ContextTypes.DEFAULT_TYPE, game_type):
    user_id = update.effective_user.id
    user_data = db['users'][user_id]
    
    await update.message.reply_text(
        f"💵 Введите сумму ставки (от 10 до {user_data['balance']} монет):"
    )
    # Сохраняем тип игры для обработки ввода
    context.user_data['awaiting_bet'] = game_type

# Анимация 1: Быстрое вращение для Бандита
async def bandit_animation_fast(update: Update, context: ContextTypes.DEFAULT_TYPE, final_slots, bet_amount):
    message = await update.message.reply_text("🎰 Крутим барабаны...")
    
    # Быстрая анимация вращения
    for i in range(6):
        temp_slots = [random.choice(SLOT_SYMBOLS) for _ in range(3)]
        slot_display = f"┌───┐ ┌───┐ ┌───┐\n│ {temp_slots[0]} │ │ {temp_slots[1]} │ │ {temp_slots[2]} │\n└───┘ └───┘ └───┘"
        await message.edit_text(f"🎰 Крутим барабаны...\n\n{slot_display}")
        await asyncio.sleep(0.2)
    
    # Финальный результат
    slot_display = f"┌───┐ ┌───┐ ┌───┐\n│ {final_slots[0]} │ │ {final_slots[1]} │ │ {final_slots[2]} │\n└───┘ └───┘ └───┘"
    await message.edit_text(f"🎰 Результат:\n\n{slot_display}")

# Анимация 2: Медленное вращение для Бандита с затуханием
async def bandit_animation_slow(update: Update, context: ContextTypes.DEFAULT_TYPE, final_slots, bet_amount):
    message = await update.message.reply_text("🎰 Запускаем автомат...")
    await asyncio.sleep(0.5)
    
    # Медленная анимация с затуханием скорости
    speeds = [0.4, 0.3, 0.3, 0.2, 0.2, 0.1]
    
    for i, speed in enumerate(speeds):
        if i < len(speeds) - 1:  # Не последняя итерация
            temp_slots = [random.choice(SLOT_SYMBOLS) for _ in range(3)]
        else:  # Последняя итерация - финальный результат
            temp_slots = final_slots
            
        slot_display = f"┌───┐ ┌───┐ ┌───┐\n│ {temp_slots[0]} │ │ {temp_slots[1]} │ │ {temp_slots[2]} │\n└───┘ └───┘ └───┘"
        text = "🎰 Замедляемся..." if i >= 3 else "🎰 Крутим барабаны..."
        await message.edit_text(f"{text}\n\n{slot_display}")
        await asyncio.sleep(speed)

# Анимация 3: Поочередная остановка барабанов
async def bandit_animation_sequential(update: Update, context: ContextTypes.DEFAULT_TYPE, final_slots, bet_amount):
    message = await update.message.reply_text("🎰 Запускаем автомат...")
    
    # Все барабаны крутятся
    for i in range(4):
        temp_slots = [random.choice(SLOT_SYMBOLS) for _ in range(3)]
        slot_display = f"┌───┐ ┌───┐ ┌───┐\n│ {temp_slots[0]} │ │ {temp_slots[1]} │ │ {temp_slots[2]} │\n└───┘ └───┘ └───┘"
        await message.edit_text(f"🎰 Крутим все барабаны...\n\n{slot_display}")
        await asyncio.sleep(0.3)
    
    # Останавливаем первый барабан
    temp_slots = [final_slots[0], random.choice(SLOT_SYMBOLS), random.choice(SLOT_SYMBOLS)]
    slot_display = f"┌───┐ ┌───┐ ┌───┐\n│ {temp_slots[0]} │ │ {temp_slots[1]} │ │ {temp_slots[2]} │\n└───┘ └───┘ └───┘"
    await message.edit_text(f"🎰 Останавливаем первый барабан...\n\n{slot_display}")
    await asyncio.sleep(0.5)
    
    # Останавливаем второй барабан
    temp_slots = [final_slots[0], final_slots[1], random.choice(SLOT_SYMBOLS)]
    slot_display = f"┌───┐ ┌───┐ ┌───┐\n│ {temp_slots[0]} │ │ {temp_slots[1]} │ │ {temp_slots[2]} │\n└───┘ └───┘ └───┘"
    await message.edit_text(f"🎰 Останавливаем второй барабан...\n\n{slot_display}")
    await asyncio.sleep(0.5)
    
    # Финальный результат
    slot_display = f"┌───┐ ┌───┐ ┌───┐\n│ {final_slots[0]} │ │ {final_slots[1]} │ │ {final_slots[2]} │\n└───┘ └───┘ └───┘"
    await message.edit_text(f"🎰 Финальный результат!\n\n{slot_display}")

# Анимация 1: Быстрое вращение для Рулетки
async def roulette_animation_fast(update: Update, context: ContextTypes.DEFAULT_TYPE, winning_number):
    message = await update.message.reply_text("🎡 Запускаем рулетку...")
    
    # Быстрое вращение
    for i in range(10):
        temp_number = random.randint(0, 36)
        color = "🟢" if temp_number == 0 else "🔴" if temp_number % 2 == 1 else "⚫"
        await message.edit_text(f"🎡 Крутим рулетку...\n\n🎲 Выпадает: *{temp_number}* {color}", parse_mode='Markdown')
        await asyncio.sleep(0.2)
    
    # Финальный результат
    final_color = "🟢" if winning_number == 0 else "🔴" if winning_number % 2 == 1 else "⚫"
    await message.edit_text(f"🎡 Результат!\n\n🎲 Выпало: *{winning_number}* {final_color}", parse_mode='Markdown')

# Анимация 2: Медленное вращение с затуханием для Рулетки
async def roulette_animation_slow(update: Update, context: ContextTypes.DEFAULT_TYPE, winning_number):
    message = await update.message.reply_text("🎡 Запускаем рулетку...")
    await asyncio.sleep(0.5)
    
    # Медленная анимация с затуханием скорости
    speeds = [0.5, 0.4, 0.4, 0.3, 0.3, 0.2, 0.2, 0.1]
    
    for i, speed in enumerate(speeds):
        if i < len(speeds) - 1:  # Не последняя итерация
            temp_number = random.randint(0, 36)
        else:  # Последняя итерация - финальный результат
            temp_number = winning_number
            
        color = "🟢" if temp_number == 0 else "🔴" if temp_number % 2 == 1 else "⚫"
        text = "🎡 Замедляемся..." if i >= 5 else "🎡 Крутим рулетку..."
        await message.edit_text(f"{text}\n\n🎲 Выпадает: *{temp_number}* {color}", parse_mode='Markdown')
        await asyncio.sleep(speed)

# Анимация 3: Счетчик чисел для Рулетки
async def roulette_animation_counter(update: Update, context: ContextTypes.DEFAULT_TYPE, winning_number):
    message = await update.message.reply_text("🎡 Запускаем рулетку...")
    
    # Быстрый прогон чисел
    for i in range(15):
        temp_number = (i * 3) % 37
        color = "🟢" if temp_number == 0 else "🔴" if temp_number % 2 == 1 else "⚫"
        await message.edit_text(f"🎡 Крутим рулетку...\n\n🎲 Выпадает: *{temp_number}* {color}", parse_mode='Markdown')
        await asyncio.sleep(0.15)
    
    # Медленный подход к финальному числу
    start_num = (winning_number - 5) % 37
    for i in range(6):
        temp_number = (start_num + i) % 37
        color = "🟢" if temp_number == 0 else "🔴" if temp_number % 2 == 1 else "⚫"
        await message.edit_text(f"🎡 Замедляемся...\n\n🎲 Выпадает: *{temp_number}* {color}", parse_mode='Markdown')
        await asyncio.sleep(0.3)
    
    # Финальный результат
    final_color = "🟢" if winning_number == 0 else "🔴" if winning_number % 2 == 1 else "⚫"
    await message.edit_text(f"🎡 Финальный результат!\n\n🎲 Выпало: *{winning_number}* {final_color}", parse_mode='Markdown')

# Игра "Бандит" со случайной анимацией
async def play_bandit(update: Update, context: ContextTypes.DEFAULT_TYPE, bet_amount):
    user_id = update.effective_user.id
    user_data = db['users'][user_id]
    
    if user_data['balance'] < bet_amount:
        await update.message.reply_text(f"❌ Недостаточно монет! Ваш баланс: {user_data['balance']} монет")
        return
    
    if bet_amount < 10:
        await update.message.reply_text("❌ Минимальная ставка: 10 монет")
        return
    
    # Вычитаем ставку
    user_data['balance'] -= bet_amount
    
    # Генерируем слоты
    slots = [random.choice(SLOT_SYMBOLS) for _ in range(3)]
    
    # Выбираем случайную анимацию из 3 вариантов
    animation_type = random.randint(1, 3)
    
    if animation_type == 1:
        await bandit_animation_fast(update, context, slots, bet_amount)
    elif animation_type == 2:
        await bandit_animation_slow(update, context, slots, bet_amount)
    else:
        await bandit_animation_sequential(update, context, slots, bet_amount)
    
    # Проверяем выигрыш
    win = False
    win_amount = 0
    multiplier = bet_amount / 50  # Базовый множитель от ставки
    
    if slots[0] == slots[1] == slots[2]:
        if slots[0] == "💎":
            win_amount = int(500 * multiplier)
        elif slots[0] == "7️⃣":
            win_amount = int(300 * multiplier)
        elif slots[0] == "🔔":
            win_amount = int(200 * multiplier)
        else:
            win_amount = int(100 * multiplier)
        win = True
    elif slots[0] == slots[1] or slots[1] == slots[2]:
        win_amount = int(25 * multiplier)
        win = True
    
    if win:
        user_data['balance'] += win_amount
        result_text = f"🎉 ПОБЕДА! +{win_amount} монет!"
    else:
        result_text = "😔 Проигрыш"
    
    await update.message.reply_text(
        f"🎰 *ИГРОВЫЕ АВТОМАТЫ*\n\n"
        f"💰 Ставка: *{bet_amount} монет*\n"
        f"{result_text}\n"
        f"💵 Новый баланс: *{user_data['balance']} монет*",
        parse_mode='Markdown'
    )

# Игра "Рулетка" со случайной анимацией
async def play_roulette(update: Update, context: ContextTypes.DEFAULT_TYPE, chosen_color, bet_amount):
    user_id = update.effective_user.id
    user_data = db['users'][user_id]
    
    if user_data['balance'] < bet_amount:
        await update.message.reply_text(f"❌ Недостаточно монет! Ваш баланс: {user_data['balance']} монет")
        return
    
    if bet_amount < 10:
        await update.message.reply_text("❌ Минимальная ставка: 10 монет")
        return
    
    # Вычитаем ставку
    user_data['balance'] -= bet_amount
    
    # Генерируем число рулетки (0-36)
    winning_number = random.randint(0, 36)
    
    # Определяем цвет выигрышного числа
    if winning_number == 0:
        winning_color = "green"
        winning_color_emoji = "🟢"
    elif winning_number % 2 == 1:
        winning_color = "red"
        winning_color_emoji = "🔴"
    else:
        winning_color = "black" 
        winning_color_emoji = "⚫"
    
    # Выбираем случайную анимацию из 3 вариантов
    animation_type = random.randint(1, 3)
    
    if animation_type == 1:
        await roulette_animation_fast(update, context, winning_number)
    elif animation_type == 2:
        await roulette_animation_slow(update, context, winning_number)
    else:
        await roulette_animation_counter(update, context, winning_number)
    
    # Определяем выигрыш
    win = False
    win_amount = 0
    
    color_mapping = {
        "red": "🔴 Красный",
        "black": "⚫ Черный", 
        "green": "🟢 Зеленый"
    }
    
    chosen_color_text = color_mapping.get(chosen_color, chosen_color)
    
    if chosen_color == winning_color:
        if chosen_color == "green":
            win_amount = bet_amount * 14  # 14 к 1 за зеро
        else:
            win_amount = bet_amount * 2  # 2 к 1 за красный/черный
        win = True
    
    if win:
        user_data['balance'] += win_amount
        result_text = f"🎉 ПОБЕДА! +{win_amount} монет!"
    else:
        result_text = f"😔 Проигрыш. Выиграл {winning_color_emoji}"
    
    await update.message.reply_text(
        f"🎡 *РУЛЕТКА*\n\n"
        f"🎲 Выпало: *{winning_number}* {winning_color_emoji}\n"
        f"🎨 Ваша ставка: {chosen_color_text}\n"
        f"💰 Ставка: *{bet_amount} монет*\n\n"
        f"{result_text}\n"
        f"💵 Новый баланс: *{user_data['balance']} монет*",
        parse_mode='Markdown'
    )

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    # Инициализируем пользователя если его нет
    if user_id not in db['users']:
        init_user(user_id, update.effective_user.username)
    
    # Проверяем, ожидаем ли мы ввод ставки
    if 'awaiting_bet' in context.user_data:
        game_type = context.user_data['awaiting_bet']
        try:
            bet_amount = int(text)
            user_data = db['users'][user_id]
            
            if bet_amount < 10:
                await update.message.reply_text("❌ Минимальная ставка: 10 монет")
            elif bet_amount > user_data['balance']:
                await update.message.reply_text(f"❌ Недостаточно монет! Ваш баланс: {user_data['balance']} монет")
            else:
                if game_type == 'bandit':
                    await play_bandit(update, context, bet_amount)
                    await asyncio.sleep(1)
                    await bandit_bet_menu(update, context)
                elif game_type == 'roulette':
                    await roulette_color_menu(update, context, bet_amount)
                
                # Очищаем состояние ожидания ставки
                del context.user_data['awaiting_bet']
            return
        except ValueError:
            await update.message.reply_text("❌ Пожалуйста, введите число для ставки")
            return
    
    if text == "🚀 Старт":
        await show_main_menu(update, context)
    
    elif text == "🎰 Бандит":
        await bandit_bet_menu(update, context)
    
    elif text == "🎡 Рулетка":
        await roulette_bet_menu(update, context)
    
    elif text in ["50 🎰", "100 🎰", "200 🎰", "500 🎰"]:
        bet_amount = int(text.split()[0])
        await play_bandit(update, context, bet_amount)
        await asyncio.sleep(1)
        await bandit_bet_menu(update, context)
    
    elif text in ["50 🎡", "100 🎡", "200 🎡", "500 🎡"]:
        bet_amount = int(text.split()[0])
        await roulette_color_menu(update, context, bet_amount)
    
    elif text == "💵 Своя ставка":
        current_menu = context.user_data.get('current_menu')
        if current_menu == 'bandit':
            await handle_custom_bet(update, context, 'bandit')
        elif current_menu == 'roulette':
            await handle_custom_bet(update, context, 'roulette')
        else:
            await update.message.reply_text("❌ Пожалуйста, выберите игру сначала")
    
    elif text in ["🔴 Красный", "⚫ Черный", "🟢 Зеленый"]:
        if 'roulette_bet' in context.user_data:
            bet_amount = context.user_data['roulette_bet']
            color_map = {
                "🔴 Красный": "red",
                "⚫ Черный": "black", 
                "🟢 Зеленый": "green"
            }
            chosen_color = color_map[text]
            await play_roulette(update, context, chosen_color, bet_amount)
            await asyncio.sleep(1)
            # Очищаем ставку из контекста
            del context.user_data['roulette_bet']
            await roulette_bet_menu(update, context)
        else:
            await update.message.reply_text("❌ Сначала выберите ставку")
            await roulette_bet_menu(update, context)
    
    elif text == "🔙 Назад":
        # Очищаем все временные данные
        if 'awaiting_bet' in context.user_data:
            del context.user_data['awaiting_bet']
        if 'roulette_bet' in context.user_data:
            del context.user_data['roulette_bet']
        if 'current_menu' in context.user_data:
            del context.user_data['current_menu']
        await show_main_menu(update, context)
    
    else:
        # Если это число, проверяем не пытается ли пользователь ввести ставку
        try:
            bet_amount = int(text)
            current_menu = context.user_data.get('current_menu')
            if current_menu in ['bandit', 'roulette']:
                await handle_custom_bet(update, context, current_menu)
            else:
                await update.message.reply_text("Используйте кнопки меню для навигации!")
        except ValueError:
            await update.message.reply_text("Используйте кнопки меню для навигации!")

# Обработка ошибок
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f'Update {update} caused error {context.error}')

def main():
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error)
    
    # Запускаем бота
    print("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()