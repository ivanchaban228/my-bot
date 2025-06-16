import sqlite3
from datetime import datetime, timedelta
from telegram import Update, ForceReply
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackContext
)
import asyncio

# Визначення станів для квізу
CHOOSING_SUBJECT, ASKING_QUESTION = range(2)

# Визначення станів для нагадувань
REMINDER, WAITING_FOR_TIME = range(2, 4)

# Визначення станів для /subjects
SELECTING_SUBJECT, SENDING_LINKS = range(4, 6)

# Посилання для кожного предмету

subject_links = {
    "математика": ["Курси з арифметики, алгебри та математичного аналізу: https://uk.khanacademy.org", "Сайт з завданнями, калькуляторами та теоретичними матеріалами для вивчення математики: https://ua.onlinemschool.com", "Онлайн-курси математики для дорослих: https://studyabroadnations.com/uk"],
    "фізика": ["Добірка з 40 онлайн-курсів фізики, включаючи термодинаміку, квантову механіку та електромагнетизм: https://www.guru99.com/uk/online-physics-course.html", "Інтерактивні симуляції з фізики: https://phet.colorado.edu/uk/simulations/filter?subjects=physics&type=html"],
    "хімія": ["Відеоуроки з  хімії: https://udhtu.edu.ua/onlajn-uroky-vid-him-tehu", "Курси для вичення хімії (для підвищення кваліфікації чи для самостійного вивчення): https://naurok.com.ua/upgrade/kursy-dlya-vchyteliv-khimiyi"],
    "біологія": ["Відеоуроки з біології: https://udhtu.edu.ua/onlajn-uroky-vid-him-tehu", "Ресурс дял дистанційного вивчення біології, включаючи ботаніку, зоологію, анатомію людини та загальну біологію: https://osvitanova.com.ua/posts/3593-biolohiia-dystantsiino-dobirka-korysnykh-onlain-resursiv"],
    "інформатика": ["БезкоштовнІ IT-курси: https://happymonday.ua/dobirka-bezkoshtovnyh-kursiv-it", "Вивчення програмування, тестування, дата-аналітику та Web3: https://www.enableme.com.ua/ua/article/najkrasi-bezkostovni-onlajn-kursi-dla-ukrainciv-11573"]
}

# Функція для команди /subjects
async def subjects(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    subjects_text = (
        "Доступні предмети:\n"
        "1. Математика\n"
        "2. Фізика\n"
        "3. Хімія\n"
        "4. Біологія\n"
        "5. Інформатика\n\n"
        "Виберіть номер або назву предмету, щоб отримати навчальні посилання."
    )
    await update.message.reply_text(subjects_text)
    return SELECTING_SUBJECT

# Функція для вибору предмету
async def choose_subject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip().lower()  # Убираємо зайві пробіли і робимо текст малими літерами
    subject_map = {
        "1": "математика",
        "2": "фізика",
        "3": "хімія",
        "4": "біологія",
        "5": "інформатика",
        "математика": "математика",
        "фізика": "фізика",
        "хімія": "хімія",
        "біологія": "біологія",
        "інформатика": "інформатика"
    }

    subject = subject_map.get(text)  # Отримуємо правильний предмет з мапи

    # Логування: перевіряємо, що отримано правильний предмет
    print(f"Вибраний предмет: {subject}")

    if subject and subject in subject_links:  # Якщо предмет знайдений у словнику subject_links
        links = "\n".join(subject_links[subject])  # Формуємо список посилань
        await update.message.reply_text(
            f"Ось корисні посилання для вивчення предмету *{subject.capitalize()}*:\n{links}",
            parse_mode="Markdown"  # Використовуємо формат Markdown для коректного відображення
        )
        return ConversationHandler.END  # Завершаємо розмову
    else:
        await update.message.reply_text("Будь ласка, оберіть дійсний предмет, використовуючи номери або назви.")
        return SELECTING_SUBJECT  # Повертаємось до вибору предмету
# Функція для команди /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
    f"Привіт, {user.mention_html()}! Я LearnHelper21Bot. Як можу допомогти вам сьогодні? Введіть команку /help щоб ознайомится з переліком дій",
        parse_mode="HTML",
        reply_markup=ForceReply(selective=True)
    )
# Функція для команди /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "Я можу надати наступні команди та функції:\n\n"
        "/start - Початок роботи з ботом та привітання.\n"
        "/help - Отримати список доступних команд та їх опис.\n"
        "/subjects - Дізнатися про доступні предмети та отримати навчальні посилання.\n"
        "/resources - Отримати корисні навчальні ресурси.\n"
        "/quiz - Пройти короткий тест з обраного предмета.\n"
        "/reminder - Встановити нагадування.\n"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")
# Функція для команди /resources
async def resources(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    resources_text = (
        "Ось корисні навчальні ресурси:\n"
        "• [Khan Academy](https://www.khanacademy.org)\n"
        "• [Coursera](https://www.coursera.org)\n"
        "• [edX](https://www.edx.org)\n"
        "• [YouTube EDU](https://www.youtube.com/education)"
    )
    await update.message.reply_text(resources_text, parse_mode="Markdown")
 # Функція для початку квізу (/quiz)
# Функція для отримання питань для вибраного предмета з бази даних
def get_questions_for_subject(subject: str):
    conn = sqlite3.connect('quiz_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT question, option1, option2, option3, option4, answer
        FROM quizzes WHERE subject = ?
    ''', (subject,))
    questions = cursor.fetchall()
    conn.close()
    return questions
# Логіка для старту квізу
async def quiz_start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Вибери предмет для квізу:\n"
                                    "1) Математика\n"
                                    "2) Фізика\n"
                                    "3) Хімія\n"
                                    "4) Біологія\n"
                                    "5) Інформатика\n"
                                    "Або введи назву предмета.")
    return CHOOSING_SUBJECT

# Логіка для вибору предмета
async def quiz_choose_subject(update: Update, context: CallbackContext) -> int:
    subject = update.message.text.lower()

    # Перевіряємо, чи введено число або назву предмета
    valid_subjects = {
        "математика": "математика",
        "фізика": "фізика",
        "хімія": "хімія",
        "біологія": "біологія",
        "інформатика": "інформатика",
        "1": "математика",
        "2": "фізика",
        "3": "хімія",
        "4": "біологія",
        "5": "інформатика"
    }
    
    if subject not in valid_subjects:
        await update.message.reply_text("Невірний предмет. Спробуй ще раз.")
        return CHOOSING_SUBJECT

    # Отримуємо питання для вибраного предмета
    subject = valid_subjects[subject]
    questions = get_questions_for_subject(subject)
    if not questions:
        await update.message.reply_text(f"Для предмету '{subject}' немає питань.")
        return ConversationHandler.END

    # Зберігаємо питання для наступних кроків
    context.user_data['questions'] = questions
    context.user_data['current_question_index'] = 0
    context.user_data['correct_answers'] = 0
    context.user_data['wrong_answers'] = 0

    # Переходимо до наступного стану
    return await ask_question(update, context)

# Логіка для запитання питання
async def ask_question(update: Update, context: CallbackContext) -> int:
    questions = context.user_data['questions']
    current_question_index = context.user_data['current_question_index']

    # Виводимо питання
    question = questions[current_question_index]
    await update.message.reply_text(f"Питання: {question[0]}\n"
                                    f"1) {question[1]}\n"
                                    f"2) {question[2]}\n"
                                    f"3) {question[3]}\n"
                                    f"4) {question[4]}\n"
                                    "Введи номер відповіді або текст.")

    return ASKING_QUESTION

# Логіка для обробки відповіді на питання
async def handle_quiz_answer(update: Update, context: CallbackContext) -> int:
    questions = context.user_data['questions']
    current_question_index = context.user_data['current_question_index']
    correct_answer = questions[current_question_index][5]

    # Перевірка відповіді
    user_answer = update.message.text.strip().lower()

    if user_answer in ["1", "2", "3", "4"]:
        user_answer_text = questions[current_question_index][int(user_answer)]
    else:
        user_answer_text = user_answer

    # Перевірка, чи правильна відповідь
    if user_answer_text.lower() == correct_answer.lower():
        context.user_data['correct_answers'] += 1
        await update.message.reply_text("Правильна відповідь!")
    else:
        context.user_data['wrong_answers'] += 1
        await update.message.reply_text(f"Неправильна відповідь! Правильна відповідь: {correct_answer}")

    # Переходимо до наступного питання
    current_question_index += 1
    if current_question_index < len(questions):
        context.user_data['current_question_index'] = current_question_index
        return await ask_question(update, context)

    # Якщо питання закінчилися
    correct = context.user_data['correct_answers']
    wrong = context.user_data['wrong_answers']
    await update.message.reply_text(f"Квіз завершено! Спасибі за участь.\n"
                                    f"Правильних відповідей: {correct}\n"
                                    f"Неправильних відповідей: {wrong}")
    return ConversationHandler.END

# Логіка для скасування квізу
async def cancel_quiz(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Квіз скасовано.")
    return ConversationHandler.END
 
# Імпортуємо функцію reminder_handler з reminders.py
from reminders import reminder_handler

# Завантажуємо всі обробники
def get_handlers():
    return [+
        CommandHandler("start", start),
        CommandHandler("help", help_command),
        CommandHandler("subjects", subjects),
        CommandHandler("resources", resources),
        reminder_handler,  # Додаємо обробник для нагадувань
        ConversationHandler(
            entry_points=[CommandHandler("quiz", quiz_start)],
            states={
                CHOOSING_SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, quiz_choose_subject)],
                ASKING_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_quiz_answer)],
            },
            fallbacks=[CommandHandler("cancel", cancel_quiz)],
        )
    ]