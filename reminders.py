import asyncio 
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)

# Визначення станів для ConversationHandler
REMINDER, WAITING_FOR_TIME = range(2)

# Функція для команди /reminder
async def reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Будь ласка, введіть текст нагадування.")
    return REMINDER

# Функція для обробки тексту нагадування
async def process_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['reminder_text'] = update.message.text
    await update.message.reply_text("На який час ви хочете поставити нагадування? (Формат: ГГ:ХХ, наприклад, 13:50)")
    return WAITING_FOR_TIME

# Окрема функція, яка викликається у фоновому режимі
async def send_reminder_after_delay(update: Update, text: str, delay: float):
    await asyncio.sleep(delay)
    try:
        await update.message.reply_text(f"⏰ Нагадування: {text}")
    except Exception as e:
        print(f"Помилка при надсиланні нагадування: {e}")

# Функція для налаштування часу нагадування
async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reminder_text = context.user_data.get('reminder_text', 'Нагадування')
    time_str = update.message.text

    try:
        reminder_time = datetime.strptime(time_str, "%H:%M").time()
        now = datetime.now()
        reminder_datetime = datetime.combine(now.date(), reminder_time)

        # Якщо час вже минув сьогодні — нагадування на завтра
        if reminder_datetime < now:
            reminder_datetime += timedelta(days=1)

        wait_time = (reminder_datetime - now).total_seconds()

        await update.message.reply_text(f"Нагадування встановлено на {reminder_time}.")

        # Запускаємо фонову задачу
        asyncio.create_task(send_reminder_after_delay(update, reminder_text, wait_time))

    except ValueError:
        await update.message.reply_text("Невірний формат. Будь ласка, введіть час у форматі ГГ:ХХ.")
    
    return ConversationHandler.END

# Обробник скасування
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Нагадування скасовано.")
    return ConversationHandler.END

# Обʼєкт обробника нагадувань
reminder_handler = ConversationHandler(
    entry_points=[CommandHandler('reminder', reminder)],
    states={
        REMINDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_reminder)],
        WAITING_FOR_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_reminder)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)
