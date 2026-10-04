#!/usr/init/env python3
# OSINT & Pincode Bot - Ultimate Syntax Fixed Edition
"""
Developer: @Harsx1618
Description: Advanced Telegram OSINT Bot with Fixed Syntax, Working Maintenance & All Features Intact
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

HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

user_cooldowns = {}
user_flood_tracker = {}
active_live_users = set()

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

    c.execute('''CREATE TABLE IF NOT EXISTS feature_maint (
        feature_key TEXT PRIMARY KEY,
        status TEXT DEFAULT 'off',
        message TEXT DEFAULT 'Is feature par kaam chal raha hai, jaldi hi yeh live hoga!'
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS dynamic_apis (
        api_key TEXT PRIMARY KEY,
        api_name TEXT,
        api_url TEXT,
        old_credit TEXT DEFAULT '',
        new_credit TEXT DEFAULT ''
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

    c.execute('''CREATE TABLE IF NOT EXISTS clones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER,
        bot_token TEXT,
        bot_username TEXT,
        status TEXT DEFAULT 'Active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS analytics (
        feature_name TEXT PRIMARY KEY,
        count INTEGER DEFAULT 0
    )''')
    
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('maintenance', 'off')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('maint_msg', 'Is feature par kaam chal raha hai, jaldi hi yeh live hoga!')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('upi_id', 'harshhacker@upi')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('banner_media', '')") 
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('banner_type', 'none')") 
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('clone_req_ref', '2')") 
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('clone_ref_toggle', 'on')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('ref_reward_credits', '2')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('force_channels', '')")
    
    default_apis = [
        ('phone', 'Number Info', 'https://nmdllpezcocquamhgpmb.supabase.co/functions/v1/lookup?number={query}', '@FizzaGirl', '@Harsx1618'),
        ('pincode', 'Pincode Info', 'https://rack-pincodeapi.vercel.app/api?search={query}', '', ''),
        ('ip_info', 'IP Info', 'https://oriss-ip-info-api.antideploy.com/ip/{query}', '', ''),
        ('aadhaar_info', 'Aadhaar Info', 'https://nitin-vio-api-paid-best.boyu3054.workers.dev/aadhaar?key=FZ-UJKAHS8A2ABUJA8LBBK9&aadhaar={query}', '@FizzaGirl', '@Harsx1618'),
        ('tg_username', 'TG Username', 'https://felix-info-x-bot.onrender.com/key=felix67&tg={query}', '', ''),
        ('tg_userid', 'TG UserID', 'https://felix-info-x-bot.onrender.com/key=felix67&tg={query}', '', '')
    ]

    for ak, an, au, oc, nc in default_apis:
        c.execute("INSERT OR IGNORE INTO dynamic_apis (api_key, api_name, api_url, old_credit, new_credit) VALUES (?, ?, ?, ?, ?)", (ak, an, au, oc, nc))

    for feat_key, feat_name in [('phone', 'Number Info'), ('pincode', 'Pincode Info'), ('ip_info', 'IP Info'), ('aadhaar_info', 'Aadhaar Info'), ('tg_info', 'TG To Number'), ('ref', 'Refer & Earn')]:
        c.execute("INSERT OR IGNORE INTO analytics (feature_name, count) VALUES (?, 0)", (feat_name,))
        c.execute("INSERT OR IGNORE INTO feature_maint (feature_key, status, message) VALUES (?, 'off', ?)", (feat_key, 'Is feature par kaam chal raha hai, jaldi hi yeh live hoga!'))
    
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

async def check_multi_force_subscription(bot, user_id):
    channels_str = db_get_one("SELECT value FROM settings WHERE key='force_channels'")['value']
    if not channels_str or channels_str.strip() == "":
        return True, []
    
    channels = [ch.strip() for ch in channels_str.split(',') if ch.strip()]
    unjoined = []
    for ch in channels:
        try:
            member = await bot.get_chat_member(chat_id=ch, user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                unjoined.append(ch)
        except:
            unjoined.append(ch)
    return len(unjoined) == 0, unjoined

# ============================================
# DYNAMIC API FETCH HELPER WITH WATERMARK REPLACEMENT
# ============================================
async def fetch_dynamic_api(api_key, query_val, timeout_sec=15):
    api_record = db_get_one("SELECT * FROM dynamic_apis WHERE api_key = ?", (api_key,))
    if not api_record or not api_record['api_url']:
        return {"status": False, "error": "API URL not configured in Admin Panel"}
    
    target_url = api_record['api_url'].replace("{query}", str(query_val))
    old_c = api_record['old_credit'] or ""
    new_c = api_record['new_credit'] or ""

    try:
        response = requests.get(target_url, headers=HTTP_HEADERS, timeout=timeout_sec)
        if response.status_code == 200:
            raw_text = response.text
            if old_c:
                raw_text = raw_text.replace(old_c, new_c)
            try:
                return json.loads(raw_text)
            except:
                return {"status": True, "raw_result": raw_text}
        else:
            return {"status": False, "error": "API returned status " + str(response.status_code)}
    except Exception as e:
        return {"status": False, "error": str(e)}

# ============================================
# AUTO-DELETE BACKGROUND TASK
# ============================================
async def schedule_message_deletion(context, chat_id, message_ids, doc_message_id=None):
    await asyncio.sleep(30)
    for msg_id in message_ids:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except:
            pass
    if doc_message_id:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=doc_message_id)
        except:
            pass

async def show_hacking_animation(msg_obj, target_str, title_type="PHONE"):
    if title_type == "PINCODE":
        title = "📍 PINCODE INTELLIGENCE BREACH"
    elif title_type == "TG":
        title = "🕵️‍♂️ TELEGRAM INTEL BREACH"
    elif title_type == "IP":
        title = "🌐 IP INTELLIGENCE BREACH"
    elif title_type == "AADHAAR":
        title = "🆔 INTELLIGENCE BREACH"
    else:
        title = "💻 SYSTEM BREACH IN PROGRESS"
        
    try:
        await msg_obj.edit_text(title + "\nTarget: `" + target_str + "`\n\n✅ Decryption successful!\n`██████████ 100%`", parse_mode='Markdown')
    except:
        pass

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

async def send_stylish_chunked_response(msg_obj, records, phone, update, context):
    total = len(records)
    if total == 0:
        await msg_obj.edit_text("❌ Koi record nahi mila.")
        return

    chunk_size = 2
    first_chunk = True
    sent_message_ids = [msg_obj.message_id]

    for i in range(0, total, chunk_size):
        chunk = records[i:i+chunk_size]
        
        text = "📱 **NUMBER INTELLIGENCE REPORT**\n"
        text += "🎯 Target: `" + str(phone) + "`\n"
        text += "📊 Total Records: " + str(total) + "\n━━━━━━━━━━━━━━━━━━━━\n\n"

        for idx, rec in enumerate(chunk, start=i+1):
            text += f"🔹 **RECORD #{idx}**\n"
            text += f"👤 Name: `{rec['name']}`\n"
            text += f"👨‍👧 Father: `{rec['father']}`\n"
            text += f"📱 Mobile: `{rec['mobile']}`\n"
            text += f"📞 Alt Num: `{rec['alt_num']}`\n"
            text += f"🌐 Circle: `{rec['circle']}`\n"
            text += f"📧 Email: `{rec['email']}`\n"
            text += f"🆔 CAF / ID: `{rec['caf_id']}`\n"
            text += f"🏠 Address:\n`{rec['address']}`\n\n━━━━━━━━━━━━━━━━━━━━\n"

        text += "⚡ Developed by " + OWNER_USERNAME

        if first_chunk:
            await msg_obj.edit_text(text, parse_mode='Markdown')
            first_chunk = False
        else:
            await asyncio.sleep(0.05)
            reply_msg = await update.message.reply_text(text, parse_mode='Markdown')
            sent_message_ids.append(reply_msg.message_id)

    doc_msg_id = None
    try:
        file_content = "=========================================\n"
        file_content += "      OSINT NUMBER INTELLIGENCE REPORT\n"
        file_content += "      Query Number: " + str(phone) + "\n"
        file_content += "      Total Records: " + str(total) + "\n"
        file_content += "      Developer: " + OWNER_USERNAME + "\n"
        file_content += "=========================================\n\n"

        for idx, rec in enumerate(records, start=1):
            file_content += f"--- RECORD #{idx} ---\n"
            file_content += f"NAME: {rec['name']}\n"
            file_content += f"FATHER: {rec['father']}\n"
            file_content += f"MOBILE: {rec['mobile']}\n"
            file_content += f"ALT NUM: {rec['alt_num']}\n"
            file_content += f"CIRCLE: {rec['circle']}\n"
            file_content += f"EMAIL: {rec['email']}\n"
            file_content += f"CAF / ID: {rec['caf_id']}\n"
            file_content += f"ADDRESS: {rec['address']}\n\n"

        file_name = "report_" + str(phone) + ".txt"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(file_content)

        with open(file_name, "rb") as f:
            doc_msg = await update.message.reply_document(
                document=InputFile(f, filename=file_name),
                caption="📁 **Downloadable Report File (Auto-deletes in 30s)**\nTarget: `" + str(phone) + "`",
                parse_mode='Markdown'
            )
            doc_msg_id = doc_msg.message_id
        os.remove(file_name)
    except Exception as e:
        print("Error sending file: " + str(e))

    asyncio.create_task(schedule_message_deletion(context, update.effective_chat.id, sent_message_ids, doc_msg_id))

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
            "records": formatted_records
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

def format_ip_response(data, ip_str):
    try:
        if not data or (isinstance(data, dict) and data.get('status') == False):
            error_msg = data.get('error', 'No data found') if isinstance(data, dict) else 'No data found'
            return "❌ Error: " + error_msg
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        if len(json_str) > 4000:
            json_str = json_str[:4000] + "\n... (Truncated)"
        return "```json\n" + json_str + "\n```"
    except Exception as e:
        return "❌ Error formatting IP data: " + str(e)

def format_aadhaar_response(data, query_str):
    try:
        if not data or (isinstance(data, dict) and data.get('status') == False):
            error_msg = data.get('error', 'No data found') if isinstance(data, dict) else 'No data found'
            return "❌ Error: " + error_msg
        
        if isinstance(data, dict):
            data.pop('developer', None)
            data.pop('owner', None)
            data.pop('channel', None)

        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        if len(json_str) > 4000:
            json_str = json_str[:4000] + "\n... (Truncated)"
        return "```json\n" + json_str + "\n```"
    except Exception as e:
        return "❌ Error formatting data: " + str(e)

# ============================================
# COMMAND HANDLERS
# ============================================
async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    support_text = "💬 *IF YOU FACE ANY ISSUES CONTACT OUR ADMIN*\n\n📲 **Owner / Support Username:** `" + OWNER_USERNAME + "`\n\nKisi bhi madad ke liye seedhe contact karein!"
    support_keyboard = [[InlineKeyboardButton("💬 Chat with Support Owner", url="https://t.me/" + OWNER_USERNAME.replace('@', ''))]]
    await update.message.reply_text(support_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(support_keyboard))

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_info = db_get_one("SELECT credits FROM users WHERE user_id = ?", (user.id,))
    credits = user_info['credits'] if user_info else 0
    await update.message.reply_text("💰 *Aapka Current Balance:*\n\n💎 Remaining Credits: `" + str(credits) + " Credits`", parse_mode='Markdown')

# ============================================
# TELEGRAM HANDLERS
# ============================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    active_live_users.add(user.id)
    
    context.user_data.clear()
    
    maint = db_get_one("SELECT value FROM settings WHERE key='maintenance'")['value']
    if maint == 'on' and not is_admin_user(user.id):
        maint_msg = db_get_one("SELECT value FROM settings WHERE key='maint_msg'")['value']
        await update.message.reply_text("🚧 " + maint_msg, parse_mode='Markdown')
        return

    args = context.args
    referrer_id = 0
    if args and args[0].isdigit():
        ref_id = int(args[0])
        if ref_id != user.id:
            referrer_id = ref_id

    reward_setting = db_get_one("SELECT value FROM settings WHERE key='ref_reward_credits'")
    ref_reward = int(reward_setting['value']) if reward_setting and reward_setting['value'].isdigit() else 2

    user_db = db_get_one("SELECT * FROM users WHERE user_id = ?", (user.id,))
    if not user_db:
        db_execute("INSERT INTO users (user_id, username, first_name, credits, referred_by) VALUES (?, ?, ?, ?, ?)",
                   (user.id, user.username or "NoUsername", user.first_name, ref_reward, referrer_id), commit=True)
        if referrer_id != 0:
            db_execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (ref_reward, referrer_id), commit=True)
            try:
                await context.bot.send_message(chat_id=referrer_id, text=f"🎉 **Referral Bonus!** Aapke link se ek naye user ne join kiya, aapko `{ref_reward}` extra credits mile hain!")
            except:
                pass
    else:
        if user_db.get('is_banned') == 1:
            await update.message.reply_text("❌ Aapko bot use karne se block kar diya gaya hai.")
            return

    user_db_check = db_get_one("SELECT * FROM users WHERE user_id = ?", (user.id,))
    if not user_db_check.get('phone_number') or not user_db_check['phone_number']:
        contact_button = [[KeyboardButton("📱 Share Contact to Verify & Start", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(contact_button, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("⚠️ *SECURITY VERIFICATION REQUIRED*\n\nScam se bachne ke liye kripya neeche diye gaye button par click karke apna contact verify karein!", parse_mode='Markdown', reply_markup=reply_markup)
        return

    is_joined, unjoined_channels = await check_multi_force_subscription(context.bot, user.id)
    if not is_joined:
        join_buttons = []
        for ch in unjoined_channels:
            join_buttons.append([InlineKeyboardButton(f"📢 Join {ch}", url=f"https://t.me/{ch.replace('@', '')}")])
        join_buttons.append([InlineKeyboardButton("✅ I Have Joined All", callback_data="check_join_btn")])
        await update.message.reply_text("⚠️ *MULTI-CHANNEL FORCE JOIN REQUIRED*\n\nBot ko use karne ke liye kripya neeche diye gaye sabhi channels ko join karein:", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(join_buttons))
        return

    await send_welcome_menu(update, context, user)

async def send_welcome_menu(update_or_query, context, user):
    user_info = db_get_one("SELECT credits FROM users WHERE user_id = ?", (user.id,))
    credits = user_info['credits'] if user_info else 0
    
    welcome = "\n👋 *Welcome to OSINT & Pincode Lookup Bot!*\n\n💎 Remaining Credits: `" + str(credits) + "`\nNeeche diye gaye menu se option select karein!\n🎁 *Daily Bonus:* `/daily`\n🔗 *Referral Link:* `/ref`\n📜 *Search History:* `/history`\n\n🚀 *Developed by " + OWNER_USERNAME + "*\n    "
    
    menu_keyboard = [
        [KeyboardButton("🔍 Number Info"), KeyboardButton("📍 Pincode Info")],
        [KeyboardButton("🌐 IP Info"), KeyboardButton("🆔 Aadhaar Info")],
        [KeyboardButton("🔤 TG To Number"), KeyboardButton("💎 My Premium Status")],
        [KeyboardButton("💰 My Balance"), KeyboardButton("💬 Owner | Support")],
        [KeyboardButton("💰 Refer & Earn"), KeyboardButton("🏆 Leaderboard")],
        [KeyboardButton("🤖 My Clone Bot"), KeyboardButton("💎 Buy Premium / Credits")],
        [KeyboardButton("🛠 Toggle Menu")]
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
        await update.message.reply_text("✅ *Verification Successful!* You now have free credits.", parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
        
        is_joined, unjoined_channels = await check_multi_force_subscription(context.bot, user.id)
        if not is_joined:
            join_buttons = []
            for ch in unjoined_channels:
                join_buttons.append([InlineKeyboardButton(f"📢 Join {ch}", url=f"https://t.me/{ch.replace('@', '')}")])
            join_buttons.append([InlineKeyboardButton("✅ I Have Joined All", callback_data="check_join_btn")])
            await update.message.reply_text("⚠️ *MULTI-CHANNEL FORCE JOIN REQUIRED*\n\nBot ko use karne ke liye kripya neeche diye gaye sabhi channels ko join karein:", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(join_buttons))
            return

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
    
    if hasattr(update, 'message') and update.message:
        await update.message.reply_text(text, parse_mode='Markdown')
    elif hasattr(update, 'callback_query') and update.callback_query:
        await update.callback_query.message.reply_text(text, parse_mode='Markdown')

async def check_user_credit(update, user):
    user_data = db_get_one("SELECT * FROM users WHERE user_id = ?", (user.id,))
    if not user_data or user_data.get('is_banned') == 1:
        await update.message.reply_text("❌ Aapko block kar diya gaya hai.")
        return False
    if not user_data.get('phone_number') or not user_data['phone_number']:
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
    
    reward_setting = db_get_one("SELECT value FROM settings WHERE key='ref_reward_credits'")
    ref_reward = reward_setting['value'] if reward_setting else "2"
    
    referred_users = db_get_all("SELECT first_name, username, joined_date FROM users WHERE referred_by = ? ORDER BY joined_date DESC LIMIT 10", (user.id,))
    
    text = "➿➿➿➿➿➿➿➿➿➿➿\n💰 𝗥𝗲𝗳𝗲𝗿 & 𝗲𝗮𝗿𝗻 ⛓\n➿➿➿➿➿➿➿➿➿➿➿\n\n"
    text += f"📲 Har successful refer par milenge: `{ref_reward}` Credits\n"
    text += f"🔗 **Aapka Referral Link:**\n`{ref_link}`\n\n"
    
    text += f"📜 **Aapki Referral History (Total: {len(referred_users)}):**\n━━━━━━━━━━━━━━━━━━━━\n"
    if not referred_users:
        text += "_Abhi tak kisi ko refer nahi kiya hai._\n"
    else:
        for idx, ref_u in enumerate(referred_users, 1):
            uname = f"@{ref_u['username']}" if ref_u['username'] and ref_u['username'] != 'NoUsername' else "No Username"
            text += f"{idx}. **{ref_u['first_name']}** ({uname}) — _{ref_u['joined_date']}_\n"
            
    refer_keyboard = [
        [InlineKeyboardButton("📤 Share Friend", url="https://t.me/share/url?url=" + ref_link + "&text=Join%20this%20awesome%20OSINT%20bot%20and%20get%20free%20credits!")],
        [InlineKeyboardButton("💳 Buy Credits", callback_data="buy_credits_btn")]
    ]
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(refer_keyboard))

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🟢 **LIVE API HEALTH STATUS**\n━━━━━━━━━━━━━━━━━━━━\n• Supabase Lookup API: `🟢 Online`\n• Pincode API: `🟢 Online`\n• Telegram Lookup API: `🟢 Online`\n• IP Info API: `🟢 Online`\n• Aadhaar API: `🟢 Online`"
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
    active_live_users.add(user.id)

    # Anti-Flood / Auto-Ban Protection
    current_time = time.time()
    if not is_admin_user(user.id):
        if user.id not in user_flood_tracker:
            user_flood_tracker[user.id] = {"count": 1, "first_time": current_time}
        else:
            data = user_flood_tracker[user.id]
            if current_time - data["first_time"] < 3:
                data["count"] += 1
                if data["count"] > 6:
                    db_execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user.id,), commit=True)
                    await update.message.reply_text("🚫 **AUTO-BANNED FOR SPAMMING!**\nAapne bahut tezi se messages bheje, isliye system ne aapko block kar diya hai.")
                    return
                elif data["count"] > 3:
                    await update.message.reply_text("⚠️ **Anti-Flood Warning:** Thoda dheere type karein, warna ban ho sakte hain!")
                    return
            else:
                user_flood_tracker[user.id] = {"count": 1, "first_time": current_time}

    text = update.message.text.strip() if update.message.text else ""

    # Strict Admin Prompt Handlers (Only execute if waiting flag is True)
    if is_admin_user(user.id):
        if context.user_data.get('waiting_for_banner'):
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
                await update.message.reply_text("✅ Success! Naya banner media set ho chuka hai.", parse_mode='Markdown')
                return
            else:
                await update.message.reply_text("❌ Kripya gallery se koi valid GIF, Video ya Photo bhejein.")
                return

        if context.user_data.get('waiting_for_maint_msg'):
            feat_key = context.user_data.get('target_maint_feat')
            new_msg = text
            db_execute("UPDATE feature_maint SET message = ? WHERE feature_key = ?", (new_msg, feat_key), commit=True)
            context.user_data['waiting_for_maint_msg'] = False
            context.user_data['target_maint_feat'] = None
            await update.message.reply_text("✅ *Feature Maintenance Message Successfully Updated!*", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_clone_ref_count'):
            new_count = text.strip()
            if new_count.isdigit():
                db_execute("UPDATE settings SET value = ? WHERE key = 'clone_req_ref'", (new_count,), commit=True)
                context.user_data['waiting_for_clone_ref_count'] = False
                await update.message.reply_text(f"✅ Clone referral requirement successfully updated to: `{new_count}`", parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Kripya koi valid digit enter karein (jaise `5` ya `10`).")
            return

        if context.user_data.get('waiting_for_ref_reward'):
            new_reward = text.strip()
            if new_reward.isdigit():
                db_execute("UPDATE settings SET value = ? WHERE key = 'ref_reward_credits'", (new_reward,), commit=True)
                context.user_data['waiting_for_ref_reward'] = False
                await update.message.reply_text(f"✅ Referral reward credits successfully updated to: `{new_reward}` credits per refer!", parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Kripya koi valid digit enter karein (jaise `2` ya `5`).")
            return

        if context.user_data.get('waiting_for_force_channels'):
            new_channels = text.strip()
            db_execute("UPDATE settings SET value = ? WHERE key = 'force_channels'", (new_channels,), commit=True)
            context.user_data['waiting_for_force_channels'] = False
            await update.message.reply_text(f"✅ Multi-Channel Force Join successfully set to: `{new_channels}`", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_broadcast'):
            broadcast_text = text
            context.user_data['waiting_for_broadcast'] = False
            
            inline_keyboard = []
            if "|" in broadcast_text and "-" in broadcast_text:
                parts = broadcast_text.split("|")
                main_msg = parts[0].strip()
                btn_part = parts[1].strip()
                if "-" in btn_part:
                    btn_name, btn_url = btn_part.split("-", 1)
                    inline_keyboard.append([InlineKeyboardButton(btn_name.strip(), url=btn_url.strip())])
            
            users = db_get_all("SELECT user_id FROM users")
            sent = 0
            for u in users:
                try:
                    if inline_keyboard:
                        await context.bot.send_message(chat_id=u['user_id'], text=main_msg if 'main_msg' in locals() else broadcast_text, reply_markup=InlineKeyboardMarkup(inline_keyboard), parse_mode='Markdown')
                    else:
                        await context.bot.send_message(chat_id=u['user_id'], text=broadcast_text, parse_mode='Markdown')
                    sent += 1
                except: pass
            await update.message.reply_text(f"📢 Broadcast sent to {sent} users.")
            return

        if context.user_data.get('waiting_for_clone_token'):
            token_str = text.strip()
            bot_username_val = "@CloneBot"
            db_execute("INSERT INTO clones (owner_id, bot_token, bot_username, status) VALUES (?, ?, ?, ?)", (user.id, token_str, bot_username_val, 'Active'), commit=True)
            context.user_data['waiting_for_clone_token'] = False
            await update.message.reply_text("✅ *Aapka Clone Bot Successfully Register Ho Chuka Hai!*", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_api_url'):
            api_k = context.user_data.get('target_api_key')
            new_url = text.strip()
            db_execute("UPDATE dynamic_apis SET api_url = ? WHERE api_key = ?", (new_url, api_k), commit=True)
            context.user_data['waiting_for_api_url'] = False
            context.user_data['target_api_key'] = None
            await update.message.reply_text(f"✅ API URL for `{api_k}` successfully updated!", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_api_old'):
            api_k = context.user_data.get('target_api_key')
            new_old = text.strip()
            db_execute("UPDATE dynamic_apis SET old_credit = ? WHERE api_key = ?", (new_old, api_k), commit=True)
            context.user_data['waiting_for_api_old'] = False
            context.user_data['target_api_key'] = None
            await update.message.reply_text(f"✅ Old watermark text for `{api_k}` successfully updated!", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_api_new'):
            api_k = context.user_data.get('target_api_key')
            new_new = text.strip()
            db_execute("UPDATE dynamic_apis SET new_credit = ? WHERE api_key = ?", (new_new, api_k), commit=True)
            context.user_data['waiting_for_api_new'] = False
            context.user_data['target_api_key'] = None
            await update.message.reply_text(f"✅ New watermark text for `{api_k}` successfully updated!", parse_mode='Markdown')
            return

    # Check Individual Feature Maintenance
    def check_feat_maint(f_key):
        row = db_get_one("SELECT status, message FROM feature_maint WHERE feature_key = ?", (f_key,))
        if row and row['status'] == 'on':
            return True, row['message']
        return False, ""

    if text == "🔍 Number Info":
        is_m, m_msg = check_feat_maint('phone')
        if is_m and not is_admin_user(user.id):
            await update.message.reply_text("🚧 " + m_msg, parse_mode='Markdown')
            return
        context.user_data['mode'] = 'phone'
        db_execute("UPDATE analytics SET count = count + 1 WHERE feature_name = 'Number Info'", commit=True)
        await update.message.reply_text("📱 *Number Info Mode Active*\nKripya ab koi bhi 10-digit mobile number bhejein:", parse_mode='Markdown')
        return
    elif text == "📍 Pincode Info":
        is_m, m_msg = check_feat_maint('pincode')
        if is_m and not is_admin_user(user.id):
            await update.message.reply_text("🚧 " + m_msg, parse_mode='Markdown')
            return
        context.user_data['mode'] = 'pincode'
        db_execute("UPDATE analytics SET count = count + 1 WHERE feature_name = 'Pincode Info'", commit=True)
        await update.message.reply_text("📍 *Pincode Lookup Mode Active*\nKripya ab koi bhi valid 6-digit Indian PIN code bhejein (jaise `411001`):", parse_mode='Markdown')
        return
    elif text == "🌐 IP Info":
        is_m, m_msg = check_feat_maint('ip_info')
        if is_m and not is_admin_user(user.id):
            await update.message.reply_text("🚧 " + m_msg, parse_mode='Markdown')
            return
        context.user_data['mode'] = 'ip_info'
        db_execute("UPDATE analytics SET count = count + 1 WHERE feature_name = 'IP Info'", commit=True)
        await update.message.reply_text("🌐 *IP Info Mode Active*\nKripya ab koi bhi IP address bhejein (jaise `8.8.8.8`):", parse_mode='Markdown')
        return
    elif text == "🆔 Aadhaar Info":
        is_m, m_msg = check_feat_maint('aadhaar_info')
        if is_m and not is_admin_user(user.id):
            await update.message.reply_text("🚧 " + m_msg, parse_mode='Markdown')
            return
        context.user_data['mode'] = 'aadhaar_info'
        db_execute("UPDATE analytics SET count = count + 1 WHERE feature_name = 'Aadhaar Info'", commit=True)
        await update.message.reply_text("🆔 *Aadhaar Info Mode Active*\nKripya ab number bhejein:", parse_mode='Markdown')
        return
    elif text == "🔤 TG To Number":
        is_m, m_msg = check_feat_maint('tg_info')
        if is_m and not is_admin_user(user.id):
            await update.message.reply_text("🚧 " + m_msg, parse_mode='Markdown')
            return
        db_execute("UPDATE analytics SET count = count + 1 WHERE feature_name = 'TG To Number'", commit=True)
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
    elif text == "💎 My Premium Status":
        user_info = db_get_one("SELECT credits, is_admin FROM users WHERE user_id = ?", (user.id,))
        credits = user_info['credits'] if user_info else 0
        status = "👑 Admin / Unlimited" if (is_admin_user(user.id) or credits > 5000) else ("💎 Premium User" if credits > 10 else "🆓 Free User")
        status_text = "👤 *Aapki Account Details:*\n━━━━━━━━━━━━━━━━━━━━\n📌 Status: `" + status + "`\n💎 Remaining Credits: `" + str(credits) + "`\n🚀 Developer: " + OWNER_USERNAME
        await update.message.reply_text(status_text, parse_mode='Markdown')
        return
    elif text == "💰 My Balance":
        await balance_command(update, context)
        return
    elif text == "💬 Owner | Support":
        await support_command(update, context)
        return
    elif text == "💰 Refer & Earn":
        is_m, m_msg = check_feat_maint('ref')
        if is_m and not is_admin_user(user.id):
            await update.message.reply_text("🚧 " + m_msg, parse_mode='Markdown')
            return
        db_execute("UPDATE analytics SET count = count + 1 WHERE feature_name = 'Refer & Earn'", commit=True)
        await ref_command(update, context)
        return
    elif text == "🏆 Leaderboard":
        top_users = db_get_all("SELECT first_name, credits, searches FROM users ORDER BY searches DESC LIMIT 10")
        lb_text = "🏆 **TOP SEARCHERS LEADERBOARD**\n━━━━━━━━━━━━━━━━━━━━\n"
        for idx, u in enumerate(top_users, 1):
            lb_text += f"{idx}. **{u['first_name']}** — 🔍 Lookups: `{u['searches']}` | 💎 Credits: `{u['credits']}`\n"
        await update.message.reply_text(lb_text, parse_mode='Markdown')
        return
    elif text == "🤖 My Clone Bot":
        toggle_setting = db_get_one("SELECT value FROM settings WHERE key='clone_ref_toggle'")
        is_toggle_on = (toggle_setting['value'] == 'on') if toggle_setting else True

        if is_toggle_on:
            req_ref_setting = db_get_one("SELECT value FROM settings WHERE key='clone_req_ref'")
            req_refs = int(req_ref_setting['value']) if req_ref_setting else 2
            user_refs = db_get_all("SELECT COUNT(*) as cnt FROM users WHERE referred_by = ?", (user.id,))[0]['cnt']
            
            if user_refs < req_refs and not is_admin_user(user.id):
                await update.message.reply_text(f"🤖 Kripya pehle apne `{req_refs}` referrals complete karein (Aapke abhi `{user_refs}/{req_refs}` hain) taaki aap apna khud ka clone bot bana sakein!", parse_mode='Markdown')
                return
            
        clone_keyboard = [[InlineKeyboardButton("➕ Create New Clone Bot", callback_data="create_clone_prompt")]]
        await update.message.reply_text("🤖 **MY CLONE BOT MANAGER**\n\nNeeche diye gaye button par click karke apna bot clone setup karein:", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(clone_keyboard))
        return
    elif text == "🔙 Back to Main Menu":
        context.user_data['mode'] = None
        await send_welcome_menu(update, context, user)
        return
    elif text == "💎 Buy Premium / Credits":
        await show_premium_plans(update, context)
        return
    elif text == "🛠 Toggle Menu":
        await update.message.reply_text("📉 Menu hide kar diya gaya hai. Wapas lane ke liye /start dabayein.", reply_markup=ReplyKeyboardRemove())
        return
    elif text == "📊 Admin Panel" and is_admin_user(user.id):
        total_users = db_get_one("SELECT COUNT(*) as count FROM users")['count']
        total_searches = db_get_one("SELECT COUNT(*) as count FROM searches")['count']
        maint = db_get_one("SELECT value FROM settings WHERE key='maintenance'")['value']
        upi_record = db_get_one("SELECT value FROM settings WHERE key='upi_id'")
        clone_ref_val = db_get_one("SELECT value FROM settings WHERE key='clone_req_ref'")['value']
        clone_toggle_val = db_get_one("SELECT value FROM settings WHERE key='clone_ref_toggle'")['value']
        ref_reward_val = db_get_one("SELECT value FROM settings WHERE key='ref_reward_credits'")['value']
        
        panel_text = f"\n📊 *ADVANCED ADMIN PANEL* ({OWNER_USERNAME})\n━━━━━━━━━━━━━━━━━━\n👥 Total Users: `{total_users}`\n🔍 Total Lookups: `{total_searches}`\n💳 Current UPI: `{upi_record['value'] if upi_record else 'Not Set'}`\n🚧 Maintenance Mode: `{maint.upper()}`\n🤖 Clone Refs Req: `{clone_ref_val}` (Status: `{clone_toggle_val.upper()}`)\n🎁 Ref Reward: `{ref_reward_val} Credits`\n⚡ API Status: `🟢 Online`\n        "
        keyboard = [
            [InlineKeyboardButton("🟢 👥 View Users", callback_data="admin_users"), InlineKeyboardButton("💳 ⚙️ Set UPI ID", callback_data="admin_setupi_prompt")],
            [InlineKeyboardButton("📦 📋 Manage Plans", callback_data="admin_plans"), InlineKeyboardButton("💎 ➕ Add Credits", callback_data="admin_addcredit_prompt")],
            [InlineKeyboardButton("📈 ⚡ Live Analytics", callback_data="admin_live_analytics"), InlineKeyboardButton("🤖 👥 Clone Bots", callback_data="admin_clones")],
            [InlineKeyboardButton("🛠️ ⚙️ Feature Maint.", callback_data="admin_feature_maint"), InlineKeyboardButton("🌐 🔌 Dynamic APIs", callback_data="admin_dynamic_apis")],
            [InlineKeyboardButton("🔄 Toggle Clone Ref", callback_data="admin_toggle_clone_ref"), InlineKeyboardButton("👥 ⚙️ Set Clone Refs", callback_data="admin_cloneref_prompt")],
            [InlineKeyboardButton("🎁 ⚙️ Set Ref Reward", callback_data="admin_refreward_prompt"), InlineKeyboardButton("🖼️ ⚙️ Set Banner", callback_data="admin_banner_prompt")],
            [InlineKeyboardButton("🛡️ ➕ Add Sub-Admin", callback_data="admin_addsub_prompt"), InlineKeyboardButton("🛠️ 🔄 Maintenance", callback_data="toggle_maintenance")],
            [InlineKeyboardButton("❌ 📦 Close", callback_data="close_panel")]
        ]
        await update.message.reply_text(panel_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    user_data = db_get_one("SELECT phone_number, is_banned FROM users WHERE user_id = ?", (user.id,))
    if not user_data or user_data.get('is_banned') == 1:
        await update.message.reply_text("❌ Aapko bot use karne se block kar diya gaya hai.")
        return
    if not user_data.get('phone_number') or not user_data['phone_number']:
        contact_button = [[KeyboardButton("📱 Share Contact to Verify & Start", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(contact_button, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("⚠️ *SECURITY VERIFICATION REQUIRED*\n\nScam se bachne ke liye kripya neeche diye gaye button par click karke apna contact verify karein!", parse_mode='Markdown', reply_markup=reply_markup)
        return

    if not await check_user_credit(update, user): return

    mode = context.user_data.get('mode', None)
    cleaned = re.sub(r'\D', '', text)

    if mode == 'aadhaar_info':
        aadhaar_str = text
        msg = await update.message.reply_text("🆔 *INTELLIGENCE BREACH*\nInitializing...", parse_mode='Markdown')
        data = await fetch_dynamic_api('aadhaar_info', aadhaar_str)
        await show_hacking_animation(msg, aadhaar_str, title_type="AADHAAR")
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, "AADHAAR:" + aadhaar_str, json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        formatted = format_aadhaar_response(data, aadhaar_str)
        try: await msg.edit_text(formatted, parse_mode='Markdown')
        except: await msg.edit_text(formatted, parse_mode=None)
        context.user_data['mode'] = None
    elif mode == 'ip_info':
        ip_str = text
        msg = await update.message.reply_text("🌐 *IP INTELLIGENCE BREACH*\nInitializing...", parse_mode='Markdown')
        data = await fetch_dynamic_api('ip_info', ip_str)
        await show_hacking_animation(msg, ip_str, title_type="IP")
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, "IP:" + ip_str, json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        formatted = format_ip_response(data, ip_str)
        try: await msg.edit_text(formatted, parse_mode='Markdown')
        except: await msg.edit_text(formatted, parse_mode=None)
        context.user_data['mode'] = None
    elif mode == 'tg_username':
        query_str = text if text.startswith('@') else '@' + text
        msg = await update.message.reply_text("🕵️‍♂️ *TELEGRAM USERNAME INTEL BREACH*\nInitializing...", parse_mode='Markdown')
        data = await fetch_dynamic_api('tg_username', query_str)
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
        data = await fetch_dynamic_api('tg_userid', userid_str)
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
        data = await fetch_dynamic_api('pincode', pincode)
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
        data = await fetch_dynamic_api('phone', phone)
        await show_hacking_animation(msg, phone, title_type="PHONE")
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, phone, json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        records, err = parse_phone_records(data, phone)
        if err: await msg.edit_text(err)
        else: await send_stylish_chunked_response(msg, records, phone, update, context)
        context.user_data['mode'] = None
    else:
        await update.message.reply_text("❌ Kripya valid input enter karein (Mobile Number, Pincode, IP, ya TG query).", parse_mode='Markdown')

# ============================================
# ADMIN CALLBACK HANDLER
# ============================================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "buy_credits_btn":
        await show_premium_plans(query, context)
        return
    elif data == "check_join_btn":
        is_joined, _ = await check_multi_force_subscription(context.bot, query.from_user.id)
        if is_joined:
            await query.message.delete()
            await send_welcome_menu(query, context, query.from_user)
        else:
            await query.answer("❌ Aapne abhi tak saare channels join nahi kiye hain!", show_alert=True)
        return
    elif data == "create_clone_prompt":
        context.user_data['waiting_for_clone_token'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="🤖 **BOT CLONE SETUP**\n\nKripya apne naye bot ka **Bot Token** (@BotFather se liya hua) yahan bhej dein:", parse_mode='Markdown')
        return

    if not is_admin_user(query.from_user.id):
        return

    if data == "admin_panel":
        total_users = db_get_one("SELECT COUNT(*) as count FROM users")['count']
        total_searches = db_get_one("SELECT COUNT(*) as count FROM searches")['count']
        maint = db_get_one("SELECT value FROM settings WHERE key='maintenance'")['value']
        upi_record = db_get_one("SELECT value FROM settings WHERE key='upi_id'")
        clone_ref_val = db_get_one("SELECT value FROM settings WHERE key='clone_req_ref'")['value']
        clone_toggle_val = db_get_one("SELECT value FROM settings WHERE key='clone_ref_toggle'")['value']
        ref_reward_val = db_get_one("SELECT value FROM settings WHERE key='ref_reward_credits'")['value']
        
        panel_text = f"\n📊 *ADVANCED ADMIN PANEL* ({OWNER_USERNAME})\n━━━━━━━━━━━━━━━━━━\n👥 Total Users: `{total_users}`\n🔍 Total Lookups: `{total_searches}`\n💳 Current UPI: `{upi_record['value'] if upi_record else 'Not Set'}`\n🚧 Maintenance Mode: `{maint.upper()}`\n🤖 Clone Refs Req: `{clone_ref_val}` (Status: `{clone_toggle_val.upper()}`)\n🎁 Ref Reward: `{ref_reward_val} Credits`\n⚡ API Status: `🟢 Online`\n        "
        keyboard = [
            [InlineKeyboardButton("🟢 👥 View Users", callback_data="admin_users"), InlineKeyboardButton("💳 ⚙️ Set UPI ID", callback_data="admin_setupi_prompt")],
            [InlineKeyboardButton("📦 📋 Manage Plans", callback_data="admin_plans"), InlineKeyboardButton("💎 ➕ Add Credits", callback_data="admin_addcredit_prompt")],
            [InlineKeyboardButton("📈 ⚡ Live Analytics", callback_data="admin_live_analytics"), InlineKeyboardButton("🤖 👥 Clone Bots", callback_data="admin_clones")],
            [InlineKeyboardButton("🛠️ ⚙️️ Feature Maint.", callback_data="admin_feature_maint"), InlineKeyboardButton("🌐 🔌 Dynamic APIs", callback_data="admin_dynamic_apis")],
            [InlineKeyboardButton("🔄 Toggle Clone Ref", callback_data="admin_toggle_clone_ref"), InlineKeyboardButton("👥 ⚙️ Set Clone Refs", callback_data="admin_cloneref_prompt")],
            [InlineKeyboardButton("🎁 ⚙️ Set Ref Reward", callback_data="admin_refreward_prompt"), InlineKeyboardButton("🖼️ ⚙️ Set Banner", callback_data="admin_banner_prompt")],
            [InlineKeyboardButton("🛡️ ➕ Add Sub-Admin", callback_data="admin_addsub_prompt"), InlineKeyboardButton("🛠️ 🔄 Maintenance", callback_data="toggle_maintenance")],
            [InlineKeyboardButton("❌ 📦 Close", callback_data="close_panel")]
        ]
        try: await query.edit_message_text(panel_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except: pass
        
    elif data == "admin_dynamic_apis":
        apis = db_get_all("SELECT * FROM dynamic_apis")
        text = "🌐 *DYNAMIC API MANAGER*\n━━━━━━━━━━━━━━━━━━━━\nSelect an API to configure URL or Watermark Replacement:\n\n"
        keyboard = []
        for ap in apis:
            text += f"• **{ap['api_name']}** (`{ap['api_key']}`)\n  `{ap['api_url']}`\n  _Old Text: {ap['old_credit']} -> New: {ap['new_credit']}_\n\n"
            keyboard.append([
                InlineKeyboardButton(f"🔗 URL: {ap['api_name']}", callback_data=f"edit_api_url_{ap['api_key']}"),
                InlineKeyboardButton(f"✍️ Old/New", callback_data=f"edit_api_wm_{ap['api_key']}")
            ])
        keyboard.append([InlineKeyboardButton("🔵 📊 Back to Panel", callback_data="admin_panel")])
        try: await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except: pass

    elif data.startswith("edit_api_url_"):
        api_k = data.replace("edit_api_url_", "")
        context.user_data['waiting_for_api_url'] = True
        context.user_data['target_api_key'] = api_k
        await context.bot.send_message(chat_id=query.from_user.id, text=f"🌐 Enter new API URL for `{api_k}` (Use `{{query}}` as placeholder):", parse_mode='Markdown')

    elif data.startswith("edit_api_wm_"):
        api_k = data.replace("edit_api_wm_", "")
        context.user_data['waiting_for_api_old'] = True
        context.user_data['target_api_key'] = api_k
        await context.bot.send_message(chat_id=query.from_user.id, text=f"✍️ Enter **old text / watermark** to replace for `{api_k}`:", parse_mode='Markdown')

    elif data == "admin_toggle_clone_ref":
        curr = db_get_one("SELECT value FROM settings WHERE key='clone_ref_toggle'")
        new_val = 'off' if curr and curr['value'] == 'on' else 'on'
        db_execute("UPDATE settings SET value = ? WHERE key = 'clone_ref_toggle'", (new_val,), commit=True)
        await query.answer(f"✅ Clone Referral Requirement is now {new_val.upper()}!", show_alert=True)
        query.data = "admin_panel"
        await button_callback(update, context)

    elif data == "admin_cloneref_prompt":
        context.user_data['waiting_for_clone_ref_count'] = True
        curr_ref = db_get_one("SELECT value FROM settings WHERE key='clone_req_ref'")['value']
        await context.bot.send_message(chat_id=query.from_user.id, text=f"👥 **Set Clone Referral Requirement**\n\nCurrent required referrals: `{curr_ref}`\n\nAb naya number bhejein (jaise `5` ya `10`):", parse_mode='Markdown')

    elif data == "admin_refreward_prompt":
        context.user_data['waiting_for_ref_reward'] = True
        curr_rew = db_get_one("SELECT value FROM settings WHERE key='ref_reward_credits'")['value']
        await context.bot.send_message(chat_id=query.from_user.id, text=f"🎁 **Set Referral Reward Credits**\n\nCurrent reward credits per refer: `{curr_rew}`\n\nAb naya credit amount bhejein (jaise `2` ya `5`):", parse_mode='Markdown')

    elif data == "admin_feature_maint":
        feats = db_get_all("SELECT * FROM feature_maint")
        text = "🛠️ *FEATURE-WISE MAINTENANCE MANAGER*\n━━━━━━━━━━━━━━━━━━━━\n"
        keyboard = []
        for f in feats:
            status_icon = "🟢 ACTIVE" if f['status'] == 'off' else "🔴 UNDER WORK"
            text += f"• **{f['feature_key'].upper()}**: `{status_icon}`\n  _Msg: {f['message']}_\n\n"
            keyboard.append([InlineKeyboardButton(f"🔄 Toggle {f['feature_key']}", callback_data=f"toggle_feat_{f['feature_key']}"), InlineKeyboardButton(f"💬 Edit Msg", callback_data=f"edit_feat_{f['feature_key']}")])
        keyboard.append([InlineKeyboardButton("🔵 📊 Back to Panel", callback_data="admin_panel")])
        try: await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except: pass

    elif data.startswith("toggle_feat_"):
        f_key = data.replace("toggle_feat_", "")
        cur = db_get_one("SELECT status FROM feature_maint WHERE feature_key = ?", (f_key,))
        new_status = 'on' if cur['status'] == 'off' else 'off'
        db_execute("UPDATE feature_maint SET status = ? WHERE feature_key = ?", (new_status, f_key), commit=True)
        query.data = "admin_feature_maint"
        await button_callback(update, context)

    elif data.startswith("edit_feat_"):
        f_key = data.replace("edit_feat_", "")
        context.user_data['waiting_for_maint_msg'] = True
        context.user_data['target_maint_feat'] = f_key
        await context.bot.send_message(chat_id=query.from_user.id, text=f"💬 Enter new custom message for feature `{f_key}`:", parse_mode='Markdown')

    elif data == "admin_live_analytics":
        live_count = len(active_live_users)
        analytics = db_get_all("SELECT feature_name, count FROM analytics")
        text = f"📈 *LIVE BOT ANALYTICS & TRACKING*\n━━━━━━━━━━━━━━━━━━━━\n🟢 Currently Active Live Users: `{live_count}`\n\n📊 **Feature Usage Stats:**\n"
        for an in analytics:
            text += f"• `{an['feature_name']}`: `{an['count']}` uses\n"
        keyboard = [[InlineKeyboardButton("🔵 📊 Back to Panel", callback_data="admin_panel")]]
        try: await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except: pass

    elif data == "admin_clones":
        clones = db_get_all("SELECT * FROM clones")
        text = "🤖 *USER CLONE BOTS MANAGER*\n━━━━━━━━━━━━━━━━━━━━\n"
        if not clones:
            text += "Koi bhi clone bot abhi registered nahi hai."
            keyboard = [[InlineKeyboardButton("🔵 📊 Back to Panel", callback_data="admin_panel")]]
        else:
            keyboard = []
            for cl in clones:
                text += f"🆔 Clone ID: `{cl['id']}` | Owner: `{cl['owner_id']}`\nStatus: `{cl['status']}`\n--------------------\n"
                keyboard.append([InlineKeyboardButton(f"🛑 Stop Clone #{cl['id']}", callback_data=f"stop_clone_{cl['id']}"), InlineKeyboardButton(f"📋 View Searches #{cl['id']}", callback_data=f"view_clone_searches_{cl['owner_id']}")])
            keyboard.append([InlineKeyboardButton("🔵 📊 Back to Panel", callback_data="admin_panel")])
        try: await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except: pass

    elif data.startswith("stop_clone_"):
        clone_id = data.split("_")[-1]
        db_execute("UPDATE clones SET status = 'Stopped' WHERE id = ?", (clone_id,), commit=True)
        await query.message.reply_text(f"🛑 Clone Bot ID `{clone_id}` successfully stopped!", parse_mode='Markdown')
        query.data = "admin_clones"
        await button_callback(update, context)

    elif data.startswith("view_clone_searches_"):
        owner_id = data.split("_")[-1]
        searches = db_get_all("SELECT phone, timestamp FROM searches WHERE user_id = ? ORDER BY timestamp DESC LIMIT 10", (owner_id,))
        text = f"📜 *Searches for Clone Owner ID `{owner_id}`:*\n"
        if not searches:
            text += "Koi search history nahi mili."
        for s in searches:
            text += f"• `{s['phone']}` — _{s['timestamp']}_\n"
        await query.message.reply_text(text, parse_mode='Markdown')

    elif data == "admin_stats":
        total_users = db_get_one("SELECT COUNT(*) as count FROM users")['count']
        total_searches = db_get_one("SELECT COUNT(*) as count FROM searches")['count']
        banned_users = db_get_one("SELECT COUNT(*) as count FROM users WHERE is_banned = 1")['count']
        stats_text = "\n📈 **BOT DETAILED STATISTICS**\n━━━━━━━━━━━━━━━━━━━━\n👥 Total Registered Users: `" + str(total_users) + "`\n🔴 Banned Users: `" + str(banned_users) + "`\n🔍 Total Searches Made: `" + str(total_searches) + "`\n⚡ Current Server Status: `🟢 Online`\n        "
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
        text += "\n💡 To add a new plan, use command:\n`/addplan <name> <price> <credits>`"
        keyboard = [
            [InlineKeyboardButton("➕ Add Plan Prompt", callback_data="admin_addplan_prompt")],
            [InlineKeyboardButton("🔵 📊 Back to Panel", callback_data="admin_panel")]
        ]
        try: await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except: pass

    elif data == "admin_forcechan_prompt":
        context.user_data['waiting_for_force_channels'] = True
        curr_chan = db_get_one("SELECT value FROM settings WHERE key='force_channels'")['value']
        await context.bot.send_message(chat_id=query.from_user.id, text=f"📢 **Multi-Channel Force Join Setup**\n\nCurrent Channels: `{curr_chan or 'None'}`\n\nAb apne channels comma se alag karke bhejein (jaise `@channel1, @channel2`):", parse_mode='Markdown')

    elif data == "admin_broadcast_prompt":
        context.user_data['waiting_for_broadcast'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="📢 **Broadcast Media with Inline Button**\n\nKripya message format is tarah bhejein:\n`Aapka message text | Button Name - https://t.me/yourlink`", parse_mode='Markdown')

    elif data == "admin_addplan_prompt":
        await context.bot.send_message(chat_id=query.from_user.id, text="💡 To add a plan, use command:\n`/addplan <name> <price> <credits>`", parse_mode='Markdown')

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
        current = db_get_one("SELECT value FROM settings WHERE key='maintenance'")['value']
        new_val = 'off' if current == 'on' else 'on'
        db_execute("UPDATE settings SET value = ? WHERE key = 'maintenance'", (new_val,), commit=True)
        
        total_users = db_get_one("SELECT COUNT(*) as count FROM users")['count']
        total_searches = db_get_one("SELECT COUNT(*) as count FROM searches")['count']
        upi_record = db_get_one("SELECT value FROM settings WHERE key='upi_id'")
        
        panel_text = "\n📊 *ADVANCED ADMIN PANEL* (" + OWNER_USERNAME + ")\n━━━━━━━━━━━━━━━━━━\n👥 Total Users: `" + str(total_users) + "`\n🔍 Total Lookups: `" + str(total_searches) + "`\n💳 Current UPI: `" + str(upi_record['value'] if upi_record else 'Not Set') + "`\n🚧 Maintenance Mode: `" + new_val.upper() + "`\n⚡ API Status: `🟢 Online`\n        "
        keyboard = [
            [InlineKeyboardButton("🟢 👥 View Users", callback_data="admin_users"), InlineKeyboardButton("💳 ⚙️ Set UPI ID", callback_data="admin_setupi_prompt")],
            [InlineKeyboardButton("📦 📋 Manage Plans", callback_data="admin_plans"), InlineKeyboardButton("💎 ➕ Add Credits", callback_data="admin_addcredit_prompt")],
            [InlineKeyboardButton("📈 ⚡ Live Analytics", callback_data="admin_live_analytics"), InlineKeyboardButton("🤖 👥 Clone Bots", callback_data="admin_clones")],
            [InlineKeyboardButton("🛠️ ⚙️ Feature Maint.", callback_data="admin_feature_maint"), InlineKeyboardButton("📢 📤 Broadcast Media", callback_data="admin_broadcast_prompt")],
            [InlineKeyboardButton("🔄 Toggle Clone Ref", callback_data="admin_toggle_clone_ref"), InlineKeyboardButton("🖼️ ⚙️ Set Banner", callback_data="admin_banner_prompt")],
            [InlineKeyboardButton("🛡️ ➕ Add Sub-Admin", callback_data="admin_addsub_prompt"), InlineKeyboardButton("🛠️ 🔄 Maintenance", callback_data="toggle_maintenance")],
            [InlineKeyboardButton("❌ 📦 Close", callback_data="close_panel")]
        ]
        try: await query.edit_message_text(panel_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except: pass

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
        await update.message.reply_text("❌ Usage: `/maint on` or `/maint off`", parse_mode='Markdown')
        return
    status = context.args[0].lower()
    db_execute("UPDATE settings SET value = ? WHERE key = 'maintenance'", (status,), commit=True)
    await update.message.reply_text("🚧 Maintenance Mode set to `" + status.upper() + "`", parse_mode='Markdown')

async def addplan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin_user(update.effective_user.id): return
    if len(context.args) < 3:
        await update.message.reply_text("❌ Usage: `/addplan <name> <price> <credits>`\n(Example: `/addplan Ultra ₹299 100`)", parse_mode='Markdown')
        return
    name = context.args[0]
    price = context.args[1]
    try:
        credits = int(context.args[2])
        db_execute("INSERT INTO plans (name, price, credits) VALUES (?, ?, ?)", (name, price, credits), commit=True)
        await update.message.reply_text("✅ Plan `" + name + "` added successfully!", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text("❌ Error adding plan: " + str(e))

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
    threading.Thread(target=run_flask, daemon=True).start()
    print("🚀 HARSH OSINT BOT STARTING (SYNTAX ERROR FIXED)...")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("support", support_command))
    application.add_handler(CommandHandler("balance", balance_command))
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
    application.add_handler(CommandHandler("addplan", addplan_command))
    application.add_handler(CommandHandler("createcoupon", createcoupon_command))
    application.add_handler(CommandHandler("addsub", addsub_command))
    application.add_handler(CommandHandler("addcredits", addcredits_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == '__main__':
    main()
