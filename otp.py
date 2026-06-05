import telebot
from telebot import types
import sqlite3
import requests
import re
import threading
import time
from datetime import datetime, timedelta

# === CONFIGURATION ===
TOKEN = '8727256915:AAFPulBKZkcxs6ydHPw8h70dHFmlWQ0nOyU' 
ADMIN_ID = 8244470589
CHANNEL_USERNAME = "@do_nothing_1" 
CREDIT = "DEEPAK SAINI"

# === BOT ECONOMICS (SUBSCRIPTION MODEL) ===
REFERS_FOR_NEW_PLAN = 10
REFERS_FOR_RENEWAL = 8
PLAN_DURATION_HOURS = 24

# === OTP API CONFIG ===
API_URL = "http://147.135.212.197/crapi/st/viewstats"
API_TOKEN = "RFdUREJBUzR9T4dVc49ndmFra1NYV5CIhpGVcnaOYmqHhJZXfYGJSQ=="

bot = telebot.TeleBot(TOKEN)
db_lock = threading.Lock()

# === FULL COUNTRY MAP ===
COUNTRY_MAP = {
    "1": ("United States", "🇺🇸"), "7": ("Russia", "🇷🇺"),
    "20": ("Egypt", "🇪🇬"), "27": ("South Africa", "🇿🇦"),
    "30": ("Greece", "🇬🇷"), "31": ("Netherlands", "🇳🇱"),
    "32": ("Belgium", "🇧🇪"), "33": ("France", "🇫🇷"),
    "34": ("Spain", "🇪🇸"), "36": ("Hungary", "🇭🇺"),
    "39": ("Italy", "🇮🇹"), "40": ("Romania", "🇷🇴"),
    "41": ("Switzerland", "🇨🇭"), "43": ("Austria", "🇦🇹"),
    "44": ("United Kingdom", "🇬🇧"), "45": ("Denmark", "🇩🇰"),
    "46": ("Sweden", "🇸🇪"), "47": ("Norway", "🇳🇴"),
    "48": ("Poland", "🇵🇱"), "49": ("Germany", "🇩🇪"),
    "51": ("Peru", "🇵🇪"), "52": ("Mexico", "🇲🇽"),
    "53": ("Cuba", "🇨🇺"), "54": ("Argentina", "🇦🇷"),
    "55": ("Brazil", "🇧🇷"), "56": ("Chile", "🇨🇱"),
    "57": ("Colombia", "🇨🇴"), "58": ("Venezuela", "🇻🇪"),
    "60": ("Malaysia", "🇲🇾"), "61": ("Australia", "🇦🇺"),
    "62": ("Indonesia", "🇮🇩"), "63": ("Philippines", "🇵🇭"),
    "64": ("New Zealand", "🇳🇿"), "65": ("Singapore", "🇸🇬"),
    "66": ("Thailand", "🇹🇭"), "81": ("Japan", "🇯🇵"),
    "82": ("South Korea", "🇰🇷"), "84": ("Vietnam", "🇻🇳"),
    "86": ("China", "🇨🇳"), "91": ("India", "🇮🇳"),
    "92": ("Pakistan", "🇵🇰"), "93": ("Afghanistan", "🇦🇫"),
    "94": ("Sri Lanka", "🇱🇰"), "95": ("Myanmar", "🇲🇲"),
    "98": ("Iran", "🇮🇷"), "211": ("South Sudan", "🇸🇸"),
    "212": ("Morocco", "🇲🇦"), "213": ("Algeria", "🇩🇿"),
    "216": ("Tunisia", "🇹🇳"), "218": ("Libya", "🇱🇾"),
    "220": ("Gambia", "🇬🇲"), "221": ("Senegal", "🇸🇳"),
    "222": ("Mauritania", "🇲🇷"), "223": ("Mali", "🇲🇱"),
    "224": ("Guinea", "🇬🇳"), "225": ("Ivory Coast", "🇨🇮"),
    "226": ("Burkina Faso", "🇧🇫"), "227": ("Niger", "🇳🇪"),
    "228": ("Togo", "🇹🇬"), "229": ("Benin", "🇧🇯"),
    "230": ("Mauritius", "🇲🇺"), "231": ("Liberia", "🇱🇷"),
    "232": ("Sierra Leone", "🇸🇱"), "233": ("Ghana", "🇬🇭"),
    "234": ("Nigeria", "🇳🇬"), "235": ("Chad", "🇹🇩"),
    "236": ("Central African Republic", "🇨🇫"), "237": ("Cameroon", "🇨🇲"),
    "238": ("Cape Verde", "🇨🇻"), "239": ("Sao Tome and Principe", "🇸🇹"),
    "240": ("Equatorial Guinea", "🇬🇶"), "241": ("Gabon", "🇬🇦"),
    "242": ("Congo", "🇨🇬"), "243": ("DR Congo", "🇨🇩"),
    "244": ("Angola", "🇦🇴"), "248": ("Seychelles", "🇸🇨"),
    "249": ("Sudan", "🇸🇩"), "250": ("Rwanda", "🇷🇼"),
    "251": ("Ethiopia", "🇪🇹"), "252": ("Somalia", "🇸🇴"),
    "253": ("Djibouti", "🇩🇯"), "254": ("Kenya", "🇰🇪"),
    "255": ("Tanzania", "🇹🇿"), "256": ("Uganda", "🇺🇬"),
    "257": ("Burundi", "🇧🇮"), "258": ("Mozambique", "🇲🇿"),
    "260": ("Zambia", "🇿🇲"), "261": ("Madagascar", "🇲🇬"),
    "262": ("Reunion", "🇷🇪"), "263": ("Zimbabwe", "🇿🇼"),
    "264": ("Namibia", "🇳🇦"), "265": ("Malawi", "🇲🇼"),
    "266": ("Lesotho", "🇱🇸"), "267": ("Botswana", "🇧🇼"),
    "268": ("Eswatini", "🇸🇿"), "269": ("Comoros", "🇰🇲"),
    "290": ("Saint Helena", "🇸🇭"), "291": ("Eritrea", "🇪🇷"),
    "297": ("Aruba", "🇦🇼"), "298": ("Faroe Islands", "🇫🇴"),
    "299": ("Greenland", "🇬🇱"), "350": ("Gibraltar", "🇬🇮"),
    "351": ("Portugal", "🇵🇹"), "352": ("Luxembourg", "🇱🇺"),
    "353": ("Ireland", "🇮🇪"), "354": ("Iceland", "🇮🇸"),
    "355": ("Albania", "🇦🇱"), "356": ("Malta", "🇲🇹"),
    "357": ("Cyprus", "🇨🇾"), "358": ("Finland", "🇫🇮"),
    "359": ("Bulgaria", "🇧🇬"), "370": ("Lithuania", "🇱🇹"),
    "371": ("Latvia", "🇱🇻"), "372": ("Estonia", "🇪🇪"),
    "373": ("Moldova", "🇲🇩"), "374": ("Armenia", "🇦🇲"),
    "375": ("Belarus", "🇧🇾"), "376": ("Andorra", "🇦🇩"),
    "377": ("Monaco", "🇲🇨"), "378": ("San Marino", "🇸🇲"),
    "380": ("Ukraine", "🇺🇦"), "381": ("Serbia", "🇷🇸"),
    "382": ("Montenegro", "🇲🇪"), "383": ("Kosovo", "🇽🇰"),
    "385": ("Croatia", "🇭🇷"), "386": ("Slovenia", "🇸🇮"),
    "387": ("Bosnia and Herzegovina", "🇧🇦"), "389": ("North Macedonia", "🇲🇰"),
    "420": ("Czech Republic", "🇨🇿"), "421": ("Slovakia", "🇸🇰"),
    "423": ("Liechtenstein", "🇱🇮"), "500": ("Falkland Islands", "🇫🇰"),
    "501": ("Belize", "🇧🇿"), "502": ("Guatemala", "🇬🇹"),
    "503": ("El Salvador", "🇸🇻"), "504": ("Honduras", "🇭🇳"),
    "505": ("Nicaragua", "🇳🇮"), "506": ("Costa Rica", "🇨🇷"),
    "507": ("Panama", "🇵🇦"), "509": ("Haiti", "🇭🇹"),
    "590": ("Guadeloupe", "🇬🇵"), "591": ("Bolivia", "🇧🇴"),
    "592": ("Guyana", "🇬🇾"), "593": ("Ecuador", "🇪🇨"),
    "594": ("French Guiana", "🇬🇫"), "595": ("Paraguay", "🇵🇾"),
    "596": ("Martinique", "🇲🇶"), "597": ("Suriname", "🇸🇷"),
    "598": ("Uruguay", "🇺🇾"), "599": ("Caribbean Netherlands", "🇧🇶"),
    "670": ("Timor-Leste", "🇹🇱"), "672": ("Norfolk Island", "🇳🇫"),
    "673": ("Brunei", "🇧🇳"), "674": ("Nauru", "🇳🇷"),
    "675": ("Papua New Guinea", "🇵🇬"), "676": ("Tonga", "🇹🇴"),
    "677": ("Solomon Islands", "🇸🇧"), "678": ("Vanuatu", "🇻🇺"),
    "679": ("Fiji", "🇫🇯"), "680": ("Palau", "🇵🇼"),
    "681": ("Wallis and Futuna", "🇼🇫"), "682": ("Cook Islands", "🇨🇰"),
    "683": ("Niue", "🇳🇺"), "685": ("Samoa", "🇼🇸"),
    "686": ("Kiribati", "🇰🇮"), "687": ("New Caledonia", "🇳🇨"),
    "688": ("Tuvalu", "🇹🇻"), "689": ("French Polynesia", "🇵🇫"),
    "690": ("Tokelau", "🇹🇰"), "691": ("Micronesia", "🇫🇲"),
    "692": ("Marshall Islands", "🇲🇭"), "850": ("North Korea", "🇰🇵"),
    "852": ("Hong Kong", "🇭🇰"), "853": ("Macau", "🇲🇴"),
    "855": ("Cambodia", "🇰🇭"), "856": ("Laos", "🇱🇦"),
    "880": ("Bangladesh", "🇧🇩"), "886": ("Taiwan", "🇹🇼"),
    "960": ("Maldives", "🇲🇻"), "961": ("Lebanon", "🇱🇧"),
    "962": ("Jordan", "🇯🇴"), "963": ("Syria", "🇸🇾"),
    "964": ("Iraq", "🇮🇶"), "965": ("Kuwait", "🇰🇼"),
    "966": ("Saudi Arabia", "🇸🇦"), "967": ("Yemen", "🇾🇪"),
    "968": ("Oman", "🇴🇲"), "971": ("UAE", "🇦🇪"),
    "973": ("Bahrain", "🇧🇭"),
    "974": ("Qatar", "🇶🇦"), "975": ("Bhutan", "🇧🇹"),
    "976": ("Mongolia", "🇲🇳"), "977": ("Nepal", "🇳🇵"),
    "992": ("Tajikistan", "🇹🇯"), "993": ("Turkmenistan", "🇹🇲"),
    "994": ("Azerbaijan", "🇦🇿"), "995": ("Georgia", "🇬🇪"),
    "996": ("Kyrgyzstan", "🇰🇬"), "998": ("Uzbekistan", "🇺🇿"),
}

# === DATABASE SETUP ===
db = sqlite3.connect('otp_subscription.db', check_same_thread=False)
cursor = db.cursor()
with db_lock:
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, joined_at TEXT, referred_by INTEGER DEFAULT 0, refer_rewarded INTEGER DEFAULT 0, active_refers INTEGER DEFAULT 0, plan_expiry TEXT, last_notified TEXT)''')
    db.commit()

# === HELPER FUNCTIONS ===
def detect_country(phone: str) -> tuple:
    clean = phone.lstrip('+')
    for code in sorted(COUNTRY_MAP, key=len, reverse=True):
        if clean.startswith(code):
            return COUNTRY_MAP[code]
    return ("Unknown", "🌍")

def extract_otp(msg: str) -> str:
    m = re.search(
        r'(?:code|كود|رمز|كود التفعيل|رمز التحقق|código|кود|验证码'
        r'|code de vérification|codice|verification code'
        r'|Your .* code|Your .* código|Your .* код'
        r'|imo verification code|WhatsApp code|code is|is)'
        r'[\s\W:-]*(\d{3,8}(?:[-\s]\d{3,8})?)',
        msg, re.IGNORECASE | re.UNICODE
    )
    if m:
        return re.sub(r'[- ]', '', m.group(1))
    m = re.search(r'\b(\d{3,4}[-\s]\d{3,4})\b', msg)
    if m:
        return re.sub(r'[- ]', '', m.group(1))
    m = re.search(r'\b(\d{4,8})\b', msg)
    return m.group(1) if m else "N/A"

def fetch_live_numbers():
    try:
        r = requests.get(API_URL, params={"token": API_TOKEN, "records": ""}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            unique_numbers = []
            seen = set()
            if isinstance(data, list):
                for entry in data:
                    phone = entry[1].strip()
                    if phone not in seen:
                        seen.add(phone)
                        country, flag = detect_country(phone)
                        unique_numbers.append({'phone': phone, 'flag': flag, 'country': country})
                    if len(unique_numbers) >= 8: 
                        break
            return unique_numbers
    except Exception as e:
        print(f"API Error: {e}")
    return []

def fetch_otp_for_number(target_phone):
    try:
        r = requests.get(API_URL, params={"token": API_TOKEN, "records": ""}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                for entry in data:
                    phone = entry[1].strip()
                    if phone == target_phone:
                        app = entry[0].strip()
                        full_msg = entry[2].strip().replace('\n', ' ')
                        time_str = entry[3]
                        otp = extract_otp(full_msg)
                        return app, otp, full_msg, time_str
    except Exception as e:
        print(f"API Error: {e}")
    return None, None, None, None

def is_joined(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return False

def is_plan_active(u_id):
    if u_id == ADMIN_ID:
        return True
    with db_lock:
        cursor.execute("SELECT plan_expiry FROM users WHERE user_id=?", (u_id,))
        res = cursor.fetchone()
        if res and res[0]:
            expiry = datetime.strptime(res[0], "%Y-%m-%d %H:%M:%S")
            if datetime.now() < expiry:
                return True
    return False

def main_menu_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton("💳 My Profile"), types.KeyboardButton("🎁 Refer Link"))
    markup.add(types.KeyboardButton("📱 Live Premium Numbers"))
    if user_id == ADMIN_ID:
        markup.add(types.KeyboardButton("👑 Admin Panel"))
    return markup

# === BACKGROUND HOURLY NOTIFIER ===
def hourly_notifier():
    while True:
        now = datetime.now()
        try:
            with db_lock:
                cursor.execute("SELECT user_id, plan_expiry, active_refers, last_notified FROM users WHERE plan_expiry IS NOT NULL")
                active_users = cursor.fetchall()
                
            for u in active_users:
                user_id, expiry_str, refers, last_not_str = u
                try:
                    expiry = datetime.strptime(expiry_str, "%Y-%m-%d %H:%M:%S")
                    
                    if now > expiry:
                        with db_lock:
                            cursor.execute("UPDATE users SET plan_expiry = NULL WHERE user_id=?", (user_id,))
                            db.commit()
                        bot.send_message(user_id, "⚠️ Aapka 24 Hours ka Premium Plan expire ho gaya hai! Wapas activate karne ke liye 10 naye refer karein.")
                        continue
                        
                    send_notif = False
                    if last_not_str:
                        last_not = datetime.strptime(last_not_str, "%Y-%m-%d %H:%M:%S")
                        if (now - last_not).total_seconds() >= 3600:
                            send_notif = True
                    else:
                        send_notif = True

                    if send_notif:
                        with db_lock:
                            cursor.execute("UPDATE users SET last_notified = ? WHERE user_id=?", (now.strftime("%Y-%m-%d %H:%M:%S"), user_id))
                            db.commit()
                        
                        needed = REFERS_FOR_RENEWAL - refers
                        if needed > 0:
                            bot.send_message(user_id, f"⏰ Reminder: Aapka plan abhi chalu hai! Agle din ke liye renew karne ke liye {needed} aur refer jaldi karein, warna plan expire ho jayega.")
                        else:
                            pass 
                except Exception as inner_e:
                    pass
        except Exception as e:
            pass
        time.sleep(60) 

threading.Thread(target=hourly_notifier, daemon=True).start()


# === MAIN PROCESS FOR START & VERIFY ===
def process_user_start(u_id, chat_id, text=""):
    parts = text.split()
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        with db_lock:
            cursor.execute("SELECT user_id, referred_by, refer_rewarded FROM users WHERE user_id=?", (u_id,))
            user_data = cursor.fetchone()

            if not user_data:
                ref_id = 0
                if len(parts) > 1:
                    try: ref_id = int(parts[1])
                    except: pass
                    
                cursor.execute("INSERT INTO users (user_id, joined_at, referred_by, refer_rewarded, active_refers) VALUES (?, ?, ?, 0, 0)", (u_id, today_date, ref_id))
                db.commit()
                try: bot.send_message(chat_id, "🎉 Welcome to OTP Premium Bot! VIP plan lene ke liye refer karein.")
                except: pass
                
    except Exception as e:
        print(f"Error checking user: {e}")
        return
        
    if not is_joined(u_id):
        m = types.InlineKeyboardMarkup()
        m.add(types.InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"))
        m.add(types.InlineKeyboardButton("✅ Verify", callback_data="check_join"))
        bot.send_message(chat_id, "⚠️ OTP Bot use karne ke liye pehle hamara channel join karein, fir Verify dabayein.", reply_markup=m)
        return

    try:
        with db_lock:
            cursor.execute("SELECT referred_by, refer_rewarded FROM users WHERE user_id=?", (u_id,))
            fresh_data = cursor.fetchone()
            
            if fresh_data:
                current_ref = fresh_data[0]
                is_rewarded = fresh_data[1]
                
                if current_ref != 0 and current_ref != u_id and is_rewarded == 0:
                    cursor.execute("SELECT user_id FROM users WHERE user_id=?", (current_ref,))
                    if not cursor.fetchone():
                        cursor.execute("INSERT INTO users (user_id, joined_at, referred_by, refer_rewarded, active_refers) VALUES (?, ?, 0, 0, 0)", (current_ref, today_date))
                    
                    cursor.execute("UPDATE users SET active_refers = active_refers + 1 WHERE user_id=?", (current_ref,))
                    cursor.execute("UPDATE users SET refer_rewarded = 1 WHERE user_id=?", (u_id,))
                    db.commit()
                    
                    # Logic for Auto-Activate and Auto-Renew
                    cursor.execute("SELECT active_refers, plan_expiry FROM users WHERE user_id=?", (current_ref,))
                    ref_info = cursor.fetchone()
                    a_refers = ref_info[0]
                    p_expiry_str = ref_info[1]
                    
                    now = datetime.now()
                    is_curr_active = False
                    if p_expiry_str:
                        exp_dt = datetime.strptime(p_expiry_str, "%Y-%m-%d %H:%M:%S")
                        if exp_dt > now:
                            is_curr_active = True
                            
                    if not is_curr_active and a_refers >= REFERS_FOR_NEW_PLAN:
                        new_expiry = now + timedelta(hours=PLAN_DURATION_HOURS)
                        new_refers = a_refers - REFERS_FOR_NEW_PLAN
                        cursor.execute("UPDATE users SET plan_expiry = ?, active_refers = ?, last_notified = ? WHERE user_id=?", (new_expiry.strftime("%Y-%m-%d %H:%M:%S"), new_refers, now.strftime("%Y-%m-%d %H:%M:%S"), current_ref))
                        db.commit()
                        try: bot.send_message(current_ref, "🎉 Badhai ho! Aapke 10 refers pure ho gaye. Aapka 24 Hours UNLIMITED Premium Plan activate ho gaya hai!")
                        except: pass
                    elif is_curr_active and a_refers >= REFERS_FOR_RENEWAL:
                        exp_dt = datetime.strptime(p_expiry_str, "%Y-%m-%d %H:%M:%S")
                        new_expiry = exp_dt + timedelta(hours=PLAN_DURATION_HOURS)
                        new_refers = a_refers - REFERS_FOR_RENEWAL
                        cursor.execute("UPDATE users SET plan_expiry = ?, active_refers = ? WHERE user_id=?", (new_expiry.strftime("%Y-%m-%d %H:%M:%S"), new_refers, current_ref))
                        db.commit()
                        try: bot.send_message(current_ref, "🎉 Superb! Aapne active plan mein 8 refer kar liye. Aapka plan agle 24 hours ke liye RENEW ho gaya hai!")
                        except: pass
                    else:
                        try: bot.send_message(current_ref, f"🎊 Referral Success! Ek naya refer count hua hai. Current Valid Refers: {a_refers}")
                        except: pass

        bot.send_message(chat_id, "✅ Verification Successful. Welcome to Unlimited OTP Panel!", reply_markup=main_menu_keyboard(u_id))
        
    except Exception as e:
        print(f"Error processing reward: {e}")


# === COMMAND HANDLERS ===
@bot.message_handler(commands=['start'])
def start_cmd(message):
    process_user_start(message.from_user.id, message.chat.id, message.text)

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def verify_join_callback(call):
    u_id = call.from_user.id
    if not is_joined(u_id):
        bot.answer_callback_query(call.id, "❌ Aapne abhi tak channel join nahi kiya hai!", show_alert=True)
        return
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except: pass
    process_user_start(u_id, call.message.chat.id, "")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    u_id = message.from_user.id

    if message.text == "💳 My Profile":
        with db_lock:
            cursor.execute("SELECT active_refers, plan_expiry FROM users WHERE user_id=?", (u_id,))
            res = cursor.fetchone()
            
        a_refers = res[0] if res else 0
        expiry_str = res[1] if res else None
        
        status_msg = "Inactive (Needs 10 refers)"
        if u_id == ADMIN_ID:
            status_msg = "Lifetime Active (Unlimited Access)"
        elif expiry_str:
            expiry = datetime.strptime(expiry_str, "%Y-%m-%d %H:%M:%S")
            if datetime.now() < expiry:
                status_msg = f"Active till {expiry_str}"
            
        profile_msg = f"💳 YOUR PROFILE\n\n👤 ID: {u_id}\n📊 Plan Status: {status_msg}\n👥 Current Refers: {a_refers}"
        
        if status_msg.startswith("Active") and u_id != ADMIN_ID:
            needed = REFERS_FOR_RENEWAL - a_refers
            if needed > 0:
                profile_msg += f"\n\nℹ️ Renewal: Aapko plan renew karne ke liye {needed} aur refer chahiye."
            else:
                profile_msg += "\n\nℹ️ Renewal: Aapke refers poore hain, plan auto-renew ho jayega."
                
        bot.send_message(message.chat.id, profile_msg)

    elif message.text == "🎁 Refer Link":
        link = f"https://t.me/{bot.get_me().username}?start={u_id}"
        bot.send_message(message.chat.id, f"🔗 YOUR REFERRAL LINK\n\nShare this link:\n{link}\n\n• 10 Refers = 24 Hours Unlimited OTP Plan\n• Active users only need 8 refers to Renew!")

    elif message.text == "📱 Live Premium Numbers":
        if not is_plan_active(u_id):
            bot.send_message(message.chat.id, "❌ Aapka plan inactive hai. OTP nikalne ke liye apne refer link se 10 logo ko join karwayein.")
            return
            
        bot.send_message(message.chat.id, "🔄 Fetching live premium numbers...")
        numbers = fetch_live_numbers()
        
        if numbers:
            markup = types.InlineKeyboardMarkup(row_width=1)
            for num in numbers:
                btn_text = f"{num['flag']} {num['phone']} ({num['country']})"
                callback_data = f"use_{num['phone']}"
                markup.add(types.InlineKeyboardButton(btn_text, callback_data=callback_data))
            
            bot.send_message(message.chat.id, "🌟 AVAILABLE PREMIUM NUMBERS 🌟\n\nAapka unlimited plan active hai. Kisi bhi number par click karke unlimited OTP lein:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "❌ Abhi koi naya number available nahi hai. Thodi der baad try karein.")

    elif message.text == "👑 Admin Panel" and u_id == ADMIN_ID:
        with db_lock:
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0] 
            cursor.execute("SELECT COUNT(*) FROM users WHERE plan_expiry > ?", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
            active_users = cursor.fetchone()[0]
            
        bot.send_message(message.chat.id, f"🛡 ADMIN DASHBOARD\n\n👥 Total Users: {total_users}\n🔥 Active VIP Users: {active_users}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("use_"))
def use_number_callback(call):
    u_id = call.from_user.id
    if not is_plan_active(u_id):
        bot.answer_callback_query(call.id, "❌ Plan inactive hai. Pehle 10 refers pure karein.", show_alert=True)
        return
        
    phone_to_use = call.data.split("_")[1]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 Fetch OTP", callback_data=f"getotp_{phone_to_use}"))
    
    msg = (f"🎉 NUMBER SELECTED 🎉\n\n"
           f"📞 Number: {phone_to_use}\n"
           f"🎁 Limits: Unlimited OTPs\n\n"
           f"App par number daalne ke baad niche 'Fetch OTP' button dabayein.")
    bot.send_message(call.message.chat.id, msg, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("getotp_"))
def get_otp_callback(call):
    u_id = call.from_user.id
    if not is_plan_active(u_id):
        bot.answer_callback_query(call.id, "❌ Plan inactive hai. Pehle refers pure karein.", show_alert=True)
        return
        
    target_phone = call.data.split("_")[1]
    bot.answer_callback_query(call.id, "🔄 Checking Server for OTP...")
    
    app, otp, full_msg, time_str = fetch_otp_for_number(target_phone)
    
    if otp:
        msg = (f"🌟 NEW OTP ARRIVED 🌟\n\n"
               f"📱 App: {app}\n"
               f"📞 Number: {target_phone}\n"
               f"🕐 Time: {time_str}\n\n"
               f"🔑 YOUR OTP: {otp}\n\n"
               f"💬 Message: {full_msg}\n\n"
               f"© {CREDIT}")
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text=f"📋 Tap to Copy OTP: {otp}", copy_text=types.CopyTextButton(text=otp)))
        markup.add(types.InlineKeyboardButton("🔄 Check Again", callback_data=f"getotp_{target_phone}"))
            
        bot.send_message(call.message.chat.id, msg, reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, f"⏳ Abhi tak {target_phone} par koi OTP nahi aaya hai. Thoda wait karein.")

print("OTP Subscription Bot is running...")
bot.infinity_polling()