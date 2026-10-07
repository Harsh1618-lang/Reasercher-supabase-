#!/usr/init/env python3
# OSINT & Pincode Bot - Ultimate 10 Report Styles & Complete Features Edition
"""
Developer: @Harsx1618
Description: Advanced Telegram OSINT Bot with Complete Restored Logic, Smart Auto-Detect, Custom Search UI Box, Transactions, Engagement & All Features Intact
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
BOT_START_TIME = time.time()                                    # Uptime Tracking

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
        notifications TEXT DEFAULT 'ON',
        streak_count INTEGER DEFAULT 0
    )''')
    
    try: c.execute("ALTER TABLE users ADD COLUMN ui_theme TEXT DEFAULT 'Dark'")
    except: pass
    try: c.execute("ALTER TABLE users ADD COLUMN report_mode TEXT DEFAULT 'Full'")
    except: pass
    try: c.execute("ALTER TABLE users ADD COLUMN default_style TEXT DEFAULT 'cyber'")
    except: pass
    try: c.execute("ALTER TABLE users ADD COLUMN notifications TEXT DEFAULT 'ON'")
    except: pass
    try: c.execute("ALTER TABLE users ADD COLUMN streak_count INTEGER DEFAULT 0")
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

    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        tx_type TEXT,
        amount INTEGER,
        description TEXT,
        balance_after INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS search_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        search_type TEXT,
        query_masked TEXT,
        result_count INTEGER DEFAULT 0,
        api_used TEXT,
        response_time REAL DEFAULT 0.0,
        status TEXT DEFAULT 'Success',
        credits_deducted INTEGER DEFAULT 1,
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

    c.execute('''CREATE TABLE IF NOT EXISTS bug_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        search_type TEXT,
        query_masked TEXT,
        report_type TEXT,
        message TEXT,
        status TEXT DEFAULT 'Pending',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS faqs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        answer TEXT,
        category TEXT,
        display_order INTEGER DEFAULT 1,
        status TEXT DEFAULT 'Active',
        views INTEGER DEFAULT 0
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS support_tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        subject TEXT,
        message TEXT,
        status TEXT DEFAULT 'Open',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        requirement TEXT,
        reward INTEGER,
        icon TEXT,
        status TEXT DEFAULT 'Active'
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS user_achievements (
        user_id INTEGER,
        achievement_id INTEGER,
        unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('help_center_toggle', 'on')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('faq_toggle', 'on')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('support_toggle', 'on')")

    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('stat_online', 'on')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('stat_searches', 'on')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('stat_api_status', 'on')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('stat_uptime', 'on')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('stat_premium', 'on')")

    c.execute("SELECT COUNT(*) FROM faqs")
    if c.fetchone()[0] == 0:
        default_faqs = [
            ("Credits کیسے मिलेंगे?", "Aapko daily bonus (/daily) claim karne par, ya referral link se doston ko invite karne par free credits milte hain.", "💳 Credits & Premium", 1),
            ("Search کیسے کریں?", "Quick Search menu open karke aap Number, Pincode, IP ya Telegram lookup select kar sakte hain.", "🔎 Search", 2),
            ("Referral کیسے काम करता है?", "Apna referral link /ref ya Profile se copy karke doston ko bhejein. Har naye join par aapko credits milenge.", "🎁 Referral", 3),
            ("API unavailable کیوں ہے?", "Kabhi-kabhi upstream server overload hone par API temporary down ho sakti hai. Kuch der baad koshish karein.", "🔌 API", 4),
            ("Contact support", "Kisi bhi samasya ke liye aap admin se seedhe contact kar sakte hain ya support ticket raise kar sakte hain.", "📞 Support", 5)
        ]
        for q, a, cat, ord in default_faqs:
            c.execute("INSERT INTO faqs (question, answer, category, display_order) VALUES (?, ?, ?, ?)", (q, a, cat, ord))
    
    default_welcome = "\n╔═════════════════════════════════╗\n║       👑 LYNX X BOT 👑          ║\n╚═════════════════════════════════╝\n💎 Your Vault:    {credits} Credits ✨\n🌟 Privilege: Lifetime Access ⚡\n👇 Choose Your Path:\n┌─────────────────────────────────┐\n│ 🎁 Claim Freebies ➔ /daily      │\n│ 🔑 Redeem Code   ➔ /redeem      │\n└─────────────────────────────────┘"
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

def record_transaction(user_id, tx_type, amount, description):
    user_db = db_get_one("SELECT credits FROM users WHERE user_id = ?", (user_id,))
    bal = user_db['credits'] if user_db else 0
    db_execute("INSERT INTO transactions (user_id, tx_type, amount, description, balance_after) VALUES (?, ?, ?, ?, ?)",
               (user_id, tx_type, amount, description, bal), commit=True)

def record_search_log(user_id, search_type, query_masked, result_count, api_used, resp_time, status, credits_ded):
    db_execute("INSERT INTO search_logs (user_id, search_type, query_masked, result_count, api_used, response_time, status, credits_deducted) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
               (user_id, search_type, query_masked, result_count, api_used, resp_time, status, credits_ded), commit=True)

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

def format_uptime():
    uptime_sec = int(time.time() - BOT_START_TIME)
    days = uptime_sec // 86400
    hours = (uptime_sec % 86400) // 3600
    mins = (uptime_sec % 3600) // 60
    return f"{days}d {hours}h {mins}m"

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
        start_t = time.time()
        response = requests.get(final_url, headers=HTTP_HEADERS, timeout=timeout_sec)
        resp_time = round(time.time() - start_t, 2)
        if response.status_code == 200:
            raw_text = response.text
            if old_c:
                raw_text = raw_text.replace(old_c, new_c)
            try:
                res_json = json.loads(raw_text)
                return res_json, resp_time, "Success"
            except:
                return {"status": True, "raw_result": raw_text}, resp_time, "Success"
        else:
            return {"status": False, "error": "API returned status " + str(response.status_code)}, resp_time, "Failed"
    except Exception as e:
        return {"status": False, "error": str(e)}, 0.0, "Failed"

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
# COMPREHENSIVE 10 REPORT STYLES FORMATTER
# ============================================
async def send_paginated_phone_response(msg_obj, records, phone, update, context, page=0, is_edit=True):
    total = len(records)
    if total == 0:
        await msg_obj.edit_text("❌ Koi record nahi mila.")
        return

    user_id = update.effective_user.id
    user_db = db_get_one("SELECT default_style, report_mode FROM users WHERE user_id = ?", (user_id,))
    
    global_style_rec = db_get_one("SELECT value FROM settings WHERE key='report_style'")
    global_style = global_style_rec['value'] if global_style_rec else 'cyber'

    r_style = user_db.get('default_style') if user_db and user_db.get('default_style') else global_style
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
        text = f"🌐 𝕮𝕴𝕭𝕰𝕽 𝕴𝕹𝕿𝕰𝕃𝕃𝕴𝕲𝕰𝕹𝕮𝕰 ({r_mode.upper()}) 🌐\n"
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
            if r_mode == 'Full': text += f"• Father    : **{rec['father']}`\n"
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

    bug_row = [
        InlineKeyboardButton("❓ Wrong Result", callback_data=f"bug_wrong_{phone}"),
        InlineKeyboardButton("🔌 API Error", callback_data=f"bug_apierr_{phone}")
    ]
    support_bug_row = [
        InlineKeyboardButton("💬 Contact Support", url=f"https://t.me/{OWNER_USERNAME.replace('@', '')}")
    ]
    buttons.append(bug_row)
    buttons.append(support_bug_row)

    reply_markup = InlineKeyboardMarkup(buttons)

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
# TRANSACTION HISTORY & SEARCH HISTORY UPGRADE
# ============================================
async def show_transaction_history(update_or_query, context, user_id, is_callback=False):
    txs = db_get_all("SELECT * FROM transactions WHERE user_id = ? ORDER BY id DESC LIMIT 10", (user_id,))
    user_db = db_get_one("SELECT credits FROM users WHERE user_id = ?", (user_id,))
    bal = user_db['credits'] if user_db else 0

    text = f"💳 **TRANSACTION & CREDIT LEDGER**\n\n💎 Current Balance: `{bal} Credits`\n━━━━━━━━━━━━━━━━━━━━\n"
    if not txs:
        text += "📭 Abhi tak koi transaction record nahi hai.\n"
    else:
        for t in txs:
            sign = "+" if t['amount'] > 0 else ""
            text += f"• `{t['timestamp']}`\n  `{t['description']}` ({sign}{t['amount']} Cr) | Bal: `{t['balance_after']}`\n"
    
    keyboard = [[InlineKeyboardButton("🔄 Refresh Ledger", callback_data="tx_refresh"), InlineKeyboardButton("🏠 Main Menu", callback_data="profile_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if is_callback:
        try: await update_or_query.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        except: await update_or_query.callback_query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update_or_query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def show_upgraded_search_history(update_or_query, context, user_id, is_callback=False):
    logs = db_get_all("SELECT * FROM search_logs WHERE user_id = ? ORDER BY id DESC LIMIT 5", (user_id,))
    text = f"🧾 **UPGRADED SEARCH RESULT HISTORY**\n\nAapki pichli search queries aur status:\n━━━━━━━━━━━━━━━━━━━━\n"
    if not logs:
        text += "📭 Koi search history available nahi hai.\n"
    else:
        for l in logs:
            status_icon = "✅" if l['status'] == 'Success' else "❌"
            text += f"{status_icon} **Type:** `{l['search_type']}` | Target: `{l['query_masked']}`\n"
            text += f"⏰ `{l['timestamp']}` | Results: `{l['result_count']}` | API: `{l['api_used']}`\n━━━━━━━━━━━━━━━━━━━━\n"

    keyboard = [[InlineKeyboardButton("🔄 Refresh History", callback_data="sh_refresh"), InlineKeyboardButton("🏠 Main Menu", callback_data="profile_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if is_callback:
        try: await update_or_query.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        except: await update_or_query.callback_query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update_or_query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def show_help_center(update_or_query, context, is_callback=False):
    hc_toggle = db_get_one("SELECT value FROM settings WHERE key='help_center_toggle'")
    if hc_toggle and hc_toggle['value'] == 'off':
        text = "🚧 Help Center is currently disabled by admin."
    else:
        text = "🆘 **HELP CENTER & FAQ**\n\nNeeche diye gaye topics mein se apna sawaal select karein ya support par contact karein:\n━━━━━━━━━━━━━━━━━━━━\n"
        faqs = db_get_all("SELECT * FROM faqs WHERE status='Active' ORDER BY display_order ASC")
        if not faqs:
            text += "📭 Filhal koi FAQ available nahi hai.\n"
        else:
            for f in faqs:
                text += f"❓ **{f['question']}**\n💡 _{f['answer']}_\n━━━━━━━━━━━━━━━━━━━━\n"

    keyboard = [
        [InlineKeyboardButton("💬 Contact Support", callback_data="help_support_ticket")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="profile_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if is_callback:
        try: await update_or_query.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        except: await update_or_query.callback_query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update_or_query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_help_center(update, context, is_callback=False)

async def show_live_statistics(update_or_query, context, is_callback=False):
    s_online = db_get_one("SELECT value FROM settings WHERE key='stat_online'")['value'] == 'on'
    s_search = db_get_one("SELECT value FROM settings WHERE key='stat_searches'")['value'] == 'on'
    s_api = db_get_one("SELECT value FROM settings WHERE key='stat_api_status'")['value'] == 'on'
    s_uptime = db_get_one("SELECT value FROM settings WHERE key='stat_uptime'")['value'] == 'on'
    s_prem = db_get_one("SELECT value FROM settings WHERE key='stat_premium'")['value'] == 'on'

    text = f"📈 **LIVE BOT STATISTICS**\n\n━━━━━━━━━━━━━━━━━━━━\n"
    if s_online: text += f"👥 **Online Users:** `{len(active_live_users)} Active`\n"
    if s_search:
        total_searches = db_get_one("SELECT COUNT(*) as cnt FROM searches")['cnt'] or 0
        text += f"🔎 **Total Searches:** `{total_searches:,}`\n"
    if s_api: text += f"⚡ **API Status:** `6/6 Operational`\n"
    if s_uptime: text += f"🤖 **Bot Uptime:** `{format_uptime()}`\n"
    if s_prem:
        prem_count = db_get_one("SELECT COUNT(*) as cnt FROM users WHERE credits > 10")['cnt'] or 0
        text += f"⭐ **Premium Users:** `{prem_count}`\n"
    text += f"━━━━━━━━━━━━━━━━━━━━"

    keyboard = [[InlineKeyboardButton("🔄 Refresh Stats", callback_data="stats_refresh"), InlineKeyboardButton("🏠 Main Menu", callback_data="profile_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if is_callback:
        try: await update_or_query.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        except: await update_or_query.callback_query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update_or_query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_live_statistics(update, context, is_callback=False)

async def show_notifications_center(update_or_query, context, user_id, is_callback=False):
    user_db = db_get_one("SELECT * FROM users WHERE user_id = ?", (user_id,))
    if not user_db:
        text = "❌ User profile not found."
    else:
        notifs = db_get_all("SELECT * FROM notifications WHERE status = 'Active' ORDER BY id DESC LIMIT 5")
        text = f"🔔 **NOTIFICATION CENTER**\n\nLatest updates, announcements & offers:\n━━━━━━━━━━━━━━━━━━━━\n"
        
        if not notifs:
            text += "📭 Filhal koi nayi notification nahi hai.\n"
        else:
            for n in notifs:
                read_rec = db_get_one("SELECT * FROM user_notifications WHERE user_id = ? AND notif_id = ?", (user_id, n['id']))
                status_icon = "✅ Read" if read_rec and read_rec['is_read'] == 1 else "🔵 Unread"
                
                if not read_rec:
                    db_execute("INSERT INTO user_notifications (user_id, notif_id, is_read) VALUES (?, ?, 1)", (user_id, n['id']), commit=True)
                elif read_rec['is_read'] == 0:
                    db_execute("UPDATE user_notifications SET is_read = 1 WHERE user_id = ? AND notif_id = ?", (user_id, n['id']), commit=True)

                icon_type = "📢"
                if n['notif_type'] == 'Offer': icon_type = "🎁"
                elif n['notif_type'] == 'Maintenance': icon_type = "🔧"
                elif n['notif_type'] == 'Update': icon_type = "🚀"
                elif n['notif_type'] == 'Important': icon_type = "⚠️"

                text += f"{icon_type} **{n['title']}** [{status_icon}]\n{n['message']}\n━━━━━━━━━━━━━━━━━━━━\n"

    keyboard = [
        [InlineKeyboardButton("🔄 Refresh Notifs", callback_data="notif_refresh"), InlineKeyboardButton("🗑️ Clear / Mark Read", callback_data="notif_clear")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="profile_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if is_callback:
        try: await update_or_query.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup, disable_web_page_preview=True)
        except: await update_or_query.callback_query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup, disable_web_page_preview=True)
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
        [InlineKeyboardButton("💳 Transactions", callback_data="profile_transactions"), InlineKeyboardButton("🧾 Search History", callback_data="profile_search_history")],
        [InlineKeyboardButton("🌙 Toggle Theme", callback_data="ui_toggle_theme"), InlineKeyboardButton("📄 Report Mode", callback_data="ui_toggle_mode")],
        [InlineKeyboardButton("🎨 Report Style", callback_data="ui_set_style"), InlineKeyboardButton("🔔 Notifications", callback_data="ui_toggle_notif")],
        [InlineKeyboardButton("📜 HISTORY", callback_data="profile_history"), InlineKeyboardButton("📊 STATS", callback_data="profile_stats")],
        [InlineKeyboardButton("🎁 REFER", callback_data="profile_referral"), InlineKeyboardButton("💎 BUY", callback_data="profile_buy")],
        [InlineKeyboardButton("🔄 REFRESH", callback_data="profile_refresh"), InlineKeyboardButton("🏠 MAIN MENU", callback_data="profile_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if is_callback:
        try: await update_or_query.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        except: await update_or_query.callback_query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update_or_query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await show_user_profile(update, context, user.id, is_callback=False)

async def quick_search_menu(update_or_query, context, is_callback=False):
    text = "╭━━〔 🔎 CUSTOM SEARCH 〕━━╮\n┃ ⚡ Smart Detection: ON\n┃ 🧠 Query type auto-detect hoga\n┃ 📊 Matching result show hoga\n┃\n┃ 📱 Number  •  📍 Pincode\n┃ 🪪 Aadhaar •  ✈️ Telegram\n┃ 🌐 IP      •  🔎 Other Data\n╰━━━━━━━━━━━━━━━━━━━━━━╯\n\n✦ *Enter your query →*"
    keyboard = [
        [InlineKeyboardButton("📱 Number", callback_data="qs_number"), InlineKeyboardButton("📍 Pincode", callback_data="qs_pincode")],
        [InlineKeyboardButton("🌐 IP", callback_data="qs_ip"), InlineKeyboardButton("🔤 Telegram", callback_data="qs_telegram")],
        [InlineKeyboardButton("🔎 Custom API", callback_data="qs_custom"), InlineKeyboardButton("🏠 Main Menu", callback_data="profile_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if is_callback:
        try: await update_or_query.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        except: await update_or_query.callback_query.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

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
    record_transaction(user.id, "Coupon Redeem", credits_to_add, f"Redeemed key {key}")
    log_activity(user.id, f"Redeemed key {key} for {credits_to_add} credits")
    await update.message.reply_text(f"🎉 **Redeem Successful!**\nAapke account mein `{credits_to_add}` credits aur 30 din ki premium access mil gayi hai!", parse_mode='Markdown')

async def daily_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = db_get_one("SELECT last_daily, streak_count FROM users WHERE user_id = ?", (user.id,))
    today_str = datetime.now().strftime("%Y-%m-%d")
    if user_data['last_daily'] == today_str:
        await update.message.reply_text("❌ Aapne aaj ka daily bonus pehle hi claim kar liya hai!")
        return
    
    new_streak = (user_data['streak_count'] or 0) + 1
    bonus = 2 + (new_streak if new_streak <= 7 else 7)
    db_execute("UPDATE users SET credits = credits + ?, last_daily = ?, streak_count = ? WHERE user_id = ?", (bonus, today_str, new_streak, user.id), commit=True)
    record_transaction(user.id, "Daily Check-in", bonus, f"Daily login reward (Streak: {new_streak} days)")
    log_activity(user.id, f"Claimed daily bonus of {bonus} credits (Streak {new_streak})")
    await update.message.reply_text(f"🎁 **Daily Check-in Claimed!**\n🔥 Streak: `{new_streak} Days`\n💎 Reward: `{bonus} Credits`", parse_mode='Markdown')

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
        record_transaction(user.id, "Signup Bonus", ref_reward, "Welcome bonus credits")
        log_activity(user.id, "New user joined via /start")
        if referrer_id != 0:
            db_execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (ref_reward, referrer_id), commit=True)
            record_transaction(referrer_id, "Referral Reward", ref_reward, f"Referral bonus from user {user.id}")
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
    
    static_buttons = ["🆘 Help Center", "📈 Live Stats", "🔔 Notifications", "🔍 Quick Search", "👤 MY PROFILE", "💬 Owner | Support", "💰 Refer & Earn", "🏆 Leaderboard", "🤖 My Clone Bot", "💎 Buy Premium / Credits", "🛠️ Toggle Menu"]
    
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
        [InlineKeyboardButton("💳 Transactions & Adjust", callback_data="admin_tx_mgmt"), InlineKeyboardButton("🔎 Search Logs & Audit", callback_data="admin_search_logs")],
        [InlineKeyboardButton("📚 FAQ Manager", callback_data="admin_faq_manager"), InlineKeyboardButton("🎫 Support Tickets", callback_data="admin_support_tickets")],
        [InlineKeyboardButton("📊 Analytics & Live Stats", callback_data="admin_stats_dashboard"), InlineKeyboardButton("🐛 Bug Reports", callback_data="admin_bug_reports")],
        [InlineKeyboardButton("🔔 Create Notif", callback_data="admin_create_notif"), InlineKeyboardButton("🟢 👥 View Users & Logs", callback_data="admin_users")],
        [InlineKeyboardButton("💳 ⚙ Set UPI ID", callback_data="admin_setupi_prompt"), InlineKeyboardButton("📦 📋 Manage Plans", callback_data="admin_plans")],
        [InlineKeyboardButton("💎 ➕ Add Credits", callback_data="admin_addcredit_prompt"), InlineKeyboardButton("📈 ⚡ Live Analytics", callback_data="admin_live_analytics")],
        [InlineKeyboardButton("🤖 👥 Clone Bots", callback_data="admin_clones"), InlineKeyboardButton("🌐 🔌 Dynamic APIs", callback_data="admin_dynamic_apis")],
        [InlineKeyboardButton("➕ 🔌 Add New API", callback_data="admin_add_api"), InlineKeyboardButton("🗑️ 🔌 Delete API", callback_data="admin_delete_api")],
        [InlineKeyboardButton("✏️ 📝 Edit Button Name", callback_data="admin_edit_name"), InlineKeyboardButton("🎨 🔄 Change Report Style", callback_data="admin_toggle_style")],
        [InlineKeyboardButton("🔄 Toggle Clone Ref", callback_data="admin_toggle_clone_ref"), InlineKeyboardButton("👥 ⚙️ Set Clone Refs", callback_data="admin_cloneref_prompt")],
        [InlineKeyboardButton("🎁 ⚙ Set Ref Reward", callback_data="admin_refreward_prompt"), InlineKeyboardButton("💬 ⚙ Set Maint Msg", callback_data="admin_setmaintmsg_prompt")],
        [InlineKeyboardButton("🖼️ ⚙ Set Banner", callback_data="admin_banner_prompt"), InlineKeyboardButton("🛡️ ➕ Add Sub-Admin", callback_data="admin_addsub_prompt")],
        [InlineKeyboardButton("🛠️ 🔄 Maintenance", callback_data="toggle_maintenance"), InlineKeyboardButton("💬 Set Welcome Text", callback_data="admin_welcome_prompt")],
        [InlineKeyboardButton("🔑 Gen Redeem Key", callback_data="admin_redeem_prompt"), InlineKeyboardButton("📜 View Logs", callback_data="admin_view_logs")],
        [InlineKeyboardButton("🔨 Ban User", callback_data="admin_ban_prompt"), InlineKeyboardButton("🔓 Unban User", callback_data="admin_unban_prompt")],
        [InlineKeyboardButton("📥 Download Search Logs", callback_data="admin_download_logs"), InlineKeyboardButton("❌ 📦 Close", callback_data="close_panel")]
    ]
    
    chat_id = update_or_query.message.chat_id if hasattr(update_or_query, 'message') and update_or_query.message else update_or_query.effective_chat.id
    if hasattr(update_or_query, 'callback_query') and update_or_query.callback_query:
        await update_or_query.callback_query.edit_message_text(panel_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update_or_query.message.reply_text(panel_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    print("🚀 LYNX X BOT STARTING (FULL 2500+ LINES RESTORED WITH ALL CUSTOM FEATURES)...")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("search", quick_search_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("notifications", notif_command))
    application.add_handler(CommandHandler("help", help_command))
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
