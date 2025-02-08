import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import sqlite3

# Logging ဖွင့်ခြင်း
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLite Database ကို initialize လုပ်ပါ
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            payment_status TEXT
        )
    ''')
    conn.commit()
    conn.close()

# User အသစ် ထည့်ခြင်း သို့မဟုတ် ပြင်ဆင်ခြင်း
def add_user(user_id, username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    
    if user:
        c.execute("UPDATE users SET username = ? WHERE user_id = ?", (username, user_id))
    else:
        c.execute("INSERT INTO users (user_id, username, payment_status) VALUES (?, ?, ?)", (user_id, username, 'not_paid'))
    
    conn.commit()
    conn.close()

# /start command: User က Bot ကို Start လုပ်သောအခါ
def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    add_user(user.id, user.username)
    
    update.message.reply_text(
        "မင်္ဂလာပါ! ဝယ်ယူအားပေးမူ့အတွက်ကျေးဇူးတင်ပါတယ်\nတနေ့ကို့ 3ကြိမ်Vd​​အစု့လိုက်တင်​ပါတယ်ရှင့်။"
    )

# Admin အတွက် /markpaid command: User ကို paid status ပြောင်းခြင်း
def mark_paid(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 1:
        user_name = context.args[0]
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("UPDATE users SET payment_status = 'paid' WHERE username = ?", (user_name,))
        conn.commit()
        conn.close()
        update.message.reply_text(f"User @{user_name} ကို paid အဖြစ်မှတ်သားပြီးပါပြီ။")
    else:
        update.message.reply_text("User နာမည်ကို ပေးပါ။")

# Admin အတွက် /blockuser command: User ကို block လုပ်ခြင်း
def block_user(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 1:
        user_name = context.args[0]
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("UPDATE users SET payment_status = 'blocked' WHERE username = ?", (user_name,))
        conn.commit()
        conn.close()
        update.message.reply_text(f"User @{user_name} ကို Movie မရရှိစေဖို့ Block လုပ်ပြီးပါပြီ။")
    else:
        update.message.reply_text("User နာမည်ကို ပေးပါ။")

# Admin အတွက် Message ပို့ပေးရန်
def handle_message(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT username, payment_status FROM users WHERE user_id = ?", (user.id,))
    user_data = c.fetchone()
    
    if user_data:
        username = user_data[0]
        payment_status = user_data[1]
        
        admin = 1794465007  # Admin ရဲ့ Telegram ID ထည့်ပေးပါ
        if payment_status == 'paid':
            context.bot.send_message(chat_id=admin, text=f"Paid user: @{username} has started the bot.\nTheir Username Link: https://t.me/{username}")
        else:
            context.bot.send_message(chat_id=admin, text=f"Non-paid user: @{username} has started the bot.\nTheir Username Link: https://t.me/{username}")
    
    conn.close()

# Main function: Bot ကို run လိုက်မယ်
def main():
    # Database ကို initialize လုပ်ပါ
    init_db()

    # Updater နဲ့ Dispatcher ကို set up လုပ်ပါ
    application = Application.builder().token("7509251415:AAEW2B-TOwHUF7aQmez1fr_6pf6oil7me8M").build()
    
    # Command Handlers ထည့်ပါ
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("markpaid", mark_paid))
    application.add_handler(CommandHandler("blockuser", block_user))

    # Message Handler ထည့်ပါ
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Bot ကို start လုပ်ပါ
    application.run_polling()

if __name__ == '__main__':
    main()