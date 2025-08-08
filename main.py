# main.py
 
import telebot import json import os from dotenv import load_dotenv from telebot import types from datetime import datetime
 
load_dotenv()
 
BOT_TOKEN = os.getenv("8414826538:AAESRvyfwhA6xfZ0laUc6rHuqvkEvyBTHrM") ADMIN_ID = int(os.getenv("7944027261"))
 
bot = telebot.TeleBot(BOT_TOKEN)
 
# ========== قواعد بيانات بسيطة ==========
 
USERS_FILE = "users.json" PRODUCTS_FILE = "products.json" ORDERS_FILE = "orders.json"
 
# ========== أدوات المساعدة ==========
 
def load_data(file): if not os.path.exists(file): with open(file, 'w') as f: json.dump({}, f) with open(file, 'r') as f: return json.load(f)
 
def save_data(file, data): with open(file, 'w') as f: json.dump(data, f, indent=2)
 
# ========== تسجيل المستخدم ==========
 
@bot.message_handler(commands=['start']) def handle_start(message): users = load_data(USERS_FILE) user_id = str(message.chat.id) if user_id not in users: users[user_id] = { "username": message.from_user.username or "-", "balance": 0, "vip": False, "orders": [], "joined": str(datetime.now()) } save_data(USERS_FILE, users) bot.send_message(message.chat.id, "👋 مرحبًا بك في بوت المتجر!")
 
# ========== عرض الرصيد ==========
 
@bot.message_handler(commands=['balance']) def check_balance(message): users = load_data(USERS_FILE) user = users.get(str(message.chat.id), {}) balance = user.get("balance", 0) vip = "✅ نعم" if user.get("vip") else "❌ لا" bot.send_message(message.chat.id, f"💰 رصيدك: {balance} نقطة\n💎 VIP: {vip}")
 
# ========== أوامر الأدمن ==========
 
@bot.message_handler(commands=['admin']) def admin_panel(message): if message.chat.id != ADMIN_ID: return bot.send_message(message.chat.id, "🚫 لا تملك صلاحية.")
 `markup = types.InlineKeyboardMarkup() markup.add(types.InlineKeyboardButton("➕ شحن رصيد", callback_data="add_balance")) markup.add(types.InlineKeyboardButton("📦 عرض الطلبات", callback_data="view_orders")) bot.send_message(message.chat.id, "🔧 لوحة التحكم:", reply_markup=markup) ` 
# ========== استقبال أزرار الأدمن ==========
 
@bot.callback_query_handler(func=lambda call: True) def handle_callbacks(call): if call.message.chat.id != ADMIN_ID: return
 `if call.data == "add_balance":     msg = bot.send_message(call.message.chat.id, "أرسل: user_id amount")     bot.register_next_step_handler(msg, process_balance_addition)  elif call.data == "view_orders":     orders = load_data(ORDERS_FILE)     if not orders:         bot.send_message(call.message.chat.id, "لا توجد طلبات.")     else:         text = "\n".join([f"{k}: {v['product']} - {v['status']}" for k, v in orders.items()])         bot.send_message(call.message.chat.id, f"📦 الطلبات:\n{text}") ` 
# ========== إضافة رصيد للمستخدم ==========
 
def process_balance_addition(message): try: user_id, amount = message.text.split() users = load_data(USERS_FILE) users[user_id]["balance"] += int(amount) save_data(USERS_FILE, users) bot.send_message(message.chat.id, "✅ تم شحن الرصيد.") except: bot.send_message(message.chat.id, "❌ صيغة خاطئة. جرب: user_id amount")
 
# ========== أمر شراء وهمي ==========
 
@bot.message_handler(commands=['buy']) def handle_buy(message): users = load_data(USERS_FILE) user_id = str(message.chat.id) user = users.get(user_id) if not user: return bot.send_message(message.chat.id, "❌ أنت غير مسجل.")
 `if user['balance'] < 10:     return bot.send_message(message.chat.id, "❌ رصيد غير كافٍ.")  user['balance'] -= 10 save_data(USERS_FILE, users)  orders = load_data(ORDERS_FILE) order_id = str(len(orders)+1) orders[order_id] = {     "user": user_id,     "product": "منتج تجريبي",     "status": "✅ مكتمل",     "time": str(datetime.now()) } save_data(ORDERS_FILE, orders) bot.send_message(message.chat.id, "🎉 تم شراء المنتج بنجاح!") ` 
# ========== شحن الرصيد ==========
 
@bot.message_handler(commands=['recharge']) def handle_recharge(message): bot.send_message(message.chat.id, "💳 الرجاء التواصل مع الأدمن لشحن الرصيد.")
 
# ========== مشاركة البوت ==========
 
@bot.message_handler(commands=['share']) def share_bot(message): link = f"[https://t.me/{bot.get_me().username}](https://t.me/{bot.get_me().username})" bot.send_message(message.chat.id, f"📢 شارك البوت مع أصدقائك:\n{link}")
 
# ========== تشغيل البوت ==========
 
bot.infinity_polling()
