#!/usr/init/env python3
# OSINT & Pincode Bot - Ultimate 10 Report Styles & Fully Restored Admin Panel
"""
Developer: @Harsx1618
Description: Advanced Telegram OSINT Bot with All Restored Admin Buttons, Redeem Keys & Full Features
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

USER_BOT_TOKEN = "8664550290:AAFe6m8yQrx5Km8mvh-tz5Y8rcfY1zcWIZ4"  # Users Bot Token[span_0](start_span)[span_0](end_span)
ADMIN_BOT_TOKEN = "8664550290:AAFe6m8yQrx5Km8mvh-tz5Y8rcfY1zcWIZ4" # Admin Control Bot Token[span_1](start_span)[span_1](end_span)
ADMIN_ID = 1420016904                                           # Main Admin ID[span_2](start_span)[span_2](end_span)
OWNER_USERNAME = "@Harsx1618"                                   # Owner Username[span_3](start_span)[span_3](end_span)
BOT_USERNAME = "@Reasercherinfobot"                             # Bot Username[span_4](start_span)[span_4](end_span)

HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

user_cooldowns = {}
user_flood_tracker = {}
active_live_users = set()

# ============================================
# DATABASE SETUP & AUTO-MIGRATION
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
        last_daily TEXT DEFAULT '',
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_premium INTEGER DEFAULT 0,
        premium_expiry TEXT DEFAULT ''
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS searches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        phone TEXT,
        response TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS redeem_keys (
        key TEXT PRIMARY KEY,
        credits INTEGER,
        is_used INTEGER DEFAULT 0,
        used_by INTEGER DEFAULT 0
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS sub_admins (
        user_id INTEGER PRIMARY KEY
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
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
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('maint_msg', '🚧 Bot abhi maintenance mode par hai. Kripya baad mein koshish karein!')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('upi_id', 'harshhacker@upi')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('upi_qr', '')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('banner_media', '')") 
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('banner_type', 'none')") 
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('clone_req_ref', '2')") 
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('clone_ref_toggle', 'on')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('ref_reward_credits', '2')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('force_channels', '')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('report_style', 'cyber')")
    
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

    for feat_name in ['Number Info', 'Pincode Info', 'IP Info', 'Aadhaar Info', 'TG To Number', 'Refer & Earn']:
        c.execute("INSERT OR IGNORE INTO analytics (feature_name, count) VALUES (?, 0)", (feat_name,))
    
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

def log_activity(user_id, action):
    db_execute("INSERT INTO logs (user_id, action) VALUES (?, ?)", (user_id, action), commit=True)[span_5](start_span)[span_5](end_span)

def get_user_rank(searches):
    if searches >= 100: return "🏆 OSINT Master[span_6](start_span)"[span_6](end_span)
    elif searches >= 50: return "🥇 Elite Hunter[span_7](start_span)"[span_7](end_span)
    elif searches >= 20: return "🥈 Senior Investigator[span_8](start_span)"[span_8](end_span)
    elif searches >= 10: return "🥉 Junior Analyst[span_9](start_span)"[span_9](end_span)
    return "🌱 Beginner[span_10](start_span)"[span_10](end_span)

def background_periodic_worker():
    while True:
        try:
            time.sleep(3600)
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("UPDATE users SET is_premium = 0 WHERE is_premium = 1 AND premium_expiry != '' AND premium_expiry < ?", (now_str,))
            conn.commit()
            conn.close()
        except:
            pass

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
# DYNAMIC API FETCH HELPER
# ============================================
async def fetch_dynamic_api(api_key, query_val, timeout_sec=15):
    api_record = db_get_one("SELECT * FROM dynamic_apis WHERE api_key = ?", (api_key,))
    
    target_url = ""
    if api_record and api_record.get('api_url'):
        target_url = api_record['api_url'].strip()
    
    if not target_url:
        if api_key == 'phone':
            target_url = "https://nmdllpezcocquamhgpmb.supabase.co/functions/v1/lookup?number={query}"
        elif api_key == 'pincode':
            target_url = "https://rack-pincodeapi.vercel.app/api?search={query}"
        elif api_key == 'ip_info':
            target_url = "https://oriss-ip-info-api.antideploy.com/ip/{query}"
        elif api_key == 'aadhaar_info':
            target_url = "https://nitin-vio-api-paid-best.boyu3054.workers.dev/aadhaar?key=FZ-UJKAHS8A2ABUJA8LBBK9&aadhaar={query}"
        elif api_key in ['tg_username', 'tg_userid']:
            target_url = "https://felix-info-x-bot.onrender.com/key=felix67&tg={query}"

    final_url = target_url.replace("{query}", str(query_val))
    old_c = api_record['old_credit'] if api_record and api_record.get('old_credit') else ""
    new_c = api_record['new_credit'] if api_record and api_record.get('new_credit') else ""

    try:
        response = requests.get(final_url, headers=HTTP_HEADERS, timeout=timeout_sec)
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

# ============================================
# REPORT STYLES FORMATTER
# ============================================
async def send_paginated_phone_response(msg_obj, records, phone, update, context, page=0, is_edit=True):
    total = len(records)
    if total == 0:
        await msg_obj.edit_text("❌ Koi record nahi mila.")
        return

    report_style_setting = db_get_one("SELECT value FROM settings WHERE key='report_style'")
    r_style = report_style_setting['value'] if report_style_setting else 'cyber'

    per_page = 5
    total_pages = (total + per_page - 1) // per_page
    page = max(0, min(page, total_pages - 1))
    
    start_idx = page * per_page
    end_idx = min(start_idx + per_page, total)
    chunk = records[start_idx:end_idx]

    if r_style == 'json':
        json_output = {"status": True, "target": str(phone), "total_records": total, "current_page": page + 1, "total_pages": total_pages, "records": chunk, "developer": OWNER_USERNAME}
        text = "```json\n" + json.dumps(json_output, indent=2, ensure_ascii=False) + "\n```"
    elif r_style == 'hacker':
        text = f"💀 [ ROOT ACCESS GRANTED ] 💀\n🎯 TARGET: `{phone}`\n📊 Records: {total} | Page: {page + 1}/{total_pages}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for idx, rec in enumerate(chunk, start=start_idx + 1):
            text += f"⚡ [TARGET #{idx}] ⚡\n• IDENT: `{rec['name']}`\n• COMMS: `{rec['mobile']}`\n• LOC: `{rec['address']}`\n\n"
    else:
        text = f"📱 **NUMBER INTELLIGENCE REPORT**\n🎯 Target: `{phone}`\n📊 Total Records: {total} | Page: {page + 1}/{total_pages}\n━━━━━━━━━━━━━━━━━━━━\n\n"
        for idx, rec in enumerate(chunk, start=start_idx + 1):
            text += f"🔹 **RECORD #{idx}**\n👤 Name: `{rec['name']}`\n📱 Mobile: `{rec['mobile']}`\n🏠 Address:\n`{rec['address']}`\n\n━━━━━━━━━━━━━━━━━━━━\n"

    text += f"⚡ Developed by {OWNER_USERNAME}"
    buttons = []
    nav_row = []
    if page > 0: nav_row.append(InlineKeyboardButton("⬅️️ Previous", callback_data=f"phone_page_{page - 1}"))
    if page < total_pages - 1: nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"phone_page_{page + 1}"))
    if nav_row: buttons.append(nav_row)

    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
    if is_edit:
        try: await msg_obj.edit_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        except: pass
    else:
        reply_msg = await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        msg_obj = reply_msg

def format_pincode_response(data, pincode):
    try:
        json_output = {"status": "success", "pincode": str(pincode), "records": data.get('records', [])[:10]}
        return "```json\n" + json.dumps(json_output, indent=2, ensure_ascii=False) + "\n```"
    except Exception as e:
        return "❌ Error: " + str(e)

def format_tg_response(data, query_str):
    return "```json\n" + json.dumps(data, indent=2, ensure_ascii=False)[:4000] + "\n```"

def format_ip_response(data, ip_str):
    return "```json\n" + json.dumps(data, indent=2, ensure_ascii=False)[:4000] + "\n```"

def format_aadhaar_response(data, query_str):
    return "```json\n" + json.dumps(data, indent=2, ensure_ascii=False)[:4000] + "\n```"

# ============================================
# COMMAND HANDLERS
# ============================================
async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    support_text = "💬 *IF YOU FACE ANY ISSUES CONTACT OUR ADMIN*\n\n📲 **Owner / Support Username:** `" + OWNER_USERNAME + "`"
    support_keyboard = [[InlineKeyboardButton("💬 Chat with Support Owner", url="https://t.me/" + OWNER_USERNAME.replace('@', ''))]]
    await update.message.reply_text(support_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(support_keyboard))

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_info = db_get_one("SELECT credits FROM users WHERE user_id = ?", (user.id,))
    credits = user_info['credits'] if user_info else 0
    await update.message.reply_text(f"💰 *Aapka Current Balance:*\n\n💎 Remaining Credits: `{credits} Credits`", parse_mode='Markdown')

async def redeem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    if not args:
        await update.message.reply_text("⚠️ Kripya key dalein. Sahi tarika: `/redeem YOUR_KEY`", parse_mode='Markdown')
        return
    key = args[0].strip()
    key_data = db_get_one("SELECT * FROM redeem_keys WHERE key = ? AND is_used = 0", (key,))
    if not key_data:
        await update.message.reply_text("❌ Yeh redeem key invalid hai ya pehle hi use ki ja chuki hai.")
        return
    credits_to_add = key_data['credits']
    db_execute("UPDATE users SET credits = credits + ?, is_premium = 1, premium_expiry = datetime('now', '+30 days') WHERE user_id = ?", (credits_to_add, user.id), commit=True)
    db_execute("UPDATE redeem_keys SET is_used = 1, used_by = ? WHERE key = ?", (user.id, key), commit=True)
    log_activity(user.id, f"Redeemed key {key} for {credits_to_add} credits")
    await update.message.reply_text(f"🎉 **Redeem Successful!**\nAapke account mein `{credits_to_add}` credits aur 30 din ki premium access mil gayi hai!", parse_mode='Markdown')

async def daily_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = db_get_one("SELECT last_daily, is_premium FROM users WHERE user_id = ?", (user.id,))
    today_str = datetime.now().strftime("%Y-%m-%d")
    if user_data['last_daily'] == today_str:
        await update.message.reply_text("❌ Aapne aaj ka daily bonus pehle hi claim kar liya hai!")
        return
    bonus = 4 if user_data.get('is_premium') == 1 else 2
    db_execute("UPDATE users SET credits = credits + ?, last_daily = ? WHERE user_id = ?", (bonus, today_str, user.id), commit=True)
    log_activity(user.id, f"Claimed daily bonus of {bonus} credits")
    await update.message.reply_text(f"🎁 **Daily Bonus Claimed!**\nAapko `{bonus}` free credits mile hain.", parse_mode='Markdown')

async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin_user(user.id): return
    try:
        with open(DB_FILE, "rb") as f:
            log_activity(user.id, "Exported database file")
            await update.message.reply_document(document=InputFile(f, filename="supabase_osint.sqlite"), caption="📦 **Database Export File**", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

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
        if ref_id != user.id: referrer_id = ref_id

    reward_setting = db_get_one("SELECT value FROM settings WHERE key='ref_reward_credits'")
    ref_reward = int(reward_setting['value']) if reward_setting and reward_setting['value'].isdigit() else 2

    user_db = db_get_one("SELECT * FROM users WHERE user_id = ?", (user.id,))
    if not user_db:
        db_execute("INSERT INTO users (user_id, username, first_name, credits, referred_by, last_active) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
                   (user.id, user.username or "NoUsername", user.first_name, ref_reward, referrer_id), commit=True)
        log_activity(user.id, "New user joined via /start")
        if referrer_id != 0:
            db_execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (ref_reward, referrer_id), commit=True)
    else:
        db_execute("UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE user_id = ?", (user.id,), commit=True)

    user_db_check = db_get_one("SELECT * FROM users WHERE user_id = ?", (user.id,))
    if user_db_check and user_db_check.get('is_banned') == 1:
        await update.message.reply_text("❌ Aapko bot use karne se block kar diya gaya hai.")
        return

    if not user_db_check.get('phone_number') or not user_db_check['phone_number']:
        contact_button = [[KeyboardButton("📱 Share Contact to Verify & Start", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(contact_button, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("⚠️ *SECURITY VERIFICATION REQUIRED*\nKripya contact verify karein!", parse_mode='Markdown', reply_markup=reply_markup)
        return

    is_joined, unjoined_channels = await check_multi_force_subscription(context.bot, user.id)
    if not is_joined:
        join_buttons = []
        for ch in unjoined_channels:
            join_buttons.append([InlineKeyboardButton(f"📢 Join {ch}", url=f"https://t.me/{ch.replace('@', '')}")])
        join_buttons.append([InlineKeyboardButton("✅ I Have Joined All", callback_data="check_join_btn")])
        await update.message.reply_text("⚠️ *FORCE JOIN REQUIRED*\nChannels join karein:", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(join_buttons))
        return

    await send_welcome_menu(update, context, user)

async def send_welcome_menu(update_or_query, context, user):
    user_info = db_get_one("SELECT credits, searches FROM users WHERE user_id = ?", (user.id,))
    credits = user_info['credits'] if user_info else 0
    searches = user_info['searches'] if user_info else 0
    rank = get_user_rank(searches)
    
    welcome = f"\n👋 *Welcome to OSINT & Pincode Lookup Bot!*\n\n💎 Remaining Credits: `{credits}`\n🎖️ Rank: `{rank}` (Searches: `{searches}`)\n\n🚀 *Developed by {OWNER_USERNAME}*"
    
    apis = db_get_all("SELECT api_name FROM dynamic_apis")
    menu_keyboard = []
    row = []
    
    static_buttons = ["💬 Owner | Support", "💰 Refer & Earn", "🏆 Leaderboard", "🤖 My Clone Bot", "💎 Buy Premium / Credits", "🛠 Toggle Menu"]
    api_button_names = []
    for ap in apis:
        name = ap['api_name']
        if name == 'Number Info': api_button_names.append("🔍 NUMBER INFO")
        elif name == 'Pincode Info': api_button_names.append("📍 PINCODE INFO")
        elif name == 'IP Info': api_button_names.append("🌐 IP INFO")
        elif name == 'Aadhaar Info': api_button_names.append("🆔 AADHAAR INFO")
        elif name == 'TG Username' or name == 'TG UserID':
            if "🔤 TG TO NUMBER" not in api_button_names: api_button_names.append("🔤 TG TO NUMBER")
        else:
            api_button_names.append(f"🔮 {name.upper()}")

    all_menu_items = api_button_names + ["💎 MY PREMIUM STATUS", "💰 MY BALANCE"] + static_buttons
    for item in all_menu_items:
        row.append(KeyboardButton(item))
        if len(row) == 2:
            menu_keyboard.append(row)
            row = []
    if row: menu_keyboard.append(row)

    if is_admin_user(user.id):
        menu_keyboard.append([KeyboardButton("📊 Admin Panel")])

    reply_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)
    banner_media = db_get_one("SELECT value FROM settings WHERE key='banner_media'")['value']
    banner_type = db_get_one("SELECT value FROM settings WHERE key='banner_type'")['value']
    chat_id = update_or_query.message.chat_id if hasattr(update_or_query, 'message') and update_or_query.message else update_or_query.effective_chat.id

    try:
        if banner_type == 'photo' and banner_media:
            await context.bot.send_photo(chat_id=chat_id, photo=banner_media, caption=welcome, parse_mode='Markdown', reply_markup=reply_markup)
            return
    except: pass 

    if hasattr(update_or_query, 'message') and update_or_query.message:
        await update_or_query.message.reply_text(welcome, parse_mode='Markdown', reply_markup=reply_markup)

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    contact = update.message.contact
    if contact and contact.user_id == user.id:
        db_execute("UPDATE users SET phone_number = ?, username = ? WHERE user_id = ?", (contact.phone_number, user.username or "NoUsername", user.id), commit=True)
        log_activity(user.id, "Verified contact successfully")
        await update.message.reply_text("✅ *Verification Successful!*", parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
        await send_welcome_menu(update, context, user)
    else:
        await update.message.reply_text("❌ Kripya apna khud ka contact share karein.", reply_markup=ReplyKeyboardRemove())

async def show_premium_plans(update, context):
    upi_record = db_get_one("SELECT value FROM settings WHERE key='upi_id'")
    upi_id = upi_record['value'] if upi_record else "harshhacker@upi"
    plans = db_get_all("SELECT * FROM plans")
    text = f"💎 **BUY PREMIUM & ADD CREDITS**\n━━━━━━━━━━━━━━━━━━━━━━\n📲 **Admin UPI ID:** `{upi_id}`\n\n📦 **Available Plans:**\n"
    for p in plans:
        text += f"• **{p['name']}** — `{p['price']}` for **{p['credits']} Credits**\n"
    
    chat_id = update.message.chat_id if hasattr(update, 'message') and update.message else update.callback_query.message.chat_id
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
    if user_data['credits'] <= 0 and not is_admin_user(user.id) and user_data.get('is_premium') == 0:
        await update.message.reply_text("❌ Aapke credits khatam ho chuke hain!", parse_mode='Markdown')
        return False
    return True

# ============================================
# MESSAGE HANDLER
# ============================================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    active_live_users.add(user.id)
    db_execute("UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE user_id = ?", (user.id,), commit=True)

    if is_admin_user(user.id):
        if context.user_data.get('waiting_for_banner'):
            if update.message.photo:
                media_id = update.message.photo[-1].file_id
                db_execute("UPDATE settings SET value = ? WHERE key = 'banner_media'", (media_id,), commit=True)
                db_execute("UPDATE settings SET value = 'photo' WHERE key = 'banner_type'", (id,), commit=True)
                context.user_data['waiting_for_banner'] = False
                await update.message.reply_text("✅ Success! Banner updated.", parse_mode='Markdown')
                return

    text = update.message.text.strip() if update.message.text else ""

    if is_admin_user(user.id):
        if context.user_data.get('waiting_for_maint_msg'):
            db_execute("UPDATE settings SET value = ? WHERE key = 'maint_msg'", (text,), commit=True)
            context.user_data['waiting_for_maint_msg'] = False
            await update.message.reply_text(f"✅ Maintenance message updated.", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_ban_id') and text.isdigit():
            db_execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (int(text),), commit=True)
            context.user_data['waiting_for_ban_id'] = False
            await update.message.reply_text(f"✅ User ID `{text}` banned successfully.", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_unban_id') and text.isdigit():
            db_execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (int(text),), commit=True)
            context.user_data['waiting_for_unban_id'] = False
            await update.message.reply_text(f"✅ User ID `{text}` unbanned successfully.", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_redeem_gen'):
            parts = text.split()
            if len(parts) == 2 and parts[1].isdigit():
                db_execute("INSERT OR REPLACE INTO redeem_keys (key, credits, is_used) VALUES (?, ?, 0)", (parts[0], int(parts[1])), commit=True)
                context.user_data['waiting_for_redeem_gen'] = False
                await update.message.reply_text(f"🎉 Redeem Key `{parts[0]}` generated for `{parts[1]}` credits!", parse_mode='Markdown')
                return

        if context.user_data.get('waiting_for_force_channels'):
            db_execute("UPDATE settings SET value = ? WHERE key = 'force_channels'", ("" if text.lower() == 'none' else text.strip(),), commit=True)
            context.user_data['waiting_for_force_channels'] = False
            await update.message.reply_text("✅ Force channels updated.", parse_mode='Markdown')
            return

    maint = db_get_one("SELECT value FROM settings WHERE key='maintenance'")['value']
    if maint == 'on' and not is_admin_user(user.id):
        await update.message.reply_text("🚧 " + db_get_one("SELECT value FROM settings WHERE key='maint_msg'")['value'], parse_mode='Markdown')
        return

    clean_input_text = text
    for prefix in ["🔍 ", "📍 ", "🌐 ", "🆔 ", "🔤 ", "🔮 "]:
        clean_input_text = clean_input_text.replace(prefix, "")
    
    matched_api = db_get_one("SELECT * FROM dynamic_apis WHERE UPPER(api_name) = ? OR api_key = ?", (clean_input_text.upper(), text.lower()))
    if matched_api:
        api_k = matched_api['api_key']
        context.user_data['mode'] = f"custom_api_{api_k}"
        await update.message.reply_text(f"🔍 *{matched_api['api_name']} Mode Active*\nQuery enter karein:", parse_mode='Markdown')
        return

    if text == "💎 MY PREMIUM STATUS":
        user_info = db_get_one("SELECT credits, searches FROM users WHERE user_id = ?", (user.id,))
        credits = user_info['credits'] if user_info else 0
        searches = user_info['searches'] if user_info else 0
        await update.message.reply_text(f"👤 *Aapki Details:*\nRank: `{get_user_rank(searches)}`\nCredits: `{credits}`", parse_mode='Markdown')
        return
    elif text == "💰 MY BALANCE":
        await balance_command(update, context)
        return
    elif text == "💬 Owner | Support":
        await support_command(update, context)
        return
    elif text == "💰 Refer & Earn":
        await ref_command(update, context)
        return
    elif text == "🏆 Leaderboard":
        top_users = db_get_all("SELECT first_name, credits, searches FROM users ORDER BY searches DESC LIMIT 10")
        lb_text = "🏆 **LEADERBOARD**\n"
        for idx, u in enumerate(top_users, 1):
            lb_text += f"{idx}. {u['first_name']} — Lookups: `{u['searches']}`\n"
        await update.message.reply_text(lb_text, parse_mode='Markdown')
        return
    elif text == "💎 Buy Premium / Credits":
        await show_premium_plans(update, context)
        return
    elif text == "📊 Admin Panel" and is_admin_user(user.id):
        await show_full_admin_panel(update, context)
        return

    user_data = db_get_one("SELECT phone_number, is_banned FROM users WHERE user_id = ?", (user.id,))
    if not user_data or user_data['is_banned'] == 1:
        await update.message.reply_text("❌ Aapko block kar diya gaya hai.")
        return
    if not user_data.get('phone_number'):
        contact_button = [[KeyboardButton("📱 Share Contact", request_contact=True)]]
        await update.message.reply_text("⚠️ Kripya contact verify karein!", reply_markup=ReplyKeyboardMarkup(contact_button, resize_keyboard=True))
        return

    if not await check_user_credit(update, user): return

    mode = context.user_data.get('mode', None)
    cleaned = re.sub(r'\D', '', text)

    if mode and mode.startswith("custom_api_"):
        api_k = mode.replace("custom_api_", "")
        msg = await update.message.reply_text("💻 *PROCESSING QUERY...*", parse_mode='Markdown')
        data = await fetch_dynamic_api(api_k, text)
        await show_hacking_animation(msg, text, title_type="PHONE")
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, f"{api_k}:{text}", json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        log_activity(user.id, f"Custom API search: {api_k}")
        
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        if len(json_str) > 4000: json_str = json_str[:4000] + "\n... (Truncated)"
        try: await msg.edit_text(f"```json\n{json_str}\n```", parse_mode='Markdown')
        except: await msg.edit_text(f"```json\n{json_str}\n```", parse_mode=None)
        context.user_data['mode'] = None
        return

    if mode == 'phone' or (10 <= len(cleaned) <= 15):
        msg = await update.message.reply_text("💻 *SYSTEM BREACH IN PROGRESS*", parse_mode='Markdown')
        data = await fetch_dynamic_api('phone', cleaned)
        await show_hacking_animation(msg, cleaned, title_type="PHONE")
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, cleaned, json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        log_activity(user.id, f"Phone lookup performed on {cleaned}")
        records, err = parse_phone_records(data, cleaned)
        if err: await msg.edit_text(err)
        else: 
            context.user_data['last_phone_records'] = records
            context.user_data['last_phone_target'] = cleaned
            await send_paginated_phone_response(msg, records, cleaned, update, context, page=0, is_edit=True)
        context.user_data['mode'] = None
    else:
        await update.message.reply_text("❌ Kripya valid input enter karein.", parse_mode='Markdown')

async def show_full_admin_panel(update_or_query, context):
    total_users = db_get_one("SELECT COUNT(*) as count FROM users")['count']
    total_searches = db_get_one("SELECT COUNT(*) as count FROM searches")['count']
    maint = db_get_one("SELECT value FROM settings WHERE key='maintenance'")['value']
    upi_record = db_get_one("SELECT value FROM settings WHERE key='upi_id'")
    
    panel_text = f"\n📊 *ADVANCED ADMIN PANEL* ({OWNER_USERNAME})\n━━━━━━━━━━━━━━━━━━\n👥 Total Users: `{total_users}`\n🔍 Total Lookups: `{total_searches}`\n💳 UPI: `{upi_record['value'] if upi_record else 'Not Set'}`\n🚧 Maintenance: `{maint.upper()}`\n"
    keyboard = [
        [InlineKeyboardButton("🟢 View Users", callback_data="admin_users"), InlineKeyboardButton("💳 Set UPI ID", callback_data="admin_setupi_prompt")],
        [InlineKeyboardButton("📦 Manage Plans", callback_data="admin_plans"), InlineKeyboardButton("💎 Add Credits", callback_data="admin_addcredit_prompt")],
        [InlineKeyboardButton("📈 Live Analytics", callback_data="admin_live_analytics"), InlineKeyboardButton("🤖 Clone Bots", callback_data="admin_clones")],
        [InlineKeyboardButton("🌐 Dynamic APIs", callback_data="admin_dynamic_apis"), InlineKeyboardButton("➕ Add New API", callback_data="admin_add_api")],
        [InlineKeyboardButton("🗑️ Delete API", callback_data="admin_delete_api"), InlineKeyboardButton("✏️ Edit Button Name", callback_data="admin_edit_name")],
        [InlineKeyboardButton("🎨 Report Style", callback_data="admin_toggle_style"), InlineKeyboardButton("🔄 Toggle Clone Ref", callback_data="admin_toggle_clone_ref")],
        [InlineKeyboardButton("👥 Set Clone Refs", callback_data="admin_cloneref_prompt"), InlineKeyboardButton("🎁 Set Ref Reward", callback_data="admin_refreward_prompt")],
        [InlineKeyboardButton("💬 Set Maint Msg", callback_data="admin_setmaintmsg_prompt"), InlineKeyboardButton("🖼️ Set Banner", callback_data="admin_banner_prompt")],
        [InlineKeyboardButton("🛡️️ Add Sub-Admin", callback_data="admin_addsub_prompt"), InlineKeyboardButton("🛠️ Maintenance", callback_data="toggle_maintenance")],
        [InlineKeyboardButton("🔑 Gen Redeem Key", callback_data="admin_redeem_prompt"), InlineKeyboardButton("📜 View Logs", callback_data="admin_view_logs")],
        [InlineKeyboardButton("🔨 Ban User", callback_data="admin_ban_prompt"), InlineKeyboardButton("🔓 Unban User", callback_data="admin_unban_prompt")],
        [InlineKeyboardButton("📢 Force Channels", callback_data="admin_force_channels_prompt"), InlineKeyboardButton("❌ Close", callback_data="close_panel")]
    ]
    
    chat_id = update_or_query.message.chat_id if hasattr(update_or_query, 'message') and update_or_query.message else update_or_query.effective_chat.id
    if hasattr(update_or_query, 'callback_query') and update_or_query.callback_query:
        await update_or_query.callback_query.edit_message_text(panel_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update_or_query.message.reply_text(panel_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

# ============================================
# ADMIN CALLBACK HANDLER
# ============================================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data.startswith("phone_page_"):
        page_num = int(data.split("_")[-1])
        records = context.user_data.get('last_phone_records', [])
        phone = context.user_data.get('last_phone_target', 'Unknown')
        await send_paginated_phone_response(query.message, records, phone, update, context, page=page_num, is_edit=True)
        return

    if not is_admin_user(query.from_user.id):
        return

    if data == "admin_panel":
        await show_full_admin_panel(update, context)
        return
    elif data == "admin_setupi_prompt":
        context.user_data['waiting_for_upi'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="💳 Nayi UPI ID bhejein:", parse_mode='Markdown')
        return
    elif data == "admin_ban_prompt":
        context.user_data['waiting_for_ban_id'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="🔨 Ban karne ke liye User ID bhejein:", parse_mode='Markdown')
        return
    elif data == "admin_unban_prompt":
        context.user_data['waiting_for_unban_id'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="🔓 Unban karne ke liye User ID bhejein:", parse_mode='Markdown')
        return
    elif data == "admin_redeem_prompt":
        context.user_data['waiting_for_redeem_gen'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="🔑 Format: `KEY_NAME CREDITS` (jaise: `VIP50 50`)", parse_mode='Markdown')
        return
    elif data == "admin_force_channels_prompt":
        context.user_data['waiting_for_force_channels'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="📢 Force channels comma separated bhejein:", parse_mode='Markdown')
        return
    elif data == "admin_view_logs":
        logs = db_get_all("SELECT * FROM logs ORDER BY id DESC LIMIT 15")
        text = "📜 *SYSTEM LOGS*\n"
        for l in logs: text += f"• UID: `{l['user_id']}` | {l['action']} (`{l['timestamp']}`)\n"
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]]
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return
    elif data == "admin_users":
        users = db_get_all("SELECT user_id, first_name, credits FROM users LIMIT 15")
        text = "👥 *Users List*\n"
        for u in users: text += f"• {u['first_name']} (ID: `{u['user_id']}`) - `{u['credits']} Credits`\n"
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]]
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return
    elif data == "toggle_maintenance":
        current = db_get_one("SELECT value FROM settings WHERE key='maintenance'")['value']
        new_val = 'off' if current == 'on' else 'on'
        db_execute("UPDATE settings SET value = ? WHERE key = 'maintenance'", (new_val,), commit=True)
        await show_full_admin_panel(update, context)
        return
    elif data == "close_panel":
        try: await query.message.delete()
        except: pass
        return

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=background_periodic_worker, daemon=True).start()
    print("🚀 HARSH OSINT BOT STARTING (ALL RESTORED BUTTONS & ADVANCED ADMIN PANEL)...")
    
    application = Application.builder().token(USER_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("support", support_command))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("redeem", redeem_command))
    application.add_handler(CommandHandler("daily", daily_command))
    application.add_handler(CommandHandler("export", export_command))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.Document.ALL, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == '__main__':
    main()
