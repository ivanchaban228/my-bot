import asyncio
import nest_asyncio
nest_asyncio.apply()

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)
from config import TOKEN
from handlers import (
    start,
    help_command,
    subjects,
    choose_subject,
    resources,
    quiz_start,
    quiz_choose_subject,
    ask_question,
    handle_quiz_answer,
    cancel_quiz,
    reminder_handler 
)

# Визначаємо стани для /subjects
SELECTING_SUBJECT, SENDING_LINKS = range(4, 6)

# Визначаємо стани для /quiz
CHOOSING_SUBJECT, ASKING_QUESTION = range(2)

async def main() -> None:
    # Створюємо додаток
    application = ApplicationBuilder().token(TOKEN).build()

    # Додаємо обробники команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("resources", resources))


    # Налаштовуємо ConversationHandler для /subjects
    subjects_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("subjects", subjects)],  # Початкова команда
        states={
            SELECTING_SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_subject)],
        },
        fallbacks=[],  # Можна додати обробник відміни, якщо потрібно
    )
    application.add_handler(subjects_conv_handler)

    # Налаштовуємо ConversationHandler для /quiz
    quiz_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("quiz", quiz_start)],
        states={
            CHOOSING_SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, quiz_choose_subject)],
            ASKING_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_quiz_answer)],
        },
        fallbacks=[CommandHandler("cancel", cancel_quiz)],
    )
    application.add_handler(quiz_conv_handler)

    # Обробник для нагадувань
    application.add_handler(reminder_handler)

    # Запускаємо бота
    await application.run_polling()

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(main())
    except RuntimeError as e:
        if "This event loop is already running" in str(e):
            print("Event loop is already running. Scheduling main() as a task.")
            loop.create_task(main())
            loop.run_forever()
        else:
            raise e