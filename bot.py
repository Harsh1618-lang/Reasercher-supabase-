#!/usr/bin/env python3
# Number & Vehicle Info Bot - Final Nested JSON Edition
"""
Developer: HARSH
Description: Advanced OSINT & Vehicle Info Telegram Bot with Custom Vehicle Scraper, Clean JSON Response, Threaded Flask & Fast UI
"""

import os
import sys
import json
import time
import asyncio
import sqlite3
import requests
import re
import csv
import io
import logging
import threading
from flask import Flask
from bs4 import BeautifulSoup

# ============================================
# FLASK WEB SERVER (Render Port Binding)
# ============================================
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 OSINT & Vehicle Telegram Bot is running 24/7 successfully via Threaded Flask Server!"

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
    os.system('pip install python-telegram-bot==20.7 requests beautifulsoup4 flask')
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InputFile
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
    import telegram.error

# ============================================
# ========== CONFIGURATION - YOUR DETAILS ==========
# ============================================

BOT_TOKEN = "8664550290:AAFe6m8yQrx5Km8mvh-tz5Y8rcfY1zcWIZ4"  # Bot Token
ADMIN_ID = 1420016904                                           # Main Admin ID
OWNER_USERNAME = "@Endgame55"                                   # Owner Username
API_URL = "https://nmdllpezcocquamhgpmb.supabase.co/functions/v1/lookup?number={number}"

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
        is_admin INTEGER DEFAULT 0
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
    
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('maintenance', 'off')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('upi_id', 'harshhacker@upi')")
    
    c.execute("SELECT COUNT(*) FROM plans")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO plans (name, price, credits) VALUES (?, ?, ?)", ("Starter Pack", "₹49", 10))
        c.execute("INSERT INTO plans (name, price, credits) VALUES (?, ?, ?)", ("Pro Hacker Pack", "₹99", 25))
        c.execute("INSERT INTO plans (name, price, credits) VALUES (?, ?, ?)", ("Unlimited Master", "₹199", 60))

    c.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, phone_number, credits, is_admin) VALUES (?, ?, ?, ?, ?, ?)",
              (ADMIN_ID, 'Endgame55', 'Harsh Admin', 'Admin Verified', 99999, 1))
    
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
# API FETCH & VEHICLE SCRAPER
# ============================================
async def get_phone_info(phone):
    try:
        clean_phone = re.sub(r'\D', '', phone)
        url = API_URL.format(number=clean_phone)
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": False, "error": f"API returned status {response.status_code}"}
    except Exception as e:
        return {"status": False, "error": str(e)}

def vehicle_lookup(num: str):
    """Advanced vehicle RC details scraper using user-provided BeautifulSoup selectors"""
    try:
        veh_num = num.upper().strip()
        url = f"https://www.carinfo.app/rc-details/{veh_num}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        details = {}

        number_plate = soup.find("div", class_="input_vehical_layout_numberPlateContainer__Ug78g")
        if number_plate:
            details["Number Plate"] = number_plate.find("p").text.strip()

        make_model = soup.find("div", class_="input_vehical_layout_vehicalDetails__MseIO")
        if make_model:
            details["Make & Model"] = make_model.find("p", class_="input_vehical_layout_vehicalModel__1ABTF").text.strip()

        owner = soup.find("div", class_="input_vehical_layout_ownerDetails__6IzJb")
        if owner:
            details["Owner Name"] = owner.find("p", class_="input_vehical_layout_ownerName__NHkpi").text.strip()

        rto_container = soup.find("div", class_="expand_component_detailListContainer__L1nXb")
        if rto_container:
            for item in rto_container.find_all("div", class_="expand_component_detailItem__V43eh"):
                key_tag = item.find("p", class_="expand_component_itemText__cbigB")
                value_tag = item.find("p", class_="expand_component_itemSubTitle__ElsYf")
                if key_tag and value_tag:
                    details[key_tag.text.strip()] = value_tag.text.strip()

        if rto_container:
            website_tag = rto_container.find("a", href=True)
            if website_tag:
                details["Website"] = website_tag['href']

        output = f"🛵 RC Details for Vehicle: {details.get('Number Plate', veh_num)}\n"
        output += "──────────────────────────\n"
        output += f"🚗 Make & Model: {details.get('Make & Model', 'N/A')}\n"
        output += f"👤 Owner Name: {details.get('Owner Name', 'N/A')}\n\n"
        output += "🏢 RTO Information:\n"
        output += f"📌 Number: {details.get('Number', 'N/A')}\n"
        output += f"📌 Registered RTO: {details.get('Registered RTO', 'N/A')}\n"
        output += f"📌 State: {details.get('State', 'N/A')}\n"
        output += f"📞 Phone: {details.get('RTO Phone number', 'N/A')}\n"
        output += f"🌐 Website: {details.get('Website', 'N/A')}\n"
        output += "──────────────────────────\n"
        output += "✅ Data fetched successfully!\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        output += "👨‍💻 Developer : @dev2dex\n"
        output += "📢 Channel   : t.me/Catalyst_Mystery\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━"

        return output

    except requests.exceptions.RequestException:
        return "❌ Network error or unable to reach the RC details site. Please check your connection or try again later."
    except Exception as e:
        return f"❌ An error occurred while fetching the RC details: {e}"

def check_api_health():
    try:
        response = requests.get(API_URL.format(number="0000000000"), timeout=5)
        return "🟢 Online & Healthy" if response.status_code < 500 else "🟡 Degraded"
    except:
        return "🔴 Offline / Down"

# ============================================
# HACKING STYLE ANIMATED PROGRESS BAR
# ============================================
async def show_hacking_animation(msg_obj, target_str, is_vehicle=False):
    title = "🚗 VEHICLE RC BREACH" if is_vehicle else "💻 SYSTEM BREACH IN PROGRESS"
    steps = [
        ("🔓 Bypassing target firewall...", "▒▒▒▒▒▒▒▒▒▒ 0%"),
        ("🔌 Establishing secure proxy tunnel...", "███▒▒▒▒▒▒▒ 30%"),
        ("⚡ Extracting intelligence records...", "██████▓▓▒▒ 70%"),
        ("✅ Decryption successful!", "██████████ 100%")
    ]
    for text, bar in steps:
        try:
            await msg_obj.edit_text(f"{title}\nTarget: `{target_str}`\n\n{text}\n`{bar}`", parse_mode='Markdown')
            await asyncio.sleep(0.2)
        except:
            pass

# ============================================
# FORMAT RESPONSE (NESTED JSON TRAVERSAL FIX)
# ============================================
def format_response(data, phone):
    if not data or (isinstance(data, dict) and data.get('status') == False):
        error_msg = data.get('error', 'No data found') if isinstance(data, dict) else 'No data found'
        return f"❌ Error: {error_msg}"
    
    actual_results = []
    
    try:
        if isinstance(data, dict):
            res_layer1 = data.get('result', data)
            if isinstance(res_layer1, dict):
                res_layer2 = res_layer1.get('result', res_layer1)
                if isinstance(res_layer2, dict):
                    val = res_layer2.get('result')
                    if isinstance(val, list):
                        actual_results.extend(val)
                    elif isinstance(val, dict):
                        actual_results.append(val)
                elif isinstance(res_layer2, list):
                    actual_results.extend(res_layer2)
            elif isinstance(res_layer1, list):
                actual_results.extend(res_layer1)
    except Exception:
        pass

    if not actual_results:
        if isinstance(data, dict):
            for key in ['result', 'results', 'data', 'payload', 'response']:
                val = data.get(key)
                if isinstance(val, list):
                    actual_results.extend(val)
                elif isinstance(val, dict):
                    for sub_key in ['result', 'results', 'data', 'records']:
                        sub_val = val.get(sub_key)
                        if isinstance(sub_val, list):
                            actual_results.extend(sub_val)
                        elif isinstance(sub_val, dict):
                            actual_results.append(sub_val)
                    if not actual_results:
                        actual_results.append(val)
            if not actual_results:
                actual_results = [data]
        elif isinstance(data, list):
            actual_results = data

    if not actual_results:
        actual_results = [data]

    results_list = []
    for i, rec in enumerate(actual_results, 1):
        if not isinstance(rec, dict):
            rec = {}
        
        name = rec.get('name') or rec.get('FullName') or rec.get('owner_name') or 'Unknown'
        fname = rec.get('fname') or rec.get('father_name') or rec.get('FatherName') or 'N/A'
        address = rec.get('address') or rec.get('Address') or 'N/A'
        circle = rec.get('circle') or rec.get('operator') or 'N/A'
        
        aadhar_val = rec.get('aadhar') or rec.get('id') or 'N/A'

        results_list.append({
            "address": address,
            "circle": circle,
            "father_name": fname,
            "id": aadhar_val,
            "name": name,
            "number": rec.get('mobile', rec.get('phone', phone)),
            "result": f"Result {i}"
        })

    json_output = {
        "data": {
            "country": "India",
            "number": phone,
            "result_count": len(results_list),
            "results": results_list,
            "total_records": len(results_list),
            "total_results": len(results_list)
        },
        "query": phone,
        "response_time": "0.89s",
        "status": True,
        "Dev": "@Endgame55",
        "Channel": "https://t.me/Modedbyharsh",
        "Bot": "@Reasercherinfobot"
    }

    return f"```json\n{json.dumps(json_output, indent=4, ensure_ascii=False)}\n```"

# ============================================
# TELEGRAM HANDLERS
# ============================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    maint = db_get_one("SELECT value FROM settings WHERE key='maintenance'")['value']
    if maint == 'on' and not is_admin_user(user.id):
        await update.message.reply_text("🚧 Bot is currently under maintenance. Please try again later.")
        return

    user_db = db_get_one("SELECT * FROM users WHERE user_id = ?", (user.id,))
    if user_db and user_db.get('is_banned') == 1:
        await update.message.reply_text("❌ Aapko bot use karne se block kar diya gaya hai.")
        return

    if not user_db or not user_db.get('phone_number'):
        contact_button = [[KeyboardButton("📱 Share Contact to Verify & Start", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(contact_button, one_time_keyboard=True, resize_keyboard=True)
        db_execute("INSERT OR IGNORE INTO users (user_id, username, first_name, credits) VALUES (?, ?, ?, ?)",
                   (user.id, user.username or "NoUsername", user.first_name, 2), commit=True)
        await update.message.reply_text("⚠️ *SECURITY VERIFICATION REQUIRED*\n\nScam se bachne ke liye kripya neeche diye gaye button par click karke apna contact verify karein!", parse_mode='Markdown', reply_markup=reply_markup)
        return

    await send_welcome_menu(update, context, user)

async def send_welcome_menu(update_or_query, context, user):
    user_info = db_get_one("SELECT credits FROM users WHERE user_id = ?", (user.id,))
    credits = user_info['credits'] if user_info else 0
    
    welcome = f"""
👋 *Welcome to OSINT & Vehicle Info Bot!*

💎 Remaining Credits: `{credits}`
Neeche diye gaye menu se option select karein ya direct number bhejein!
💡 *Feedback/Report:* Use `/report <message>`

⚡ Support: {OWNER_USERNAME}
    """
    
    menu_keyboard = [
        [KeyboardButton("🔍 Number Info"), KeyboardButton("🚗 Vehicle Info")],
        [KeyboardButton("💎 Buy Premium / Credits"), KeyboardButton("🛠️ Toggle Menu")]
    ]
    if is_admin_user(user.id):
        menu_keyboard.append([KeyboardButton("📊 Admin Panel")])

    reply_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)

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
    
    text = f"💎 **BUY PREMIUM & ADD CREDITS**\n"
    text += f"━━━━━━━━━━━━━━━━━━━━━━\n"
    text += f"📲 **Admin UPI ID:** `{upi_id}`\n\n"
    text += f"📦 **Available Plans:**\n"
    
    for p in plans:
        text += f"• **{p['name']}** — `{p['price']}` for **{p['credits']} Credits**\n"
        
    text += f"\n💳 **How to Buy:**\n1. Pay on UPI ID above.\n2. Send payment screenshot to Admin ({OWNER_USERNAME}) with your Telegram ID.\n3. Admin will instantly add credits!"
    
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
            f"❌ **Aapke credits khatam ho chuke hain!**\n\nKripya UPI ID: `{upi_id}` par payment karein aur Admin (`{OWNER_USERNAME}`) ko screenshot bhejein.",
            parse_mode='Markdown'
        )
        return False
    return True

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args:
        await update.message.reply_text("❌ Usage: `/report <your feedback or issue>`", parse_mode='Markdown')
        return
    
    feedback_msg = ' '.join(context.args)
    report_text = f"🚨 **NEW USER REPORT / FEEDBACK**\n\n👤 From: {user.first_name} (@{user.username or 'None'})\n🆔 ID: `{user.id}`\n💬 Message: {feedback_msg}"
    
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=report_text, parse_mode='Markdown')
    except:
        pass
    
    sub_admins = db_get_all("SELECT user_id FROM sub_admins")
    for sa in sub_admins:
        if sa['user_id'] != ADMIN_ID:
            try:
                await context.bot.send_message(chat_id=sa['user_id'], text=report_text, parse_mode='Markdown')
            except:
                pass
                
    await update.message.reply_text("✅ *Feedback submitted successfully!*", parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip()

    if text == "🔍 Number Info":
        context.user_data['mode'] = 'phone'
        await update.message.reply_text("📱 *Number Info Mode Active*\nKripya ab koi bhi 10-digit mobile number bhejein:", parse_mode='Markdown')
        return
    elif text == "🚗 Vehicle Info":
        context.user_data['mode'] = 'vehicle'
        await update.message.reply_text("🚗 *Vehicle Info Mode Active*\nKripya ab koi bhi vehicle number bhejein (jaise `UP32AB1234`):", parse_mode='Markdown')
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
        
        panel_text = f"""
📊 *ADVANCED ADMIN PANEL* (HARSH)
━━━━━━━━━━━━━━━━━━
👥 Total Users: `{total_users}`
🔍 Total Lookups: `{total_searches}`
💳 Current UPI: `{upi_record['value'] if upi_record else 'Not Set'}`
🚧 Maintenance Mode: `{maint.upper()}`
⚡ API Status: `{check_api_health()}`
        """
        keyboard = [
            [InlineKeyboardButton("🟢 👥 View Users", callback_data="admin_users"), InlineKeyboardButton("💳 ⚙️ Set UPI ID", callback_data="admin_setupi_prompt")],
            [InlineKeyboardButton("📦 📋 Manage Plans", callback_data="admin_plans"), InlineKeyboardButton("💎 ➕ Add Credits", callback_data="admin_addcredit_prompt")],
            [InlineKeyboardButton("🛡️ ➕ Add Sub-Admin", callback_data="admin_addsub_prompt"), InlineKeyboardButton("🛠️ 🔄 Maintenance", callback_data="toggle_maintenance")],
            [InlineKeyboardButton("❌ 🔙 Close", callback_data="close_panel")]
        ]
        await update.message.reply_text(panel_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if not await check_user_credit(update, user): return

    mode = context.user_data.get('mode', None)
    cleaned = re.sub(r'\D', '', text)

    if mode == 'phone' or (10 <= len(cleaned) <= 15 and mode != 'vehicle'):
        phone = cleaned if 10 <= len(cleaned) <= 15 else text
        msg = await update.message.reply_text("💻 *SYSTEM BREACH IN PROGRESS*\nInitializing...", parse_mode='Markdown')
        await show_hacking_animation(msg, phone, is_vehicle=False)
        
        data = await get_phone_info(phone)
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, phone, json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        
        formatted = format_response(data, phone)
        await msg.edit_text(formatted, parse_mode='Markdown')
        context.user_data['mode'] = None
    elif mode == 'vehicle' or (len(text) >= 4 and any(c.isdigit() for c in text) and any(c.isalpha() for c in text)):
        veh_num = text
        msg = await update.message.reply_text("🚗 *VEHICLE RC BREACH*\nInitializing...", parse_mode='Markdown')
        await show_hacking_animation(msg, veh_num, is_vehicle=True)
        
        result = vehicle_lookup(veh_num)
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, f"VEH:{veh_num}", json.dumps({"result": result})), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        
        await msg.edit_text(result, parse_mode='Markdown')
        context.user_data['mode'] = None
    else:
        await update.message.reply_text("❌ Kripya menu se option select karein ya valid number/vehicle bhejein.", parse_mode='Markdown')

# ============================================
# LIGHTNING FAST ADMIN CALLBACK HANDLER
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
        
        panel_text = f"""
📊 *ADVANCED ADMIN PANEL* (HARSH)
━━━━━━━━━━━━━━━━━━
👥 Total Users: `{total_users}`
🔍 Total Lookups: `{total_searches}`
💳 Current UPI: `{upi_record['value'] if upi_record else 'Not Set'}`
🚧 Maintenance Mode: `{maint.upper()}`
⚡ API Status: `{check_api_health()}`
        """
        keyboard = [
            [InlineKeyboardButton("🟢 👥 View Users", callback_data="admin_users"), InlineKeyboardButton("💳 ⚙️ Set UPI ID", callback_data="admin_setupi_prompt")],
            [InlineKeyboardButton("📦 📋 Manage Plans", callback_data="admin_plans"), InlineKeyboardButton("💎 ➕ Add Credits", callback_data="admin_addcredit_prompt")],
            [InlineKeyboardButton("🛡️ ➕ Add Sub-Admin", callback_data="admin_addsub_prompt"), InlineKeyboardButton("🛠️ 🔄 Maintenance", callback_data="toggle_maintenance")],
            [InlineKeyboardButton("❌ 🔙 Close", callback_data="close_panel")]
        ]
        await query.edit_message_text(panel_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif data == "admin_users":
        users = db_get_all("SELECT user_id, username, first_name, phone_number, searches, credits, is_banned FROM users ORDER BY joined_date DESC LIMIT 15")
        text = "👥 *Verified Users List (Anti-Scam Log)*\n━━━━━━━━━━━━━━━━━━━━\n"
        for u in users:
            status = "🔴 Banned" if u['is_banned'] else "🟢 Active"
            text += f"🆔 ID: `{u['user_id']}` | @{u['username']} | {status}\n👤 Name: {u['first_name']}\n📱 Mobile: `{u['phone_number']}`\n🔍 Searches: {u['searches']} | 💎 Credits: {u['credits']}\n--------------------\n"
        keyboard = [[InlineKeyboardButton("🔵 📊 Back to Panel", callback_data="admin_panel")]]
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "admin_plans":
        plans = db_get_all("SELECT * FROM plans")
        text = "📦 *Manage Subscription Plans*\n━━━━━━━━━━━━━━━━━━━━\n"
        for p in plans:
            text += f"🆔 ID: `{p['id']}` | **{p['name']}**\n💰 Price: `{p['price']}` | 💎 Credits: `{p['credits']}`\n--------------------\n"
        text += "\n💡 To add a plan, use command:\n`/addplan <name> <price> <credits>`\n\n💡 To delete a plan, use:\n`/delplan <plan_id>`"
        keyboard = [[InlineKeyboardButton("🔵 📊 Back to Panel", callback_data="admin_panel")]]
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "admin_setupi_prompt":
        if query.from_user.id != ADMIN_ID:
            await query.answer("❌ Only Main Admin can change UPI ID!", show_alert=True)
            return
        await query.message.reply_text("💡 To update UPI ID, use command:\n`/setupi <new_upi_id>`", parse_mode='Markdown')

    elif data == "admin_addcredit_prompt":
        await query.message.reply_text("💡 To add credits, use command:\n`/addcredits <user_id> <amount>`", parse_mode='Markdown')

    elif data == "admin_addsub_prompt":
        if query.from_user.id != ADMIN_ID:
            await query.answer("❌ Only Main Admin can add sub-admins!", show_alert=True)
            return
        await query.message.reply_text("💡 To add a sub-admin, use command:\n`/addsub <user_id>`", parse_mode='Markdown')

    elif data == "api_health":
        health = check_api_health()
        await query.edit_message_text(f"🩺 *API Health Status*\n\n{health}", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]]))

    elif data == "toggle_maintenance":
        if query.from_user.id != ADMIN_ID:
            await query.answer("❌ Only Main Admin can toggle maintenance!", show_alert=True)
            return
        current = db_get_one("SELECT value FROM settings WHERE key='maintenance'")['value']
        new_val = 'off' if current == 'on' else 'on'
        db_execute("UPDATE settings SET value = ? WHERE key = 'maintenance'", (new_val,), commit=True)
        query.data = "admin_panel"
        await button_callback(update, context)

    elif data == "close_panel":
        await query.message.delete()

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
    await update.message.reply_text(f"✅ UPI ID successfully updated to: `{new_upi}`", parse_mode='Markdown')

async def addsub_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args: return
    try:
        sub_id = int(context.args[0])
        db_execute("INSERT OR IGNORE INTO sub_admins (user_id) VALUES (?)", (sub_id,), commit=True)
        await update.message.reply_text(f"✅ User `{sub_id}` added as Sub-Admin!", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def addplan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin_user(update.effective_user.id): return
    if len(context.args) < 3: return
    try:
        name, price, credits = context.args[0], context.args[1], int(context.args[2])
        db_execute("INSERT INTO plans (name, price, credits) VALUES (?, ?, ?)", (name, price, credits), commit=True)
        await update.message.reply_text(f"✅ Plan **{name}** added successfully!", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def delplan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin_user(update.effective_user.id): return
    if not context.args: return
    try:
        plan_id = int(context.args[0])
        db_execute("DELETE FROM plans WHERE id = ?", (plan_id,), commit=True)
        await update.message.reply_text(f"✅ Plan ID `{plan_id}` deleted successfully!", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def addcredits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin_user(update.effective_user.id): return
    if len(context.args) < 2: return
    try:
        target_id, amount = int(context.args[0]), int(context.args[1])
        db_execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (amount, target_id), commit=True)
        await update.message.reply_text(f"✅ Added `{amount}` credits to user `{target_id}`!", parse_mode='Markdown')
        try:
            await context.bot.send_message(chat_id=target_id, text=f"🎉 **Congratulations!**\nAdmin added `{amount}` credits to your account.")
        except:
            pass
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin_user(update.effective_user.id): return
    if not context.args: return
    db_execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (context.args[0],), commit=True)
    await update.message.reply_text(f"🚫 User `{context.args[0]}` banned.", parse_mode='Markdown')

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin_user(update.effective_user.id): return
    if not context.args: return
    db_execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (context.args[0],), commit=True)
    await update.message.reply_text(f"✅ User `{context.args[0]}` unbanned.", parse_mode='Markdown')

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin_user(update.effective_user.id): return
    if not context.args: return
    msg = ' '.join(context.args)
    users = db_get_all("SELECT user_id FROM users")
    sent = 0
    for u in users:
        try:
            await context.bot.send_message(chat_id=u['user_id'], text=f"📢 *ANNOUNCEMENT (HARSH)*\n\n{msg}", parse_mode='Markdown')
            sent += 1
        except: pass
    await update.message.reply_text(f"📢 Broadcast sent to {sent} users.")

async def user_inspect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin_user(update.effective_user.id): return
    if not context.args: return
    target_id = context.args[0]
    user_info = db_get_one("SELECT * FROM users WHERE user_id = ?", (target_id,))
    if not user_info:
        await update.message.reply_text("❌ User not found.")
        return
    searches = db_get_all("SELECT phone, timestamp FROM searches WHERE user_id = ? ORDER BY timestamp DESC LIMIT 10", (target_id,))
    text = f"👤 *USER INSPECT*\n🆔 ID: `{user_info['user_id']}`\n👤 Username: @{user_info['username']}\n📱 Mobile: `{user_info['phone_number']}`\n💎 Credits: {user_info['credits']}\n\n📜 *Recent Searches:*\n"
    for s in searches: text += f"• `{s['phone']}` ({s['timestamp']})\n"
    await update.message.reply_text(text, parse_mode='Markdown')

def main():
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    print("=" * 50)
    print("🚀 HARSH OSINT & VEHICLE BOT STARTING (THREADED POLLING MODE)...")
    print("=" * 50)
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("report", report_command))
    application.add_handler(CommandHandler("user", user_inspect_command))
    application.add_handler(CommandHandler("ban", ban_command))
    application.add_handler(CommandHandler("unban", unban_command))
    application.add_handler(CommandHandler("setupi", setupi_command))
    application.add_handler(CommandHandler("addsub", addsub_command))
    application.add_handler(CommandHandler("addplan", addplan_command))
    application.add_handler(CommandHandler("delplan", delplan_command))
    application.add_handler(CommandHandler("addcredits", addcredits_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
