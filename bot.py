import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Подключение к Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Шаблон_таблицы_экипажи").sheet1

# Telegram логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния диалога
NAME, MODEL, YEAR, VIN, PHONE = range(5)
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Введи имя главного:")
    return NAME

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["name"] = update.message.text
    await update.message.reply_text("Марка и модель машины:")
    return MODEL

async def model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["model"] = update.message.text
    await update.message.reply_text("Год выпуска:")
    return YEAR

async def year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["year"] = update.message.text
    await update.message.reply_text("VIN-код:")
    return VIN

async def vin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["vin"] = update.message.text
    await update.message.reply_text("Контактный номер телефона:")
    return PHONE

async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["phone"] = update.message.text
    sheet.append_row([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        user_data["name"],
        user_data["model"],
        user_data["year"],
        user_data["vin"],
        user_data["phone"]
    ])
    await update.message.reply_text("Данные записаны. Спасибо!")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END

def main():
    token = os.environ.get("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            MODEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, model)],
            YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, year)],
            VIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, vin)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    # Webhook вместо polling
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/"
    )

if __name__ == "__main__":
    main()
