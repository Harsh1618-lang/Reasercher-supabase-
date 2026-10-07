#!/usr/init/env python3
# OSINT & Pincode Bot - Ultimate 10 Report Styles & Notification Center Edition
"""
Developer: @Harsx1618
Description: Advanced Telegram OSINT Bot with User-side & Admin-side Notification Center, Analytics, Profile, UI Settings & All Features Intact
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
        last_daily TEXT DEFAULT '',
        ui_theme TEXT DEFAULT 'Dark',
        report_mode TEXT DEFAULT 'Full',
        default_style TEXT DEFAULT 'cyber',
        notifications TEXT DEFAULT 'ON'
    )''')
    
    # Safe column checks & migrations
    try: c.execute("ALTER TABLE users ADD COLUMN ui_theme TEXT DEFAULT 'Dark'")
    except: pass
    try: c.execute("ALTER TABLE users ADD COLUMN report_mode TEXT DEFAULT 'Full'")
    except: pass
    try: c.execute("ALTER TABLE users ADD COLUMN default_style TEXT DEFAULT 'cyber'")
    except: pass
    try: c.execute("ALTER TABLE users ADD COLUMN notifications TEXT DEFAULT 'ON'")
    except: pass

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

    # Notification Center Tables
    c.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        message TEXT,
        media_url TEXT DEFAULT '',
        btn_text TEXT DEFAULT '',
        btn_url TEXT DEFAULT '',
        notif_type TEXT DEFAULT 'Announcement',
        target_group TEXT DEFAULT 'All users',
        status TEXT DEFAULT 'Active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS user_notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        notif_id INTEGER,
        is_read INTEGER DEFAULT 0,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    default_welcome = "\n╔═════════════════════════════════╗\n║       👑 HARSHX1618 ELITE 👑       ║\n╚═════════════════════════════════╝\n💎 Your Vault:    {credits} Credits ✨\n🌟 Privilege: Lifetime Access ⚡\n👇 Choose Your Path:\n┌─────────────────────────────────┐\n│ 🎁 Claim Freebies ➔ /daily      │\n│ 🔑 Redeem Code   ➔ /redeem      │\n└─────────────────────────────────┘"
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('welcome_msg', ?)", (default_welcome,))

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
    db_execute("INSERT INTO logs (user_id, action) VALUES (?, ?)", (user_id, action), commit=True)

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

# ============================================
# RADAR & SATELLITE SEARCH ANIMATION
# ============================================
async def show_radar_animation(msg_obj, target_str):
    try:
        await msg_obj.edit_text(f"📡 Scanning global nodes for `{target_str}`...\n`[ ⏳ ] 25%`", parse_mode='Markdown')
        await asyncio.sleep(0.5)
        await msg_obj.edit_text(f"🛰️ Connecting to encrypted servers for `{target_str}`...\n`[ 🔄 ] 50%`", parse_mode='Markdown')
        await asyncio.sleep(0.5)
        await msg_obj.edit_text(f"🔍 Filtering database logs for `{target_str}`...\n`[ ⚡ ] 75%`", parse_mode='Markdown')
        await asyncio.sleep(0.5)
        await msg_obj.edit_text(f"✅ Target details extracted successfully for `{target_str}`!\n`[ 🎯 ] 100%`", parse_mode='Markdown')
        await asyncio.sleep(0.3)
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
# 10 UNIQUE & COOL REPORT STYLES FORMATTER
# ============================================
async def send_paginated_phone_response(msg_obj, records, phone, update, context, page=0, is_edit=True):
    total = len(records)
    if total == 0:
        await msg_obj.edit_text("❌ Koi record nahi mila.")
        return

    user_id = update.effective_user.id
    user_db = db_get_one("SELECT default_style, report_mode FROM users WHERE user_id = ?", (user_id,))
    r_style = user_db.get('default_style', 'cyber') if user_db and user_db.get('default_style') else 'cyber'
    r_mode = user_db.get('report_mode', 'Full') if user_db and user_db.get('report_mode') else 'Full'

    per_page = 3 if r_mode == 'Compact' else 5
    total_pages = (total + per_page - 1) // per_page
    page = max(0, min(page, total_pages - 1))
    
    start_idx = page * per_page
    end_idx = min(start_idx + per_page, total)
    chunk = records[start_idx:end_idx]

    if r_style == 'json':
        json_output = {
            "status": True,
            "target": str(phone),
            "total_records": total,
            "current_page": page + 1,
            "total_pages": total_pages,
            "report_mode": r_mode,
            "records": chunk,
            "developer": OWNER_USERNAME
        }
        text = "```json\n" + json.dumps(json_output, indent=2, ensure_ascii=False) + "\n```"

    elif r_style == 'hacker':
        text = f"💀 [ ROOT ACCESS GRANTED ] ({r_mode.upper()} MODE) 💀\n"
        text += f"🎯 TARGET_IP/NUM: `{phone}`\n"
        text += f"📊 PACKETS: {total} | PAGE: {page + 1}/{total_pages}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for idx, rec in enumerate(chunk, start=start_idx + 1):
            text += f"⚡ [TARGET #{idx}] ⚡\n"
            text += f"• IDENT: `{rec['name']}`\n"
            if r_mode == 'Full': text += f"• PARENT: `{rec['father']}`\n"
            text += f"• COMMS: `{rec['mobile']}` | `{rec['alt_num']}`\n"
            text += f"• NODE: `{rec['circle']}`\n"
            if r_mode == 'Full':
                text += f"• MAIL: `{rec['email']}`\n"
                text += f"• REG_ID: `{rec['caf_id']}`\n"
            text += f"• LOC: `{rec['address']}`\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"⚡ HACKED BY {OWNER_USERNAME}"

    elif r_style == 'matrix':
        text = f"🟩 010101 MATRIX INTEL ({r_mode.upper()}) 010101 🟩\n"
        text += f"Target: `{phone}` | Page: {page + 1}/{total_pages}\n════════════════════════════════\n\n"
        for idx, rec in enumerate(chunk, start=start_idx + 1):
            text += f"🟢 MATRIX_REC_{idx}:\n"
            text += f"├ Name: `{rec['name']}`\n"
            text += f"├ Mobile: `{rec['mobile']}`\n"
            text += f"├ Circle: `{rec['circle']}`\n"
            if r_mode == 'Full': text += f"├ Father: `{rec['father']}`\n"
            text += f"└ Addr: `{rec['address']}`\n\n"
        text += f"System Core: {OWNER_USERNAME}"

    elif r_style == 'cyber':
        text = f"🌐 𝕮𝖄𝕭𝕰𝕽 𝕴𝕹𝕿𝕰𝕃𝕃𝕴𝕲𝕰𝕹𝕮𝕰 ({r_mode.upper()}) 🌐\n"
        text += f"🎯 Target: `{phone}`\n"
        text += f"📊 Records: {total} | Page: {page + 1}/{total_pages}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for idx, rec in enumerate(chunk, start=start_idx + 1):
            text += f"🔹 **CYBER_NODE #{idx}**\n"
            text += f"👤 Subject: `{rec['name']}`\n"
            if r_mode == 'Full': text += f"👨‍👧 Guardian: `{rec['father']}`\n"
            text += f"📱 Phone: `{rec['mobile']}`\n"
            if r_mode == 'Full': text += f"📞 Alt: `{rec['alt_num']}`\n"
            text += f"📡 Telecom: `{rec['circle']}`\n"
            if r_mode == 'Full':
                text += f"📧 Mail: `{rec['email']}`\n"
                text += f"🆔 UID: `{rec['caf_id']}`\n"
            text += f"🏠 Sector:\n`{rec['address']}`\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"⚡ Secured by {OWNER_USERNAME}"

    elif r_style == 'neon':
        text = f"🟣 🪩 NEON GLOW INTEL ({r_mode.upper()}) 🪩 🟣\n"
        text += f"🎯 Target: `{phone}` (Page {page + 1}/{total_pages})\n──────────────────────────────\n\n"
        for idx, rec in enumerate(chunk, start=start_idx + 1):
            text += f"✨ **[RECORD {idx}]**\n"
            text += f"👤 `[NAME]` : {rec['name']}\n"
            text += f"📱 `[CELL]` : {rec['mobile']}\n"
            text += f"🌐 `[AREA]` : {rec['circle']}\n"
            text += f"🏠 `[HOME]` : {rec['address']}\n\n──────────────────────────────\n"

    elif r_style == 'card':
        text = f"🪪 **VIP CARD INTELLIGENCE REPORT**\n"
        text += f"🎯 Target Number: `{phone}` | Mode: {r_mode}\n📊 Records: {total} | Page: {page + 1}/{total_pages}\n════════════════════════\n\n"
        for idx, rec in enumerate(chunk, start=start_idx + 1):
            text += f"┌ 👑 **IDENTITY CARD #{idx}**\n"
            text += f"├ 👤 **Name:** `{rec['name']}`\n"
            if r_mode == 'Full': text += f"├ 👨‍👧 **Father:** `{rec['father']}`\n"
            text += f"├ 📱 **Mobile:** `{rec['mobile']}`\n"
            text += f"├ 🌐 **Circle:** `{rec['circle']}`\n"
            text += f"└ 🏠 **Address:** `{rec['address']}`\n\n════════════════════════\n"

    elif r_style == 'compact':
        text = f"⚡ **COMPACT INTEL REPORT ({phone}) [Page {page + 1}/{total_pages}]**\n────────────────────────\n"
        for idx, rec in enumerate(chunk, start=start_idx + 1):
            text += f"`{idx}.` **{rec['name']}** | `{rec['mobile']}` | `{rec['circle']}`\n   🏠 `{rec['address']}`\n"
        text += f"────────────────────────\n"

    elif r_style == 'minimal':
        text = f"▪️ **INTEL // {phone} ({page + 1}/{total_pages})**\n\n"
        for idx, rec in enumerate(chunk, start=start_idx + 1):
            text += f"`{idx}` {rec['name']} | {rec['mobile']} | {rec['circle']}\n"
        text += f"\n▪️ Auth: {OWNER_USERNAME}"

    elif r_style == 'vip':
        text = f"⭐ 👑 **VIP EXCLUSIVE OSINT REPORT** 👑 ⭐\n"
        text += f"🎯 Target: `{phone}` | Page: {page + 1}/{total_pages}\n──────────────────────────────\n\n"
        for idx, rec in enumerate(chunk, start=start_idx + 1):
            text += f"🌟 **VIP PROFILE #{idx}**\n"
            text += f"• Full Name : **{rec['name']}**\n"
            if r_mode == 'Full': text += f"• Father    : **{rec['father']}**\n"
            text += f"• Contact   : `{rec['mobile']}`\n"
            text += f"• Region    : {rec['circle']}\n"
            text += f"• Location  : _{rec['address']}_\n\n──────────────────────────────\n"

    else:  # Standard
        text = f"📱 **NUMBER INTELLIGENCE REPORT** ({r_mode.upper()})\n"
        text += f"🎯 Target: `{phone}`\n"
        text += f"📊 Total Records: {total} | Page: {page + 1}/{total_pages}\n━━━━━━━━━━━━━━━━━━━━\n\n"
        for idx, rec in enumerate(chunk, start=start_idx + 1):
            text += f"🔹 **RECORD #{idx}**\n"
            text += f"👤 Name: `{rec['name']}`\n"
            if r_mode == 'Full': text += f"👨‍👧 Father: `{rec['father']}`\n"
            text += f"📱 Mobile: `{rec['mobile']}`\n"
            if r_mode == 'Full': text += f"📞 Alt Num: `{rec['alt_num']}`\n"
            text += f"🌐 Circle: `{rec['circle']}`\n"
            if r_mode == 'Full':
                text += f"📧 Email: `{rec['email']}`\n"
                text += f"🆔 CAF / ID: `{rec['caf_id']}`\n"
            text += f"🏠 Address:\n`{rec['address']}`\n\n━━━━━━━━━━━━━━━━━━━━\n"

    text += f"⚡ Developed by {OWNER_USERNAME}"

    buttons = []
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"phone_page_{page - 1}"))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"phone_page_{page + 1}"))
    if nav_row:
        buttons.append(nav_row)

    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None

    if is_edit:
        try:
            await msg_obj.edit_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        except:
            pass
    else:
        reply_msg = await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        msg_obj = reply_msg

    if page == 0:
        sent_message_ids = [msg_obj.message_id]
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
        json_output = {"status": "success", "pincode": str(pincode), "total_records_shown": len(formatted_records), "records": formatted_records}
        return "```json\n" + json.dumps(json_output, indent=2, ensure_ascii=False) + "\n```"
    except Exception as e:
        return "❌ Error formatting pincode data: " + str(e)

def format_tg_response(data, query_str):
    try:
        if not data or (isinstance(data, dict) and data.get('status') == False and 'error' in data):
            return "❌ Error: " + data.get('error', 'No data found')
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        if len(json_str) > 4000: json_str = json_str[:4000] + "\n... (Truncated)"
        return "```json\n" + json_str + "\n```"
    except Exception as e:
        return "❌ Error formatting TG data: " + str(e)

def format_ip_response(data, ip_str):
    try:
        if not data or (isinstance(data, dict) and data.get('status') == False):
            return "❌ Error: " + data.get('error', 'No data found')
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        if len(json_str) > 4000: json_str = json_str[:4000] + "\n... (Truncated)"
        return "```json\n" + json_str + "\n```"
    except Exception as e:
        return "❌ Error formatting IP data: " + str(e)

def format_aadhaar_response(data, query_str):
    try:
        if not data or (isinstance(data, dict) and data.get('status') == False):
            return "❌ Error: " + data.get('error', 'No data found')
        if isinstance(data, dict):
            data.pop('developer', None)
            data.pop('owner', None)
            data.pop('channel', None)
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        if len(json_str) > 4000: json_str = json_str[:4000] + "\n... (Truncated)"
        return "```json\n" + json_str + "\n```"
    except Exception as e:
        return "❌ Error formatting data: " + str(e)

# ============================================
# NOTIFICATION CENTER & USER PROFILE HANDLERS
# ============================================
async def show_notifications_center(update_or_query, context, user_id, is_callback=False):
    user_db = db_get_one("SELECT * FROM users WHERE user_id = ?", (user_id,))
    if not user_db:
        text = "❌ User profile not found."
    else:
        # Fetch active notifications targeted to this user
        notifs = db_get_all("SELECT * FROM notifications WHERE status = 'Active' ORDER BY id DESC LIMIT 5")
        text = f"🔔 **NOTIFICATION CENTER**\n\n"
        text += f"Aapke latest updates, announcements aur offers:\n━━━━━━━━━━━━━━━━━━━━\n"
        
        if not notifs:
        
            text += "📭 Filhal koi nayi notification nahi hai.\n"
        else:
            for n in notifs:
                # Check read status
                read_rec = db_get_one("SELECT * FROM user_notifications WHERE user_id = ? AND notif_id = ?", (user_id, n['id']))
                status_icon = "✅ Read" if read_rec and read_rec['is_read'] == 1 else "🔵 Unread"
                
                # Mark as read automatically when opened
                if not read_rec:
                    db_execute("INSERT INTO user_notifications (user_id, notif_id, is_read) VALUES (?, ?, 1)", (user_id, n['id']), commit=True)
                elif read_rec['is_read'] == 0:
                    db_execute("UPDATE user_notifications SET is_read = 1 WHERE user_id = ? AND notif_id = ?", (user_id, n['id']), commit=True)

                icon_type = "📢"
                if n['notif_type'] == 'Offer': icon_type = "🎁"
                elif n['notif_type'] == 'Maintenance': icon_type = "🔧"
                elif n['notif_type'] == 'Update': icon_type = "🚀"
                elif n['notif_type'] == 'Important': icon_type = "⚠️"

                text += f"{icon_type} **{n['title']}** [{status_icon}]\n"
                text += f"{n['message']}\n"
                if n['btn_text'] and n['btn_url']:
                    text += f"🔗 [{n['btn_text']}]({n['btn_url']})\n"
                text += f"━━━━━━━━━━━━━━━━━━━━\n"

    keyboard = [
        [InlineKeyboardButton("🔄 Refresh Notifs", callback_data="notif_refresh"), InlineKeyboardButton("🗑️ Clear / Mark Read", callback_data="notif_clear")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="profile_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if is_callback:
        try:
            await update_or_query.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup, disable_web_page_preview=True)
        except:
            await update_or_query.callback_query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup, disable_web_page_preview=True)
    else:
        await update_or_query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup, disable_web_page_preview=True)

async def notif_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await show_notifications_center(update, context, user.id, is_callback=False)

async def show_user_profile(update_or_query, context, user_id, is_callback=False):
    user_db = db_get_one("SELECT * FROM users WHERE user_id = ?", (user_id,))
    if not user_db:
        text = "❌ User profile not found in database."
    else:
        name = user_db.get('first_name') or 'User'
        username = "@" + user_db.get('username') if user_db.get('username') and user_db.get('username') != 'NoUsername' else "Not Set"
        credits = user_db.get('credits', 0)
        searches = user_db.get('searches', 0)
        joined = user_db.get('joined_date', 'N/A')
        if joined and len(str(joined)) >= 10:
            try: joined = str(joined)[:10]
            except: pass
        
        referrals = db_get_all("SELECT COUNT(*) as cnt FROM users WHERE referred_by = ?", (user_id,))
        ref_count = referrals[0]['cnt'] if referrals else 0

        theme = user_db.get('ui_theme', 'Dark')
        mode = user_db.get('report_mode', 'Full')
        style = user_db.get('default_style', 'cyber').upper()
        notif = user_db.get('notifications', 'ON')

        text = f"👤 **USER PROFILE & UI SETTINGS**\n\n"
        text += f"━━━━━━━━━━━━━━━━━━━━\n"
        text += f"📛 **Name:** {name}\n"
        text += f"👤 **Username:** {username}\n"
        text += f"🆔 **Telegram ID:** `{user_id}`\n\n"
        text += f"💎 **Credits:** `{credits}`\n"
        text += f"🔍 **Total Searches:** `{searches}`\n"
        text += f"🎁 **Referrals:** `{ref_count}`\n"
        text += f"📅 **Joined:** `{joined}`\n\n"
        text += f"⚙️ **UI Preferences:**\n"
        text += f"• Theme: `{theme}` | Report Mode: `{mode}`\n"
        text += f"• Default Style: `{style}` | Notifications: `{notif}`\n"
        text += f"━━━━━━━━━━━━━━━━━━━━"

    keyboard = [
        [InlineKeyboardButton("🌙 Toggle Theme", callback_data="ui_toggle_theme"), InlineKeyboardButton("📄 Report Mode", callback_data="ui_toggle_mode")],
        [InlineKeyboardButton("🎨 Report Style", callback_data="ui_set_style"), InlineKeyboardButton("🔔 Notifications", callback_data="ui_toggle_notif")],
        [InlineKeyboardButton("📜 HISTORY", callback_data="profile_history"), InlineKeyboardButton("📊 STATS", callback_data="profile_stats")],
        [InlineKeyboardButton("🎁 REFER", callback_data="profile_referral"), InlineKeyboardButton("💎 BUY", callback_data="profile_buy")],
        [InlineKeyboardButton("🔄 REFRESH", callback_data="profile_refresh"), InlineKeyboardButton("🏠 MAIN MENU", callback_data="profile_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if is_callback:
        try:
            await update_or_query.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        except:
            await update_or_query.callback_query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update_or_query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await show_user_profile(update, context, user.id, is_callback=False)

async def quick_search_menu(update_or_query, context, is_callback=False):
    text = "🔍 **QUICK SEARCH MENU**\n\nNeeche diye gaye buttons mein se apna lookup type select karein:"
    keyboard = [
        [InlineKeyboardButton("📱 Number", callback_data="qs_number"), InlineKeyboardButton("📍 Pincode", callback_data="qs_pincode")],
        [InlineKeyboardButton("🌐 IP", callback_data="qs_ip"), InlineKeyboardButton("🔤 Telegram", callback_data="qs_telegram")],
        [InlineKeyboardButton("🔎 Custom API", callback_data="qs_custom"), InlineKeyboardButton("🏠 Main Menu", callback_data="profile_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if is_callback:
        try:
            await update_or_query.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        except:
            await update_or_query.callback_query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update_or_query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def quick_search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await quick_search_menu(update, context, is_callback=False)

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

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text("🟢 *API & System Status: ALL SYSTEMS ONLINE*\n\n⚡ All OSINT Modules, Pincode, IP, Aadhaar & Telegram APIs are working smoothly!", parse_mode='Markdown')

async def ref_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot_uname = BOT_USERNAME.replace('@', '')
    ref_link = f"https://t.me/{bot_uname}?start={user.id}"
    reward_setting = db_get_one("SELECT value FROM settings WHERE key='ref_reward_credits'")
    ref_reward = reward_setting['value'] if reward_setting else "2"
    
    ref_text = f"💰 **REFER & EARN FREE CREDITS**\n\n"
    ref_text += f"Aapke referral link se har ek naye user ke join karne par aapko `{ref_reward} Credits` milenge!\n\n"
    ref_text += f"🔗 **Aapka Referral Link:**\n`{ref_link}`\n\n"
    ref_text += f"Is link ko apne doston ke sath share karein!"
    await update.message.reply_text(ref_text, parse_mode='Markdown')

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
    user_data = db_get_one("SELECT last_daily FROM users WHERE user_id = ?", (user.id,))
    today_str = datetime.now().strftime("%Y-%m-%d")
    if user_data['last_daily'] == today_str:
        await update.message.reply_text("❌ Aapne aaj ka daily bonus pehle hi claim kar liya hai!")
        return
    bonus = 2
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
        db_execute("INSERT INTO users (user_id, username, first_name, credits, referred_by) VALUES (?, ?, ?, ?, ?)",
                   (user.id, user.username or "NoUsername", user.first_name, ref_reward, referrer_id), commit=True)
        log_activity(user.id, "New user joined via /start")
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
    if user_db_check and user_db_check.get('is_banned') == 1:
        await update.message.reply_text("❌ Aapko bot use karne se block kar diya gaya hai.")
        return

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
    
    welcome_template = db_get_one("SELECT value FROM settings WHERE key='welcome_msg'")['value']
    welcome = welcome_template.format(credits=credits, owner=OWNER_USERNAME)
    
    apis = db_get_all("SELECT api_name FROM dynamic_apis")
    menu_keyboard = []
    row = []
    
    static_buttons = ["🔔 Notifications", "🔍 Quick Search", "👤 MY PROFILE", "💬 Owner | Support", "💰 Refer & Earn", "🏆 Leaderboard", "🤖 My Clone Bot", "💎 Buy Premium / Credits", "🛠️ Toggle Menu"]
    
    api_button_names = []
    for ap in apis:
        name = ap['api_name']
        if name == 'Number Info': api_button_names.append("🔍 NUMBER INFO")
        elif name == 'Pincode Info': api_button_names.append("📍 PINCODE INFO")
        elif name == 'IP Info': api_button_names.append("🌐 IP INFO")
        elif name == 'Aadhaar Info': api_button_names.append("🆔 AADHAAR INFO")
        elif name == 'TG Username' or name == 'TG UserID' or name == 'Telegram To Num':
            if "✈️ TELEGRAM TO NUM" not in api_button_names: api_button_names.append("✈️ TELEGRAM TO NUM")
        else:
            api_button_names.append(f"🔮 {name.upper()}")

    if "✈️ TELEGRAM TO NUM" not in api_button_names:
        api_button_names.append("✈️ TELEGRAM TO NUM")

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
        if banner_type == 'animation' and banner_media:
            await context.bot.send_animation(chat_id=chat_id, animation=banner_media, caption=welcome, parse_mode=None, reply_markup=reply_markup)
            return
        elif banner_type == 'photo' and banner_media:
            await context.bot.send_photo(chat_id=chat_id, photo=banner_media, caption=welcome, parse_mode=None, reply_markup=reply_markup)
            return
        elif banner_type == 'video' and banner_media:
            await context.bot.send_video(chat_id=chat_id, video=banner_media, caption=welcome, parse_mode=None, reply_markup=reply_markup)
            return
    except: pass 

    if hasattr(update_or_query, 'message') and update_or_query.message:
        await update_or_query.message.reply_text(welcome, parse_mode=None, reply_markup=reply_markup)

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
    upi_qr_record = db_get_one("SELECT value FROM settings WHERE key='upi_qr'")
    upi_id = upi_record['value'] if upi_record else "harshhacker@upi"
    upi_qr = upi_qr_record['value'] if upi_qr_record else ""
    plans = db_get_all("SELECT * FROM plans")
    text = f"💎 **BUY PREMIUM & ADD CREDITS**\n━━━━━━━━━━━━━━━━━━━━━━\n📲 **Admin UPI ID:** `{upi_id}`\n\n📦 **Available Plans:**\n"
    for p in plans:
        text += f"• **{p['name']}** — `{p['price']}` for **{p['credits']} Credits**\n"
    
    chat_id = update.message.chat_id if hasattr(update, 'message') and update.message else update.callback_query.message.chat_id
    if upi_qr:
        try:
            await context.bot.send_photo(chat_id=chat_id, photo=upi_qr, caption=text, parse_mode='Markdown')
            return
        except: pass

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
        contact_button = [[KeyboardButton("📱 Share Contact to Verify & Start", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(contact_button, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("⚠️ *SECURITY VERIFICATION REQUIRED*\n\nScam se bachne ke liye kripya neeche diye gaye button par click karke apna contact verify karein!", parse_mode='Markdown', reply_markup=reply_markup)
        return False
    if user_data['credits'] <= 0 and not is_admin_user(user.id):
        upi_record = db_get_one("SELECT value FROM settings WHERE key='upi_id'")
        await update.message.reply_text(f"❌ **Aapke credits khatam ho chuke hain!**\n\nKripya UPI ID: `{upi_record['value'] if upi_record else 'harshhacker@upi'}` par payment karein.", parse_mode='Markdown')
        return False
    return True

# ============================================
# MESSAGE HANDLER
# ============================================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    active_live_users.add(user.id)
    text = update.message.text.strip() if update.message.text else ""

    # Strict Admin Prompt Handlers for Notifications & Settings
    if is_admin_user(user.id):
        if context.user_data.get('waiting_for_notif_title'):
            context.user_data['temp_notif_title'] = text
            context.user_data['waiting_for_notif_title'] = False
            context.user_data['waiting_for_notif_msg'] = True
            await update.message.reply_text("📝 Ab notification ka **Message / Body** enter karein:", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_notif_msg'):
            context.user_data['temp_notif_msg'] = text
            context.user_data['waiting_for_notif_msg'] = False
            context.user_data['waiting_for_notif_type'] = True
            await update.message.reply_text("🏷️ Notification ka type select karein (Type:\n`Announcement`, `Offer`, `Maintenance`, `Update`, `Important`):", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_notif_type'):
            context.user_data['temp_notif_type'] = text.strip()
            context.user_data['waiting_for_notif_type'] = False
            context.user_data['waiting_for_notif_target'] = True
            await update.message.reply_text("👥 Kise bhejna hai? (Options:\n`All users`, `Premium users`, `New users`):", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_notif_target'):
            title = context.user_data.get('temp_notif_title')
            msg = context.user_data.get('temp_notif_msg')
            ntype = context.user_data.get('temp_notif_type')
            target = text.strip()
            
            db_execute("INSERT INTO notifications (title, message, notif_type, target_group) VALUES (?, ?, ?, ?)", (title, msg, ntype, target), commit=True)
            context.user_data.clear()
            log_activity(user.id, f"Admin created notification: {title}")
            await update.message.reply_text("🎉 Notification successfully created and sent to target group!", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_welcome_msg'):
            db_execute("UPDATE settings SET value = ? WHERE key = 'welcome_msg'", (text,), commit=True)
            context.user_data['waiting_for_welcome_msg'] = False
            log_activity(user.id, "Admin updated welcome message template")
            await update.message.reply_text(f"✅ Welcome message successfully updated to:\n\n{text}", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_banner'):
            media_id = ""
            media_type = "none"
            try:
                if update.message.animation:
                    media_id = update.message.animation.file_id
                    media_type = "animation"
                elif update.message.video:
                    media_id = update.message.video.file_id
                    media_type = "video"
                elif update.message.photo:
                    media_id = update.message.photo[-1].file_id
                    media_type = "photo"
                elif update.message.document:
                    media_id = update.message.document.file_id
                    media_type = "video"

                if media_id:
                    db_execute("UPDATE settings SET value = ? WHERE key = 'banner_media'", (media_id,), commit=True)
                    db_execute("UPDATE settings SET value = ? WHERE key = 'banner_type'", (media_type,), commit=True)
                    context.user_data['waiting_for_banner'] = False
                    log_activity(user.id, "Admin updated banner")
                    
                    await update.message.reply_text("✅ Success! Naya banner media successfully set ho chuka hai.", parse_mode='Markdown')
                    return
            except Exception as e:
                await update.message.reply_text(f"❌ Error saving banner: {str(e)}")
                return

        if context.user_data.get('waiting_for_maint_msg'):
            db_execute("UPDATE settings SET value = ? WHERE key = 'maint_msg'", (text,), commit=True)
            context.user_data['waiting_for_maint_msg'] = False
            log_activity(user.id, "Admin updated maintenance message")
            await update.message.reply_text(f"✅ Maintenance message updated to:\n`{text}`", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_upi'):
            if update.message.photo:
                qr_id = update.message.photo[-1].file_id
                db_execute("UPDATE settings SET value = ? WHERE key = 'upi_qr'", (qr_id,), commit=True)
                context.user_data['waiting_for_upi'] = False
                log_activity(user.id, "Admin updated UPI QR Code")
                await update.message.reply_text("✅ UPI QR Code successfully updated!", parse_mode='Markdown')
                return
            elif update.message.document:
                qr_id = update.message.document.file_id
                db_execute("UPDATE settings SET value = ? WHERE key = 'upi_qr'", (qr_id,), commit=True)
                context.user_data['waiting_for_upi'] = False
                log_activity(user.id, "Admin updated UPI QR Code")
                await update.message.reply_text("✅ UPI QR Code successfully updated!", parse_mode='Markdown')
                return
            elif text:
                db_execute("UPDATE settings SET value = ? WHERE key = 'upi_id'", (text,), commit=True)
                context.user_data['waiting_for_upi'] = False
                log_activity(user.id, f"Admin updated UPI ID to {text}")
                await update.message.reply_text(f"✅ UPI ID successfully updated to: `{text}`\n\nAb aap chahe toh payment QR code ka photo bhi bhej sakte hain.", parse_mode='Markdown')
                return

        if context.user_data.get('waiting_for_ban_id'):
            if text.isdigit():
                target_id = int(text)
                db_execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (target_id,), commit=True)
                context.user_data['waiting_for_ban_id'] = False
                log_activity(user.id, f"Admin banned user {target_id}")
                await update.message.reply_text(f"✅ User ID `{target_id}` successfully ban kar diya gaya hai!", parse_mode='Markdown')
                try: await context.bot.send_message(chat_id=target_id, text="❌ Aapko bot use karne se block kar diya gaya hai.")
                except: pass
            else:
                await update.message.reply_text("❌ Kripya valid numeric User ID enter karein.")
            return

        if context.user_data.get('waiting_for_unban_id'):
            if text.isdigit():
                target_id = int(text)
                db_execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (target_id,), commit=True)
                context.user_data['waiting_for_unban_id'] = False
                log_activity(user.id, f"Admin unbanned user {target_id}")
                await update.message.reply_text(f"✅ User ID `{target_id}` successfully unban kar diya gaya hai!", parse_mode='Markdown')
                try: await context.bot.send_message(chat_id=target_id, text="🎉 Aapko unban kar diya gaya hai! Ab aap bot use kar sakte hain.")
                except: pass
            else:
                await update.message.reply_text("❌ Kripya valid numeric User ID enter karein.")
            return

        if context.user_data.get('waiting_for_redeem_gen'):
            parts = text.split()
            if len(parts) == 2 and parts[1].isdigit():
                db_execute("INSERT OR REPLACE INTO redeem_keys (key, credits, is_used) VALUES (?, ?, 0)", (parts[0], int(parts[1])), commit=True)
                context.user_data['waiting_for_redeem_gen'] = False
                log_activity(user.id, f"Admin generated redeem key {parts[0]}")
                await update.message.reply_text(f"🎉 Redeem Key `{parts[0]}` generated for `{parts[1]}` credits!", parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Sahi format use karein: `KEY_NAME CREDITS` (jaise: `VIP50 50`)", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_force_channels'):
            channels_val = "" if text.lower() == 'none' else text.strip()
            db_execute("UPDATE settings SET value = ? WHERE key = 'force_channels'", (channels_val,), commit=True)
            context.user_data['waiting_for_force_channels'] = False
            log_activity(user.id, f"Admin updated force channels: {channels_val}")
            await update.message.reply_text(f"✅ Force join channels successfully updated to:\n`{channels_val if channels_val else 'None (Disabled)'}`", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_plan_name'):
            context.user_data['temp_plan_name'] = text
            context.user_data['waiting_for_plan_name'] = False
            context.user_data['waiting_for_plan_price'] = True
            await update.message.reply_text("💵 Plan ki price enter karein (jaise: `₹149`):", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_plan_price'):
            context.user_data['temp_plan_price'] = text
            context.user_data['waiting_for_plan_price'] = False
            context.user_data['waiting_for_plan_credits'] = True
            await update.message.reply_text("💎 Is plan mein kitne credits milenge? (Sirf number dalein):", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_plan_credits'):
            if text.isdigit():
                p_name = context.user_data.get('temp_plan_name')
                p_price = context.user_data.get('temp_plan_price')
                p_credits = int(text)
                db_execute("INSERT INTO plans (name, price, credits) VALUES (?, ?, ?)", (p_name, p_price, p_credits), commit=True)
                context.user_data['waiting_for_plan_credits'] = False
                log_activity(user.id, f"Admin added plan {p_name}")
                await update.message.reply_text(f"🎉 Naya plan successfully add ho gaya!\n• Name: `{p_name}`\n• Price: `{p_price}`\n• Credits: `{p_credits}`", parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Kripya credits ke liye valid numeric value enter karein.")
            return

        if context.user_data.get('waiting_for_add_sub'):
            if text.isdigit():
                db_execute("INSERT OR IGNORE INTO sub_admins (user_id) VALUES (?)", (int(text),), commit=True)
                log_activity(user.id, f"Admin added sub-admin {text}")
                await update.message.reply_text(f"✅ User ID `{text}` successfully added as Sub-Admin!", parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Kripya valid numeric User ID enter karein.")
            context.user_data['waiting_for_add_sub'] = False
            return

        if context.user_data.get('waiting_for_add_credits_id'):
            if text.isdigit():
                context.user_data['add_credit_target_id'] = int(text)
                context.user_data['waiting_for_add_credits_id'] = False
                context.user_data['waiting_for_add_credits_amount'] = True
                await update.message.reply_text("💎 Ab kitne **credits** add karne hain? Amount enter karein:", parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Kripya valid numeric User ID enter karein.")
            return

        if context.user_data.get('waiting_for_add_credits_amount'):
            if text.isdigit():
                target_id = context.user_data.get('add_credit_target_id')
                amount = int(text)
                db_execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (amount, target_id), commit=True)
                context.user_data['waiting_for_add_credits_amount'] = False
                context.user_data['add_credit_target_id'] = None
                log_activity(user.id, f"Admin added {amount} credits to user {target_id}")
                await update.message.reply_text(f"✅ Successfully added `{amount}` credits to User ID `{target_id}`!", parse_mode='Markdown')
                try: await context.bot.send_message(chat_id=target_id, text=f"🎉 Admin ne aapke account mein `{amount}` credits add kar diye hain!")
                except: pass
            else:
                await update.message.reply_text("❌ Kripya valid digit enter karein.")
            return

        if context.user_data.get('waiting_for_clone_ref_count'):
            if text.isdigit():
                db_execute("UPDATE settings SET value = ? WHERE key = 'clone_req_ref'", (text,), commit=True)
                context.user_data['waiting_for_clone_ref_count'] = False
                await update.message.reply_text(f"✅ Clone referral requirement updated to: `{text}`", parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Kripya valid digit enter karein.")
            return

        if context.user_data.get('waiting_for_ref_reward'):
            if text.isdigit():
                db_execute("UPDATE settings SET value = ? WHERE key = 'ref_reward_credits'", (text,), commit=True)
                context.user_data['waiting_for_ref_reward'] = False
                await update.message.reply_text(f"✅ Referral reward updated to: `{text}` credits per refer!", parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Kripya valid digit enter karein.")
            return

        if context.user_data.get('waiting_for_new_api_key'):
            context.user_data['waiting_for_new_api_key'] = False
            context.user_data['new_api_key_temp'] = text.strip().lower().replace(" ", "_")
            context.user_data['waiting_for_new_api_name'] = True
            await update.message.reply_text("📝 Ab is nayi API ka **Button Display Name** enter karein:", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_new_api_name'):
            context.user_data['waiting_for_new_api_name'] = False
            context.user_data['new_api_name_temp'] = text.strip()
            context.user_data['waiting_for_new_api_url'] = True
            await update.message.reply_text("🔗 Ab is nayi API ka **URL** enter karein (use `{query}` placeholder):", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_new_api_url'):
            db_execute("INSERT OR REPLACE INTO dynamic_apis (api_key, api_name, api_url, old_credit, new_credit) VALUES (?, ?, ?, '', '')", 
                       (context.user_data.get('new_api_key_temp'), context.user_data.get('new_api_name_temp'), text.strip()), commit=True)
            context.user_data['waiting_for_new_api_url'] = False
            log_activity(user.id, f"Admin added new dynamic API {context.user_data.get('new_api_key_temp')}")
            await update.message.reply_text("🎉 Nayee API aur Button successfully add ho chuka hai!", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_delete_api_key'):
            del_key = text.strip().lower()
            if del_key in ['phone', 'pincode', 'ip_info', 'aadhaar_info', 'tg_username', 'tg_userid']:
                await update.message.reply_text("❌ Aap default system APIs ko delete nahi kar sakte!", parse_mode='Markdown')
            else:
                existing = db_get_one("SELECT * FROM dynamic_apis WHERE api_key = ? OR LOWER(api_name) = ?", (del_key, del_key))
                if existing:
                    db_execute("DELETE FROM dynamic_apis WHERE api_key = ? OR LOWER(api_name) = ?", (del_key, del_key), commit=True)
                    log_activity(user.id, f"Admin deleted API {del_key}")
                    await update.message.reply_text("🗑️ API & Button successfully deleted!", parse_mode='Markdown')
                else:
                    await update.message.reply_text("❌ Aisi koi API nahi mili!", parse_mode='Markdown')
            context.user_data['waiting_for_delete_api_key'] = False
            return

        if context.user_data.get('waiting_for_edit_name_key'):
            existing = db_get_one("SELECT * FROM dynamic_apis WHERE api_key = ? OR LOWER(api_name) = ?", (text.strip().lower(), text.strip().lower()))
            if existing:
                context.user_data['edit_name_target_key'] = existing['api_key']
                context.user_data['waiting_for_edit_name_key'] = False
                context.user_data['waiting_for_edit_name_new'] = True
                await update.message.reply_text(f"✏️ Ab is API (`{existing['api_name']}`) ke liye **Naya Button Name** enter karein:", parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Aisi koi API nahi mili!", parse_mode='Markdown')
                context.user_data['waiting_for_edit_name_key'] = False
            return

        if context.user_data.get('waiting_for_edit_name_new'):
            db_execute("UPDATE dynamic_apis SET api_name = ? WHERE api_key = ?", (text.strip(), context.user_data.get('edit_name_target_key')), commit=True)
            context.user_data['waiting_for_edit_name_new'] = False
            await update.message.reply_text(f"✅ Button name successfully updated to `{text.strip()}`!", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_api_url'):
            target_key = context.user_data.get('target_api_key')
            db_execute("UPDATE dynamic_apis SET api_url = ? WHERE api_key = ?", (text.strip(), target_key), commit=True)
            context.user_data['waiting_for_api_url'] = False
            context.user_data['target_api_key'] = None
            await update.message.reply_text("✅ API URL successfully updated!", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_api_old'):
            context.user_data['temp_old_credit'] = text.strip()
            context.user_data['waiting_for_api_old'] = False
            context.user_data['waiting_for_api_new'] = True
            await update.message.reply_text("✍️ Ab **New Watermark / Credit Replacement** text bhejein:", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_api_new'):
            target_key = context.user_data.get('target_api_key')
            old_c = context.user_data.get('temp_old_credit')
            new_c = text.strip()
            db_execute("UPDATE dynamic_apis SET old_credit = ?, new_credit = ? WHERE api_key = ?", (old_c, new_c, target_key), commit=True)
            context.user_data['waiting_for_api_new'] = False
            context.user_data['target_api_key'] = None
            context.user_data['temp_old_credit'] = None
            await update.message.reply_text("✅ API Watermark replacement successfully updated!", parse_mode='Markdown')
            return

    # Check Maintenance
    maint = db_get_one("SELECT value FROM settings WHERE key='maintenance'")['value']
    if maint == 'on' and not is_admin_user(user.id):
        await update.message.reply_text("🚧 " + db_get_one("SELECT value FROM settings WHERE key='maint_msg'")['value'], parse_mode='Markdown')
        return

    clean_input_text = text
    for prefix in ["🔍 ", "📍 ", "🌐 ", "🆔 ", "🔤 ", "🔮 ", "✈️ ", "👤 ", "🔔 "]:
        clean_input_text = clean_input_text.replace(prefix, "")

    if clean_input_text.upper() == "NOTIFICATIONS" or text == "/notifications":
        await show_notifications_center(update, context, user.id, is_callback=False)
        return

    # Smart Auto-Detect for Telegram to Number (Username vs User ID)
    if clean_input_text.upper() == "TELEGRAM TO NUM":
        context.user_data['mode'] = 'telegram_auto_detect'
        menu_display = f"\n✈️ *TELEGRAM TO NUMBER*\n\n👉 *SEND TELEGRAM ID OR USERNAME*\n\n┌─────────────┬──────────────┐\n│ USERNAME    │ `@username`  │\n├─────────────┼──────────────┤\n│ USER ID     │ `1234567890` │\n└─────────────┴──────────────┘"
        await update.message.reply_text(menu_display, parse_mode='Markdown')
        return

    if clean_input_text.upper() == "MY PROFILE" or text == "/profile":
        await show_user_profile(update, context, user.id, is_callback=False)
        return

    if clean_input_text.upper() == "QUICK SEARCH" or text == "/search":
        await quick_search_menu(update, context, is_callback=False)
        return

    matched_api = db_get_one("SELECT * FROM dynamic_apis WHERE UPPER(api_name) = ? OR api_key = ?", (clean_input_text.upper(), text.lower()))
    if matched_api:
        api_k = matched_api['api_key']
        if api_k == 'phone':
            context.user_data['mode'] = 'phone'
            await update.message.reply_text("📱 *Number Info Mode Active*\nKripya ab 10-digit mobile number bhejein:", parse_mode='Markdown')
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
        else:
            context.user_data['mode'] = f"custom_api_{api_k}"
            await update.message.reply_text(f"🔍 *{matched_api['api_name']} Mode Active*\nQuery enter karein:", parse_mode='Markdown')
            return

    if text == "💎 MY PREMIUM STATUS":
        user_info = db_get_one("SELECT credits FROM users WHERE user_id = ?", (user.id,))
        credits = user_info['credits'] if user_info else 0
        status = "👑 Admin / Unlimited" if (is_admin_user(user.id) or credits > 5000) else ("💎 Premium User" if credits > 10 else "🆓 Free User")
        await update.message.reply_text(f"👤 *Aapki Details:*\nStatus: `{status}`\nCredits: `{credits}`", parse_mode='Markdown')
        return
    elif text == "💰 MY BALANCE":
        await balance_command(update, context)
        return
    elif text == "💬 Owner | Support" or text == "/support":
        await support_command(update, context)
        return
    elif text == "💰 Refer & Earn" or text == "/ref":
        await ref_command(update, context)
        return
    elif text == "🏆 Leaderboard":
        top_users = db_get_all("SELECT first_name, credits, searches FROM users ORDER BY searches DESC LIMIT 10")
        lb_text = "🏆 **TOP SEARCHERS LEADERBOARD**\n━━━━━━━━━━━━━━━━━━━━\n"
        for idx, u in enumerate(top_users, 1):
            lb_text += f"{idx}. **{u['first_name']}** — Lookups: `{u['searches']}` | Credits: `{u['credits']}`\n"
        await update.message.reply_text(lb_text, parse_mode='Markdown')
        return
    elif text == "🤖 My Clone Bot":
        toggle_setting = db_get_one("SELECT value FROM settings WHERE key='clone_ref_toggle'")
        if toggle_setting and toggle_setting['value'] == 'on':
            req_refs = int(db_get_one("SELECT value FROM settings WHERE key='clone_req_ref'")['value'])
            user_refs = db_get_all("SELECT COUNT(*) as cnt FROM users WHERE referred_by = ?", (user.id,))[0]['cnt']
            if user_refs < req_refs and not is_admin_user(user.id):
                await update.message.reply_text(f"🤖 Kripya pehle apne `{req_refs}` referrals complete karein (Aapke `{user_refs}/{req_refs}` hain).", parse_mode='Markdown')
                return
        clone_keyboard = [[InlineKeyboardButton("➕ Create New Clone Bot", callback_data="create_clone_prompt")]]
        await update.message.reply_text("🤖 **MY CLONE BOT MANAGER**\nButton par click karke setup karein:", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(clone_keyboard))
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
        await show_full_admin_panel(update, context)
        return

    user_data = db_get_one("SELECT phone_number, is_banned FROM users WHERE user_id = ?", (user.id,))
    if not user_data or user_data['is_banned'] == 1:
        await update.message.reply_text("❌ Aapko block kar diya gaya hai.")
        return
    if not user_data.get('phone_number') or not user_data['phone_number']:
        contact_button = [[KeyboardButton("📱 Share Contact to Verify & Start", request_contact=True)]]
        await update.message.reply_text("⚠️ *SECURITY VERIFICATION REQUIRED*\nKripya contact verify karein!", parse_mode='Markdown', reply_markup=ReplyKeyboardMarkup(contact_button, one_time_keyboard=True, resize_keyboard=True))
        return

    if not await check_user_credit(update, user): return

    mode = context.user_data.get('mode', None)

    if mode == 'telegram_auto_detect':
        msg = await update.message.reply_text("📡 Scanning global nodes...", parse_mode='Markdown')
        await show_radar_animation(msg, text)
        if text.startswith('@') or not text.isdigit():
            query_str = text if text.startswith('@') else '@' + text
            data = await fetch_dynamic_api('tg_username', query_str)
            log_activity(user.id, f"Telegram username lookup: {query_str}")
        else:
            cleaned_tg = re.sub(r'\D', '', text)
            data = await fetch_dynamic_api('tg_userid', cleaned_tg)
            log_activity(user.id, f"Telegram userid lookup: {cleaned_tg}")

        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, f"TG:{text}", json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        formatted = format_tg_response(data, text)
        try: await msg.edit_text(formatted, parse_mode='Markdown')
        except: await msg.edit_text(formatted, parse_mode=None)
        context.user_data['mode'] = None
        return

    if mode == 'pincode':
        msg = await update.message.reply_text("📡 Scanning global nodes...", parse_mode='Markdown')
        await show_radar_animation(msg, text)
        data = await fetch_dynamic_api('pincode', text.strip())
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, f"PIN:{text.strip()}", json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        log_activity(user.id, f"Pincode lookup performed on {text.strip()}")
        formatted = format_pincode_response(data, text.strip())
        try: await msg.edit_text(formatted, parse_mode='Markdown')
        except: await msg.edit_text(formatted, parse_mode=None)
        context.user_data['mode'] = None
        return

    if mode == 'ip_info':
        msg = await update.message.reply_text("📡 Scanning global nodes...", parse_mode='Markdown')
        await show_radar_animation(msg, text)
        data = await fetch_dynamic_api('ip_info', text.strip())
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, f"IP:{text.strip()}", json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        log_activity(user.id, f"IP lookup performed on {text.strip()}")
        formatted = format_ip_response(data, text.strip())
        try: await msg.edit_text(formatted, parse_mode='Markdown')
        except: await msg.edit_text(formatted, parse_mode=None)
        context.user_data['mode'] = None
        return

    if mode == 'aadhaar_info':
        cleaned_aadhaar = re.sub(r'\D', '', text)
        msg = await update.message.reply_text("📡 Scanning global nodes...", parse_mode='Markdown')
        await show_radar_animation(msg, cleaned_aadhaar)
        data = await fetch_dynamic_api('aadhaar_info', cleaned_aadhaar)
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, f"AADHAAR:{cleaned_aadhaar}", json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        log_activity(user.id, f"Aadhaar lookup performed on {cleaned_aadhaar}")
        formatted = format_aadhaar_response(data, cleaned_aadhaar)
        try: await msg.edit_text(formatted, parse_mode='Markdown')
        except: await msg.edit_text(formatted, parse_mode=None)
        context.user_data['mode'] = None
        return

    if mode and mode.startswith("custom_api_"):
        api_k = mode.replace("custom_api_", "")
        msg = await update.message.reply_text("📡 Scanning global nodes...", parse_mode='Markdown')
        await show_radar_animation(msg, text)
        data = await fetch_dynamic_api(api_k, text)
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, f"{api_k}:{text}", json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        log_activity(user.id, f"Custom API search: {api_k}")
        
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        if len(json_str) > 4000: json_str = json_str[:4000] + "\n... (Truncated)"
        try: await msg.edit_text(f"```json\n{json_str}\n```", parse_mode='Markdown')
        except: await msg.edit_text(f"```json\n{json_str}\n```", parse_mode=None)
        context.user_data['mode'] = None
        return

    cleaned_phone = re.sub(r'\D', '', text)
    if mode == 'phone' or (10 <= len(cleaned_phone) <= 15):
        msg = await update.message.reply_text("📡 Scanning global nodes...", parse_mode='Markdown')
        await show_radar_animation(msg, cleaned_phone)
        data = await fetch_dynamic_api('phone', cleaned_phone)
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, cleaned_phone, json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        log_activity(user.id, f"Phone lookup performed on {cleaned_phone}")
        records, err = parse_phone_records(data, cleaned_phone)
        if err: await msg.edit_text(err)
        else: 
            context.user_data['last_phone_records'] = records
            context.user_data['last_phone_target'] = cleaned_phone
            await send_paginated_phone_response(msg, records, cleaned_phone, update, context, page=0, is_edit=True)
        context.user_data['mode'] = None
    else:
        if len(cleaned_phone) >= 10:
            msg = await update.message.reply_text("📡 Scanning global nodes...", parse_mode='Markdown')
            await show_radar_animation(msg, cleaned_phone)
            data = await fetch_dynamic_api('phone', cleaned_phone)
            db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, cleaned_phone, json.dumps(data)), commit=True)
            db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
            log_activity(user.id, f"Direct phone lookup on {cleaned_phone}")
            records, err = parse_phone_records(data, cleaned_phone)
            if err: await msg.edit_text(err)
            else:
                context.user_data['last_phone_records'] = records
                context.user_data['last_phone_target'] = cleaned_phone
                await send_paginated_phone_response(msg, records, cleaned_phone, update, context, page=0, is_edit=True)
            return

        await update.message.reply_text("❌ Kripya pehle menu se koi option select karein ya valid input enter karein.", parse_mode='Markdown')

async def show_full_admin_panel(update_or_query, context):
    total_users = db_get_one("SELECT COUNT(*) as count FROM users")['count']
    total_searches = db_get_one("SELECT COUNT(*) as count FROM searches")['count']
    maint = db_get_one("SELECT value FROM settings WHERE key='maintenance'")['value']
    upi_record = db_get_one("SELECT value FROM settings WHERE key='upi_id'")
    clone_ref_val = db_get_one("SELECT value FROM settings WHERE key='clone_req_ref'")['value']
    clone_toggle_val = db_get_one("SELECT value FROM settings WHERE key='clone_ref_toggle'")['value']
    ref_reward_val = db_get_one("SELECT value FROM settings WHERE key='ref_reward_credits'")['value']
    report_style_val = db_get_one("SELECT value FROM settings WHERE key='report_style'")['value']
    
    panel_text = f"\n📊 *ADVANCED ADMIN PANEL* ({OWNER_USERNAME})\n━━━━━━━━━━━━━━━━━━\n👥 Total Users: `{total_users}`\n🔍 Total Lookups: `{total_searches}`\n💳 UPI: `{upi_record['value'] if upi_record else 'Not Set'}`\n🎨 Report Style: `{report_style_val.upper()}`\n🚧 Maintenance: `{maint.upper()}`\n🤖 Clone Refs: `{clone_ref_val}` (`{clone_toggle_val.upper()}`)\n🎁 Ref Reward: `{ref_reward_val} Credits`\n"
    keyboard = [
        [InlineKeyboardButton("🔔 📢 Create Notification", callback_data="admin_create_notif"), InlineKeyboardButton("📈 📊 Notif Analytics", callback_data="admin_notif_analytics")],
        [InlineKeyboardButton("🟢 👥 View Users & Logs", callback_data="admin_users"), InlineKeyboardButton("💳 ⚙ Set UPI ID", callback_data="admin_setupi_prompt")],
        [InlineKeyboardButton("📦 📋 Manage Plans", callback_data="admin_plans"), InlineKeyboardButton("💎 ➕ Add Credits", callback_data="admin_addcredit_prompt")],
        [InlineKeyboardButton("📈 ⚡ Live Analytics", callback_data="admin_live_analytics"), InlineKeyboardButton("🤖 👥 Clone Bots", callback_data="admin_clones")],
        [InlineKeyboardButton("🌐 🔌 Dynamic APIs", callback_data="admin_dynamic_apis"), InlineKeyboardButton("➕ 🔌 Add New API", callback_data="admin_add_api")],
        [InlineKeyboardButton("🗑️ 🔌 Delete API", callback_data="admin_delete_api"), InlineKeyboardButton("✏️ 📝 Edit Button Name", callback_data="admin_edit_name")],
        [InlineKeyboardButton("🎨 🔄 Change Report Style", callback_data="admin_toggle_style"), InlineKeyboardButton("🔄 Toggle Clone Ref", callback_data="admin_toggle_clone_ref")],
        [InlineKeyboardButton("👥 ⚙️ Set Clone Refs", callback_data="admin_cloneref_prompt"), InlineKeyboardButton("🎁 ⚙ Set Ref Reward", callback_data="admin_refreward_prompt")],
        [InlineKeyboardButton("💬 ⚙ Set Maint Msg", callback_data="admin_setmaintmsg_prompt"), InlineKeyboardButton("🖼️ ⚙ Set Banner", callback_data="admin_banner_prompt")],
        [InlineKeyboardButton("🛡️ ➕ Add Sub-Admin", callback_data="admin_addsub_prompt"), InlineKeyboardButton("🛠️ 🔄 Maintenance", callback_data="toggle_maintenance")],
        [InlineKeyboardButton("💬 Set Welcome Text", callback_data="admin_welcome_prompt"), InlineKeyboardButton("🔑 Gen Redeem Key", callback_data="admin_redeem_prompt")],
        [InlineKeyboardButton("📜 View Logs", callback_data="admin_view_logs"), InlineKeyboardButton("🔨 Ban User", callback_data="admin_ban_prompt")],
        [InlineKeyboardButton("🔓 Unban User", callback_data="admin_unban_prompt"), InlineKeyboardButton("📥 Download Search Logs", callback_data="admin_download_logs")],
        [InlineKeyboardButton("❌ 📦 Close", callback_data="close_panel")]
    ]
    
    chat_id = update_or_query.message.chat_id if hasattr(update_or_query, 'message') and update_or_query.message else update_or_query.effective_chat.id
    if hasattr(update_or_query, 'callback_query') and update_or_query.callback_query:
        await update_or_query.callback_query.edit_message_text(panel_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update_or_query.message.reply_text(panel_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

# ============================================
# ADMIN, PROFILE & NOTIFICATION CALLBACK HANDLER
# ============================================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = query.from_user
    
    if data.startswith("phone_page_"):
        page_num = int(data.split("_")[-1])
        records = context.user_data.get('last_phone_records', [])
        phone = context.user_data.get('last_phone_target', 'Unknown')
        await send_paginated_phone_response(query.message, records, phone, update, context, page=page_num, is_edit=True)
        return

    # Notification Center User Callbacks
    if data == "notif_refresh":
        await show_notifications_center(update, context, user.id, is_callback=True)
        return
    elif data == "notif_clear":
        db_execute("UPDATE user_notifications SET is_read = 1 WHERE user_id = ?", (user.id,), commit=True)
        await query.answer("✅ Saari notifications read mark kar di gayi hain!", show_alert=True)
        await show_notifications_center(update, context, user.id, is_callback=True)
        return

    # UI Settings Callback Handlers
    if data == "ui_toggle_theme":
        curr = db_get_one("SELECT ui_theme FROM users WHERE user_id = ?", (user.id,))
        new_theme = 'Light' if curr and curr.get('ui_theme') == 'Dark' else 'Dark'
        db_execute("UPDATE users SET ui_theme = ? WHERE user_id = ?", (new_theme, user.id), commit=True)
        await show_user_profile(update, context, user.id, is_callback=True)
        return
    elif data == "ui_toggle_mode":
        curr = db_get_one("SELECT report_mode FROM users WHERE user_id = ?", (user.id,))
        new_mode = 'Compact' if curr and curr.get('report_mode') == 'Full' else 'Full'
        db_execute("UPDATE users SET report_mode = ? WHERE user_id = ?", (new_mode, user.id), commit=True)
        await show_user_profile(update, context, user.id, is_callback=True)
        return
    elif data == "ui_set_style":
        styles = ['cyber', 'json', 'hacker', 'matrix', 'neon', 'card', 'compact', 'minimal', 'vip', 'standard']
        curr = db_get_one("SELECT default_style FROM users WHERE user_id = ?", (user.id,))
        curr_style = curr.get('default_style', 'cyber') if curr else 'cyber'
        next_style = styles[(styles.index(curr_style) + 1) % len(styles)] if curr_style in styles else 'cyber'
        db_execute("UPDATE users SET default_style = ? WHERE user_id = ?", (next_style, user.id), commit=True)
        await show_user_profile(update, context, user.id, is_callback=True)
        return
    elif data == "ui_toggle_notif":
        curr = db_get_one("SELECT notifications FROM users WHERE user_id = ?", (user.id,))
        new_notif = 'OFF' if curr and curr.get('notifications') == 'ON' else 'ON'
        db_execute("UPDATE users SET notifications = ? WHERE user_id = ?", (new_notif, user.id), commit=True)
        await show_user_profile(update, context, user.id, is_callback=True)
        return

    # Quick Search Menu Callback Handlers
    if data == "qs_number":
        context.user_data['mode'] = 'phone'
        await query.message.reply_text("📱 *Number Info Mode Active*\nKripya ab 10-digit mobile number bhejein:", parse_mode='Markdown')
        return
    elif data == "qs_pincode":
        context.user_data['mode'] = 'pincode'
        await query.message.reply_text("📍 *Pincode Lookup Mode Active*\nKripya 6-digit PIN code bhejein:", parse_mode='Markdown')
        return
    elif data == "qs_ip":
        context.user_data['mode'] = 'ip_info'
        await query.message.reply_text("🌐 *IP Info Mode Active*\nKripya IP address bhejein:", parse_mode='Markdown')
        return
    elif data == "qs_telegram":
        context.user_data['mode'] = 'telegram_auto_detect'
        await query.message.reply_text("✈️ *Telegram Lookup Mode Active*\nKripya Telegram ID ya Username bhejein:", parse_mode='Markdown')
        return
    elif data == "qs_custom":
        context.user_data['mode'] = 'custom_api_phone'
        await query.message.reply_text("🔎 *Custom API Mode Active*\nQuery enter karein:", parse_mode='Markdown')
        return

    # Profile Inline Button Handlers
    if data == "profile_refresh":
        await show_user_profile(update, context, user.id, is_callback=True)
        return
    elif data == "profile_stats":
        user_db = db_get_one("SELECT * FROM users WHERE user_id = ?", (user.id,))
        searches = user_db.get('searches', 0) if user_db else 0
        credits = user_db.get('credits', 0) if user_db else 0
        joined = user_db.get('joined_date', 'N/A') if user_db else 'N/A'
        if joined and len(str(joined)) >= 10: joined = str(joined)[:10]
        referrals = db_get_all("SELECT COUNT(*) as cnt FROM users WHERE referred_by = ?", (user.id,))
        ref_count = referrals[0]['cnt'] if referrals else 0
        
        stats_text = f"📊 **MY STATISTICS**\n\n🔍 **Total Searches:** `{searches}`\n💎 **Current Credits:** `{credits}`\n🎁 **Total Referrals:** `{ref_count}`\n📅 **Account Created:** `{joined}`"
        kb = [[InlineKeyboardButton("🔙 Back to Profile", callback_data="profile_refresh")]]
        await query.edit_message_text(stats_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
        return
    elif data == "profile_history":
        searches = db_get_all("SELECT phone, timestamp FROM searches WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5", (user.id,))
        hist_text = "📜 **RECENT SEARCH HISTORY**\n\n"
        if not searches:
            hist_text += "Aapne abhi tak koi search nahi ki hai."
        else:
            for idx, s in enumerate(searches, 1):
                hist_text += f"{idx}. Target: `{s['phone']}` | ⏰ `{s['timestamp']}`\n"
        kb = [[InlineKeyboardButton("🔙 Back to Profile", callback_data="profile_refresh")]]
        await query.edit_message_text(hist_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
        return
    elif data == "profile_referral":
        bot_uname = BOT_USERNAME.replace('@', '')
        ref_link = f"https://t.me/{bot_uname}?start={user.id}"
        reward_setting = db_get_one("SELECT value FROM settings WHERE key='ref_reward_credits'")
        ref_reward = reward_setting['value'] if reward_setting else "2"
        ref_text = f"💰 **REFER & EARN FREE CREDITS**\n\nHar naye user ke join par `{ref_reward} Credits` milenge!\n\n🔗 **Aapka Link:**\n`{ref_link}`"
        kb = [[InlineKeyboardButton("🔙 Back to Profile", callback_data="profile_refresh")]]
        await query.edit_message_text(ref_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
        return
    elif data == "profile_buy":
        upi_record = db_get_one("SELECT value FROM settings WHERE key='upi_id'")
        upi_id = upi_record['value'] if upi_record else "harshhacker@upi"
        plans = db_get_all("SELECT * FROM plans")
        buy_text = f"💎 **BUY PREMIUM & ADD CREDITS**\n\n📲 **Admin UPI:** `{upi_id}`\n\n📦 **Plans:**\n"
        for p in plans:
            buy_text += f"• {p['name']} — {p['price']} ({p['credits']} Credits)\n"
        kb = [[InlineKeyboardButton("🔙 Back to Profile", callback_data="profile_refresh")]]
        await query.edit_message_text(buy_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
        return
    elif data == "profile_menu":
        await query.message.delete()
        await send_welcome_menu(update, context, user)
        return

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
        await context.bot.send_message(chat_id=query.from_user.id, text="🤖 **BOT CLONE SETUP**\nBot Token bhejein:", parse_mode='Markdown')
        return

    if not is_admin_user(query.from_user.id):
        return

    if data == "admin_create_notif":
        context.user_data['waiting_for_notif_title'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="📢 **CREATE NOTIFICATION**\nNayi notification ka **Title** enter karein:", parse_mode='Markdown')
        return
    elif data == "admin_notif_analytics":
        total_users_count = db_get_one("SELECT COUNT(*) as cnt FROM users")['cnt'] or 1
        total_notifs_sent = db_get_one("SELECT COUNT(*) as cnt FROM notifications")['cnt'] or 0
        total_delivered = db_get_one("SELECT COUNT(*) as cnt FROM user_notifications")['cnt'] or 0
        total_read = db_get_one("SELECT COUNT(*) as cnt FROM user_notifications WHERE is_read = 1")['cnt'] or 0
        read_pct = round((total_read / total_delivered * 100), 2) if total_delivered > 0 else 0.0

        analytics_text = f"📊 **NOTIFICATION ANALYTICS**\n\n"
        analytics_text += f"• **Total Sent (Campaigns):** `{total_notifs_sent}`\n"
        analytics_text += f"• **Total Delivered:** `{total_delivered}`\n"
        analytics_text += f"• **Read:** `{total_read}`\n"
        analytics_text += f"• **Unread:** `{total_delivered - total_read}`\n"
        analytics_text += f"• **Read Percentage:** `{read_pct}%`"

        kb = [[InlineKeyboardButton("🔙 Back to Panel", callback_data="admin_panel")]]
        await query.edit_message_text(analytics_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
        return

    if data == "admin_panel":
        await show_full_admin_panel(update, context)
        return
    elif data == "admin_welcome_prompt":
        context.user_data['waiting_for_welcome_msg'] = True
        curr_msg = db_get_one("SELECT value FROM settings WHERE key='welcome_msg'")['value']
        await context.bot.send_message(chat_id=query.from_user.id, text=f"💬 **Current Welcome Message:**\n\n`{curr_msg}`\n\nAb naya welcome message template bhejein:", parse_mode='Markdown')
        return
    elif data == "admin_setupi_prompt":
        context.user_data['waiting_for_upi'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="💳 **Set Admin UPI ID & QR Code**\nNayi UPI ID text mein bhejein, ya phir payment **QR Code ka photo** bhejein:", parse_mode='Markdown')
        return
    elif data == "admin_ban_prompt":
        context.user_data['waiting_for_ban_id'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="🔨 **Ban User**\nJis user ko ban karna hai uski numeric **User ID** bhejein:", parse_mode='Markdown')
        return
    elif data == "admin_unban_prompt":
        context.user_data['waiting_for_unban_id'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="🔓 **Unban User**\nJis user ko unban karna hai uski numeric **User ID** bhejein:", parse_mode='Markdown')
        return
    elif data == "admin_redeem_prompt":
        context.user_data['waiting_for_redeem_gen'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="🔑 **Generate Redeem Key**\nFormat bhejein: `KEY_NAME CREDITS` (jaise: `VIP50 50`)", parse_mode='Markdown')
        return
    elif data == "admin_plans":
        plans = db_get_all("SELECT * FROM plans")
        text = "📦 *SUBSCRIPTION PLANS MANAGER*\n━━━━━━━━━━━━━━━━━━━━\n"
        keyboard = []
        for p in plans:
            text += f"• **{p['name']}** — `{p['price']}` ({p['credits']} Credits)\n"
            keyboard.append([InlineKeyboardButton(f"🗑️ Delete: {p['name']}", callback_data=f"del_plan_{p['id']}")])
        keyboard.append([InlineKeyboardButton("➕ Add New Plan", callback_data="admin_add_plan_prompt")])
        keyboard.append([InlineKeyboardButton("🔵 📊 Back to Panel", callback_data="admin_panel")])
        try: await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except: await query.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return
    elif data == "admin_add_plan_prompt":
        context.user_data['waiting_for_plan_name'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="📦 **Add New Plan**\nPlan ka naam enter karein (jaise: `Ultra Pack`):", parse_mode='Markdown')
        return
    elif data.startswith("del_plan_"):
        plan_id = int(data.split("_")[-1])
        db_execute("DELETE FROM plans WHERE id = ?", (plan_id,), commit=True)
        await query.answer("🗑️ Plan successfully delete ho gaya!", show_alert=True)
        plans = db_get_all("SELECT * FROM plans")
        text = "📦 *SUBSCRIPTION PLANS MANAGER*\n━━━━━━━━━━━━━━━━━━━━\n"
        keyboard = []
        for p in plans:
            text += f"• **{p['name']}** — `{p['price']}` ({p['credits']} Credits)\n"
            keyboard.append([InlineKeyboardButton(f"🗑️ Delete: {p['name']}", callback_data=f"del_plan_{p['id']}")])
        keyboard.append([InlineKeyboardButton("➕ Add New Plan", callback_data="admin_add_plan_prompt")])
        keyboard.append([InlineKeyboardButton("🔵 📊 Back to Panel", callback_data="admin_panel")])
        try: await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except: pass
        return
    elif data == "admin_addcredit_prompt":
        context.user_data['waiting_for_add_credits_id'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="💎 **Add Credits**\nUser ki numeric **User ID** bhejein:", parse_mode='Markdown')
        return
    elif data == "admin_banner_prompt":
        context.user_data['waiting_for_banner'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="🖼️ **Set Welcome Banner**\nKripya koi bhi Photo, GIF ya Video bhejein:", parse_mode='Markdown')
        return
    elif data == "admin_addsub_prompt":
        context.user_data['waiting_for_add_sub'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="🛡️ **Add Sub-Admin**\nJise Sub-Admin banana hai uski **User ID** bhejein:", parse_mode='Markdown')
        return
    elif data == "admin_dynamic_apis":
        apis = db_get_all("SELECT * FROM dynamic_apis")
        text = "🌐 *DYNAMIC API MANAGER*\n━━━━━━━━━━━━━━━━━━━━\n"
        keyboard = []
        for ap in apis:
            text += f"• **{ap['api_name']}** (`{ap['api_key']}`)\n  `{ap['api_url']}`\n\n"
            keyboard.append([
                InlineKeyboardButton(f"🔗 URL: {ap['api_name']}", callback_data=f"edit_api_url_{ap['api_key']}"),
                InlineKeyboardButton(f"✍️ Old/New", callback_data=f"edit_api_wm_{ap['api_key']}")
            ])
        keyboard.append([InlineKeyboardButton("🔵 📊 Back to Panel", callback_data="admin_panel")])
        try: await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except: await query.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return
    elif data == "admin_add_api":
        context.user_data['waiting_for_new_api_key'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="🔌 *ADD NEW API*\nUnique **API Key** enter karein (bina space ke):", parse_mode='Markdown')
        return
    elif data == "admin_delete_api":
        context.user_data['waiting_for_delete_api_key'] = True
        apis = db_get_all("SELECT api_key, api_name FROM dynamic_apis")
        api_list_str = "\n".join([f"• `{ap['api_name']}` (Key: `{ap['api_key']}`)" for ap in apis])
        await context.bot.send_message(chat_id=query.from_user.id, text=f"🗑️ **DELETE API**\n\n{api_list_str}\n\nJise delete karna hai uska **API Key** ya **Name** bhejein:", parse_mode='Markdown')
        return
    elif data == "admin_edit_name":
        context.user_data['waiting_for_edit_name_key'] = True
        apis = db_get_all("SELECT api_key, api_name FROM dynamic_apis")
        api_list_str = "\n".join([f"• `{ap['api_name']}` (Key: `{ap['api_key']}`)" for ap in apis])
        await context.bot.send_message(chat_id=query.from_user.id, text=f"✏️ **EDIT BUTTON NAME**\n\n{api_list_str}\n\nJiska name change karna hai uska **API Key** bhejein:", parse_mode='Markdown')
        return
    elif data == "admin_users":
        users = db_get_all("SELECT * FROM users ORDER BY joined_date DESC LIMIT 10")
        text = "👥 **ADMIN PANEL: USERS & SEARCH LOGS**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for u in users:
            uid = u['user_id']
            name = u['first_name'] or 'Unknown'
            uname = "@" + u['username'] if u['username'] and u['username'] != 'NoUsername' else 'NoUsername'
            phone = u['phone_number'] or 'Not Verified'
            credits = u['credits']
            
            user_searches = db_get_all("SELECT phone, timestamp FROM searches WHERE user_id = ? ORDER BY timestamp DESC LIMIT 3", (uid,))
            searches_str = ", ".join([f"{s['phone']}" for s in user_searches]) if user_searches else "None"
            
            text += f"👤 **Name:** {name} ({uname})\n"
            text += f"🆔 **ID:** `{uid}` | 📱 **Ph:** `{phone}` | 💎 **Cr:** `{credits}`\n"
            text += f"🔍 **Recent Searches:** `{searches_str}`\n"
            text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Panel", callback_data="admin_panel")]]
        try: await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except: await query.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return
    elif data == "admin_view_logs":
        logs = db_get_all("SELECT * FROM logs ORDER BY id DESC LIMIT 15")
        text = "📜 *SYSTEM LOGS*\n━━━━━━━━━━━━━━━━━━━━\n"
        for l in logs:
            text += f"• UID: `{l['user_id']}` | {l['action']} (`{l['timestamp']}`)\n"
        keyboard = [[InlineKeyboardButton("🔵 📊 Back", callback_data="admin_panel")]]
        try: await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except: await query.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return
    elif data == "admin_download_logs":
        await download_search_logs_file(update, context)
        return
    elif data == "toggle_maintenance":
        current = db_get_one("SELECT value FROM settings WHERE key='maintenance'")['value']
        new_val = 'off' if current == 'on' else 'on'
        db_execute("UPDATE settings SET value = ? WHERE key = 'maintenance'", (new_val,), commit=True)
        await query.answer(f"✅ Maintenance is now {new_val.upper()}!", show_alert=True)
        await show_full_admin_panel(update, context)
        return
    elif data == "close_panel":
        try: await query.message.delete()
        except: pass
        return

async def download_search_logs_file(update, context):
    user = update.effective_user
    if not is_admin_user(user.id): return
    try:
        searches = db_get_all("SELECT s.user_id, u.first_name, s.phone, s.response, s.timestamp FROM searches s LEFT JOIN users u ON s.user_id = u.user_id ORDER BY s.timestamp DESC")
        file_content = "=========================================\n"
        file_content += "      USER SEARCH HISTORY & RESULTS\n"
        file_content += "=========================================\n\n"
        for idx, s in enumerate(searches, 1):
            file_content += f"--- SEARCH RECORD #{idx} ---\nUser ID: {s['user_id']}\nName: {s['first_name'] or 'Unknown'}\nQuery Target: {s['phone']}\nTimestamp: {s['timestamp']}\nResponse:\n{s['response']}\n\n-----------------------------------------\n\n"
        
        file_name = "record.txt"
        with open(file_name, "w", encoding="utf-8") as f: f.write(file_content)
        with open(file_name, "rb") as f:
            if hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.message.reply_document(document=InputFile(f, filename=file_name), caption="📂 Search History (`record.txt`)", parse_mode='Markdown')
        os.remove(file_name)
        log_activity(user.id, "Exported user search history as record.txt")
    except Exception as e:
        if hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.message.reply_text(f"❌ Error: {str(e)}")

# ============================================
# ADMIN COMMANDS
# ============================================
async def setupi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args: return
    db_execute("UPDATE settings SET value = ? WHERE key = 'upi_id'", (context.args[0],), commit=True)
    await update.message.reply_text("✅ UPI updated.", parse_mode='Markdown')

async def maint_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin_user(update.effective_user.id): return
    if not context.args: return
    db_execute("UPDATE settings SET value = ? WHERE key = 'maintenance'", (context.args[0].lower(),), commit=True)
    await update.message.reply_text("✅ Maintenance updated.", parse_mode='Markdown')

async def addcredits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin_user(update.effective_user.id): return
    if len(context.args) < 2: return
    db_execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (int(context.args[1]), int(context.args[0])), commit=True)
    await update.message.reply_text("✅ Credits added.", parse_mode='Markdown')

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin_user(update.effective_user.id): return
    users = db_get_all("SELECT user_id FROM users")
    sent = 0
    for u in users:
        try:
            await context.bot.send_message(chat_id=u['user_id'], text="📢 *ANNOUNCEMENT*\n\n" + ' '.join(context.args), parse_mode='Markdown')
            sent += 1
        except: pass
    await update.message.reply_text(f"📢 Broadcast sent to {sent} users.")

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    print("🚀 HARSH OSINT BOT STARTING (NOTIFICATION CENTER, UI SETTINGS & ALL FEATURES)...")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("search", quick_search_command))
    application.add_handler(CommandHandler("notifications", notif_command))
    application.add_handler(CommandHandler("support", support_command))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("redeem", redeem_command))
    application.add_handler(CommandHandler("daily", daily_command))
    application.add_handler(CommandHandler("ref", ref_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("export", export_command))
    application.add_handler(CommandHandler("setupi", setupi_command))
    application.add_handler(CommandHandler("maint", maint_command))
    application.add_handler(CommandHandler("addcredits", addcredits_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.Document.ALL, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == '__main__':
    main()
