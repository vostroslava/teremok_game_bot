from telegram import Update
from telegram.ext import (
    ContextTypes, 
    ConversationHandler, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler, 
    filters
)
from bot.resources import (
    DIAG_INTRO_TEXT, DIAG_Q2_TEXT, DIAG_Q3_TEXT, 
    DIAG_EMAIL_TEXT, DIAG_FINAL_TEXT,
    PROBLEM_KEYBOARD, ENGAGEMENT_KEYBOARD,
    BTN_DIAGNOSTICS
)
from bot.services.storage import save_lead

# Состояния разговора
ROLE, PROBLEM, ENGAGEMENT, EMAIL = range(4)

async def start_diagnostics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало диагностики."""
    await update.message.reply_text(
        DIAG_INTRO_TEXT,
        parse_mode="Markdown"
    )
    return ROLE

async def ask_problem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохраняем роль и спрашиваем проблему."""
    user_role = update.message.text
    context.user_data["role"] = user_role
    
    await update.message.reply_text(
        DIAG_Q2_TEXT,
        reply_markup=PROBLEM_KEYBOARD,
        parse_mode="Markdown"
    )
    return PROBLEM

async def ask_engagement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохраняем проблему и спрашиваем вовлеченность."""
    query = update.callback_query
    await query.answer()
    
    problem_code = query.data.replace("prob_", "")
    context.user_data["problem"] = problem_code
    
    await query.edit_message_text(
        text=f"{DIAG_Q2_TEXT}\n\n✅ Выбрано: {problem_code}" # Упрощено для примера
    )
    
    await query.message.reply_text(
        DIAG_Q3_TEXT,
        reply_markup=ENGAGEMENT_KEYBOARD,
        parse_mode="Markdown"
    )
    return ENGAGEMENT

async def ask_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохраняем вовлеченность, генерируем результат и просим email."""
    query = update.callback_query
    await query.answer()
    
    engagement_code = query.data.replace("eng_", "")
    context.user_data["engagement"] = engagement_code
    
    # Простая логика результата (заглушка)
    result = "Требуется внимание к мотивации"
    if engagement_code == "drama":
        result = "⚠️ Высокий риск саботажа"
    elif engagement_code == "high":
        result = "🌟 Отличная база для роста"
        
    context.user_data["result"] = result
    
    await query.edit_message_text(
        text=f"{DIAG_Q3_TEXT}\n\n✅ Выбрано: {engagement_code}"
    )
    
    await query.message.reply_text(
        DIAG_EMAIL_TEXT.format(result=result),
        parse_mode="Markdown"
    )
    return EMAIL

async def finish_diagnostics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохраняем email и завершаем."""
    email = update.message.text
    context.user_data["email"] = email
    
    # Сохранение лида
    user = update.effective_user
    lead_data = {
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "role_team": context.user_data.get("role"),
        "problem": context.user_data.get("problem"),
        "engagement": context.user_data.get("engagement"),
        "result": context.user_data.get("result"),
        "email": email
    }
    save_lead(lead_data)
    
    await update.message.reply_text(
        DIAG_FINAL_TEXT.format(email=email),
        parse_mode="Markdown"
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена диалога."""
    await update.message.reply_text("Диагностика отменена. Возвращаемся в меню.")
    return ConversationHandler.END

# Сборка ConversationHandler
diagnostics_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(f"^{BTN_DIAGNOSTICS}$"), start_diagnostics)],
    states={
        ROLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_problem)],
        PROBLEM: [CallbackQueryHandler(ask_engagement, pattern="^prob_")],
        ENGAGEMENT: [CallbackQueryHandler(ask_email, pattern="^eng_")],
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, finish_diagnostics)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
