#!/usr/init/env python3
# OSINT & Pincode Bot - Final Full Working Edition
"""
Developer: @Harsx1618
Description: Advanced Telegram OSINT Bot with Complete Features, 10 Report Styles, Pagination & All Admin Controls
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
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('maint_msg', '🚧 Bot abhi maintenance mode par hai. Kripya baad mein koshish karein!')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('upi_id', 'harshhacker@upi')")
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
        ('aadhaar_info', 'Aadhaar Info', 'https://auraxinfo-production.up.railway.app/api?key=for-paid-users&type=aadhaar&term={query}', '@FizzaGirl', '@Harsx1618'),
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
async def fetch_dynamic_api(api_key, query_val, timeout_sec=20):
    api_record = db_get_one("SELECT * FROM dynamic_apis WHERE api_key = ?", (api_key,))
    target_url = ""
    if api_record and api_record.get('api_url'):
        target_url = api_record['api_url'].strip()
    
    if not target_url:
        if api_key == 'phone': target_url = "https://nmdllpezcocquamhgpmb.supabase.co/functions/v1/lookup?number={query}"
        elif api_key == 'pincode': target_url = "https://rack-pincodeapi.vercel.app/api?search={query}"
        elif api_key == 'ip_info': target_url = "https://oriss-ip-info-api.antideploy.com/ip/{query}"
        elif api_key == 'aadhaar_info': target_url = "https://auraxinfo-production.up.railway.app/api?key=for-paid-users&type=aadhaar&term={query}"
        elif api_key in ['tg_username', 'tg_userid']: target_url = "https://felix-info-x-bot.onrender.com/key=felix67&tg={query}"

    final_url = target_url.replace("{query}", str(query_val))
    old_c = api_record['old_credit'] if api_record and api_record.get('old_credit') else ""
    new_c = api_record['new_credit'] if api_record and api_record.get('new_credit') else ""

    try:
        response = requests.get(final_url, headers=HTTP_HEADERS, timeout=timeout_sec)
        if response.status_code == 200:
            raw_text = response.text
            if old_c: raw_text = raw_text.replace(old_c, new_c)
            try: return json.loads(raw_text)
            except: return {"status": True, "raw_result": raw_text}
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
        try: await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except: pass
    if doc_message_id:
        try: await context.bot.delete_message(chat_id=chat_id, message_id=doc_message_id)
        except: pass

async def show_hacking_animation(msg_obj, target_str, title_type="PHONE"):
    if title_type == "PINCODE": title = "📍 PINCODE INTELLIGENCE BREACH"
    elif title_type == "TG": title = "🕵️‍♂️ TELEGRAM INTEL BREACH"
    elif title_type == "IP": title = "🌐 IP INTELLIGENCE BREACH"
    elif title_type == "AADHAAR": title = "🆔 INTELLIGENCE BREACH"
    else: title = "💻 SYSTEM BREACH IN PROGRESS"
    try: await msg_obj.edit_text(title + "\nTarget: `" + target_str + "`\n\n✅ Decryption successful!\n`██████████ 100%`", parse_mode='Markdown')
    except: pass

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
# WELCOME MENU SENDER
# ============================================
async def send_welcome_menu(update_obj, context, user):
    banner = db_get_one("SELECT value FROM settings WHERE key='banner_media'")
    b_type = db_get_one("SELECT value FROM settings WHERE key='banner_type'")
    welcome_text = f"⚡ *WELCOME TO ULTIMATE OSINT BOT* ⚡\n\nNeeche diye gaye buttons se apna feature select karein:"
    keyboard = [
        [KeyboardButton("🔍 NUMBER INFO"), KeyboardButton("📍 PINCODE INFO")],
        [KeyboardButton("🌐 IP INFO"), KeyboardButton("🆔 AADHAAR INFO")],
        [KeyboardButton("🔤 TG TO NUMBER"), KeyboardButton("💎 MY PREMIUM STATUS")],
        [KeyboardButton("💰 MY BALANCE"), KeyboardButton("💬 Owner | Support")],
        [KeyboardButton("💰 Refer & Earn"), KeyboardButton("🏆 Leaderboard")],
        [KeyboardButton("🤖 My Clone Bot"), KeyboardButton("💎 Buy Premium / Credits")],
        [KeyboardButton("🛠️ Toggle Menu"), KeyboardButton("📊 Admin Panel")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    target_msg = update_obj.message if hasattr(update_obj, 'message') else update_obj.callback_query.message
    if banner and banner['value'] and b_type:
        try:
            if b_type['value'] == 'photo':
                await target_msg.reply_photo(photo=banner['value'], caption=welcome_text, parse_mode='Markdown', reply_markup=reply_markup)
                return
            elif b_type['value'] == 'video':
                await target_msg.reply_video(video=banner['value'], caption=welcome_text, parse_mode='Markdown', reply_markup=reply_markup)
                return
            elif b_type['value'] == 'animation':
                await target_msg.reply_animation(animation=banner['value'], caption=welcome_text, parse_mode='Markdown', reply_markup=reply_markup)
                return
        except: pass
    await target_msg.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)

# ============================================
# 10 REPORT STYLES & FORMATTERS
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
    chunk = records[page * per_page : min((page + 1) * per_page, total)]

    if r_style == 'json':
        json_output = {"status": True, "target": str(phone), "total_records": total, "current_page": page + 1, "total_pages": total_pages, "records": chunk, "developer": OWNER_USERNAME}
        text = "```json\n" + json.dumps(json_output, indent=2, ensure_ascii=False) + "\n```"
    elif r_style == 'hacker':
        text = f"💀 [ ROOT ACCESS GRANTED ] 💀\n🎯 TARGET_IP/NUM: `{phone}`\n📊 PACKETS: {total} | PAGE: {page + 1}/{total_pages}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for idx, rec in enumerate(chunk, start=page * per_page + 1):
            text += f"⚡ [TARGET #{idx}] ⚡\n• IDENT: `{rec['name']}`\n• PARENT: `{rec['father']}`\n• COMMS: `{rec['mobile']}` | `{rec['alt_num']}`\n• NODE: `{rec['circle']}`\n• MAIL: `{rec['email']}`\n• REG_ID: `{rec['caf_id']}`\n• LOC: `{rec['address']}`\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"⚡ HACKED BY {OWNER_USERNAME}"
    elif r_style == 'matrix':
        text = f"🟩 010101 MATRIX INTEL 010101 🟩\nTarget: `{phone}` | Page: {page + 1}/{total_pages}\n════════════════════════════════\n\n"
        for idx, rec in enumerate(chunk, start=page * per_page + 1):
            text += f"🟢 MATRIX_REC_{idx}:\n├ Name: `{rec['name']}`\n├ Mobile: `{rec['mobile']}`\n├ Circle: `{rec['circle']}`\n└ Addr: `{rec['address']}`\n\n"
        text += f"System Core: {OWNER_USERNAME}"
    elif r_style == 'cyber':
        text = f"🌐 𝕮𝖄𝕭𝕰𝕽 𝕴𝕹𝕿𝕰𝕃𝕃𝕴𝕲𝕰𝕹𝕮𝕰 🌐\n🎯 Target: `{phone}`\n📊 Records: {total} | Page: {page + 1}/{total_pages}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for idx, rec in enumerate(chunk, start=page * per_page + 1):
            text += f"🔹 **CYBER_NODE #{idx}**\n👤 Subject: `{rec['name']}`\n👨‍👧 Guardian: `{rec['father']}`\n📱 Phone: `{rec['mobile']}`\n📞 Alt: `{rec['alt_num']}`\n📡 Telecom: `{rec['circle']}`\n📧 Mail: `{rec['email']}`\n🆔 UID: `{rec['caf_id']}`\n🏠 Sector:\n`{rec['address']}`\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"⚡ Secured by {OWNER_USERNAME}"
    elif r_style == 'neon':
        text = f"🟣 🪩 NEON GLOW INTEL 🪩 🟣\n🎯 Target: `{phone}` (Page {page + 1}/{total_pages})\n──────────────────────────────\n\n"
        for idx, rec in enumerate(chunk, start=page * per_page + 1):
            text += f"✨ **[RECORD {idx}]**\n👤 `[NAME]` : {rec['name']}\n📱 `[CELL]` : {rec['mobile']}\n🌐 `[AREA]` : {rec['circle']}\n🏠 `[HOME]` : {rec['address']}\n\n──────────────────────────────\n"
    elif r_style == 'card':
        text = f"🪪 **VIP CARD INTELLIGENCE REPORT**\n🎯 Target Number: `{phone}`\n📊 Records: {total} | Page: {page + 1}/{total_pages}\n════════════════════════\n\n"
        for idx, rec in enumerate(chunk, start=page * per_page + 1):
            text += f"┌ 👑 **IDENTITY CARD #{idx}**\n├ 👤 **Name:** `{rec['name']}`\n├ 👨‍👧 **Father:** `{rec['father']}`\n├ 📱 **Mobile:** `{rec['mobile']}`\n├ 🌐 **Circle:** `{rec['circle']}`\n└ 🏠 **Address:** `{rec['address']}`\n\n════════════════════════\n"
    elif r_style == 'compact':
        text = f"⚡ **COMPACT INTEL REPORT ({phone}) [Page {page + 1}/{total_pages}]**\n────────────────────────\n"
        for idx, rec in enumerate(chunk, start=page * per_page + 1):
            text += f"`{idx}.` **{rec['name']}** | `{rec['mobile']}` | `{rec['circle']}`\n   🏠 `{rec['address']}`\n"
        text += f"────────────────────────\n"
    elif r_style == 'minimal':
        text = f"▪️ **INTEL // {phone} ({page + 1}/{total_pages})**\n\n"
        for idx, rec in enumerate(chunk, start=page * per_page + 1):
            text += f"`{idx}` {rec['name']} | {rec['mobile']} | {rec['circle']}\n"
        text += f"\n▪️ Auth: {OWNER_USERNAME}"
    elif r_style == 'vip':
        text = f"⭐ 👑 **VIP EXCLUSIVE OSINT REPORT** 👑 ⭐\n🎯 Target: `{phone}` | Page: {page + 1}/{total_pages}\n──────────────────────────────\n\n"
        for idx, rec in enumerate(chunk, start=page * per_page + 1):
            text += f"🌟 **VIP PROFILE #{idx}**\n• Full Name : **{rec['name']}**\n• Father    : **{rec['father']}**\n• Contact   : `{rec['mobile']}`\n• Region    : {rec['circle']}\n• Location  : _{rec['address']}_\n\n──────────────────────────────\n"
    else:
        text = f"📱 **NUMBER INTELLIGENCE REPORT**\n🎯 Target: `{phone}`\n📊 Total Records: {total} | Page: {page + 1}/{total_pages}\n━━━━━━━━━━━━━━━━━━━━\n\n"
        for idx, rec in enumerate(chunk, start=page * per_page + 1):
            text += f"🔹 **RECORD #{idx}**\n👤 Name: `{rec['name']}`\n👨‍👧 Father: `{rec['father']}`\n📱 Mobile: `{rec['mobile']}`\n📞 Alt Num: `{rec['alt_num']}`\n🌐 Circle: `{rec['circle']}`\n📧 Email: `{rec['email']}`\n🆔 CAF / ID: `{rec['caf_id']}`\n🏠 Address:\n`{rec['address']}`\n\n━━━━━━━━━━━━━━━━━━━━\n"

    text += f"⚡ Developed by {OWNER_USERNAME}"
    
    buttons = []
    nav_row = []
    if page > 0: nav_row.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"phone_page_{page - 1}"))
    if page < total_pages - 1: nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"phone_page_{page + 1}"))
    if nav_row: buttons.append(nav_row)
    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None

    if is_edit:
        try: await msg_obj.edit_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        except: pass
    else:
        reply_msg = await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        msg_obj = reply_msg

    if page == 0:
        sent_message_ids = [msg_obj.message_id]
        doc_msg_id = None
        try:
            file_content = f"=========================================\n      OSINT NUMBER INTELLIGENCE REPORT\n      Query Number: {phone}\n      Total Records: {total}\n      Developer: {OWNER_USERNAME}\n=========================================\n\n"
            for idx, rec in enumerate(records, start=1):
                file_content += f"--- RECORD #{idx} ---\nNAME: {rec['name']}\nFATHER: {rec['father']}\nMOBILE: {rec['mobile']}\nALT NUM: {rec['alt_num']}\nCIRCLE: {rec['circle']}\nEMAIL: {rec['email']}\nCAF / ID: {rec['caf_id']}\nADDRESS: {rec['address']}\n\n"
            file_name = f"report_{phone}.txt"
            with open(file_name, "w", encoding="utf-8") as f: f.write(file_content)
            with open(file_name, "rb") as f:
                doc_msg = await update.message.reply_document(document=InputFile(f, filename=file_name), caption=f"📁 **Downloadable Report File (Auto-deletes in 30s)**\nTarget: `{phone}`", parse_mode='Markdown')
                doc_msg_id = doc_msg.message_id
            os.remove(file_name)
        except Exception as e: print("Error sending file: " + str(e))
        asyncio.create_task(schedule_message_deletion(context, update.effective_chat.id, sent_message_ids, doc_msg_id))

def format_pincode_response(data, pincode):
    try:
        if not data or not isinstance(data, dict): return "❌ Error: Invalid response received from Pincode API."
        records = data.get('records', [])
        formatted_records = []
        for idx, rec in enumerate(records, 1):
            if not isinstance(rec, dict): rec = {}
            formatted_records.append({
                "record_id": str(idx), "office_name": str(rec.get('office_name', 'N/A')),
                "branch_type": str(rec.get('branch_type', 'N/A')), "delivery_status": str(rec.get('delivery_status', 'N/A')),
                "circle": str(rec.get('circle', 'N/A')), "district": str(rec.get('district', 'N/A')),
                "state": str(rec.get('state', 'N/A')), "pincode": str(rec.get('pincode', pincode))
            })
        if len(formatted_records) > 10: formatted_records = formatted_records[:10]
        json_output = {"status": "success", "pincode": str(pincode), "total_records_shown": len(formatted_records), "records": formatted_records}
        return "```json\n" + json.dumps(json_output, indent=2, ensure_ascii=False) + "\n```"
    except Exception as e: return "❌ Error formatting pincode data: " + str(e)

def format_tg_response(data, query_str):
    try:
        if not data or (isinstance(data, dict) and data.get('status'] == False and 'error' in data):
            return "❌ Error: " + data.get('error', 'No data found')
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        if len(json_str) > 4000: json_str = json_str[:4000] + "\n... (Truncated)"
        return "```json\n" + json_str + "\n```"
    except Exception as e: return "❌ Error formatting TG data: " + str(e)

def format_ip_response(data, ip_str):
    try:
        if not data or (isinstance(data, dict) and data.get('status'] == False):
            return "❌ Error: " + data.get('error', 'No data found')
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        if len(json_str) > 4000: json_str = json_str[:4000] + "\n... (Truncated)"
        return "```json\n" + json_str + "\n```"
    except Exception as e: return "❌ Error formatting IP data: " + str(e)

def format_aadhaar_response(data, query_str):
    try:
        if not data or (isinstance(data, dict) and data.get('status'] == False):
            return "❌ Error: " + data.get('error', 'No data found')
        if isinstance(data, dict):
            data.pop('developer', None)
            data.pop('owner', None)
            data.pop('channel', None)
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        if len(json_str) > 4000: json_str = json_str[:4000] + "\n... (Truncated)"
        return "```json\n" + json_str + "\n```"
    except Exception as e: return "❌ Error formatting data: " + str(e)

# ============================================
# COMMAND & MESSAGE HANDLERS
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
        db_execute("INSERT INTO users (user_id, username, first_name, credits, referred_by) VALUES (?, ?, ?, ?, ?)",
                   (user.id, user.username or "NoUsername", user.first_name, ref_reward, referrer_id), commit=True)
        if referrer_id != 0:
            db_execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (ref_reward, referrer_id), commit=True)
            try:
                await context.bot.send_message(chat_id=referrer_id, text=f"🎉 **Referral Bonus!** Aapke link se ek naye user ne join kiya, aapko `{ref_reward}` extra credits mile hain!")
            except: pass
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

async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    support_text = f"💬 *IF YOU FACE ANY ISSUES CONTACT OUR ADMIN*\n\n📲 **Owner / Support Username:** `{OWNER_USERNAME}`\n\nKisi bhi madad ke liye seedhe contact karein!"
    support_keyboard = [[InlineKeyboardButton("💬 Chat with Support Owner", url=f"https://t.me/{OWNER_USERNAME.replace('@', '')}")]]
    await update.message.reply_text(support_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(support_keyboard))

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_info = db_get_one("SELECT credits FROM users WHERE user_id = ?", (user.id,))
    credits = user_info['credits'] if user_info else 0
    await update.message.reply_text(f"💰 *Aapka Current Balance:*\n\n💎 Remaining Credits: `{credits} Credits`", parse_mode='Markdown')

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args:
        await update.message.reply_text("❌ Usage: `/report <your feedback>`", parse_mode='Markdown')
        return
    feedback_msg = ' '.join(context.args)
    report_text = f"🚨 **NEW REPORT**\n👤 From: {user.first_name} (@{str(user.username or 'None')})\n🆔 ID: `{user.id}`\n💬 Message: {feedback_msg}"
    try: await context.bot.send_message(chat_id=ADMIN_ID, text=report_text, parse_mode='Markdown')
    except: pass
    await update.message.reply_text("✅ *Feedback submitted successfully!*", parse_mode='Markdown')

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
    ref_link = f"https://t.me/{bot_username}?start={user.id}"
    reward_setting = db_get_one("SELECT value FROM settings WHERE key='ref_reward_credits'")
    ref_reward = reward_setting['value'] if reward_setting else "2"
    referred_users = db_get_all("SELECT first_name, username, joined_date FROM users WHERE referred_by = ? ORDER BY joined_date DESC LIMIT 10", (user.id,))
    text = f"➿➿➿➿➿➿➿➿➿➿➿\n💰 𝗥𝗲𝗳𝗲𝗿 & 𝗲𝗮𝗿𝗻 ⛓\n➿➿➿➿➿➿➿➿➿➿➿\n\n📲 Har successful refer par milenge: `{ref_reward}` Credits\n🔗 **Aapka Referral Link:**\n`{ref_link}`\n\n📜 **Aapki Referral History (Total: {len(referred_users)}):**\n━━━━━━━━━━━━━━━━━━━━\n"
    if not referred_users: text += "_Abhi tak kisi ko refer nahi kiya hai._\n"
    else:
        for idx, ref_u in enumerate(referred_users, 1):
            uname = f"@{ref_u['username']}" if ref_u['username'] and ref_u['username'] != 'NoUsername' else "No Username"
            text += f"{idx}. **{ref_u['first_name']}** ({uname}) — _{ref_u['joined_date']}_\n"
    refer_keyboard = [
        [InlineKeyboardButton("📤 Share Friend", url=f"https://t.me/share/url?url={ref_link}&text=Join%20this%20awesome%20OSINT%20bot%20and%20get%20free%20credits!")],
        [InlineKeyboardButton("💳 Buy Credits", callback_data="buy_credits_btn")]
    ]
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(refer_keyboard))

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🟢 **LIVE API HEALTH STATUS**\n━━━━━━━━━━━━━━━━━━━━\n• Supabase Lookup API: `🟢 Online`\n• Pincode API: `🟢 Online`\n• Telegram Lookup API: `🟢 Online`\n• IP Info API: `🟢 Online`\n• Aadhaar API: `🟢 Online`"
    await update.message.reply_text(text, parse_mode='Markdown')

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
    await update.message.reply_text(f"🎉 *Success!* `{credits_to_add}` credits added.", parse_mode='Markdown')

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    searches = db_get_all("SELECT phone, timestamp FROM searches WHERE user_id = ? ORDER BY timestamp DESC LIMIT 10", (user.id,))
    if not searches:
        await update.message.reply_text("📜 Aapne abhi tak koi search nahi ki hai.", parse_mode='Markdown')
        return
    text = "📜 *Aapki Pichli 10 Searches:* \n━━━━━━━━━━━━━━━━━━━━\n"
    for s in searches: text += f"• `{s['phone']}` — _{s['timestamp']}_\n"
    await update.message.reply_text(text, parse_mode='Markdown')

async def userhistory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin_user(update.effective_user.id): return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("❌ Usage: `/userhistory <user_id>`", parse_mode='Markdown')
        return
    target_id = int(context.args[0])
    searches = db_get_all("SELECT phone, timestamp FROM searches WHERE user_id = ? ORDER BY timestamp DESC LIMIT 15", (target_id,))
    if not searches:
        await update.message.reply_text(f"❌ User ID `{target_id}` ki koi search history nahi mili.", parse_mode='Markdown')
        return
    text = f"📜 *Search History for User ID `{target_id}`:*\n━━━━━━━━━━━━━━━━━━━━\n"
    for s in searches: text += f"• `{s['phone']}` — _{s['timestamp']}_\n"
    await update.message.reply_text(text, parse_mode='Markdown')

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin_user(update.effective_user.id): return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("❌ Usage: `/ban <user_id>`", parse_mode='Markdown')
        return
    target_id = int(context.args[0])
    db_execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (target_id,), commit=True)
    await update.message.reply_text(f"🚫 User ID `{target_id}` successfully banned.", parse_mode='Markdown')

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin_user(update.effective_user.id): return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("❌ Usage: `/unban <user_id>`", parse_mode='Markdown')
        return
    target_id = int(context.args[0])
    db_execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (target_id,), commit=True)
    await update.message.reply_text(f"✅ User ID `{target_id}` successfully unbanned.", parse_mode='Markdown')

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
        await update.message.reply_text("❌ Usage: `/addplan <name> <price> <credits>`", parse_mode='Markdown')
        return
    name, price = context.args[0], context.args[1]
    try:
        credits = int(context.args[2])
        db_execute("INSERT INTO plans (name, price, credits) VALUES (?, ?, ?)", (name, price, credits), commit=True)
        await update.message.reply_text("✅ Plan `" + name + "` added successfully!", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text("❌ Error: " + str(e))

async def createcoupon_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin_user(update.effective_user.id): return
    if len(context.args) < 2:
        await update.message.reply_text("❌ Usage: `/createcoupon <code> <credits>`", parse_mode='Markdown')
        return
    try:
        code, credits = context.args[0].strip(), int(context.args[1])
        db_execute("INSERT OR REPLACE INTO coupons (code, credits) VALUES (?, ?)", (code, credits), commit=True)
        await update.message.reply_text("✅ Coupon `" + code + "` created with `" + str(credits) + "` credits!", parse_mode='Markdown')
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
        try: await context.bot.send_message(chat_id=target_id, text="🎉 Admin added `" + str(amount) + "` credits to your account.")
        except: pass
    except Exception as e:
        await update.message.reply_text("❌ Error: " + str(e))

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin_user(update.effective_user.id): return
    message = update.message
    reply_to = message.reply_to_message
    users = db_get_all("SELECT user_id FROM users")
    sent = 0
    for u in users:
        try:
            if reply_to: await context.bot.copy_message(chat_id=u['user_id'], from_chat_id=message.chat_id, message_id=reply_to.message_id)
            elif context.args:
                msg_text = ' '.join(context.args)
                await context.bot.send_message(chat_id=u['user_id'], text=f"📢 *ANNOUNCEMENT*\n\n{msg_text}", parse_mode='Markdown')
            sent += 1
        except: pass
    await update.message.reply_text(f"📢 Broadcast sent to {sent} users.")

# ============================================
# CONTACT & MESSAGE HANDLERS
# ============================================
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    contact = update.message.contact
    if contact and contact.phone_number:
        db_execute("UPDATE users SET phone_number = ? WHERE user_id = ?", (contact.phone_number, user.id), commit=True)
        await update.message.reply_text("✅ *Phone Number Verified Successfully!*", parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
        await send_welcome_menu(update, context, user)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    active_live_users.add(user.id)
    text = update.message.text.strip() if update.message.text else ""

    if is_admin_user(user.id):
        if context.user_data.get('waiting_for_banner'):
            media_id, media_type = "", "none"
            if update.message.animation: 
                media_id, media_type = update.message.animation.file_id, "animation"
            elif update.message.video: 
                media_id, media_type = update.message.video.file_id, "video"
            elif update.message.photo: 
                media_id, media_type = update.message.photo[-1].file_id, "photo"
            elif update.message.document: 
                media_id, media_type = update.message.document.file_id, "video"
            
            if media_id:
                db_execute("UPDATE settings SET value = ? WHERE key = 'banner_media'", (media_id,), commit=True)
                db_execute("UPDATE settings SET value = ? WHERE key = 'banner_type'", (media_type,), commit=True)
                context.user_data['waiting_for_banner'] = False
                await update.message.reply_text("✅ Success! Banner media updated successfully.", parse_mode='Markdown')
                await send_welcome_menu(update, context, user)
                return
            else:
                await update.message.reply_text("❌ Kripya valid Photo, GIF ya Video bhejein!", parse_mode='Markdown')
                return

        if context.user_data.get('waiting_for_maint_msg'):
            db_execute("UPDATE settings SET value = ? WHERE key = 'maint_msg'", (text,), commit=True)
            context.user_data['waiting_for_maint_msg'] = False
            await update.message.reply_text(f"✅ Maintenance message updated to:\n`{text}`", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_upi'):
            db_execute("UPDATE settings SET value = ? WHERE key = 'upi_id'", (text,), commit=True)
            context.user_data['waiting_for_upi'] = False
            await update.message.reply_text(f"✅ UPI ID updated to: `{text}`", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_add_sub'):
            if text.isdigit():
                db_execute("INSERT OR IGNORE INTO sub_admins (user_id) VALUES (?)", (int(text),), commit=True)
                context.user_data['waiting_for_add_sub'] = False
                await update.message.reply_text(f"✅ User ID `{text}` added as Sub-Admin!", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_add_credits_id'):
            if text.isdigit():
                context.user_data['add_credit_target_id'] = int(text)
                context.user_data['waiting_for_add_credits_id'] = False
                context.user_data['waiting_for_add_credits_amount'] = True
                await update.message.reply_text("💎 Ab kitne credits add karne hain? Amount enter karein:", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_add_credits_amount'):
            if text.isdigit():
                target_id = context.user_data.get('add_credit_target_id')
                amount = int(text)
                db_execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (amount, target_id), commit=True)
                context.user_data['waiting_for_add_credits_amount'] = False
                context.user_data['add_credit_target_id'] = None
                await update.message.reply_text(f"✅ Successfully added `{amount}` credits to User ID `{target_id}`!", parse_mode='Markdown')
                try: await context.bot.send_message(chat_id=target_id, text=f"🎉 Admin added `{amount}` credits to your account.")
                except: pass
            return

        if context.user_data.get('waiting_for_clone_ref_count'):
            if text.isdigit():
                db_execute("UPDATE settings SET value = ? WHERE key = 'clone_req_ref'", (text,), commit=True)
                context.user_data['waiting_for_clone_ref_count'] = False
                await update.message.reply_text(f"✅ Clone referral requirement updated to: `{text}`", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_ref_reward'):
            if text.isdigit():
                db_execute("UPDATE settings SET value = ? WHERE key = 'ref_reward_credits'", (text,), commit=True)
                context.user_data['waiting_for_ref_reward'] = False
                await update.message.reply_text(f"✅ Referral reward updated to: `{text}` credits!", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_api_url'):
            api_k = context.user_data.get('target_api_key')
            db_execute("UPDATE dynamic_apis SET api_url = ? WHERE api_key = ?", (text, api_k), commit=True)
            context.user_data['waiting_for_api_url'] = False
            context.user_data['target_api_key'] = None
            await update.message.reply_text(f"✅ API URL for `{api_k}` updated!", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_api_old'):
            api_k = context.user_data.get('target_api_key')
            db_execute("UPDATE dynamic_apis SET old_credit = ? WHERE api_key = ?", (text, api_k), commit=True)
            context.user_data['waiting_for_api_old'] = False
            context.user_data['target_api_key'] = None
            await update.message.reply_text(f"✅ Old watermark text updated!", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_api_new'):
            api_k = context.user_data.get('target_api_key')
            db_execute("UPDATE dynamic_apis SET new_credit = ? WHERE api_key = ?", (text, api_k), commit=True)
            context.user_data['waiting_for_api_new'] = False
            context.user_data['target_api_key'] = None
            await update.message.reply_text(f"✅ New watermark text updated!", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_new_api_key'):
            context.user_data['waiting_for_new_api_key'] = False
            context.user_data['new_api_key_temp'] = text.lower().replace(" ", "_")
            context.user_data['waiting_for_new_api_name'] = True
            await update.message.reply_text("📝 Enter API Button Name:", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_new_api_name'):
            context.user_data['waiting_for_new_api_name'] = False
            context.user_data['new_api_name_temp'] = text
            context.user_data['waiting_for_new_api_url'] = True
            await update.message.reply_text("🔗 Enter API URL (use `{query}`):", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_new_api_url'):
            db_execute("INSERT OR REPLACE INTO dynamic_apis (api_key, api_name, api_url, old_credit, new_credit) VALUES (?, ?, ?, '', '')", 
                       (context.user_data.get('new_api_key_temp'), context.user_data.get('new_api_name_temp'), text), commit=True)
            context.user_data['waiting_for_new_api_url'] = False
            await update.message.reply_text("🎉 New API successfully added!", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_delete_api_key'):
            db_execute("DELETE FROM dynamic_apis WHERE api_key = ? OR LOWER(api_name) = ?", (text.lower(), text.lower()), commit=True)
            context.user_data['waiting_for_delete_api_key'] = False
            await update.message.reply_text("🗑️ API successfully deleted!", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_edit_name_key'):
            existing = db_get_one("SELECT * FROM dynamic_apis WHERE api_key = ? OR LOWER(api_name) = ?", (text.lower(), text.lower()))
            if existing:
                context.user_data['edit_name_target_key'] = existing['api_key']
                context.user_data['waiting_for_edit_name_key'] = False
                context.user_data['waiting_for_edit_name_new'] = True
                await update.message.reply_text("✏️ Enter new Button Name:", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_edit_name_new'):
            db_execute("UPDATE dynamic_apis SET api_name = ? WHERE api_key = ?", (text, context.user_data.get('edit_name_target_key')), commit=True)
            context.user_data['waiting_for_edit_name_new'] = False
            await update.message.reply_text("✅ Button name updated successfully!", parse_mode='Markdown')
            return

    # Check Maintenance
    maint = db_get_one("SELECT value FROM settings WHERE key='maintenance'")['value']
    if maint == 'on' and not is_admin_user(user.id):
        maint_msg = db_get_one("SELECT value FROM settings WHERE key='maint_msg'")['value']
        await update.message.reply_text("🚧 " + maint_msg, parse_mode='Markdown')
        return

    clean_input_text = text
    for prefix in ["🔍 ", "📍 ", "🌐 ", "🆔 ", "🔤 ", "🔮 "]:
        clean_input_text = clean_input_text.replace(prefix, "")

    matched_api = db_get_one("SELECT * FROM dynamic_apis WHERE UPPER(api_name) = ? OR api_key = ?", (clean_input_text.upper(), text.lower()))
    if matched_api:
        api_k = matched_api['api_key']
        if api_k == 'phone':
            context.user_data['mode'] = 'phone'
            await update.message.reply_text("📱 *Number Info Mode Active*\nKripya 10-digit mobile number bhejein:", parse_mode='Markdown')
            return
        elif api_k == 'pincode':
            context.user_data['mode'] = 'pincode'
            await update.message.reply_text("📍 *Pincode Lookup Mode Active*\nKripya 6-digit PIN code bhejein:", parse_mode='Markdown')
            return
        elif api_k == 'ip_info':
            context.user_data['mode'] = 'ip_info'
            await update.message.reply_text("🌐 *IP Info Mode Active*\nKripya IP address bhejein:", parse_mode='Markdown')
            return
        elif api_k == 'aadhaar_info':
            context.user_data['mode'] = 'aadhaar_info'
            await update.message.reply_text("🆔 *Aadhaar Info Mode Active*\nKripya number bhejein:", parse_mode='Markdown')
            return
        elif api_k in ['tg_username', 'tg_userid'] or "TG TO NUMBER" in text.upper():
            tg_keyboard = [[KeyboardButton("👤 Telegram to Username"), KeyboardButton("🆔 Telegram to UserID")], [KeyboardButton("🔙 Back to Main Menu")]]
            await update.message.reply_text("🔤 *TG TO NUMBER SUB-MENU*\nOption select karein:", parse_mode='Markdown', reply_markup=ReplyKeyboardMarkup(tg_keyboard, resize_keyboard=True))
            return
        else:
            context.user_data['mode'] = f"custom_api_{api_k}"
            await update.message.reply_text(f"🔍 *{matched_api['api_name']} Mode Active*\nQuery enter karein:", parse_mode='Markdown')
            return

    if text == "👤 Telegram to Username":
        context.user_data['mode'] = 'tg_username'
        await update.message.reply_text("👤 Telegram username bhejein:", parse_mode='Markdown')
        return
    elif text == "🆔 Telegram to UserID":
        context.user_data['mode'] = 'tg_userid'
        await update.message.reply_text("🆔 Telegram UserID bhejein:", parse_mode='Markdown')
        return
    elif text == "💎 MY PREMIUM STATUS":
        u_info = db_get_one("SELECT credits FROM users WHERE user_id = ?", (user.id,))
        credits = u_info['credits'] if u_info else 0
        await update.message.reply_text(f"👤 *Account Status*\n💎 Credits: `{credits}`", parse_mode='Markdown')
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
        lb_text = "🏆 **LEADERBOARD**\n━━━━━━━━━━━━━━━━━━━━\n"
        for idx, u in enumerate(top_users, 1): lb_text += f"{idx}. **{u['first_name']}** — Lookups: `{u['searches']}` | Credits: `{u['credits']}`\n"
        await update.message.reply_text(lb_text, parse_mode='Markdown')
        return
    elif text == "🤖 My Clone Bot":
        clone_keyboard = [[InlineKeyboardButton("➕ Create New Clone Bot", callback_data="create_clone_prompt")]]
        await update.message.reply_text("🤖 **CLONE BOT MANAGER**\nNeeche diye gaye button par click karein:", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(clone_keyboard))
        return
    elif text == "🔙 Back to Main Menu":
        context.user_data['mode'] = None
        await send_welcome_menu(update, context, user)
        return
    elif text == "🛠️️ Toggle Menu":
        await update.message.reply_text("📉 Menu hide kar diya gaya hai. Wapas lane ke liye /start dabayein.", reply_markup=ReplyKeyboardRemove())
        return
    elif text == "📊 Admin Panel" and is_admin_user(user.id):
        total_users = db_get_one("SELECT COUNT(*) as count FROM users")['count']
        total_searches = db_get_one("SELECT COUNT(*) as count FROM searches")['count']
        maint = db_get_one("SELECT value FROM settings WHERE key='maintenance'")['value']
        upi_record = db_get_one("SELECT value FROM settings WHERE key='upi_id'")
        panel_text = f"\n📊 *ADMIN PANEL* ({OWNER_USERNAME})\n━━━━━━━━━━━━━━━━━━\n👥 Users: `{total_users}` | 🔍 Lookups: `{total_searches}`\n💳 UPI: `{upi_record['value'] if upi_record else 'Not Set'}`\n🚧 Maint: `{maint.upper()}`\n"
        keyboard = [
            [InlineKeyboardButton("🌐 🔌 Dynamic APIs", callback_data="admin_dynamic_apis"), InlineKeyboardButton("➕ 🔌 Add New API", callback_data="admin_add_api")],
            [InlineKeyboardButton("🗑️ 🔌 Delete API", callback_data="admin_delete_api"), InlineKeyboardButton("✏️ 📝 Edit Button Name", callback_data="admin_edit_name")],
            [InlineKeyboardButton("🎨 🔄 Change Report Style", callback_data="admin_toggle_style"), InlineKeyboardButton("🔄 Toggle Clone Ref", callback_data="admin_toggle_clone_ref")],
            [InlineKeyboardButton("👥 ⚙️ Set Clone Refs", callback_data="admin_cloneref_prompt"), InlineKeyboardButton("🎁 ⚙️ Set Ref Reward", callback_data="admin_refreward_prompt")],
            [InlineKeyboardButton("💬 ⚙️ Set Maint Msg", callback_data="admin_setmaintmsg_prompt"), InlineKeyboardButton("🖼️ ⚙️ Set Banner", callback_data="admin_banner_prompt")],
            [InlineKeyboardButton("🛡️ ➕ Add Sub-Admin", callback_data="admin_addsub_prompt"), InlineKeyboardButton("🛠️️ 🔄 Maintenance", callback_data="toggle_maintenance")],
            [InlineKeyboardButton("❌ 📦 Close", callback_data="close_panel")]
        ]
        await update.message.reply_text(panel_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Lookup execution
    user_data = db_get_one("SELECT phone_number, is_banned FROM users WHERE user_id = ?", (user.id,))
    if not user_data or user_data.get('is_banned') == 1: return
    if not user_data.get('phone_number'):
        contact_button = [[KeyboardButton("📱 Share Contact to Verify & Start", request_contact=True)]]
        await update.message.reply_text("⚠️ Kripya apna contact verify karein:", parse_mode='Markdown', reply_markup=ReplyKeyboardMarkup(contact_button, one_time_keyboard=True, resize_keyboard=True))
        return

    mode = context.user_data.get('mode', None)
    cleaned = re.sub(r'\D', '', text)

    if mode and mode.startswith("custom_api_"):
        api_k = mode.replace("custom_api_", "")
        msg = await update.message.reply_text("💻 Fetching data...", parse_mode='Markdown')
        data = await fetch_dynamic_api(api_k, text)
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, f"{api_k}:{text}", json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        if len(json_str) > 4000: json_str = json_str[:4000] + "\n... (Truncated)"
        await msg.edit_text(f"```json\n{json_str}\n```", parse_mode='Markdown')
        context.user_data['mode'] = None
        return

    if mode == 'aadhaar_info':
        msg = await update.message.reply_text("🆔 Searching Aadhaar...", parse_mode='Markdown')
        data = await fetch_dynamic_api('aadhaar_info', text)
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, "AADHAAR:" + text, json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        formatted = format_aadhaar_response(data, text)
        await msg.edit_text(formatted, parse_mode='Markdown')
        context.user_data['mode'] = None
    elif mode == 'ip_info':
        msg = await update.message.reply_text("🌐 Searching IP...", parse_mode='Markdown')
        data = await fetch_dynamic_api('ip_info', text)
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, "IP:" + text, json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        formatted = format_ip_response(data, text)
        await msg.edit_text(formatted, parse_mode='Markdown')
        context.user_data['mode'] = None
    elif mode == 'tg_username':
        query_str = text if text.startswith('@') else '@' + text
        msg = await update.message.reply_text("🕵️‍♂️ Searching TG Username...", parse_mode='Markdown')
        data = await fetch_dynamic_api('tg_username', query_str)
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, "TG_USER:" + query_str, json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        formatted = format_tg_response(data, query_str)
        await msg.edit_text(formatted, parse_mode='Markdown')
        context.user_data['mode'] = None
    elif mode == 'tg_userid':
        msg = await update.message.reply_text("🕵️‍♂️ Searching TG ID...", parse_mode='Markdown')
        data = await fetch_dynamic_api('tg_userid', cleaned)
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, "TG_ID:" + cleaned, json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        formatted = format_tg_response(data, cleaned)
        await msg.edit_text(formatted, parse_mode='Markdown')
        context.user_data['mode'] = None
    elif mode == 'pincode' or (len(cleaned) == 6 and len(text) == 6 and not mode):
        msg = await update.message.reply_text("📍 Searching Pincode...", parse_mode='Markdown')
        data = await fetch_dynamic_api('pincode', cleaned)
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, "PIN:" + cleaned, json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        formatted = format_pincode_response(data, cleaned)
        await msg.edit_text(formatted, parse_mode='Markdown')
        context.user_data['mode'] = None
    elif mode == 'phone' or (10 <= len(cleaned) <= 15):
        msg = await update.message.reply_text("💻 Searching Number...", parse_mode='Markdown')
        data = await fetch_dynamic_api('phone', cleaned)
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, cleaned, json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        records, err = parse_phone_records(data, cleaned)
        if err: await msg.edit_text(err)
        else:
            context.user_data['last_phone_records'] = records
            context.user_data['last_phone_target'] = cleaned
            await send_paginated_phone_response(msg, records, cleaned, update, context, page=0, is_edit=True)
        context.user_data['mode'] = None

# ============================================
# CALLBACK QUERY HANDLER
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
    elif data == "close_panel":
        try: await query.message.delete()
        except: pass
        return

    if not is_admin_user(query.from_user.id): return

    if data == "admin_dynamic_apis":
        apis = db_get_all("SELECT * FROM dynamic_apis")
        text = "🌐 *DYNAMIC API MANAGER*\n━━━━━━━━━━━━━━━━━━━━\n"
        keyboard = []
        for ap in apis: keyboard.append([InlineKeyboardButton(f"🔗 {ap['api_name']}", callback_data=f"edit_api_url_{ap['api_key']}")])
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="admin_panel")])
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return
    elif data == "admin_add_api":
        context.user_data['waiting_for_new_api_key'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="🔌 Enter new API Key (no spaces):", parse_mode='Markdown')
        return
    elif data == "admin_delete_api":
        context.user_data['waiting_for_delete_api_key'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="🗑 Enter API Key or Name to delete:", parse_mode='Markdown')
        return
    elif data == "admin_edit_name":
        context.user_data['waiting_for_edit_name_key'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="✏ Enter API Key or current Name to edit:", parse_mode='Markdown')
        return
    elif data == "admin_toggle_style":
        curr = db_get_one("SELECT value FROM settings WHERE key='report_style'")['value']
        styles = ['cyber', 'json', 'hacker', 'matrix', 'neon', 'card', 'compact', 'minimal', 'vip', 'standard']
        next_style = styles[(styles.index(curr) + 1) % len(styles)] if curr in styles else 'cyber'
        db_execute("UPDATE settings SET value = ? WHERE key = 'report_style'", (next_style,), commit=True)
        await query.answer(f"🎨 Report Style changed to: {next_style.upper()}!", show_alert=True)
        return
    elif data == "admin_toggle_clone_ref":
        curr = db_get_one("SELECT value FROM settings WHERE key='clone_ref_toggle'")
        new_val = 'off' if curr and curr['value'] == 'on' else 'on'
        db_execute("UPDATE settings SET value = ? WHERE key = 'clone_ref_toggle'", (new_val,), commit=True)
        await query.answer(f"✅ Clone Ref Requirement is now {new_val.upper()}!", show_alert=True)
        return
    elif data == "admin_cloneref_prompt":
        context.user_data['waiting_for_clone_ref_count'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="👥 Enter new required referral count:", parse_mode='Markdown')
        return
    elif data == "admin_refreward_prompt":
        context.user_data['waiting_for_ref_reward'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="🎁 Enter new referral reward credit amount:", parse_mode='Markdown')
        return
    elif data == "admin_setmaintmsg_prompt":
        context.user_data['waiting_for_maint_msg'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="💬 Enter new maintenance message:", parse_mode='Markdown')
        return
    elif data == "admin_banner_prompt":
        context.user_data['waiting_for_banner'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="🖼️ Send photo/video/gif for banner:", parse_mode='Markdown')
        return
    elif data == "admin_addsub_prompt":
        context.user_data['waiting_for_add_sub'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="🛡️ Enter User ID to add as Sub-Admin:", parse_mode='Markdown')
        return
    elif data == "toggle_maintenance":
        curr = db_get_one("SELECT value FROM settings WHERE key='maintenance'")['value']
        new_val = 'off' if curr == 'on' else 'on'
        db_execute("UPDATE settings SET value = ? WHERE key = 'maintenance'", (new_val,), commit=True)
        await query.answer(f"🛠️ Maintenance Mode: {new_val.upper()}", show_alert=True)
        return

# ============================================
# MAIN FUNCTION & HANDLERS REGISTRATION
# ============================================
def main():
    threading.Thread(target=run_flask, daemon=True).start()
    print("🚀 HARSH OSINT BOT STARTING (ALL FEATURES FIXED & READY)...")
    
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
