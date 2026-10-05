#!/usr/init/env python3
# OSINT & Pincode Bot - Ultimate 10 Report Styles & Fully Fixed Admin Edition
"""
Developer: @Harsx1618
Description: Advanced Telegram OSINT Bot with 10 Hacker/JSON/Cyber Report Styles, Fixed Admin Panel & All Features Intact
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
            return {"status": False, "error": "API status " + str(response.status_code)}
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
# LONG & SLEEK PROGRESS BAR ANIMATION
# ============================================
async def show_smooth_progress_animation(msg_obj, target_str, title_type="PHONE"):
    if title_type == "PINCODE":
        title = "📍 PINCODE INTELLIGENCE BREACH"
    elif title_type == "TG":
        title = "🕵️‍♂️ TELEGRAM INTEL BREACH"
    elif title_type == "IP":
        title = "🌐 IP INTELLIGENCE BREACH"
    elif title_type == "AADHAAR":
        title = "🆔 AADHAAR INTELLIGENCE BREACH"
    else:
        title = "💻 SYSTEM BREACH IN PROGRESS"

    steps = [
        ("--- -- -- -- -- -- -- -- -- --", "10%"),
        ("=== --- -- -- -- -- -- -- -- --", "30%"),
        ("=== === === -- -- -- -- -- -- --", "50%"),
        ("=== === === === === -- -- -- --", "70%"),
        ("=== === === === === === === -- --", "90%"),
        ("=== === === === === === === === ===", "100%")
    ]

    for bar, pct in steps:
        try:
            await msg_obj.edit_text(
                f"{title}\nTarget: `{target_str}`\n\n⚡ COLLECTING INFO...\n`{bar} {pct}`",
                parse_mode='Markdown'
            )
            await asyncio.sleep(0.15)
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
# 10 UNIQUE REPORT STYLES FORMATTER (NO OWNER/CREDIT)
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
        json_output = {
            "status": True,
            "target": str(phone),
            "total_records": total,
            "current_page": page + 1,
            "total_pages": total_pages,
            "records": chunk
        }
        text = "```json\n" + json.dumps(json_output, indent=2, ensure_ascii=False) + "\n```"

    elif r_style == 'hacker':
        text = f"💀 [ ROOT ACCESS GRANTED ] 💀\n"
        text += f"🎯 TARGET_IP/NUM: `{phone}`\n"
        text += f"📊 PACKETS: {total} | PAGE: {page + 1}/{total_pages}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for idx, rec in enumerate(chunk, start=start_idx + 1):
            text += f"⚡ [TARGET #{idx}] ⚡\n"
            text += f"• IDENT: `{rec['name']}`\n"
            text += f"• PARENT: `{rec['father']}`\n"
            text += f"• COMMS: `{rec['mobile']}` | `{rec['alt_num']}`\n"
            text += f"• NODE: `{rec['circle']}`\n"
            text += f"• MAIL: `{rec['email']}`\n"
            text += f"• REG_ID: `{rec['caf_id']}`\n"
            text += f"• LOC: `{rec['address']}`\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

    elif r_style == 'matrix':
        text = f"🟩 010101 MATRIX INTEL 010101 🟩\n"
        text += f"Target: `{phone}` | Page: {page + 1}/{total_pages}\n════════════════════════════════\n\n"
        for idx, rec in enumerate(chunk, start=start_idx + 1):
            text += f"🟢 MATRIX_REC_{idx}:\n"
            text += f"├ Name: `{rec['name']}`\n"
            text += f"├ Mobile: `{rec['mobile']}`\n"
            text += f"├ Circle: `{rec['circle']}`\n"
            text += f"└ Addr: `{rec['address']}`\n\n"

    elif r_style == 'cyber':
        text = f"🌐 𝕮𝕴𝕭𝕰𝕽 𝕴𝕹𝕿𝕰𝕃𝕃𝕴𝕲𝕰𝕹𝕮𝕰 🌐\n"
        text += f"🎯 Target: `{phone}`\n"
        text += f"📊 Records: {total} | Page: {page + 1}/{total_pages}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for idx, rec in enumerate(chunk, start=start_idx + 1):
            text += f"🔹 **CYBER_NODE #{idx}**\n"
            text += f"👤 Subject: `{rec['name']}`\n"
            text += f"👨‍👧 Guardian: `{rec['father']}`\n"
            text += f"📱 Phone: `{rec['mobile']}`\n"
            text += f"📞 Alt: `{rec['alt_num']}`\n"
            text += f"📡 Telecom: `{rec['circle']}`\n"
            text += f"📧 Mail: `{rec['email']}`\n"
            text += f"🆔 UID: `{rec['caf_id']}`\n"
            text += f"🏠 Sector:\n`{rec['address']}`\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

    elif r_style == 'neon':
        text = f"🟣 🪩 NEON GLOW INTEL 🪩 🟣\n"
        text += f"🎯 Target: `{phone}` (Page {page + 1}/{total_pages})\n──────────────────────────────\n\n"
        for idx, rec in enumerate(chunk, start=start_idx + 1):
            text += f"✨ **[RECORD {idx}]**\n"
            text += f"👤 `[NAME]` : {rec['name']}\n"
            text += f"📱 `[CELL]` : {rec['mobile']}\n"
            text += f"🌐 `[AREA]` : {rec['circle']}\n"
            text += f"🏠 `[HOME]` : {rec['address']}\n\n──────────────────────────────\n"

    elif r_style == 'card':
        text = f"🪪 **VIP CARD INTELLIGENCE REPORT**\n"
        text += f"🎯 Target Number: `{phone}`\n"
        text += f"📊 Records: {total} | Page: {page + 1}/{total_pages}\n════════════════════════\n\n"
        for idx, rec in enumerate(chunk, start=start_idx + 1):
            text += f"┌ 👑 **IDENTITY CARD #{idx}**\n"
            text += f"├ 👤 **Name:** `{rec['name']}`\n"
            text += f"├ 👨‍👧 **Father:** `{rec['father']}`\n"
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

    elif r_style == 'vip':
        text = f"⭐ 👑 **VIP EXCLUSIVE OSINT REPORT** 👑 ⭐\n"
        text += f"🎯 Target: `{phone}` | Page: {page + 1}/{total_pages}\n──────────────────────────────\n\n"
        for idx, rec in enumerate(chunk, start=start_idx + 1):
            text += f"🌟 **VIP PROFILE #{idx}**\n"
            text += f"• Full Name : **{rec['name']}**\n"
            text += f"• Father    : **{rec['father']}**\n"
            text += f"• Contact   : `{rec['mobile']}`\n"
            text += f"• Region    : {rec['circle']}\n"
            text += f"• Location  : _{rec['address']}_\n\n──────────────────────────────\n"

    else:  # Standard
        text = f"📱 **NUMBER INTELLIGENCE REPORT**\n"
        text += f"🎯 Target: `{phone}`\n"
        text += f"📊 Total Records: {total} | Page: {page + 1}/{total_pages}\n━━━━━━━━━━━━━━━━━━━━\n\n"
        for idx, rec in enumerate(chunk, start=start_idx + 1):
            text += f"🔹 **RECORD #{idx}**\n"
            text += f"👤 Name: `{rec['name']}`\n"
            text += f"👨‍👧 Father: `{rec['father']}`\n"
            text += f"📱 Mobile: `{rec['mobile']}`\n"
            text += f"📞 Alt Num: `{rec['alt_num']}`\n"
            text += f"🌐 Circle: `{rec['circle']}`\n"
            text += f"📧 Email: `{rec['email']}`\n"
            text += f"🆔 CAF / ID: `{rec['caf_id']}`\n"
            text += f"🏠 Address:\n`{rec['address']}`\n\n━━━━━━━━━━━━━━━━━━━━\n"

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

# ============================================
# COMMAND HANDLERS
# ============================================
async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    support_text = "💬 *IF YOU FACE ANY ISSUES CONTACT OUR ADMIN*\n\n📲 **Support Available**\n\nKisi bhi madad ke liye contact karein!"
    support_keyboard = [[InlineKeyboardButton("💬 Chat with Support Owner", url="https://t.me/" + OWNER_USERNAME.replace('@', ''))]]
    await update.message.reply_text(support_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(support_keyboard))

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_info = db_get_one("SELECT credits FROM users WHERE user_id = ?", (user.id,))
    credits = user_info['credits'] if user_info else 0
    await update.message.reply_text("💰 *Aapka Current Balance:*\n\n💎 Remaining Credits: `" + str(credits) + " Credits`", parse_mode='Markdown')

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    report_style_setting = db_get_one("SELECT value FROM settings WHERE key='report_style'")
    r_style = report_style_setting['value'] if report_style_setting else 'cyber'
    await update.message.reply_text(f"🎨 **Current Report Style:** `{r_style.upper()}`\n\nAap admin panel se isey change kar sakte hain.", parse_mode='Markdown')

async def daily_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    today_str = datetime.now().strftime("%Y-%m-%d")
    user_db = db_get_one("SELECT last_daily FROM users WHERE user_id = ?", (user.id,))
    if user_db and user_db.get('last_daily') == today_str:
        await update.message.reply_text("⏳ Aapne aaj ka daily bonus pehle hi claim kar liya hai! Kal wapas koshish karein.")
        return
    db_execute("UPDATE users SET credits = credits + 2, last_daily = ? WHERE user_id = ?", (today_str, user.id), commit=True)
    await update.message.reply_text("🎁 **Daily Bonus Claimed!** Aapke account mein `2` credits add kar diye gaye hain.")

async def ref_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    reward_setting = db_get_one("SELECT value FROM settings WHERE key='ref_reward_credits'")
    ref_reward = reward_setting['value'] if reward_setting else "2"
    ref_link = f"https://t.me/{BOT_USERNAME.replace('@', '')}?start={user.id}"
    text = f"🔗 **REFER & EARN PROGRAM**\n\nApne dosto ko yeh link share karein aur har ek join par `{ref_reward}` free credits payein!\n\n👇 **Aapka Referral Link:**\n`{ref_link}`"
    await update.message.reply_text(text, parse_mode='Markdown')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_info = db_get_one("SELECT credits, searches, joined_date FROM users WHERE user_id = ?", (user.id,))
    if not user_info:
        await update.message.reply_text("❌ Aapka account database mein nahi mila. Kripya /start dabayein.")
        return
    status = "👑 Admin / Unlimited" if (is_admin_user(user.id) or user_info['credits'] > 5000) else ("💎 Premium User" if user_info['credits'] > 10 else "🆓 Free User")
    text = f"📊 **YOUR ACCOUNT STATUS**\n\n👤 Name: {user.first_name}\n🏷️ Status: `{status}`\n💎 Credits: `{user_info['credits']}`\n🔍 Total Searches: `{user_info['searches']}`\n📅 Joined: `{user_info['joined_date']}`"
    await update.message.reply_text(text, parse_mode='Markdown')

async def redeem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Kripya coupon code bhi likhein. Example: `/redeem YOURCODE`", parse_mode='Markdown')
        return
    code = context.args[0].strip()
    coupon = db_get_one("SELECT * FROM coupons WHERE code = ?", (code,))
    if not coupon:
        await update.message.reply_text("❌ Yeh coupon code galat ya expired hai.")
        return
    credits_to_add = coupon['credits']
    user = update.effective_user
    db_execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (credits_to_add, user.id), commit=True)
    db_execute("DELETE FROM coupons WHERE code = ?", (code,), commit=True)
    await update.message.reply_text(f"🎉 **Coupon Redeemed Successfully!** Aapke account mein `{credits_to_add}` credits add kar diye gaye hain.", parse_mode='Markdown')

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    searches = db_get_all("SELECT phone, timestamp FROM searches WHERE user_id = ? ORDER BY id DESC LIMIT 5", (user.id,))
    if not searches:
        await update.message.reply_text("📜 Aapne abhi tak koi search nahi kiya hai.")
        return
    text = "📜 **YOUR RECENT SEARCH HISTORY**\n━━━━━━━━━━━━━━━━━━━━\n"
    for idx, s in enumerate(searches, 1):
        text += f"{idx}. Target: `{s['phone']}` — 🕒 `{s['timestamp']}`\n"
    await update.message.reply_text(text, parse_mode='Markdown')

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

async def send_welcome_menu(update_or_query, context, user):
    user_info = db_get_one("SELECT credits FROM users WHERE user_id = ?", (user.id,))
    credits = user_info['credits'] if user_info else 0
    
    welcome = "\n👋 *Welcome to OSINT & Pincode Lookup Bot!*\n\n💎 Remaining Credits: `" + str(credits) + "`\nNeeche diye gaye menu se option select karein!\n🎁 *Daily Bonus:* `/daily`\n🔗 *Referral Link:* `/ref`\n📜 *Search History:* `/history`\n\n🚀 *Secure System Online*\n    "
    
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
            if "🔤 TG TO NUMBER" not in api_button_names:
                api_button_names.append("🔤 TG TO NUMBER")
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
        if banner_type == 'animation' and banner_media:
            await context.bot.send_animation(chat_id=chat_id, animation=banner_media, caption=welcome, parse_mode='Markdown', reply_markup=reply_markup)
            return
        elif banner_type == 'photo' and banner_media:
            await context.bot.send_photo(chat_id=chat_id, photo=banner_media, caption=welcome, parse_mode='Markdown', reply_markup=reply_markup)
            return
        elif banner_type == 'video' and banner_media:
            await context.bot.send_video(chat_id=chat_id, video=banner_media, caption=welcome, parse_mode='Markdown', reply_markup=reply_markup)
            return
    except: pass 

    if hasattr(update_or_query, 'message') and update_or_query.message:
        await update_or_query.message.reply_text(welcome, parse_mode='Markdown', reply_markup=reply_markup)

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    contact = update.message.contact
    if contact and contact.user_id == user.id:
        db_execute("UPDATE users SET phone_number = ?, username = ? WHERE user_id = ?", (contact.phone_number, user.username or "NoUsername", user.id), commit=True)
        await update.message.reply_text("✅ *Verification Successful!*", parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
        await send_welcome_menu(update, context, user)
    else:
        await update.message.reply_text("❌ Kripya apna khud ka contact share karein.", reply_markup=ReplyKeyboardRemove())

async def show_premium_plans(update, context):
    upi_record = db_get_one("SELECT value FROM settings WHERE key='upi_id'")
    upi_qr = db_get_one("SELECT value FROM settings WHERE key='upi_qr'")
    upi_id = upi_record['value'] if upi_record else "harshhacker@upi"
    qr_file_id = upi_qr['value'] if upi_qr else ""
    
    plans = db_get_all("SELECT * FROM plans")
    text = f"💎 **BUY PREMIUM & ADD CREDITS**\n━━━━━━━━━━━━━━━━━━━━━━\n📲 **Admin UPI ID:** `{upi_id}`\n\n📦 **Available Plans:**\n"
    for p in plans:
        text += f"• **{p['name']}** — `{p['price']}` for **{p['credits']} Credits**\n"
    
    if hasattr(update, 'message') and update.message:
        if qr_file_id:
            await update.message.reply_photo(photo=qr_file_id, caption=text, parse_mode='Markdown')
        else:
            await update.message.reply_text(text, parse_mode='Markdown')
    elif hasattr(update, 'callback_query') and update.callback_query:
        if qr_file_id:
            await update.callback_query.message.reply_photo(photo=qr_file_id, caption=text, parse_mode='Markdown')
        else:
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
        await update.message.reply_text(f"❌ **Aapke credits khatam ho chuke hain!**\n\nKripya UPI ID: `{upi_record['value'] if upi_record else 'harshhacker@upi'}` par payment karein.", parse_mode='Markdown')
        return False
    return True

# ============================================
# MESSAGE HANDLER
# ============================================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    active_live_users.add(user.id)
    
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
            elif update.message.document:
                media_id = update.message.document.file_id
                media_type = "animation" if update.message.document.mime_type and "gif" in update.message.document.mime_type.lower() else "photo"

            if media_id:
                db_execute("UPDATE settings SET value = ? WHERE key = 'banner_media'", (media_id,), commit=True)
                db_execute("UPDATE settings SET value = ? WHERE key = 'banner_type'", (media_type,), commit=True)
                context.user_data['waiting_for_banner'] = False
                await update.message.reply_text("✅ Success! Naya banner media successfully set ho chuka hai.", parse_mode='Markdown')
                return
            else:
                await update.message.reply_text("❌ Kripya gallery se koi valid GIF, Video ya Photo bhejein.")
                return

        if context.user_data.get('waiting_for_upi_qr'):
            if update.message.photo:
                qr_id = update.message.photo[-1].file_id
                db_execute("UPDATE settings SET value = ? WHERE key = 'upi_qr'", (qr_id,), commit=True)
                context.user_data['waiting_for_upi_qr'] = False
                await update.message.reply_text("✅ Success! UPI QR Code successfully set ho chuka hai.", parse_mode='Markdown')
                return
            else:
                await update.message.reply_text("❌ Kripya UPI QR Code ki ek valid photo bhejein.")
                return

        text = update.message.text.strip() if update.message.text else ""

        if context.user_data.get('waiting_for_maint_msg'):
            db_execute("UPDATE settings SET value = ? WHERE key = 'maint_msg'", (text,), commit=True)
            context.user_data['waiting_for_maint_msg'] = False
            await update.message.reply_text(f"✅ Maintenance message updated to:\n`{text}`", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_upi'):
            db_execute("UPDATE settings SET value = ? WHERE key = 'upi_id'", (text,), commit=True)
            context.user_data['waiting_for_upi'] = False
            await update.message.reply_text(f"✅ UPI ID successfully updated to: `{text}`", parse_mode='Markdown')
            return

        if context.user_data.get('waiting_for_add_sub'):
            if text.isdigit():
                db_execute("INSERT OR IGNORE INTO sub_admins (user_id) VALUES (?)", (int(text),), commit=True)
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

    # Check Maintenance
    maint = db_get_one("SELECT value FROM settings WHERE key='maintenance'")['value']
    if maint == 'on' and not is_admin_user(user.id):
        await update.message.reply_text("🚧 " + db_get_one("SELECT value FROM settings WHERE key='maint_msg'")['value'], parse_mode='Markdown')
        return

    text = update.message.text.strip() if update.message.text else ""
    clean_input_text = text
    for prefix in ["🔍 ", "📍 ", "🌐 ", "🆔 ", "🔤 ", "🔮 "]:
        clean_input_text = clean_input_text.replace(prefix, "")
    
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
        elif api_k in ['tg_username', 'tg_userid'] or "TG TO NUMBER" in text.upper():
            tg_keyboard = [[KeyboardButton("👤 Telegram to Username"), KeyboardButton("🆔 Telegram to UserID")], [KeyboardButton("🔙 Back to Main Menu")]]
            await update.message.reply_text("🔤 *TG SUB-MENU*\nOption select karein:", parse_mode='Markdown', reply_markup=ReplyKeyboardMarkup(tg_keyboard, resize_keyboard=True))
            return
        else:
            context.user_data['mode'] = f"custom_api_{api_k}"
            await update.message.reply_text(f"🔍 *{matched_api['api_name']} Mode Active*\nQuery enter karein:", parse_mode='Markdown')
            return

    if text == "👤 Telegram to Username":
        context.user_data['mode'] = 'tg_username'
        await update.message.reply_text("👤 *Telegram Username Mode Active*\nUsername bhejein:", parse_mode='Markdown')
        return
    elif text == "🆔 Telegram to UserID":
        context.user_data['mode'] = 'tg_userid'
        await update.message.reply_text("🆔 *Telegram UserID Mode Active*\nNumeric UserID bhejein:", parse_mode='Markdown')
        return
    elif text == "🔤 TG TO NUMBER":
        tg_keyboard = [[KeyboardButton("👤 Telegram to Username"), KeyboardButton("🆔 Telegram to UserID")], [KeyboardButton("🔙 Back to Main Menu")]]
        await update.message.reply_text("🔤 *TG SUB-MENU*\nOption select karein:", parse_mode='Markdown', reply_markup=ReplyKeyboardMarkup(tg_keyboard, resize_keyboard=True))
        return
    elif text == "💎 MY PREMIUM STATUS":
        user_info = db_get_one("SELECT credits FROM users WHERE user_id = ?", (user.id,))
        credits = user_info['credits'] if user_info else 0
        status = "👑 Admin / Unlimited" if (is_admin_user(user.id) or credits > 5000) else ("💎 Premium User" if credits > 10 else "🆓 Free User")
        await update.message.reply_text(f"👤 *Aapki Details:*\nStatus: `{status}`\nCredits: `{credits}`", parse_mode='Markdown')
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
        report_style_val = db_get_one("SELECT value FROM settings WHERE key='report_style'")['value']
        
        panel_text = f"\n📊 *ADVANCED ADMIN PANEL*\n━━━━━━━━━━━━━━━━━━\n👥 Total Users: `{total_users}`\n🔍 Total Lookups: `{total_searches}`\n💳 UPI: `{upi_record['value'] if upi_record else 'Not Set'}`\n🎨 Report Style: `{report_style_val.upper()}`\n🚧 Maintenance: `{maint.upper()}`\n🤖 Clone Refs: `{clone_ref_val}` (`{clone_toggle_val.upper()}`)\n🎁 Ref Reward: `{ref_reward_val} Credits`\n"
        keyboard = [
            [InlineKeyboardButton("🟢 👥 View Users", callback_data="admin_users"), InlineKeyboardButton("💳 ⚙ Set UPI ID", callback_data="admin_setupi_prompt")],
            [InlineKeyboardButton("📷 ⚙ Set UPI QR", callback_data="admin_setupi_qr_prompt")],
            [InlineKeyboardButton("📦 📋 Manage Plans", callback_data="admin_plans"), InlineKeyboardButton("💎 ➕ Add Credits", callback_data="admin_addcredit_prompt")],
            [InlineKeyboardButton("📈 ⚡ Live Analytics", callback_data="admin_live_analytics"), InlineKeyboardButton("🤖 👥 Clone Bots", callback_data="admin_clones")],
            [InlineKeyboardButton("🌐 🔌 Dynamic APIs", callback_data="admin_dynamic_apis"), InlineKeyboardButton("➕ 🔌 Add New API", callback_data="admin_add_api")],
            [InlineKeyboardButton("🗑️ 🔌 Delete API", callback_data="admin_delete_api"), InlineKeyboardButton("✏️ 📝 Edit Button Name", callback_data="admin_edit_name")],
            [InlineKeyboardButton("🎨 🔄 Change Report Style", callback_data="admin_toggle_style"), InlineKeyboardButton("🔄 Toggle Clone Ref", callback_data="admin_toggle_clone_ref")],
            [InlineKeyboardButton("👥 ⚙️ Set Clone Refs", callback_data="admin_cloneref_prompt"), InlineKeyboardButton("🎁 ⚙️ Set Ref Reward", callback_data="admin_refreward_prompt")],
            [InlineKeyboardButton("💬 ⚙️ Set Maint Msg", callback_data="admin_setmaintmsg_prompt"), InlineKeyboardButton("🖼️ ⚙️ Set Banner", callback_data="admin_banner_prompt")],
            [InlineKeyboardButton("🛡️ ➕ Add Sub-Admin", callback_data="admin_addsub_prompt"), InlineKeyboardButton("🛠️ 🔄 Maintenance", callback_data="toggle_maintenance")],
            [InlineKeyboardButton("🟢 🔍 Check API Status", callback_data="admin_check_api_status")],
            [InlineKeyboardButton("❌ 📦 Close", callback_data="close_panel")]
        ]
        await update.message.reply_text(panel_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    user_data = db_get_one("SELECT phone_number, is_banned FROM users WHERE user_id = ?", (user.id,))
    if not user_data or user_data['is_banned'] == 1:
        await update.message.reply_text("❌ Aapko bot use karne se block kar diya gaya hai.")
        return
    if not user_data.get('phone_number') or not user_data['phone_number']:
        contact_button = [[KeyboardButton("📱 Share Contact to Verify & Start", request_contact=True)]]
        await update.message.reply_text("⚠️ *SECURITY VERIFICATION REQUIRED*\nKripya contact verify karein!", parse_mode='Markdown', reply_markup=ReplyKeyboardMarkup(contact_button, one_time_keyboard=True, resize_keyboard=True))
        return

    if not await check_user_credit(update, user): return

    mode = context.user_data.get('mode', None)
    cleaned = re.sub(r'\D', '', text)

    # Universal Handler with Smooth Progress Animation and 10 Report Styles
    if mode and mode.startswith("custom_api_"):
        api_k = mode.replace("custom_api_", "")
        msg = await update.message.reply_text("⚡ COLLECTING INFO...\n`--- -- -- -- -- -- -- -- -- -- 10%`", parse_mode='Markdown')
        await show_smooth_progress_animation(msg, text, title_type="PHONE")
        data = await fetch_dynamic_api(api_k, text)
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, f"{api_k}:{text}", json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        
        recs, _ = parse_phone_records(data, text)
        if not recs: recs = [{"name": "Result", "mobile": text, "circle": "API", "address": str(data), "father": "N/A", "alt_num": "N/A", "caf_id": text}]
        await send_paginated_phone_response(msg, recs, text, update, context, page=0, is_edit=True)
        context.user_data['mode'] = None
        return

    if mode == 'aadhaar_info':
        msg = await update.message.reply_text("⚡ COLLECTING INFO...\n`--- -- -- -- -- -- -- -- -- -- 10%`", parse_mode='Markdown')
        await show_smooth_progress_animation(msg, text, title_type="AADHAAR")
        data = await fetch_dynamic_api('aadhaar_info', text)
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, "AADHAAR:" + text, json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        
        recs, _ = parse_phone_records(data, text)
        if not recs: recs = [{"name": "Aadhaar Result", "mobile": text, "circle": "India", "address": str(data), "father": "N/A", "alt_num": "N/A", "caf_id": text}]
        await send_paginated_phone_response(msg, recs, text, update, context, page=0, is_edit=True)
        context.user_data['mode'] = None
    elif mode == 'ip_info':
        msg = await update.message.reply_text("⚡ COLLECTING INFO...\n`--- -- -- -- -- -- -- -- -- -- 10%`", parse_mode='Markdown')
        await show_smooth_progress_animation(msg, text, title_type="IP")
        data = await fetch_dynamic_api('ip_info', text)
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, "IP:" + text, json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        
        recs, _ = parse_phone_records(data, text)
        if not recs: recs = [{"name": "IP Result", "mobile": text, "circle": "Internet", "address": str(data), "father": "N/A", "alt_num": "N/A", "caf_id": text}]
        await send_paginated_phone_response(msg, recs, text, update, context, page=0, is_edit=True)
        context.user_data['mode'] = None
    elif mode == 'tg_username':
        query_str = text if text.startswith('@') else '@' + text
        msg = await update.message.reply_text("⚡ COLLECTING INFO...\n`--- -- -- -- -- -- -- -- -- -- 10%`", parse_mode='Markdown')
        await show_smooth_progress_animation(msg, query_str, title_type="TG")
        data = await fetch_dynamic_api('tg_username', query_str)
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, "TG_USER:" + query_str, json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        
        recs, _ = parse_phone_records(data, query_str)
        if not recs: recs = [{"name": "TG User", "mobile": query_str, "circle": "Telegram", "address": str(data), "father": "N/A", "alt_num": "N/A", "caf_id": query_str}]
        await send_paginated_phone_response(msg, recs, query_str, update, context, page=0, is_edit=True)
        context.user_data['mode'] = None
    elif mode == 'tg_userid':
        msg = await update.message.reply_text("⚡ COLLECTING INFO...\n`--- -- -- -- -- -- -- -- -- -- 10%`", parse_mode='Markdown')
        await show_smooth_progress_animation(msg, cleaned, title_type="TG")
        data = await fetch_dynamic_api('tg_userid', cleaned)
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, "TG_ID:" + cleaned, json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        
        recs, _ = parse_phone_records(data, cleaned)
        if not recs: recs = [{"name": "TG ID", "mobile": cleaned, "circle": "Telegram", "address": str(data), "father": "N/A", "alt_num": "N/A", "caf_id": cleaned}]
        await send_paginated_phone_response(msg, recs, cleaned, update, context, page=0, is_edit=True)
        context.user_data['mode'] = None
    elif mode == 'pincode' or (len(cleaned) == 6 and len(text) == 6 and not mode):
        msg = await update.message.reply_text("⚡ COLLECTING INFO...\n`--- -- -- -- -- -- -- -- -- -- 10%`", parse_mode='Markdown')
        await show_smooth_progress_animation(msg, cleaned, title_type="PINCODE")
        data = await fetch_dynamic_api('pincode', cleaned)
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, "PIN:" + cleaned, json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        
        recs, _ = parse_phone_records(data, cleaned)
        if not recs: recs = [{"name": "Pincode Area", "mobile": cleaned, "circle": "Postal", "address": str(data), "father": "N/A", "alt_num": "N/A", "caf_id": cleaned}]
        await send_paginated_phone_response(msg, recs, cleaned, update, context, page=0, is_edit=True)
        context.user_data['mode'] = None
    elif mode == 'phone' or (10 <= len(cleaned) <= 15):
        msg = await update.message.reply_text("⚡ COLLECTING INFO...\n`--- -- -- -- -- -- -- -- -- -- 10%`", parse_mode='Markdown')
        await show_smooth_progress_animation(msg, cleaned, title_type="PHONE")
        data = await fetch_dynamic_api('phone', cleaned)
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, cleaned, json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        records, err = parse_phone_records(data, cleaned)
        if err: 
            await msg.edit_text(err)
        else: 
            context.user_data['last_phone_records'] = records
            context.user_data['last_phone_target'] = cleaned
            await send_paginated_phone_response(msg, records, cleaned, update, context, page=0, is_edit=True)
        context.user_data['mode'] = None
    else:
        await update.message.reply_text("❌ Kripya valid input enter karein.", parse_mode='Markdown')

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

    if data == "admin_panel":
        total_users = db_get_one("SELECT COUNT(*) as count FROM users")['count']
        total_searches = db_get_one("SELECT COUNT(*) as count FROM searches")['count']
        maint = db_get_one("SELECT value FROM settings WHERE key='maintenance'")['value']
        upi_record = db_get_one("SELECT value FROM settings WHERE key='upi_id'")
        clone_ref_val = db_get_one("SELECT value FROM settings WHERE key='clone_req_ref'")['value']
        clone_toggle_val = db_get_one("SELECT value FROM settings WHERE key='clone_ref_toggle'")['value']
        ref_reward_val = db_get_one("SELECT value FROM settings WHERE key='ref_reward_credits'")['value']
        report_style_val = db_get_one("SELECT value FROM settings WHERE key='report_style'")['value']
        
        panel_text = f"\n📊 *ADVANCED ADMIN PANEL*\n━━━━━━━━━━━━━━━━━━\n👥 Total Users: `{total_users}`\n🔍 Total Lookups: `{total_searches}`\n💳 UPI: `{upi_record['value'] if upi_record else 'Not Set'}`\n🎨 Report Style: `{report_style_val.upper()}`\n🚧 Maintenance: `{maint.upper()}`\n🤖 Clone Refs: `{clone_ref_val}` (`{clone_toggle_val.upper()}`)\n🎁 Ref Reward: `{ref_reward_val} Credits`\n"
        keyboard = [
            [InlineKeyboardButton("🟢 👥 View Users", callback_data="admin_users"), InlineKeyboardButton("💳 ⚙ Set UPI ID", callback_data="admin_setupi_prompt")],
            [InlineKeyboardButton("📷 ⚙ Set UPI QR", callback_data="admin_setupi_qr_prompt")],
            [InlineKeyboardButton("📦 📋 Manage Plans", callback_data="admin_plans"), InlineKeyboardButton("💎 ➕ Add Credits", callback_data="admin_addcredit_prompt")],
            [InlineKeyboardButton("📈 ⚡ Live Analytics", callback_data="admin_live_analytics"), InlineKeyboardButton("🤖 👥 Clone Bots", callback_data="admin_clones")],
            [InlineKeyboardButton("🌐 🔌 Dynamic APIs", callback_data="admin_dynamic_apis"), InlineKeyboardButton("➕ 🔌 Add New API", callback_data="admin_add_api")],
            [InlineKeyboardButton("🗑️ 🔌 Delete API", callback_data="admin_delete_api"), InlineKeyboardButton("✏️ 📝 Edit Button Name", callback_data="admin_edit_name")],
            [InlineKeyboardButton("🎨 🔄 Change Report Style", callback_data="admin_toggle_style"), InlineKeyboardButton("🔄 Toggle Clone Ref", callback_data="admin_toggle_clone_ref")],
            [InlineKeyboardButton("👥 ⚙️ Set Clone Refs", callback_data="admin_cloneref_prompt"), InlineKeyboardButton("🎁 ⚙️ Set Ref Reward", callback_data="admin_refreward_prompt")],
            [InlineKeyboardButton("💬 ⚙️ Set Maint Msg", callback_data="admin_setmaintmsg_prompt"), InlineKeyboardButton("🖼️ ⚙️ Set Banner", callback_data="admin_banner_prompt")],
            [InlineKeyboardButton("🛡️ ➕ Add Sub-Admin", callback_data="admin_addsub_prompt"), InlineKeyboardButton("🛠️ 🔄 Maintenance", callback_data="toggle_maintenance")],
            [InlineKeyboardButton("🟢 🔍 Check API Status", callback_data="admin_check_api_status")],
            [InlineKeyboardButton("❌ 📦 Close", callback_data="close_panel")]
        ]
        try: await query.edit_message_text(panel_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except: await query.message.reply_text(panel_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    elif data == "admin_setupi_prompt":
        context.user_data['waiting_for_upi'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="💳 **Set Admin UPI ID**\nNayi UPI ID bhejein:", parse_mode='Markdown')
        return

    elif data == "admin_setupi_qr_prompt":
        context.user_data['waiting_for_upi_qr'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="📷 **Set UPI QR Code**\nKripya QR Code ki ek Photo bhejein:", parse_mode='Markdown')
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

    elif data == "admin_toggle_style":
        curr = db_get_one("SELECT value FROM settings WHERE key='report_style'")['value']
        styles = ['cyber', 'json', 'hacker', 'matrix', 'neon', 'card', 'compact', 'minimal', 'vip', 'standard']
        next_style = styles[(styles.index(curr) + 1) % len(styles)] if curr in styles else 'cyber'
        db_execute("UPDATE settings SET value = ? WHERE key = 'report_style'", (next_style,), commit=True)
        await query.answer(f"🎨 Report Style changed to: {next_style.upper()}!", show_alert=True)
        
        total_users = db_get_one("SELECT COUNT(*) as count FROM users")['count']
        total_searches = db_get_one("SELECT COUNT(*) as count FROM searches")['count']
        maint = db_get_one("SELECT value FROM settings WHERE key='maintenance'")['value']
        upi_record = db_get_one("SELECT value FROM settings WHERE key='upi_id'")
        clone_ref_val = db_get_one("SELECT value FROM settings WHERE key='clone_req_ref'")['value']
        clone_toggle_val = db_get_one("SELECT value FROM settings WHERE key='clone_ref_toggle'")['value']
        ref_reward_val = db_get_one("SELECT value FROM settings WHERE key='ref_reward_credits'")['value']
        
        panel_text = f"\n📊 *ADVANCED ADMIN PANEL*\n━━━━━━━━━━━━━━━━━━\n👥 Total Users: `{total_users}`\n🔍 Total Lookups: `{total_searches}`\n💳 UPI: `{upi_record['value'] if upi_record else 'Not Set'}`\n🎨 Report Style: `{next_style.upper()}`\n🚧 Maintenance: `{maint.upper()}`\n🤖 Clone Refs: `{clone_ref_val}` (`{clone_toggle_val.upper()}`)\n🎁 Ref Reward: `{ref_reward_val} Credits`\n"
        keyboard = [
            [InlineKeyboardButton("🟢 👥 View Users", callback_data="admin_users"), InlineKeyboardButton("💳 ⚙ Set UPI ID", callback_data="admin_setupi_prompt")],
            [InlineKeyboardButton("📷 ⚙ Set UPI QR", callback_data="admin_setupi_qr_prompt")],
            [InlineKeyboardButton("📦 📋 Manage Plans", callback_data="admin_plans"), InlineKeyboardButton("💎 ➕ Add Credits", callback_data="admin_addcredit_prompt")],
            [InlineKeyboardButton("📈 ⚡ Live Analytics", callback_data="admin_live_analytics"), InlineKeyboardButton("🤖 👥 Clone Bots", callback_data="admin_clones")],
            [InlineKeyboardButton("🌐 🔌 Dynamic APIs", callback_data="admin_dynamic_apis"), InlineKeyboardButton("➕ 🔌 Add New API", callback_data="admin_add_api")],
            [InlineKeyboardButton("🗑️ 🔌 Delete API", callback_data="admin_delete_api"), InlineKeyboardButton("✏️ 📝 Edit Button Name", callback_data="admin_edit_name")],
            [InlineKeyboardButton("🎨 🔄 Change Report Style", callback_data="admin_toggle_style"), InlineKeyboardButton("🔄 Toggle Clone Ref", callback_data="admin_toggle_clone_ref")],
            [InlineKeyboardButton("👥 ⚙️ Set Clone Refs", callback_data="admin_cloneref_prompt"), InlineKeyboardButton("🎁 ⚙️ Set Ref Reward", callback_data="admin_refreward_prompt")],
            [InlineKeyboardButton("💬 ⚙️ Set Maint Msg", callback_data="admin_setmaintmsg_prompt"), InlineKeyboardButton("🖼️ ⚙️ Set Banner", callback_data="admin_banner_prompt")],
            [InlineKeyboardButton("🛡️ ➕ Add Sub-Admin", callback_data="admin_addsub_prompt"), InlineKeyboardButton("🛠️ 🔄 Maintenance", callback_data="toggle_maintenance")],
            [InlineKeyboardButton("🟢 🔍 Check API Status", callback_data="admin_check_api_status")],
            [InlineKeyboardButton("❌ 📦 Close", callback_data="close_panel")]
        ]
        try: await query.edit_message_text(panel_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except: pass
        return

    elif data == "admin_toggle_clone_ref":
        curr = db_get_one("SELECT value FROM settings WHERE key='clone_ref_toggle'")
        new_val = 'off' if curr and curr['value'] == 'on' else 'on'
        db_execute("UPDATE settings SET value = ? WHERE key = 'clone_ref_toggle'", (new_val,), commit=True)
        await query.answer(f"✅ Clone Referral requirement is now {new_val.upper()}!", show_alert=True)
        
        total_users = db_get_one("SELECT COUNT(*) as count FROM users")['count']
        total_searches = db_get_one("SELECT COUNT(*) as count FROM searches")['count']
        maint = db_get_one("SELECT value FROM settings WHERE key='maintenance'")['value']
        upi_record = db_get_one("SELECT value FROM settings WHERE key='upi_id'")
        clone_ref_val = db_get_one("SELECT value FROM settings WHERE key='clone_req_ref'")['value']
        clone_toggle_val = db_get_one("SELECT value FROM settings WHERE key='clone_ref_toggle'")['value']
        ref_reward_val = db_get_one("SELECT value FROM settings WHERE key='ref_reward_credits'")['value']
        report_style_val = db_get_one("SELECT value FROM settings WHERE key='report_style'")['value']
        
        panel_text = f"\n📊 *ADVANCED ADMIN PANEL*\n━━━━━━━━━━━━━━━━━━\n👥 Total Users: `{total_users}`\n🔍 Total Lookups: `{total_searches}`\n💳 UPI: `{upi_record['value'] if upi_record else 'Not Set'}`\n🎨 Report Style: `{report_style_val.upper()}`\n🚧 Maintenance: `{maint.upper()}`\n🤖 Clone Refs: `{clone_ref_val}` (`{clone_toggle_val.upper()}`)\n🎁 Ref Reward: `{ref_reward_val} Credits`\n"
        keyboard = [
            [InlineKeyboardButton("🟢 👥 View Users", callback_data="admin_users"), InlineKeyboardButton("💳 ⚙️ Set UPI ID", callback_data="admin_setupi_prompt")],
            [InlineKeyboardButton("📷 ⚙ Set UPI QR", callback_data="admin_setupi_qr_prompt")],
            [InlineKeyboardButton("📦 📋 Manage Plans", callback_data="admin_plans"), InlineKeyboardButton("💎 ➕ Add Credits", callback_data="admin_addcredit_prompt")],
            [InlineKeyboardButton("📈 ⚡ Live Analytics", callback_data="admin_live_analytics"), InlineKeyboardButton("🤖 👥 Clone Bots", callback_data="admin_clones")],
            [InlineKeyboardButton("🌐 🔌 Dynamic APIs", callback_data="admin_dynamic_apis"), InlineKeyboardButton("➕ 🔌 Add New API", callback_data="admin_add_api")],
            [InlineKeyboardButton("🗑️ 🔌 Delete API", callback_data="admin_delete_api"), InlineKeyboardButton("✏️ 📝 Edit Button Name", callback_data="admin_edit_name")],
            [InlineKeyboardButton("🎨 🔄 Change Report Style", callback_data="admin_toggle_style"), InlineKeyboardButton("🔄 Toggle Clone Ref", callback_data="admin_toggle_clone_ref")],
            [InlineKeyboardButton("👥 ⚙️ Set Clone Refs", callback_data="admin_cloneref_prompt"), InlineKeyboardButton("🎁 ⚙️ Set Ref Reward", callback_data="admin_refreward_prompt")],
            [InlineKeyboardButton("💬 ⚙️ Set Maint Msg", callback_data="admin_setmaintmsg_prompt"), InlineKeyboardButton("🖼️ ⚙️ Set Banner", callback_data="admin_banner_prompt")],
            [InlineKeyboardButton("🛡️ ➕ Add Sub-Admin", callback_data="admin_addsub_prompt"), InlineKeyboardButton("🛠️ 🔄 Maintenance", callback_data="toggle_maintenance")],
            [InlineKeyboardButton("🟢 🔍 Check API Status", callback_data="admin_check_api_status")],
            [InlineKeyboardButton("❌ 📦 Close", callback_data="close_panel")]
        ]
        try: await query.edit_message_text(panel_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except: pass
        return

    elif data == "admin_check_api_status":
        apis = db_get_all("SELECT * FROM dynamic_apis")
        text = "🟢 **LIVE API STATUS CHECKER**\n━━━━━━━━━━━━━━━━━━━━━━\n"
        for ap in apis:
            url_to_test = ap['api_url'].replace("{query}", "9999999999" if ap['api_key'] == 'phone' else "110001")
            try:
                start_t = time.time()
                res = requests.get(url_to_test, headers=HTTP_HEADERS, timeout=5)
                ping = int((time.time() - start_t) * 1000)
                if res.status_code == 200:
                    text += f"• **{ap['api_name']}**: `🟢 ONLINE` (Ping: `{ping}ms`)\n"
                else:
                    text += f"• **{ap['api_name']}**: `🟡 ISSUE ({res.status_code})`\n"
            except:
                text += f"• **{ap['api_name']}**: `🔴 OFFLINE / DOWN`\n"
        keyboard = [[InlineKeyboardButton("🔵 📊 Back", callback_data="admin_panel")]]
        try:
            await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except:
            await query.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    elif data == "admin_cloneref_prompt":
        context.user_data['waiting_for_clone_ref_count'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="👥 **Set Clone Referrals**\nNaya required referrals count bhejein:", parse_mode='Markdown')
        return

    elif data == "admin_refreward_prompt":
        context.user_data['waiting_for_ref_reward'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="🎁 **Set Referral Reward**\nNaye reward credits bhejein:", parse_mode='Markdown')
        return

    elif data == "admin_setmaintmsg_prompt":
        context.user_data['waiting_for_maint_msg'] = True
        await context.bot.send_message(chat_id=query.from_user.id, text="💬 **Set Maintenance Message**\nNaya message bhejein:", parse_mode='Markdown')
        return

    elif data.startswith("edit_api_url_"):
        context.user_data['waiting_for_api_url'] = True
        context.user_data['target_api_key'] = data.replace("edit_api_url_", "")
        await context.bot.send_message(chat_id=query.from_user.id, text="🌐 Naya API URL bhejein (use `{query}` placeholder):", parse_mode='Markdown')
        return

    elif data.startswith("edit_api_wm_"):
        context.user_data['waiting_for_api_old'] = True
        context.user_data['target_api_key'] = data.replace("edit_api_wm_", "")
        await context.bot.send_message(chat_id=query.from_user.id, text="✍️ Old watermark text bhejein:", parse_mode='Markdown')
        return

    elif data == "admin_live_analytics":
        analytics = db_get_all("SELECT feature_name, count FROM analytics")
        text = f"📈 *ANALYTICS*\nActive Live Users: `{len(active_live_users)}`\n\n"
        for an in analytics: text += f"• `{an['feature_name']}`: `{an['count']}` uses\n"
        keyboard = [[InlineKeyboardButton("🔵 📊 Back", callback_data="admin_panel")]]
        try: await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except: await query.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    elif data == "admin_clones":
        clones = db_get_all("SELECT * FROM clones")
        text = "🤖 *CLONE BOTS*\n"
        keyboard = [[InlineKeyboardButton("🔵 📊 Back", callback_data="admin_panel")]]
        if not clones: text += "Koi clone bot nahi hai."
        try: await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except: await query.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    elif data == "admin_users":
        users = db_get_all("SELECT user_id, username, first_name, phone_number, searches, credits, is_banned FROM users ORDER BY joined_date DESC LIMIT 10")
        text = "👥 *Recent Users*\n"
        for u in users:
            text += f"ID: `{u['user_id']}` | Name: {u['first_name']} | Credits: {u['credits']}\n"
        keyboard = [[InlineKeyboardButton("🔵 📊 Back", callback_data="admin_panel")]]
        try: await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except: await query.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    elif data == "admin_plans":
        plans = db_get_all("SELECT * FROM plans")
        text = "📦 *Plans*\n"
        for p in plans: text += f"• {p['name']} - {p['price']} ({p['credits']} Credits)\n"
        keyboard = [[InlineKeyboardButton("🔵 📊 Back", callback_data="admin_panel")]]
        try: await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except: await query.message.reply_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    elif data == "toggle_maintenance":
        current = db_get_one("SELECT value FROM settings WHERE key='maintenance'")['value']
        new_val = 'off' if current == 'on' else 'on'
        db_execute("UPDATE settings SET value = ? WHERE key = 'maintenance'", (new_val,), commit=True)
        await query.answer(f"✅ Maintenance is now {new_val.upper()}!", show_alert=True)
        return

    elif data == "close_panel":
        try: await query.message.delete()
        except: pass
        return

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
    print("🚀 HARSH OSINT BOT STARTING (10 REPORT STYLES & ALL ADMIN BUGS FIXED)...")
    
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
    application.add_handler(CommandHandler("setupi", setupi_command))
    application.add_handler(CommandHandler("maint", maint_command))
    application.add_handler(CommandHandler("addcredits", addcredits_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    
    application.add_handler(MessageHandler((filters.TEXT & ~filters.COMMAND) | filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.Document.ALL, handle_message))
    
    application.add_handler(CallbackQueryHandler(button_callback))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == '__main__':
    main()
