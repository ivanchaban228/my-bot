import asyncio 
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler

# Визначення станів для ConversationHandler
REMINDER, WAITING_FOR_TIME = range(2)

# Функція для команди /reminder
async def reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Будь ласка, введіть текст нагадування.")
    return REMINDER

# Функція для обробки тексту нагадування
async def process_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['reminder_text'] = update.message.text
    await update.message.reply_text("На який час ви хочете поставити нагадування? (Формат: ГГ:ХХ, наприклад, 13:50)")
    return WAITING_FOR_TIME

# Функція для налаштування часу нагадування
async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reminder_text = context.user_data.get('reminder_text', 'Нагадування')
    time_str = update.message.text

    try:
        # Отримати годину та хвилини
        reminder_time = datetime.strptime(time_str, "%H:%M").time()
        now = datetime.now()

        # Визначити час нагадування
        reminder_datetime = datetime.combine(now.date(), reminder_time)

        # Якщо час нагадування вже пройшов на сьогодні, встановити його на завтра
        if reminder_datetime < now:
            reminder_datetime += timedelta(days=1)

        wait_time = (reminder_datetime - now).total_seconds()

        await update.message.reply_text(f"Нагадування встановлено на {reminder_time}.")
        
        # Чекати до вказаного часу
        await asyncio.sleep(wait_time)
        await update.message.reply_text(f"⏰ Нагадування: {reminder_text}")

    except ValueError:
        await update.message.reply_text("Невірний формат. Будь ласка, введіть час у форматі ГГ:ХХ.")
    finally:
        return ConversationHandler.END

# Додайте нові обробники до вашого ConversationHandler
reminder_handler = ConversationHandler(
    entry_points=[CommandHandler('reminder', reminder)],
    states={
        REMINDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_reminder)],
        WAITING_FOR_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_reminder)],
    },
    fallbacks=[CommandHandler('cancel', lambda update, context: update.message.reply_text("Нагадування скасовано."))],
)