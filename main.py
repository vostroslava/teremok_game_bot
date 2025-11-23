from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

from bot.config import TELEGRAM_TOKEN
from bot.handlers.common import start, webapp_command, about_model
from bot.handlers.quiz import start_quiz, process_quiz_answer
from bot.handlers.simulation import start_sim, process_sim_answer

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data

    if data == "START_QUIZ":
        await start_quiz(update, context)
        return

    if data == "ABOUT_MODEL":
        await about_model(update, context)
        return

    if data == "START_SIM":
        await start_sim(update, context)
        return

    if data.startswith("QUIZ:"):
        await process_quiz_answer(update, context)
        return

    if data.startswith("SIM:"):
        await process_sim_answer(update, context)
        return

    await query.answer()
    await query.edit_message_text("Непонятная команда. Нажми /start, чтобы начать заново.")


def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("webapp", webapp_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
