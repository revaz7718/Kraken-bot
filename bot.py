
import logging
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Подключение к Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("/etc/secrets/credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Шаблон_таблицы_экипажи").sheet1

# Telegram логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния диалога
NAME, MODEL, YEAR, VIN, PHONE = range(5)
user_data = {}

def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Привет! Введи имя главного в экипаже:")
    return NAME

def name(update: Update, context: CallbackContext) -> int:
    user_data['name'] = update.message.text
    update.message.reply_text("Марка и модель машины:")
    return MODEL

def model(update: Update, context: CallbackContext) -> int:
    user_data['model'] = update.message.text
    update.message.reply_text("Год выпуска:")
    return YEAR

def year(update: Update, context: CallbackContext) -> int:
    user_data['year'] = update.message.text
    update.message.reply_text("VIN-код:")
    return VIN

def vin(update: Update, context: CallbackContext) -> int:
    user_data['vin'] = update.message.text
    update.message.reply_text("Контактный номер телефона:")
    return PHONE

def phone(update: Update, context: CallbackContext) -> int:
    user_data['phone'] = update.message.text
    sheet.append_row([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        user_data['name'],
        user_data['model'],
        user_data['year'],
        user_data['vin'],
        user_data['phone']
    ])
    update.message.reply_text("Данные записаны. Спасибо!")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Операция отменена.")
    return ConversationHandler.END

def main():
    updater = Updater(os.environ.get("BOT_TOKEN"))
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, name)],
            MODEL: [MessageHandler(Filters.text & ~Filters.command, model)],
            YEAR: [MessageHandler(Filters.text & ~Filters.command, year)],
            VIN: [MessageHandler(Filters.text & ~Filters.command, vin)],
            PHONE: [MessageHandler(Filters.text & ~Filters.command, phone)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
