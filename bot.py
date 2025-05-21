import os
import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

# Conversation states
ASK_NAME, ASK_QUESTION = range(2)

# Test questions and correct answers
test_questions = [
    {"question": "1. Что такое полигональная модель в 3D-графике?\nA) Модель, построенная на основе полигонов\nB) Модель, использующая только кривые\nC) Текстурированная модель", "answer": "A"},
    {"question": "2. Какой формат файла чаще всего используется для переноса 3D-сцен между приложениями?\nA) .png\nB) .obj\nC) .mp4", "answer": "B"},
    {"question": "3. Что такое рендеринг в контексте CG-технологий?\nA) Процесс моделирования\nB) Процесс визуализации сцены\nC) Процесс захвата движений", "answer": "B"},
    {"question": "4. В ивент-индустрии для чего применяют LED-стены и проекционные экраны?\nA) Для озвучивания сцены\nB) Для визуального оформления и отображения 3D-контента\nC) Для охлаждения оборудования", "answer": "B"},
    {"question": "5. Что означает термин 'motion capture'?\nA) Захват движения актера для последующей анимации\nB) Запись звука на площадке\nC) Монтаж видео", "answer": "A"},
    {"question": "6. Что такое UV-маппинг?\nA) Проецирование 2D-текстур на 3D-модель\nB) Процесс освещения сцены\nC) Метод анимации", "answer": "A"},
    {"question": "7. Что такое шейдер?\nA) Программа для расчёта вычислений на GPU\nB) Файл сцены\nC) Инструмент моделирования", "answer": "A"},
    {"question": "8. Как называется метод визуализации, рассчитывающий световые лучи?\nA) Rasterization\nB) Ray tracing\nC) Baking", "answer": "B"},
    {"question": "9. Что делает нормал-маппинг?\nA) Добавляет цвет на модель\nB) Добавляет детализацию поверхности без увеличения полигонов\nC) Уменьшает размер текстур", "answer": "B"},
    {"question": "10. Для чего используется realtime 3D в ивент-индустрии?\nA) Создание интерактивных сцен в реальном времени\nB) Запись видео\nC) Отрисовка статичных изображений", "answer": "A"}
]

# File to store results
txt_file = 'results.txt'
keyboard = ReplyKeyboardMarkup([['A', 'B', 'C']], one_time_keyboard=True, resize_keyboard=True)

# Ensure results file exists and has header
def init_file():
    if not os.path.exists(txt_file):
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write('Timestamp\tName\tScore\tMax\n')

# Append result to text file
def save_result(name: str, score: int, max_score: int):
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(txt_file, 'a', encoding='utf-8') as f:
        f.write(f"{ts}\t{name}\t{score}\t{max_score}\n")

# /start handler
def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Привет! Как тебя зовут?', reply_markup=ReplyKeyboardRemove())
    return ASK_NAME

# Receive name and ask first question
def ask_questions(update: Update, context: CallbackContext) -> int:
    context.user_data['name'] = update.message.text.strip()
    context.user_data['score'] = 0
    context.user_data['q_index'] = 0
    q = test_questions[0]['question']
    update.message.reply_text(q, reply_markup=keyboard)
    return ASK_QUESTION

# Handle answer selection
def handle_answer(update: Update, context: CallbackContext) -> int:
    idx = context.user_data['q_index']
    answer = update.message.text.strip().upper()
    if answer == test_questions[idx]['answer']:
        context.user_data['score'] += 1
    idx += 1
    if idx < len(test_questions):
        context.user_data['q_index'] = idx
        q = test_questions[idx]['question']
        update.message.reply_text(q, reply_markup=keyboard)
        return ASK_QUESTION
    # Test complete
    name = context.user_data['name']
    score = context.user_data['score']
    max_score = len(test_questions)
    # Show restart button
    restart_kb = ReplyKeyboardMarkup([['Перезапустить тест']], one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text(
        f'Тест завершён, {name}! Результат: {score}/{max_score}',
        reply_markup=restart_kb
    )
    save_result(name, score, max_score)
    return ConversationHandler.END

# /cancel handler
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Тест прерван.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Main function
if __name__ == '__main__':
    init_file()
    TOKEN = '00000000000000000000000000000000000000000'
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    conv = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(Filters.regex('^Перезапустить тест$'), start)
        ],
        states={
            ASK_NAME: [MessageHandler(Filters.text & ~Filters.command, ask_questions)],
            ASK_QUESTION: [MessageHandler(Filters.regex('^(A|B|C)$'), handle_answer)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(conv)
    print('Bot started...')
    updater.start_polling()
    updater.idle()
