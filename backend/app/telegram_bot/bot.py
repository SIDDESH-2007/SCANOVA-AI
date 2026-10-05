import os
import sys
import logging
from dotenv import load_dotenv

# Ensure project root & backend are in python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

load_dotenv(os.path.join(BACKEND_DIR, ".env"))

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN or TOKEN.strip() == "" or "PASTE_YOUR_TELEGRAM_BOT_TOKEN" in TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not configured.")

# Setup Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("telegram_bot")

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters
)

from app.telegram_bot.states import WAITING_FOR_PATIENT_ID, WAITING_FOR_PHONE
from app.telegram_bot.handlers import (
    start_command,
    handle_patient_id,
    handle_phone,
    cancel_command,
    callback_query_handler
)

def main():
    logger.info("==================================================")
    logger.info("  Radiology AI Telegram Report Bot Starting...")
    logger.info("  Database: RADIOLOGY (mongodb://127.0.0.1:27017)")
    logger.info("==================================================")

    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            WAITING_FOR_PATIENT_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_patient_id)
            ],
            WAITING_FOR_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone)
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_command),
            CommandHandler("start", start_command)
        ],
        allow_reentry=True
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(callback_query_handler))
    application.add_handler(CommandHandler("start", start_command))

    logger.info("Telegram bot polling started successfully. Press CTRL+C to stop.")
    application.run_polling()

if __name__ == "__main__":
    main()
