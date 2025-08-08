import telebot
import os
import json
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("8414826538:AAESRvyfwhA6xfZ0laUc6rHuqvkEvyBTHrM")
ADMIN_ID = os.getenv("7944027261")

bot = telebot.TeleBot(BOT_TOKEN)

USERS_FILE = "users.json"

def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f)

users = load_users()

def is_vip(user):
    return users.get(str(user), {}).get("vip", False)

def get_balance(user):
    return users.get(str(user), {}).get("balance", 0)

def update_user(user_id, field, value):
    if str(user_id) not in users:
        users[str(user_id)] = {"balance": 0, "vip": False, "orders": []}
    users[str(user_id)][field] = value
    save_users(users)

@bot.message_handler(commands=["start"])
def start(message):
    user_id = str(message.chat.id)
    if user_id not in users:
        users[user_id] = {"balance": 0, "vip": False, "orders": []}
        save_users(users)
    bot.reply_to(message, "أهلاً بك في البوت! استخدم /store لعرض المنتجات، /recharge للشحن.")

@bot.message_handler(commands=["recharge"])
def recharge(message):
    if str(message.chat.id) != ADMIN_ID:
        bot.reply_to(message, "❌ ليس لديك صلاحيات.")
        return
    bot.reply_to(message, "🛠 أرسل الأمر بصيغة:\n\n+123456789\nأو\n-123456789\nأو\nvip user_id")

@bot.message_handler(commands=["store"])
def store(message):
    balance = get_balance(message.chat.id)
    vip_status = "✅ VIP" if is_vip(message.chat.id) else "❌ عادي"
    bot.send_message(message.chat.id, f"""📦 المتجر:

1. منتج A - 5$
2. منتج B - 10$

💰 الرصيد: {balance}$
👤 الحالة: {vip_status}

للشراء أرسل: /order رقم_المنتج
""")

@bot.message_handler(commands=["order"])
def order(message):
    user_id = str(message.chat.id)
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "❌ استخدم: /order رقم_المنتج")
        return

    item = parts[1]
    prices = {"1": 5, "2": 10}
    if item not in prices:
        bot.reply_to(message, "❌ المنتج غير موجود.")
        return

    price = prices[item]
    if is_vip(user_id):
        price = int(price * 0.8)  # خصم 20%

    balance = get_balance(user_id)
    if balance < price:
        bot.reply_to(message, "❌ لا يوجد رصيد كافي.")
        return

    update_user(user_id, "balance", balance - price)
    users[user_id]["orders"].append(item)
    save_users(users)
    bot.send_message(message.chat.id, f"✅ تم شراء المنتج {item} بنجاح!")

@bot.message_handler(commands=["users"])
def list_users(message):
    if str(message.chat.id) != ADMIN_ID:
        return
    msg = "👥 المستخدمين:\n"
    for uid, info in users.items():
        msg += f"ID: {uid}, Balance: {info.get('balance', 0)}, VIP: {info.get('vip', False)}\n"
    bot.reply_to(message, msg)

@bot.message_handler(commands=["broadcast"])
def broadcast(message):
    if str(message.chat.id) != ADMIN_ID:
        return
    bot.send_message(message.chat.id, "✉️ أرسل الرسالة التي تريد إرسالها لكل المستخدمين.")

    @bot.message_handler(func=lambda m: True)
    def send_broadcast(msg):
        for uid in users.keys():
            try:
                bot.send_message(uid, f"📢 رسالة من الأدمن:\n\n{msg.text}")
            except:
                continue
        bot.send_message(message.chat.id, "✅ تم إرسال الرسالة.")
        bot.clear_step_handler_by_chat_id(message.chat.id)

@bot.message_handler(func=lambda msg: msg.text.startswith(('+', '-', 'vip')))
def admin_commands(message):
    if str(message.chat.id) != ADMIN_ID:
        return

    if message.text.startswith("+"):
        parts = message.text[1:].split()
        uid = parts[0] if len(parts) > 1 else message.chat.id
        uid = str(uid)
        balance = get_balance(uid) + int(parts[0])
        update_user(uid, "balance", balance)
        bot.send_message(message.chat.id, f"✅ تم إضافة رصيد. الرصيد الحالي: {balance}$")

    elif message.text.startswith("-"):
        parts = message.text[1:].split()
        uid = parts[0] if len(parts) > 1 else message.chat.id
        uid = str(uid)
        balance = get_balance(uid) - int(parts[0])
        update_user(uid, "balance", balance)
        bot.send_message(message.chat.id, f"✅ تم خصم رصيد. الرصيد الحالي: {balance}$")

    elif message.text.startswith("vip"):
        parts = message.text.split()
        if len(parts) < 2:
            bot.send_message(message.chat.id, "❌ استخدم: vip user_id")
            return
        uid = parts[1]
        update_user(uid, "vip", True)
        bot.send_message(message.chat.id, f"✅ تم تفعيل VIP للمستخدم {uid}")

bot.infinity_polling()
