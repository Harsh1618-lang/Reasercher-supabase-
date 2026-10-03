#!/usr/bin/env python3
# Number Info Bot - Render Web Service 24/7 Deployment Edition
"""
Developer: HARSH HACKER
Description: Advanced OSINT Telegram Bot with Flask Web Server, Admin Panel & Contact Verification
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

# ============================================
# FLASK WEB SERVER (Render Port Binding)
# ============================================
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 OSINT Telegram Bot is running 24/7 successfully!"

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

BOT_TOKEN = "8408656202:AAF_0bplZdBBsr2C5fQWV3PH8KVHVyH-YbY"  
ADMIN_ID = 1420016904                                           
OWNER_USERNAME = "@Endgame55"                                   
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
        credits INTEGER DEFAULT 10,
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
    
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('maintenance', 'off')")
    c.execute("INSERT OR IGNORE INTO users (user_id, username, is_admin, phone_number) VALUES (?, ?, ?, ?)",
              (ADMIN_ID, 'admin', 1, 'Admin Verified'))
    
    conn.commit()
    conn.close()

init_database()

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
# API FETCH & HEALTH CHECK
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

def check_api_health():
    try:
        response = requests.get(API_URL.format(number="0000000000"), timeout=5)
        return "🟢 Online & Healthy" if response.status_code < 500 else "🟡 Degraded"
    except:
        return "🔴 Offline / Down"

# ============================================
# HACKING STYLE ANIMATED PROGRESS BAR
# ============================================
async def show_hacking_animation(msg_obj, phone):
    steps = [
        ("🔓 Bypassing target firewall...", "▒▒▒▒▒▒▒▒▒▒ 0%"),
        ("🔌 Establishing secure proxy tunnel...", "███▒▒▒▒▒▒▒ 30%"),
        ("⚡ Extracting intelligence records...", "██████▓▓▒▒ 70%"),
        ("✅ Decryption successful!", "██████████ 100%")
    ]
    for text, bar in steps:
        try:
            await msg_obj.edit_text(f"💻 *SYSTEM BREACH IN PROGRESS*\nTarget: `{phone}`\n\n{text}\n`{bar}`", parse_mode='Markdown')
            await asyncio.sleep(0.5)
        except:
            pass

# ============================================
# FORMAT RESPONSE
# ============================================
def format_response(data, phone):
    if not data or (isinstance(data, dict) and data.get('status') == False):
        error_msg = data.get('error', 'Unknown error') if isinstance(data, dict) else 'No data found'
        return f"❌ Error: {error_msg}"
    
    records = data.get('results', data) if isinstance(data, dict) else data
    if isinstance(records, dict):
        records = [records]
        
    if not records:
        return f"📱 No records found for `{phone}`"
    
    lines = []
    lines.append("🔍 *PHONE NUMBER REPORT* 🔍")
    lines.append("═══════════════════════")
    lines.append(f"📞 **Searched Number:** `{phone}`")
    lines.append(f"📊 **Total Records:** {len(records) if isinstance(records, list) else 1}")
    lines.append("")
    
    for i, rec in enumerate(records if isinstance(records, list) else [records], 1):
        lines.append(f"**Record #{i}**")
        name = rec.get('name') or rec.get('Name') or 'N/A'
        fname = rec.get('fname') or rec.get('father_name') or rec.get('FatherName') or 'N/A'
        mobile = rec.get('mobile') or rec.get('number') or phone
        alt = rec.get('alt') or rec.get('alternative_number') or 'N/A'
        aadhar = "[Aadhaar Omitted]"
        circle = rec.get('circle') or 'N/A'
        state = rec.get('state') or 'N/A'
        email = rec.get('email') or 'N/A'
        address = rec.get('address') or 'N/A'
        
        lines.append(f"👤 **Name:** {name}")
        lines.append(f"👨 **Father Name:** {fname}")
        lines.append(f"📱 **Mobile Number:** `{mobile}`")
        lines.append(f"🔄 **Alternative Number:** `{alt}`")
        lines.append(f"🆔 **Aadhaar ID:** `{aadhar}`")
        lines.append(f"📡 **Circle:** {circle}")
        lines.append(f"🗺️ **State:** {state}")
        lines.append(f"📧 **Email:** `{email}`")
        lines.append(f"🏠 **Address:** {address}")
        lines.append("---")
        
    lines.append(f"\n⚡ Powered by {OWNER_USERNAME} | Developed by HARSH HACKER")
    return "\n".join(lines)

# ============================================
# TELEGRAM HANDLERS
# ============================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    maint = db_get_one("SELECT value FROM settings WHERE key='maintenance'")['value']
    if maint == 'on' and user.id != ADMIN_ID:
        await update.message.reply_text("🚧 Bot is currently under maintenance. Please try again later.")
        return

    user_db = db_get_one("SELECT * FROM users WHERE user_id = ?", (user.id,))
    if user_db and user_db.get('is_banned') == 1:
        await update.message.reply_text("❌ Aapko bot use karne se block kar diya gaya hai.")
        return

    if not user_db or not user_db.get('phone_number'):
        contact_button = [[KeyboardButton("📱 Share Contact to Verify", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(contact_button, one_time_keyboard=True, resize_keyboard=True)
        db_execute("INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
                   (user.id, user.username, user.first_name), commit=True)
        await update.message.reply_text("⚠️ *Verification Required*\nPehle apna contact share karke verify karein!", parse_mode='Markdown', reply_markup=reply_markup)
        return

    await send_welcome_menu(update, context, user)

async def send_welcome_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    user_info = db_get_one("SELECT credits FROM users WHERE user_id = ?", (user.id,))
    credits = user_info['credits'] if user_info else 0
    
    welcome = f"""
👋 *Welcome to Phone Info OSINT Bot!*

💎 Remaining Credits: `{credits}`
Send me any mobile number to fetch details.
📌 *Example:* `9876543210`

⚡ Support: {OWNER_USERNAME}
    """
    
    if user.id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("🔵 📊 Admin Panel", callback_data="admin_panel")],
            [InlineKeyboardButton("🟢 👥 View All Users", callback_data="admin_users")],
            [InlineKeyboardButton("🟡 🩺 API Health", callback_data="api_health")]
        ]
        await update.message.reply_text(welcome + "\n\n*Admin Mode Active*", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(welcome, parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    contact = update.message.contact
    if contact and contact.user_id == user.id:
        phone_number = contact.phone_number
        db_execute("UPDATE users SET phone_number = ? WHERE user_id = ?", (phone_number, user.id), commit=True)
        await update.message.reply_text("✅ *Verification Successful!*", parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())
        await send_welcome_menu(update, context, user)
    else:
        await update.message.reply_text("❌ Kripya apna khud ka contact share karein.", reply_markup=ReplyKeyboardRemove())

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = db_get_one("SELECT * FROM users WHERE user_id = ?", (user.id,))
    if not user_data or user_data.get('is_banned') == 1: return
    if not user_data.get('phone_number'):
        await update.message.reply_text("⚠️ Pehle /start dabakar apna contact verify karein!")
        return
    if user_data['credits'] <= 0 and user.id != ADMIN_ID:
        await update.message.reply_text("❌ Aapke credits khatam ho chuke hain!")
        return

    if not context.args:
        await update.message.reply_text("❌ Please provide a phone number!\nExample: `/info 9876543210`", parse_mode='Markdown')
        return
    
    phone = context.args[0]
    msg = await update.message.reply_text("💻 *SYSTEM BREACH IN PROGRESS*\nInitializing...", parse_mode='Markdown')
    await show_hacking_animation(msg, phone)
    
    data = await get_phone_info(phone)
    db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, phone, json.dumps(data)), commit=True)
    db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
    
    formatted = format_response(data, phone)
    await msg.edit_text(formatted, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = db_get_one("SELECT * FROM users WHERE user_id = ?", (user.id,))
    if not user_data or user_data.get('is_banned') == 1: return
    if not user_data.get('phone_number'):
        await update.message.reply_text("⚠️ Pehle /start dabakar apna contact verify karein!")
        return
    if user_data['credits'] <= 0 and user.id != ADMIN_ID:
        await update.message.reply_text("❌ Aapke credits khatam ho chuke hain!")
        return

    text = update.message.text.strip()
    cleaned = re.sub(r'\D', '', text)
    if 10 <= len(cleaned) <= 15:
        msg = await update.message.reply_text("💻 *SYSTEM BREACH IN PROGRESS*\nInitializing...", parse_mode='Markdown')
        await show_hacking_animation(msg, cleaned)
        
        data = await get_phone_info(cleaned)
        db_execute("INSERT INTO searches (user_id, phone, response) VALUES (?, ?, ?)", (user.id, cleaned, json.dumps(data)), commit=True)
        db_execute("UPDATE users SET searches = searches + 1, credits = credits - 1 WHERE user_id = ?", (user.id,), commit=True)
        
        formatted = format_response(data, cleaned)
        keyboard = [[InlineKeyboardButton("🔵 🔄 Search Again", callback_data=f"check_{cleaned}")]]
        await msg.edit_text(formatted, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text("❌ Please send a valid mobile number.", parse_mode='Markdown')

# ============================================
# ADMIN PANEL & CALLBACKS
# ============================================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌ Unauthorized!", show_alert=True)
        return

    if data == "admin_panel":
        total_users = db_get_one("SELECT COUNT(*) as count FROM users")['count']
        total_searches = db_get_one("SELECT COUNT(*) as count FROM searches")['count']
        maint = db_get_one("SELECT value FROM settings WHERE key='maintenance'")['value']
        
        panel_text = f"""
📊 *ADVANCED ADMIN PANEL* (HARSH HACKER)
━━━━━━━━━━━━━━━━━━
👥 Total Users: `{total_users}`
🔍 Total Lookups: `{total_searches}`
🚧 Maintenance Mode: `{maint.upper()}`
⚡ API Status: `{check_api_health()}`
        """
        keyboard = [
            [InlineKeyboardButton("🟢 👥 View Users", callback_data="admin_users"), InlineKeyboardButton("🔴 🚫 Ban/Unban", callback_data="admin_ban_menu")],
            [InlineKeyboardButton("📢 📣 Broadcast", callback_data="admin_broadcast_prompt"), InlineKeyboardButton("📁 📊 Export CSV", callback_data="export_csv")],
            [InlineKeyboardButton("🛠️ 🔄 Toggle Maintenance", callback_data="toggle_maintenance"), InlineKeyboardButton("❌ 🔙 Close", callback_data="close_panel")]
        ]
        await query.message.edit_text(panel_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif data == "admin_users":
        users = db_get_all("SELECT user_id, username, first_name, phone_number, searches, credits, is_banned FROM users ORDER BY joined_date DESC LIMIT 10")
        text = "👥 *Recent Users List (Last 10)*\n━━━━━━━━━━━━━━━━━━━━\n"
        for u in users:
            status = "🔴 Banned" if u['is_banned'] else "🟢 Active"
            text += f"🆔 ID: `{u['user_id']}` | {status}\n👤 Name: {u['first_name']}\n📱 Phone: `{u['phone_number']}`\n🔍 Searches: {u['searches']} | 💎 Credits: {u['credits']}\n--------------------\n"
        keyboard = [[InlineKeyboardButton("🔵 📊 Back to Panel", callback_data="admin_panel")]]
        await query.message.edit_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "api_health":
        health = check_api_health()
        await query.message.reply_text(f"🩺 *API Health Status*\n\n{health}", parse_mode='Markdown')

    elif data == "toggle_maintenance":
        current = db_get_one("SELECT value FROM settings WHERE key='maintenance'")['value']
        new_val = 'off' if current == 'on' else 'on'
        db_execute("UPDATE settings SET value = ? WHERE key = 'maintenance'", (new_val,), commit=True)
        await query.answer(f"Maintenance mode set to {new_val.upper()}", show_alert=True)
        query.data = "admin_panel"
        await button_callback(update, context)

    elif data == "export_csv":
        users = db_get_all("SELECT user_id, username, first_name, phone_number, searches, credits, joined_date FROM users")
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['User ID', 'Username', 'First Name', 'Phone', 'Searches', 'Credits', 'Joined Date'])
        for u in users:
            writer.writerow([u['user_id'], u['username'], u['first_name'], u['phone_number'], u['searches'], u['credits'], u['joined_date']])
        output.seek(0)
        file_bytes = io.BytesIO(output.getvalue().encode('utf-8'))
        await context.bot.send_document(chat_id=ADMIN_ID, document=InputFile(file_bytes, filename="users_export.csv"), caption="📁 *All Users Data Export*", parse_mode='Markdown')

    elif data == "admin_ban_menu":
        await query.message.reply_text("💡 Use command:\n`/ban <user_id>`\n`/unban <user_id>`", parse_mode='Markdown')

    elif data == "admin_broadcast_prompt":
        await query.message.reply_text("💡 Use command:\n`/broadcast <message>`", parse_mode='Markdown')

    elif data == "close_panel":
        await query.message.delete()
        
    elif data.startswith('check_'):
        phone = data[6:]
        msg = await query.message.reply_text("💻 *SYSTEM BREACH IN PROGRESS*\nInitializing...", parse_mode='Markdown')
        await show_hacking_animation(msg, phone)
        info = await get_phone_info(phone)
        await msg.edit_text(format_response(info, phone), parse_mode='Markdown')

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args: return
    uid = context.args[0]
    db_execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (uid,), commit=True)
    await update.message.reply_text(f"🚫 User `{uid}` banned.", parse_mode='Markdown')

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args: return
    uid = context.args[0]
    db_execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (uid,), commit=True)
    await update.message.reply_text(f"✅ User `{uid}` unbanned.", parse_mode='Markdown')

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args: return
    msg = ' '.join(context.args)
    users = db_get_all("SELECT user_id FROM users")
    sent = 0
    for u in users:
        try:
            await context.bot.send_message(chat_id=u['user_id'], text=f"📢 *ANNOUNCEMENT (HARSH HACKER)*\n\n{msg}", parse_mode='Markdown')
            sent += 1
        except: pass
    await update.message.reply_text(f"📢 Broadcast sent to {sent} users.")

async def user_inspect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args: return
    target_id = context.args[0]
    user_info = db_get_one("SELECT * FROM users WHERE user_id = ?", (target_id,))
    if not user_info:
        await update.message.reply_text("❌ User not found.")
        return
    searches = db_get_all("SELECT phone, timestamp FROM searches WHERE user_id = ? ORDER BY timestamp DESC LIMIT 10", (target_id,))
    text = f"👤 *USER DETAILS*\nID: `{user_info['user_id']}`\nName: {user_info['first_name']}\nPhone: `{user_info['phone_number']}`\nCredits: {user_info['credits']} | Searches: {user_info['searches']}\n\n📜 *Recent Searches:*\n"
    for s in searches: text += f"• `{s['phone']}` ({s['timestamp']})\n"
    await update.message.reply_text(text, parse_mode='Markdown')

def main():
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    print("=" * 50)
    print("🚀 HARSH HACKER OSINT TELEGRAM BOT STARTING...")
    print("=" * 50)
    
    application = Application.builder().token(BOT_TOKEN).http_version("1.1").get_updates_http_version("1.1").build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("user", user_inspect_command))
    application.add_handler(CommandHandler("ban", ban_command))
    application.add_handler(CommandHandler("unban", unban_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
