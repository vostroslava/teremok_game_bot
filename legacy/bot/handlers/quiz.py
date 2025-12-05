from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, 
    ConversationHandler, 
    MessageHandler, 
    CallbackQueryHandler, 
    filters,
    CommandHandler
)
from bot.resources import (
    QUIZ_INTRO, QUIZ_QUESTIONS, QUIZ_FINAL,
    BTN_QUIZ
)

# Состояния
Q1, Q2 = range(2)

async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало квиза."""
    context.user_data["score"] = 0
    
    # Показываем интро и сразу первый вопрос
    await update.message.reply_text(QUIZ_INTRO, parse_mode="Markdown")
    
    return await ask_question(update, context, 0)

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE, q_index: int):
    """Задает вопрос по индексу."""
    question = QUIZ_QUESTIONS[q_index]
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text, callback_data=f"ans_{code}")] 
        for code, text in question["options"]
    ])
    
    text = question["text"]
    
    # Если это первый вопрос, отправляем новое сообщение, иначе редактируем (если вызов из callback)
    if update.callback_query:
        await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        await update.message.reply_text(text=text, reply_markup=keyboard)
        
    return q_index

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ответ."""
    query = update.callback_query
    await query.answer()
    
    # Определяем текущий вопрос
    # В реальном проекте лучше хранить current_q_index в user_data
    # Здесь для простоты используем жесткую привязку к состояниям
    # Но так как у нас всего 2 вопроса, можно сделать проще
    
    # Определяем индекс вопроса по состоянию? Нет, лучше передавать в callback
    # Но callback ограничен.
    
    # Давайте сделаем универсальный хендлер, который смотрит на user_data["q_index"]
    q_index = context.user_data.get("q_index", 0)
    question = QUIZ_QUESTIONS[q_index]
    
    answer = query.data.replace("ans_", "")
    is_correct = answer == question["correct"]
    
    if is_correct:
        context.user_data["score"] += 1
        feedback = question["feedback_ok"]
    else:
        feedback = question["feedback_wrong"]
        
    await query.message.reply_text(feedback)
    
    # Следующий вопрос
    next_q_index = q_index + 1
    context.user_data["q_index"] = next_q_index
    
    if next_q_index < len(QUIZ_QUESTIONS):
        # Задаем следующий вопрос (новым сообщением, так как предыдущее было ответом на фидбек)
        # Или можно отправить фидбек и сразу вопрос
        return await ask_question_msg(query.message, context, next_q_index)
    else:
        # Финал
        score = context.user_data["score"]
        total = len(QUIZ_QUESTIONS)
        await query.message.reply_text(
            QUIZ_FINAL.format(score=score, total=total),
            parse_mode="Markdown"
        )
        return ConversationHandler.END

async def ask_question_msg(message, context, q_index):
    """Вспомогательная функция для отправки вопроса сообщением."""
    question = QUIZ_QUESTIONS[q_index]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text, callback_data=f"ans_{code}")] 
        for code, text in question["options"]
    ])
    await message.reply_text(text=question["text"], reply_markup=keyboard)
    return Q1 if q_index == 0 else Q2 # Возвращаем состояние (костыль для примера)

# Упростим: сделаем отдельные функции для каждого шага, чтобы ConversationHandler работал корректно
# с состояниями.

async def answer_q1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    question = QUIZ_QUESTIONS[0]
    answer = query.data.replace("ans_", "")
    
    if answer == question["correct"]:
        context.user_data["score"] += 1
        await query.message.reply_text(question["feedback_ok"])
    else:
        await query.message.reply_text(question["feedback_wrong"])
        
    # Переход ко 2 вопросу
    return await ask_question_msg(query.message, context, 1)

async def answer_q2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    question = QUIZ_QUESTIONS[1]
    answer = query.data.replace("ans_", "")
    
    if answer == question["correct"]:
        context.user_data["score"] += 1
        await query.message.reply_text(question["feedback_ok"])
    else:
        await query.message.reply_text(question["feedback_wrong"])
        
    # Финал
    score = context.user_data["score"]
    total = len(QUIZ_QUESTIONS)
    await query.message.reply_text(
        QUIZ_FINAL.format(score=score, total=total),
        parse_mode="Markdown"
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Квиз прерван.")
    return ConversationHandler.END

quiz_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(f"^{BTN_QUIZ}$"), start_quiz)],
    states={
        0: [CallbackQueryHandler(answer_q1, pattern="^ans_")], # Состояние 0 (Q1)
        1: [CallbackQueryHandler(answer_q2, pattern="^ans_")], # Состояние 1 (Q2)
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
