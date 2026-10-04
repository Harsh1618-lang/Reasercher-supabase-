#!/usr/init/env python3
# OSINT & Pincode Bot - Ultimate Branded Edition
"""
Developer: @Harsx1618
Description: Advanced Telegram OSINT Bot with TXT Report Download, Maintenance Reason, User History Inspector, Dynamic Banner & Fast Lookups
"""

import os
import sys
import json
import time
import asyncio
import sqlite3
import requests
import re
import threading
from datetime import datetime
from flask import Flask

# ============================================
# FLASK WEB SERVER (Render Port Binding)
# ============================================
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 OSINT Telegram Bot is running 24/7 successfully via Threaded Flask Server!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ============================================
# TELEGRAM BOT SETUP
# ============================================
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InputFile
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
    import telegram.error
except ImportError:
    os.system('pip install python-telegram-bot==20.7 requests flask')
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InputFile
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
    import telegram.error

# ============================================
# ========== CONFIGURATION - YOUR DETAILS ==========
# ============================================

BOT_TOKEN = "8664550290:AAFe6m8yQrx5Km8mvh-tz5Y8rcfY1zcWIZ4"  # Bot Token
ADMIN_ID = 1420016904                                           # Main Admin ID
OWNER_USERNAME = "@Harsx1618"                                   # Owner Username
BOT_USERNAME = "@Reasercherinfobot"                             # Bot Username
API_URL = "https://nmdllpezcocquamhgpmb.supabase.co/functions/v1/lookup?number={number}"
PINCODE_API_URL = "https://rack-pincodeapi.vercel.app/api?search={pincode}"
TG_USERNAME_API_URL = "https://felix-info-x-bot.onrender.com/key=felix67&tg={username}"
TG_USERID_API_URL = "https://felix-info-x-bot.onrender.com/key=felix67&tg={userid}"

HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

user_cooldowns = {}

# ============================================
# DATABASE SETUP
# ============================================
DB_FILE = "supabase_osint.sqlite"

def init_database():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        phone_number TEXT,
        joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        searches INTEGER DEFAULT 0,
        credits INTEGER DEFAULT 2,
        is_banned INTEGER DEFAULT 0,
        is_admin INTEGER DEFAULT 0,
        referred_by INTEGER DEFAULT 0,
        last_daily TEXT DEFAULT ''
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS searches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        phone TEXT,
        response TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS sub_admins (
        user_id INTEGER PRIMARY KEY
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price TEXT,
        credits INTEGER
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS coupons (
        code TEXT PRIMARY KEY,
        credits INTEGER
    )''')
    
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('maintenance', 'off')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('maint_msg', 'Bot is currently under maintenance. Please try again later.')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('upi_id', 'harshhacker@upi')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('banner_media', '')") 
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('banner_type', 'none')") 
    
    c.execute("SELECT COUNT(*) FROM plans")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO plans (name, price, credits) VALUES (?, ?, ?)", ("Starter Pack", "₹49", 10))
        c.execute("INSERT INTO plans (name, price, credits) VALUES (?, ?, ?)", ("Pro Hacker Pack", "₹99", 25))
        c.execute("INSERT INTO plans (name, price, credits) VALUES (?, ?, ?)", ("Unlimited Master", "₹199", 60))

    c.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, phone_number, credits, is_admin) VALUES (?, ?, ?, ?, ?, ?)",
              (ADMIN_ID, 'Harsx1618', 'Harsh Admin', 'Admin Verified', 99999, 1))
    
    conn.commit()
    conn.close()

init_database()

def is_admin_user(user_id):
    if user_id == ADMIN_ID:
        return True
    sub = db_get_one("SELECT * FROM sub_admins WHERE user_id = ?", (user_id,))
    return sub is not None

def db_execute(query, params=(), commit=True):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    result = c.execute(query, params)
    if commit:
        conn.commit()
        data = result.lastrowid
    else:
        data = result.fetchall()
    conn.close()
    return data

def db_get_one(query, params=()):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    result = c.execute(query, params).fetchone()
    conn.close()
    return dict(result) if result else None

def db_get_all(query, params=()):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    result = c.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in result]

# ============================================
# API FETCH FUNCTIONS
# ============================================
async def get_phone_info(phone):
    try:
        clean_phone = re.sub(r'\D', '', phone)
        url = API_URL.format(number=clean_phone)
        response = requests.get(url, headers=HTTP_HEADERS, timeout=8)
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": False, "error": f"API returned status {response.status_code}"}
    except Exception as e:
        return {"status": False, "error": str(e)}

async def get_pincode_info(pincode):
    try:
        clean_pin = re.sub(r'\D', '', pincode)
        url = PINCODE_API_URL.format(pincode=clean_pin)
        response = requests.get(url, headers=HTTP_HEADERS, timeout=8)
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "error": f"API returned status {response.status_code}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def get_tg_username_info(username):
    try:
        if not username.startswith('@'):
            username = '@' + username
        url = TG_USERNAME_API_URL.format(username=username)
        response = requests.get(url, headers=HTTP_HEADERS, timeout=8)
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": False, "error": f"API returned status {response.status_code}"}
    except Exception as e:
        return {"status": False, "error": str(e)}

async def get_tg_userid_info(userid):
    try:
        url = TG_USERID_API_URL.format(userid=userid)
        response = requests.get(url, headers=HTTP_HEADERS, timeout=8)
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": False, "error": f"API returned status {response.status_code}"}
    except Exception as e:
        return {"status": False, "error": str(e)}

def check_api_health():
    try:
        response = requests.get(API_URL.format(number="0000000000"), headers=HTTP_HEADERS, timeout=2)
        return "🟢 Online" if response.status_code < 500 else "🟡 Degraded"
    except:
        return "🔴 Offline"

# ============================================
# INSTANT PROGRESS ANIMATION
# ============================================
async def show_hacking_animation(msg_obj, target_str, title_type="PHONE"):
    if title_type == "PINCODE":
        title = "📍 PINCODE INTELLIGENCE BREACH"
    elif title_type == "TG":
        title = "🕵️‍♂️ TELEGRAM INTEL BREACH"
    else:
        title = "💻 SYSTEM BREACH IN PROGRESS"
        
    try:
        await msg_obj.edit_text(title + "\nTarget: `" + target_str + "`\n\n✅ Decryption successful!\n`██████████ 100%`", parse_mode='Markdown')
    except:
        pass

# ============================================
# PARSE PHONE RECORDS
# ============================================
def parse_phone_records(data, phone):
    try:
        if not data or (isinstance(data, dict) and data.get('status') == False):
            error_msg = data.get('error', 'No data found') if isinstance(data, dict) else 'No data found'
            return [], "❌ Error: " + error_msg
        
        actual_results = []
        if isinstance(data, dict):
            res_layer1 = data.get('result', data)
            if isinstance(res_layer1, dict):
                res_layer2 = res_layer1.get('result', res_layer1)
                if isinstance(res_layer2, dict):
                    val = res_layer2.get('result')
                    if isinstance(val, list): actual_results.extend(val)
                    elif isinstance(val, dict): actual_results.append(val)
                elif isinstance(res_layer2, list): actual_results.extend(res_layer2)
            elif isinstance(res_layer1, list): actual_results.extend(res_layer1)

        if not actual_results:
            if isinstance(data, dict):
                for key in ['result', 'results', 'data', 'payload', 'response']:
                    val = data.get(key)
                    if isinstance(val, list): actual_results.extend(val)
                    elif isinstance(val, dict):
                        for sub_key in ['result', 'results', 'data', 'records']:
                            sub_val = val.get(sub_key)
                            if isinstance(sub_val, list): actual_results.extend(sub_val)
                            elif isinstance(sub_val, dict): actual_results.append(sub_val)
                        if not actual_results: actual_results.append(val)
                if not actual_results: actual_results = [data]
            elif isinstance(data, list): actual_results = data

        if not actual_results: actual_results = [data]

        parsed_list = []
        for rec in actual_results:
            if not isinstance(rec, dict): rec = {}
            parsed_list.append({
                "name": str(rec.get('name') or rec.get('FullName') or 'Unknown'),
                "father": str(rec.get('fname') or rec.get('father_name') or 'N/A'),
                "mobile": str(rec.get('mobile', rec.get('phone', phone))),
                "alt_num": str(rec.get('alt') or rec.get('alt_num') or 'N/A'),
                "circle": str(rec.get('circle') or rec.get('operator') or 'N/A'),
                "email": str(rec.get('email') or rec.get('Email') or 'N/A'),
                "caf_id": str(rec.get('aadhar') or rec.get('id') or 'N/A'),
                "address": str(rec.get('address') or rec.get('Address') or 'N/A')
            })
        return parsed_list, None
    except Exception as e:
        return [], "❌ Parsing Error: " + str(e)

# ============================================
# STYLISH CHUNKED PHONE SENDER & TXT FILE GENERATOR
# ============================================
async def send_stylish_chunked_response(msg_obj, records, phone, update):
    total = len(records)
    if total == 0:
        await msg_obj.edit_text("❌ Koi record nahi mila.")
        return

    chunk_size = 3
    first_chunk = True

    for i in range(0, total, chunk_size):
        chunk = records[i:i+chunk_size]
        
        text = "┌─── 📱 **NUMBER INTELLIGENCE** ───┐\n"
        text += "🎯 **Query:** `" + str(phone) + "`\n"
        text += "📊 **Records Found:** " + str(total) + "\n"
        text += "└──────────────────────────────┘\n\n"

        for idx, rec in enumerate(chunk, start=i+1):
            text += "┌─── **RECORD #" + str(idx) + "** ───┐\n"
            text += "👤 **NAME:** " + rec['name'] + "\n"
            text += "👨‍👧 **FATHER:** " + rec['father'] + "\n"
            text += "📱 **MOBILE:** " + rec['mobile'] + "\n"
            text += "📞 **ALT NUM:** " + rec['alt_num'] + "\n"
            text += "🌐 **CIRCLE:** " + rec['circle'] + "\n"
            text += "📧 **EMAIL:** " + rec['email'] + "\n"
            text += "🆔 **CAF / ID:** " + rec['caf_id'] + "\n"
            text += "🏠 **ADDRESS:**\n" + rec['address'] + "\n"
            text += "└──────────────────────────────┘\n\n"

        text += "⚡ Developed by " + OWNER_USERNAME + " | Bot: " + BOT_USERNAME

        if first_chunk:
            await msg_obj.edit_text(text, parse_mode='Markdown')
            first_chunk = False
        else:
            await asyncio.sleep(0.05)
            await msg_obj.reply_text(text, parse_mode='Markdown')

    try:
        file_content = "=========================================\n"
        file_content += "      OSINT NUMBER INTELLIGENCE REPORT\n"
        file_content += "      Query Number: " + str(phone) + "\n"
        file_content += "      Total Records: " + str(total) + "\n"
        file_content += "      Developer: " + OWNER_USERNAME + "\n"
        file_content += "=========================================\n\n"

        for idx, rec in enumerate(records, start=1):
            file_content += "--- RECORD #" + str(idx) + " ---\n"
            file_content += "NAME: " + rec['name'] + "\n"
            file_content += "FATHER: " + rec['father'] + "\n"
            file_content += "MOBILE: " + rec['mobile'] + "\n"
            file_content += "ALT NUM: " + rec['alt_num'] + "\n"
            file_content += "CIRCLE: " + rec['circle'] + "\n"
            file_content += "EMAIL: " + rec['email'] + "\n"
            file_content += "CAF / ID: " + rec['caf_id'] + "\n"
            file_content += "ADDRESS: " + rec['address'] + "\n\n"

        file_name = "report_" + str(phone) + ".txt"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(file_content)

        with open(file_name, "rb") as f:
            await update.message.reply_document(
                document=InputFile(f, filename=file_name),
                caption="📁 **Downloadable Report File**\nTarget: `" + str(phone) + "`",
                parse_mode='Markdown'
            )
        os.remove(file_name)
    except Exception as e:
        print("Error sending file: " + str(e))

# ============================================
# PINCODE & TG RESPONSE FORMATTERS
# ============================================
def format_pincode_response(data, pincode):
    try:
        if not data or not isinstance(data, dict):
            return "❌ Error: Invalid response received from Pincode API."
        
        records = data.get('records', [])
        formatted_records = []
        for idx, rec in enumerate(records, 1):
            if not isinstance(rec, dict): rec = {}
            formatted_records.append({
                "record_id": str(idx),
                "office_name": str(rec.get('office_name', 'N/A')),
                "branch_type": str(rec.get('branch_type', 'N/A')),
                "delivery_status": str(rec.get('delivery_status', 'N/A')),
                "circle": str(rec.get('circle', 'N/A')),
                "district": str(rec.get('district', 'N/A')),
                "state": str(rec.get('state', 'N/A')),
                "pincode": str(rec.get('pincode', pincode))
            })

        if len(formatted_records) > 10:
            formatted_records = formatted_records[:10]

        json_output = {
            "status": "success",
            "pincode": str(pincode),
            "total_records_shown": len(formatted_records),
            "records": formatted_records,
            "Developed by": OWNER_USERNAME,
            "Bot": BOT_USERNAME
        }

        json_str = json.dumps(json_output, indent=2, ensure_ascii=False)
        return "```json\n" + json_str + "\n```"
    except Exception as e:
        return "❌ Error formatting pincode data: " + str(e)

def format_tg_response(data, query_str):
    try:
        if not data or (isinstance(data, dict) and data.get('status') == False and 'error' in data):
            error_msg = data.get('error', 'No data found') if isinstance(data, dict) else 'No data found'
            return "❌ Error: " + error_msg
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        if len(json_str) > 4000:
            json_str = json_str[:4000] + "\n... (Truncated)"
        return "```json\n" + json_str + "\n```"
    except Exception as e:
        return "❌ Error formatting TG data: " + str(e)

# ============================================
# TELEGRAM HANDLERS
# ============================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    maint = db_get_one("SELECT value FROM settings WHERE key='maintenance'")['value']
    if maint == 'on' and not is_admin_user(user.id):
        maint_msg = db_get_one("SELECT value FROM settings WHERE key='maint_msg'")['value']
        await update.message.reply_text("🚧 " + maint_msg)
        return

    args = context.args
    referrer_id = 0
    if args and args[0].isdigit():
        ref_id = int(args[0])
        if ref_id != user.id:
            referrer_id = ref_id

    user_db = db_get_one("SELECT * FROM users WHERE user_id = ?", (user.id,))
    if not user_db:
        db_execute("INSERT INTO users (user_id, username, first_name, credits, referred_by) VALUES (?, ?, ?, ?, ?)",
                   (user.id, user.username or "NoUsername", user.first_name, 2, referrer_id), commit=True)
        if referrer_id != 0:
            db_execute("UPDATE users SET credits = credits + 2 WHERE user_id = ?", (referrer_id,), commit=True)
            try:
                await context.bot.send_message(chat_id=referrer_id, text="🎉 **Referral Bonus!** Aapke link se ek naye user ne join kiya, aapko `2` extra credits mile hain!")
            except:
                pass
    else:
        if user_db.get('is_banned') == 1:
            await update.message.reply_text("❌ Aapko bot use karne se block kar diya gaya hai.")
            return

    user_db_check = db_get_one("SELECT * FROM users WHERE user_id = ?", (user.id,))
    if not user_db_check.get('phone_number'):
        contact_button = [[KeyboardButton("📱 Share Contact to Verify & Start", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(contact_button, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("⚠️ *SECURITY VERIFICATION REQUIRED*\n\nScam se bachne ke liye kripya neeche diye gaye button par click karke apna contact verify karein!", parse_mode='Markdown', reply_markup=reply_markup)
        return

    await send_welcome_menu(update, context, user)

async def send_welcome_menu(update_or_query, context, user):
    user_info = db_get_one("SELECT credits FROM users WHERE user_id = ?", (user.id,))
    credits = user_info['credits'] if user_info else 0
    
    welcome = "\n👋 *Welcome to OSINT & Pincode Lookup Bot!*\n\n💎 Remaining Credits: `" + str(credits) + "`\nNeeche diye gaye menu se option select karein!\n🎁 *Daily Bonus:* `/daily`\n🔗 *Referral Link:* `/ref`\n📜 *Search History:* `/history`\n\n🚀 *Developed by " + OWNER_USERNAME + "*\n    "
    
    menu_keyboard = [
        [KeyboardButton("🔍 Number Info"), KeyboardButton("📍 Pincode Info")],
        [KeyboardButton("🔤 TG To Number"), KeyboardButton("💎 Buy Premium / Credits")],
        [KeyboardButton("🛠️ Toggle Menu")]
    ]
    if is_admin_user(user.id):
        menu_keyboard.append([KeyboardButton("📊 Admin Panel")])

    reply_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)

    banner_media = db_get_one("SELECT value FROM settings WHERE key='banner_media'")['value']
    banner_type = db_get_one("SELECT value FROM settings WHERE key='banner_type'")['value']

    chat_id = update_or_query.message.chat_id if hasattr(update_or_query, 'message') and update_or_query.message else update_or_query.effective_chat.id

    try:
        if banner_type == 'animation' and banner_media:
            await context.bot.send_animation(chat_id=chat_id, animation=banner_media, caption=welcome, parse_mode='Markdown', reply_markup=reply_markup)
            return
        elif banner_type == 'photo' and banner_media:
            await context.bot.send_photo(chat_id=chat_id, photo=banner_media, caption=welcome, parse_mode='Markdown', reply_markup=reply_markup)
            return
        elif banner_type == 'video' and banner_media:
            await context.bot.send_video(chat_id=chat_id, video=banner_media, caption=welcome, parse_mode='Markdown', reply_markup=reply_markup)
            return
    except:
        pass 

    if hasattr(update_or_query, 'message') and update_or_query.message:
        await update_or_query.message.reply_text(welcome, parse_mode='Markdown', reply_markup=reply_markup)

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    contact = update.message.contact
    if contact and contact.user_id == user.id:
        phone_number = contact.phone_number
        username = user.username or "NoUsername"
        db_execute("UPDATE users SET phone_number = ?, username = ? WHERE user_id = ?", (phone_number, username, user.id), commit=True)
        await update.message.reply_text("✅ *Verification Successful!* You now have 2 free credits.", parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
        await send_welcome_menu(update, context, user)
    else:
        await update.message.reply_text("❌ Kripya apna khud ka contact share karein.", reply_markup=ReplyKeyboardRemove())

async def show_premium_plans(update, context):
    upi_record = db_get_one("SELECT value FROM settings WHERE key='upi_id'")
    upi_id = upi_record['value'] if upi_record else "harshhacker@upi"
    
    plans = db_get_all("SELECT * FROM plans")
    
    text = "💎 **BUY PREMIUM & ADD CREDITS**\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "📲 **Admin UPI ID:** `" + upi_id + "`\n\n"
    text += "📦 **Available Plans:**\n"
    
    for p in plans:
        text += "• **" + p['name'] + "** — `" + str(p['price']) + "` for **" + str(p['credits']) + " Credits**\n"
        
    text += "\n💳 **How to Buy:**\n1. Pay on UPI ID above.\n2. Send payment screenshot to Admin (" + OWNER_USERNAME + ") with your Telegram ID.\n3. Admin will instantly add credits!"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def check_user_credit(update, user):
    user_data = db_get_one("SELECT * FROM users WHERE user_id = ?", (user.id,))
    if not user_data or user_data.get('is_banned') == 1:
        await update.message.reply_text("❌ Aapko block kar diya gaya hai.")
        return False
    if not user_data.get('phone_number'):
        await update.message.reply_text("⚠️ Pehle /start dabakar apna contact verify karein!")
        return False
    if user_data['credits'] <= 0 and not is_admin_user(user.id):
        upi_record = db_get_one("SELECT value FROM settings WHERE key='upi_id'")
        upi_id = upi_record['value'] if upi_record else "harshhacker@upi"
        
        await update.message.reply_text(
            "❌ **Aapke credits khatam ho chuke hain!**\n\nKripya UPI ID: `" + upi_id + "` par payment karein aur Admin (`" + OWNER_USERNAME + "`) ko screenshot bhejein.",
            parse_mode='Markdown'
        )
        return False
    return True

# ============================================
# COMMANDS
# ============================================
async def daily_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = db_get_one("SELECT last_daily FROM users WHERE user_id = ?", (user.id,))
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    if user_data and user_data['last_daily'] == today_str:
        await update.message.reply_text("⏳ Aapne aaj ka daily bonus pehle hi claim kar liya hai! Kal wapas aayein.", parse_mode='Markdown')
        return
        
    db_execute("UPDATE users SET credits = credits + 2, last_daily = ? WHERE user_id = ?", (today_str, user.id), commit=True)
    await update.message.reply_text("🎉 *Daily Bonus Claimed!* Aapke account mein `2` free credits add kar diye gaye hain.", parse_mode='Markdown')

async def ref_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot_username = context.bot.username
    ref_link = "https://t.me/" + str(bot_username) + "?start=" + str(user.id)
    
    text = "🔗 **Aapka Referral Link:**\n`" + ref_link + "`\n\nIs link ko apne doston ke sath share karein. Jab koi isse join karega, toh aapko `2` free credits milenge!"
    await update.message.reply_text(text, parse_mode='Markdown')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    health = check_api_health()
    text = "🟢 **LIVE API HEALTH STATUS**\n━━━━━━━━━━━━━━━━━━━━\n• Supabase Lookup API: `" + health + "`\n• Pincode API: `🟢 Online`\n• Telegram Lookup API: `🟢 Online`"
    await update.message.reply_text(text, parse_mode='Markdown')

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args:
        await update.message.reply_text("❌ Usage: `/report <your feedback>`", parse_mode='Markdown')
        return
    feedback_msg = ' '.join(context.args)
    report_text = "🚨 **NEW REPORT**\n👤 From: " + user.first_name + " (@" + str(user.username or 'None') + ")\n🆔 ID: `" + str(user.id) + "`\n💬 Message: " + feedback_msg
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=report_text, parse_mode='Markdown')
    except:
        pass
    await update.message.reply_text("✅ *Feedback submitted successfully!*", parse_mode='Markdown')

async def redeem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args:
        await update.message.reply_text("❌ Usage: `/redeem <coupon_code>`", parse_mode='Markdown')
        return
    code = context.args[0].strip()
    coupon = db_get_one("SELECT * FROM coupons WHERE code = ?", (code,))
    if not coupon:
        await update.message.reply_text("❌ Invalid ya expired coupon code hai!", parse_mode='Markdown')
        return
    credits_to_add = coupon['credits']
    db_execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (credits_to_add, user.id), commit=True)
    db_execute("DELETE FROM coupons WHERE code = ?", (code,), commit=True)
    await update.message.reply_text("🎉 *Success!* `" + str(credits_to_add) + "` credits added.", parse_mode='Markdown')

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    searches = db_get_all("SELECT phone, timestamp FROM searches WHERE user_id = ? ORDER BY timestamp DESC LIMIT 10", (user.id,))
    if not searches:
        await update.message.reply_text("📜 Aapne abhi tak koi search nahi ki hai.", parse_mode='Markdown')
        return
    text = "📜 *Aapki Pichli 10 Searches:* \n━━━━━━━━━━━━━━━━━━━━\n"
    for s in searches:
        text += "• `" + str(s['phone']) + "` — _" + str(s['timestamp']) + "_\n"
    await update.message.reply_text(text, parse_mode='Markdown')

# ============================================
# MESSAGE HANDLER
# ============================================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip() if update.message.text else ""

    if is_admin_user(user.id) and context.user_data.get('waiting_for_banner'):
        media_id = ""
        media_type = "none"
        if update.message.animation:
            media_id = update.message.animation.file_id
            media_type = "animation"
        elif update.message.video:
            media_id = update.message.video.file_id
            media_type = "video"
        elif update.message.photo:
            media_id = update.message.photo[-1].file_id
            media_type = "photo"

        if media_id:
            db_execute("UPDATE settings SET value = ? WHERE key = 'banner_media'", (media_id,), commit=True)
            db_execute("UPDATE settings SET value = ? WHERE key = 'banner_type'", (media_type,), commit=True)
            context.user_data['waiting_for_banner'] = False
            await update.message.reply_text("✅ Success! Naya banner media (`" + media_type + "`) set ho chuka hai.", parse_mode='Markdown')
            return
        else:
            await update.message.reply_text("❌ Kripya gallery se koi valid GIF, Video ya Photo bhejein.")
            return

    current_time = time.time()
    if user.id in user_cooldowns and not is_admin_user(user.id):
        if current_time - user_cooldowns[user.id] < 3:
            await update.message.reply_text("⚠️ Thoda dheere type karein! Spam protection active hai.")
            return
    user_cooldowns[user.id] = current_time

    if text == "🔍 Number Info":
        context.user_data['mode'] = 'phone'
        await update.message.reply_text("📱 *Number Info Mode Active*\nKripya ab koi bhi 10-digit mobile number bhejein:", parse_mode='Markdown')
        return
    elif text == "📍 Pincode Info":
        context.user_data['mode'] = 'pincode'
        await update.message.reply_text("📍 *Pincode Lookup Mode Active*\nKripya ab koi bhi valid 6-digit Indian PIN code bhejein (jaise `411001`):", parse_mode='Markdown')
        return
    elif text == "🔤 TG To Number":
        tg_keyboard = [
            [KeyboardButton("👤 Telegram to Username"), KeyboardButton("🆔 Telegram to UserID")],
            [KeyboardButton("🔙 Back to Main Menu")]
        ]
        await update.message.reply_text("🔤 *TG TO NUMBER SUB-MENU*\nNeeche diye gaye option ko select karein:", parse_mode='Markdown', reply_markup=ReplyKeyboardMarkup(tg_keyboard, resize_keyboard=True))
        return
    elif text == "👤 Telegram to Username":
        context.user_data['mode'] = 'tg_username'
        await update.message.reply_text("👤 *Telegram to Username Mode Active*\nKripya ab Telegram username bhejein (jaise `@username` ya bina `@` ke):", parse_mode='Markdown')
        return
    elif text == "🆔 Telegram to UserID":
        context.user_data['mode'] = 'tg_userid'
        await update.message.reply_text("🆔 *Telegram to UserID Mode Active*\nKripya ab Telegram numeric UserID bhejein (jaise `1420016904`):", parse_mode='Markdown')
        return
    elif text == "🔙 Back to Main Menu":
        context.user_data['mode'] = None
        await send_welcome_menu(update, context, user)
        return
    elif text == "💎 Buy Premium / Credits":
        await show_premium_plans(update, context)
        return
    elif text == "🛠️ Toggle Menu":
        await update.message.reply_text("📉 Menu hide kar diya gaya hai. Wapas lane ke liye /start dabayein.", reply_markup=ReplyKeyboardRemove())
        return
    elif text == "📊 Admin Panel" and is_admin_user(user.id):
        total_users = db_get_one("SELECT COUNT(*) as count FROM users")['count']
        total_searches = db_get_one("SELECT COUNT(*) as count FROM searches")['count']
        maint = db_get_one("SELECT value FROM settings WHERE key='maintenance'")['value']
        upi_record = db_get_one("SELECT value FROM settings WHERE key='upi_id'")
        
        panel_text = "\n📊 *ADVANCED ADMIN PANEL* (" + OWNER_USERNAME + ")\n━━━━━━━━━━━━━━━━━━\n👥 Total Users: `" + str(total_users) + "`\n🔍 Total Lookups: `" + str(total_searches) + "`\n💳 Current UPI: `" + str(upi_record['value'] if upi_record else 'Not Set') + "`\n🚧 Maintenance Mode: `" + maint.upper() + "`\n⚡ API Status: `" + check_api_health() + "`\n        "
        keyboard = [
            [InlineKeyboardButton("🟢 👥 View Users", callback_data="admin_users"), InlineKeyboardButton("💳 ⚙️ Set UPI ID", callback_data="admin_setupi_prompt")],
            [InlineKeyboardButton("📦 📋 Manage Plans", callback_data="admin_plans"), InlineKeyboardButton("💎 ➕ Add Credits", callback_data="admin_addcredit_prompt")],
            [InlineKeyboardButton("🖼️ ⚙️ Set Banner Media", callback_data="admin_banner_prompt"), InlineKeyboardButton("🎟️ ➕ Create Coupon", callback_data="admin_coupon_prompt")],
            [InlineKeyboardButton("📈 📊 Bot Stats", callback_data="admin_stats"), InlineKeyboardButton("🛡️ ➕ Add Sub-Admin", callback_data="admin_addsub_prompt")],
            [InlineKeyboardButton("🛠️ 🔄 Maintenance", callback_data="toggle_maintenance"), InlineKeyboardButton("❌ 📦 Close", callback_data="close_panel")]
        ]
        await update.message.reply_text(panel_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if not await check_user_credit(update, user): return

    mode = context.user_data.get('mode', None)
    cleaned = re.sub(r'\D', '', text)

    if mode == 'tg_username':
        query_str = text if text.startswith('@') else '@' + text
        msg = await update.message.reply_text("🕵️‍♂️ *TELEGRAM USERNAME INTEL BREACH*\nInitializing...", parse_mode='Markdown')
        data = await get_tg_username_info(query_str)
        await show_hacking_animation(msg, query_str, title_type="TG")
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, "TG_USER:" + query_str, json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        formatted = format_tg_response(data, query_str)
        try: await msg.edit_text(formatted, parse_mode='Markdown')
        except: await msg.edit_text(formatted, parse_mode=None)
        context.user_data['mode'] = None
    elif mode == 'tg_userid':
        userid_str = cleaned
        msg = await update.message.reply_text("🕵️‍♂️ *TELEGRAM USERID INTEL BREACH*\nInitializing...", parse_mode='Markdown')
        data = await get_tg_userid_info(userid_str)
        await show_hacking_animation(msg, userid_str, title_type="TG")
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, "TG_ID:" + userid_str, json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        formatted = format_tg_response(data, userid_str)
        try: await msg.edit_text(formatted, parse_mode='Markdown')
        except: await msg.edit_text(formatted, parse_mode=None)
        context.user_data['mode'] = None
    elif mode == 'pincode' or (len(cleaned) == 6 and len(text) == 6 and not mode):
        pincode = cleaned
        msg = await update.message.reply_text("📍 *PINCODE INTELLIGENCE BREACH*\nInitializing...", parse_mode='Markdown')
        data = await get_pincode_info(pincode)
        await show_hacking_animation(msg, pincode, title_type="PINCODE")
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, "PIN:" + pincode, json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        formatted = format_pincode_response(data, pincode)
        try: await msg.edit_text(formatted, parse_mode='Markdown')
        except: await msg.edit_text(formatted, parse_mode=None)
        context.user_data['mode'] = None
    elif mode == 'phone' or (10 <= len(cleaned) <= 15):
        phone = cleaned
        msg = await update.message.reply_text("💻 *SYSTEM BREACH IN PROGRESS*\nInitializing...", parse_mode='Markdown')
        data = await get_phone_info(phone)
        await show_hacking_animation(msg, phone, title_type="PHONE")
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, phone, json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        records, err = parse_phone_records(data, phone)
        if err: await msg.edit_text(err)
        else: await send_stylish_chunked_response(msg, records, phone, update)
        context.user_data['mode'] = None
    else:
        await update.message.reply_text("❌ Kripya valid input enter karein (Mobile Number, Pincode, ya TG query).", parse_mode='Markdown')

# ============================================
# ADMIN CALLBACK HANDLER
# ============================================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if not is_admin_user(query.from_user.id):
        return

    if data == "admin_panel":
        total_users = db_get_one("SELECT COUNT(*) as count FROM users")['count']
        total_searches = db_get_one("SELECT COUNT(*) as count FROM searches")['count']
        maint = db_get_one("SELECT value FROM settings WHERE key='maintenance'")['value']
        upi_record = db_get_one("SELECT value FROM settings WHERE key='upi_id'")
        
        panel_text = "\n📊 *ADVANCED ADMIN PANEL* (" + OWNER_USERNAME + ")\n━━━━━━━━━━━━━━━━━━\n👥 Total Users: `" + str(total_users) + "`\n🔍 Total Lookups: `" + str(total_searches) + "`\n💳 Current UPI: `" + str(upi_record['value'] if upi_record else 'Not Set') + "`\n🚧 Maintenance Mode: `" + maint.upper() + "`\n⚡ API Status: `" + check_api_health() + "`\n        "
        keyboard = [
            [InlineKeyboardButton("🟢 👥 View Users", callback_data="admin_users"), InlineKeyboardButton("💳 ⚙️ Set UPI ID", callback_data="admin_setupi_prompt")],
            [InlineKeyboardButton("📦 📋 Manage Plans", callback_data="admin_plans"), InlineKeyboardButton("💎 ➕ Add Credits", callback_data="admin_addcredit_prompt")],
            [InlineKeyboardButton("🖼️ ⚙️️ Set Banner Media", callback_data="admin_banner_prompt"), InlineKeyboardButton("🎟️ ➕ Create Coupon", callback_data="admin_coupon_prompt")],
            [InlineKeyboardButton("📈 📊 Bot Stats", callback_data="admin_stats"), InlineKeyboardButton("🛡️ ➕ Add Sub-Admin", callback_data="admin_addsub_prompt")],
            [InlineKeyboardButton("🛠️ 🔄 Maintenance", callback_data="toggle_maintenance"), InlineKeyboardButton("❌ 📦 Close", callback_data="close_panel")]
        ]
        try: await query.edit_message_text(panel_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except: pass
        
    elif data == "admin_stats":
        total_users = db_get_one("SELECT COUNT(*) as count FROM users")['count']
        total_searches = db_get_one("SELECT COUNT(*) as count FROM searches")['count']
        banned_users = db_get_one("SELECT COUNT(*) as count FROM users WHERE is_banned = 1")['count']
        stats_text = "\n📈 **BOT DETAILED STATISTICS**\n━━━━━━━━━━━━━━━━━━━━\n👥 Total Registered Users: `" + str(total_users) + "`\n🔴 Banned Users: `" + str(banned_users) + "`\n🔍 Total Searches Made: `" + str(total_searches) + "`\n⚡ Current Server Status: `" + check_api_health() + "`\n        "
        keyboard = [[InlineKeyboardButton("🔵 📊 Back to Panel", callback_data="admin_panel")]]
        try: await query.edit_message_text(stats_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except: pass

    elif data == "admin_users":
        users = db_get_all("SELECT user_id, username, first_name, phone_number, searches, credits, is_banned FROM users ORDER BY joined_date DESC LIMIT 15")
        text = "👥 *Verified Users List*\n━━━━━━━━━━━━━━━━━━━━\n"
        for u in users:
            status = "🔴 Banned" if u['is_banned'] else "🟢 Active"
            text += "🆔 ID: `" + str(u['user_id']) + "` | @" + str(u['username']) + " | " + status + "\n👤 Name: " + u['first_name'] + "\n📱 Mobile: `" + str(u['phone_number']) + "`\n🔍 Searches: " + str(u['searches']) + " | 💎 Credits: " + str(u['credits']) + "\n--------------------\n"
        keyboard = [[InlineKeyboardButton("🔵 📊 Back to Panel", callback_data="admin_panel")]]
        try: await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except: pass

    elif data == "admin_plans":
        plans = db_get_all("SELECT * FROM plans")
        text = "📦 *Manage Subscription Plans*\n━━━━━━━━━━━━━━━━━━━━\n"
        for p in plans:
            text += "🆔 ID: `" + str(p['id']) + "` | **" + p['name'] + "**\n💰 Price: `" + str(p['price']) + "` | 💎 Credits: `" + str(p['credits']) + "`\n--------------------\n"
        keyboard = [[InlineKeyboardButton("🔵 📊 Back to Panel", callback_data="admin_panel")]]
        try: await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except: pass

    elif data == "admin_setupi_prompt":
        if query.from_user.id != ADMIN_ID: return
        await context.bot.send_message(chat_id=query.from_user.id, text="💡 To update UPI ID, use command:\n`/setupi <new_upi_id>`", parse_mode='Markdown')

    elif data == "admin_addcredit_prompt":
        await context.bot.send_message(chat_id=query.from_user.id, text="💡 To add credits, use command:\n`/addcredits <user_id> <amount>`", parse_mode='Markdown')

    elif data == "admin_coupon_prompt":
        await context.bot.send_message(chat_id=query.from_user.id, text="💡 To create a coupon, use command:\n`/createcoupon <code> <credits>`", parse_mode='Markdown')

    elif data == "admin_banner_prompt":
        context.user_data['waiting_for_banner'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="🖼️ **Banner Media Setup Active!**\n\nAb apni gallery se koi bhi **GIF, Video, ya Photo** seedhe yahan bhej dein (upload karein), bot automatic usko banner set kar dega!", parse_mode='Markdown')

    elif data == "admin_addsub_prompt":
        if query.from_user.id != ADMIN_ID: return
        await context.bot.send_message(chat_id=query.from_user.id, text="💡 To add a sub-admin, use command:\n`/addsub <user_id>`", parse_mode='Markdown')

    elif data == "toggle_maintenance":
        if query.from_user.id != ADMIN_ID: return
        current = db_get_one("SELECT value FROM settings WHERE key='maintenance'")['value']
        new_val = 'off' if current == 'on' else 'on'
        db_execute("UPDATE settings SET value = ? WHERE key = 'maintenance'", (new_val,), commit=True)
        query.data = "admin_panel"
        await button_callback(update, context)

    elif data == "close_panel":
        try: await query.message.delete()
        except: pass

# ============================================
# ADMIN COMMANDS
# ============================================
async def setupi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/setupi <new_upi_id>`", parse_mode='Markdown')
        return
    new_upi = context.args[0]
    db_execute("UPDATE settings SET value = ? WHERE key = 'upi_id'", (new_upi,), commit=True)
    await update.message.reply_text("✅ UPI ID successfully updated to: `" + new_upi + "`", parse_mode='Markdown')

async def maint_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin_user(update.effective_user.id): return
    if not context.args or context.args[0].lower() not in ['on', 'off']:
        await update.message.reply_text("❌ Usage: `/maint on <reason>` or `/maint off`", parse_mode='Markdown')
        return
    status = context.args[0].lower()
    db_execute("UPDATE settings SET value = ? WHERE key = 'maintenance'", (status,), commit=True)
    if status == 'on' and len(context.args) > 1:
        reason = ' '.join(context.args[1:])
        db_execute("UPDATE settings SET value = ? WHERE key = 'maint_msg'", (reason,), commit=True)
        await update.message.reply_text("🚧 Maintenance Mode **ON**\nReason: `" + reason + "`", parse_mode='Markdown')
    else:
        await update.message.reply_text("🚧 Maintenance Mode set to `" + status.upper() + "`", parse_mode='Markdown')

async def userhistory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin_user(update.effective_user.id): return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("❌ Usage: `/userhistory <user_id>`", parse_mode='Markdown')
        return
    target_id = int(context.args[0])
    searches = db_get_all("SELECT phone, timestamp FROM searches WHERE user_id = ? ORDER BY timestamp DESC LIMIT 15", (target_id,))
    if not searches:
        await update.message.reply_text("❌ User ID `" + str(target_id) + "` ki koi search history nahi mili.", parse_mode='Markdown')
        return
    text = "📜 *Search History for User ID `" + str(target_id) + "`:*\n━━━━━━━━━━━━━━━━━━━━\n"
    for s in searches:
        text += "• `" + str(s['phone']) + "` — _" + str(s['timestamp']) + "_\n"
    await update.message.reply_text(text, parse_mode='Markdown')

async def createcoupon_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin_user(update.effective_user.id): return
    if len(context.args) < 2:
        await update.message.reply_text("❌ Usage: `/createcoupon <code> <credits>`", parse_mode='Markdown')
        return
    try:
        code, credits = context.args[0].strip(), int(context.args[1])
        db_execute("INSERT OR REPLACE INTO coupons (code, credits) VALUES (?, ?)", (code, credits), commit=True)
        await update.message.reply_text("✅ Coupon `" + code + "` created successfully with `" + str(credits) + "` credits!", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text("❌ Error: " + str(e))

async def addsub_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args: return
    try:
        sub_id = int(context.args[0])
        db_execute("INSERT OR IGNORE INTO sub_admins (user_id) VALUES (?)", (sub_id,), commit=True)
        await update.message.reply_text("✅ User `" + str(sub_id) + "` added as Sub-Admin!", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text("❌ Error: " + str(e))

async def addcredits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin_user(update.effective_user.id): return
    if len(context.args) < 2: return
    try:
        target_id, amount = int(context.args[0]), int(context.args[1])
        db_execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (amount, target_id), commit=True)
        await update.message.reply_text("✅ Added `" + str(amount) + "` credits to user `" + str(target_id) + "`!", parse_mode='Markdown')
        try: await context.bot.send_message(chat_id=target_id, text="🎉 **Congratulations!**\nAdmin added `" + str(amount) + "` credits to your account.")
        except: pass
    except Exception as e:
        await update.message.reply_text("❌ Error: " + str(e))

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin_user(update.effective_user.id): return
    if not context.args: return
    db_execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (context.args[0],), commit=True)
    await update.message.reply_text("🚫 User `" + str(context.args[0]) + "` banned.", parse_mode='Markdown')

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin_user(update.effective_user.id): return
    if not context.args: return
    db_execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (context.args[0],), commit=True)
    await update.message.reply_text("✅ User `" + str(context.args[0]) + "` unbanned.", parse_mode='Markdown')

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin_user(update.effective_user.id): return
    message = update.message
    reply_to = message.reply_to_message
    
    users = db_get_all("SELECT user_id FROM users")
    sent = 0
    for u in users:
        try:
            if reply_to:
                await context.bot.copy_message(chat_id=u['user_id'], from_chat_id=message.chat_id, message_id=reply_to.message_id)
            elif context.args:
                msg_text = ' '.join(context.args)
                await context.bot.send_message(chat_id=u['user_id'], text="📢 *ANNOUNCEMENT (" + OWNER_USERNAME + ")*\n\n" + msg_text, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Kripya broadcast ke liye text likhein ya kisi message ko reply/quote karke `/broadcast` bhejein.")
                return
            sent += 1
        except: pass
    await update.message.reply_text("📢 Broadcast successfully sent to " + str(sent) + " users.")

def main():
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    print("=" * 50)
    print("🚀 HARSH OSINT BOT STARTING (SYNTAX FIXED)...")
    print("=" * 50)
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("report", report_command))
    application.add_handler(CommandHandler("daily", daily_command))
    application.add_handler(CommandHandler("ref", ref_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("redeem", redeem_command))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("userhistory", userhistory_command))
    application.add_handler(CommandHandler("ban", ban_command))
    application.add_handler(CommandHandler("unban", unban_command))
    application.add_handler(CommandHandler("setupi", setupi_command))
    application.add_handler(CommandHandler("maint", maint_command))
    application.add_handler(CommandHandler("createcoupon", createcoupon_command))
    application.add_handler(CommandHandler("addsub", addsub_command))
    application.add_handler(CommandHandler("addcredits", addcredits_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    application.add_handler(MessageHandler(filters.TEXT | filters.ANIMATION | filters.PHOTO | filters.VIDEO & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
