import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from config import TOKEN

# Connect to SQLite database
DB_FILE = "earnlink.db"
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

def get_referral_count(user_id):
    """Returns the number of people a user has referred."""
    cursor.execute("SELECT COUNT(*) FROM users WHERE referrer_id = ?", (user_id,))
    count = cursor.fetchone()[0]
    return count
# Create tables if they don't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    referrer_id TEXT
)
''')
# Create referrals table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS referrals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE,
    referrer_id TEXT
)
''')

conn.commit()

MIN_WITHDRAW_AMOUNT = 1000  # 40 invites * 25 ETB


def save_user(user_id):
    """Ensures a user is registered in the database."""
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()


def add_referral(user_id, referrer_id):
    """Registers a referral and adds the reward to the referrer."""
    cursor.execute("SELECT referrer_id FROM users WHERE user_id = ?", (user_id,))
    referrer = cursor.fetchone()

    if not referrer or not referrer[0]:  # If user hasn't been referred yet
        cursor.execute("UPDATE users SET referrer_id = ? WHERE user_id = ?", (referrer_id, user_id))
        cursor.execute("UPDATE users SET balance = balance + 25 WHERE user_id = ?", (referrer_id,))
        conn.commit()
        return True
    return False

async def start(update: Update, context: CallbackContext):
    """Handles the /start command and referral tracking"""
    user_id = str(update.message.from_user.id)
    args = context.args

    save_user(user_id)  # Ensure user is registered

    if args:
        referrer_id = args[0]
        if referrer_id.isdigit():
            referrer_id = str(referrer_id)
            if referrer_id != user_id and add_referral(user_id, referrer_id):
                await update.message.reply_text(f"🎉 You were referred by user {referrer_id}! They earned 25 ETB.")

    referral_link = f"https://t.me/{context.bot.username}?start={user_id}"
    await update.message.reply_text(
          f"Welcome to EarnLinkBot! 🚀\n"
        f"🎁 ሰላም ወድ {update.effective_user.first_name} እንኳን በደህና መጡ ::  business ቦትን በመጠቀም ብቻ በወር ከ20,000 ብር በላይ ተከፋይ መሆን ይችላሉ!\n\n"
      f"👬 ወደዚህ ቦት ልክ እንደገቡ የ100 ብር ስጦታ ያገኛሉ በተጨማሪም 1 ሰዉ ወደ ቦቱ ሲጋብዙ በየቀኑ የ25 ብር ቋሚ ክፍያ ያገኛሉ።\n\n"
      f"👤 የእርሶ መጋበዣ ሊንክ 👉 {referral_link}\n"
    
        f"👥 እስካሁን የጋበዙት ሰው መጠን 👉 {get_referral_count(user_id)} ሰው ነው ::\n\n"
         f"☑️ ይህ የእርሶዎ መጋበዣ ሊንክ ነው ለወዳጅ ዘመድዎ ያጋሩ ዛሬውኑ ገንዘብ መስራት ይጀምሩ።\n"
        f"Invite friends using your unique referral link:\n"
        f"{referral_link}\n\n"
        
        f"🎉 if You were referred by user ! They earned 25 ETB."
    )
    await update.message.reply_text(f"""የተጠቃሚ ስም: {update.effective_user.first_name}
ቦታችንን በመቀላቀለዎ የተሸለሙት የገንዘብ መጠን : 15,000 ETB 

ዉድ {update.effective_user.first_name} አሁኑኑ ፈጥነዉ ግሩፓችን ላይ አድ በማድረግ ገንዘቦዎትን ይቀበሉ✅

አድ ለማድረግ👇👇👇
https://t.me/gift_yshelemu_1
https://t.me/gift_yshelemu_1
https://t.me/gift_yshelemu_1

ማሳሰቢያ Add አድርገው ከጨረሱ ቦሀላ ይህን መልዕክት ለ 20ሰው share ማድረግ አለቦዎት 



መልካም እድል 
𝟮𝟬𝟭7
Thank you very much""")
    await menu(update, context)  # Show the menu automatically


async def menu(update: Update, context: CallbackContext):
    """Displays the menu with buttons."""
    keyboard = [
        ["ቀሪ ሂሳብ 💰", "💬የጋበዙት ሰው መጠን 💵"],
        ["ሰው ለመጋበዝ 👤", "ሽልማት ለመቀበል"],
        ["    አሰራር♦️♦️   "],["    ✅ስለ ድርጅቱ ማብራሪያℹ️   "]
        
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("🔽 Choose an option below:", reply_markup=reply_markup)


async def show_instructions(update: Update, context: CallbackContext):
    """Sends the instructions when the button is clicked."""
    await update.message.reply_text(
        "🎯 👤ሰው ለመጋበዝ የሚለውን በመንካት በሚላክሎዎት የሪፈራል ወይም ሰው የመጋበዣ ሊንክ "
        "ለ ሰዎች በመላክ እና በመጋበዝ ገንዘብ መስራት ይችላሉ ፡፡ "
        "የመጋበዣውን ሊንክ የላኩለት ሰው ስታርት ማለት ይኖርበታል።\n\n"
        "የእጅ ስልክዎን ብቻ በመጠቀም ብቻ እስከ 50ሺ ብር ይስሩ🎉\n"
        "መልካም እድል"
    )

async def send_about_agency(update: Update, context: CallbackContext):
    message = """🗯ይህ  ኤጀንሲ በቅን ኢትዮጲያውን ባለሀብቶች የተደራጀ የበጎ አድርጎት ድርጅት ነው ! 

🗯የዚህ ድርጅት አላማ በPromotion Express ማስታወቂያ ኢትዮጲያውንን ለመርዳት ነው ። 
በተጨማሪም በምንዛሬ ኢትዮጲያ እንዳትቸገር ይረዳል።🔋

🗯ድርጅታችን ገንዘቡን የሚያከፍፍለው በtelegram Platform ሲሆን ሰው ወደ ቦቱ በመጋበዝ  ብቻ በትንሹ ከ 500$[50ሺ ETB] እስከ 1000$ [100ሺ ETB]💵💵💵💵
ማንኛውም ሰው መስራት ይችላል ።

🗯ገንዘቡን መቀበያ መንገድ በባንክ ሲሆን
አብረውንም - 🟪የኢትዮጲያ ንግድ ባንክ
                  - 🟨አቢሲኒያ ባንክ
                  - 🟦አዋሽ ባንክ
                  - 🏧 ቴሌ ብር
                  - 🟧ወጋገን ባንክ
                  - 🟫 ዳሽን ባንክ 
🗯ከላይ ከተጠቀሱት በአንዱ ባንክ የሰበሰቡትን ገንዘብ ወጪ ማድረግ ይችላሉ ፡ 

     🎈መልካም እድል 🎊
Long live for Ethiopia📯🇪🇹"""

    await update.message.reply_text(message)


async def check_balance(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
    
    balance = result[0] if result else 0  # Default to 0 if no record exists

    await update.message.reply_text(
        f"👤 የተጠቃሚ ስም: {update.effective_user.first_name} \n"
        f"🎁 የቦነስ ስጦታ: 100 ብር\n"
        f"💵 ያሎት ቀሪ ሒሳብ: {balance} + 100 ብር\n"
        f"📊 ጠቅላላ ሂሳብ: {balance + 100} ብር"
    )



async def get_referrals(update: Update, context: CallbackContext):
    """Shows a list of users the person referred."""
    user_id = str(update.message.from_user.id)
    referral_link = f"https://t.me/{context.bot.username}?start={user_id}"
    cursor.execute("SELECT user_id FROM users WHERE referrer_id = ?", (user_id,))
    referred_users = [row[0] for row in cursor.fetchall()]

    if referred_users:
        await update.message.reply_text(
        f"""🚀የጋበዙት የሰው መጠን
= {get_referral_count(user_id)} ሰው
× 25ETB 

የእርሶ መጋበዣ ሊንክ 🔗 
{referral_link}"""
        )
    else:
        await update.message.reply_text("🙁 You haven't referred anyone yet.")
        



async def get_referral_link(update: Update, context: CallbackContext):
    """Generates a unique referral link for the user."""
    user_id = str(update.message.from_user.id)
    referral_link = f"https://t.me/{context.bot.username}?start={user_id}"
    await update.message.reply_text( f"""✓ውድ {update.effective_user.first_name}
👬 ወደ ኢትዮ ኦንላይን ስራ ቦት ልክ እንደገቡ የ100 ብር ስጦታ ያገኛሉ በተጨማሪም 1 ሰዉ ወደ ቦቱ ሲጋብዙ በየቀኑ የ25 ብር ቋሚ ክፍያ ያገኛሉ

👤የእርሶ መጋበዣ ሊንክ 👉 {referral_link}
👥እስካሁን የጋበዙት ሰው መጠን 👉 {get_referral_count(user_id)} ሰው ነው!

"""
    )


async def withdraw(update: Update, context: CallbackContext):
    """Allows users to withdraw if they have 40 referrals (1,000 ETB)."""
    user_id = str(update.message.from_user.id)
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    balance = cursor.fetchone()[0]

    if balance >= MIN_WITHDRAW_AMOUNT:
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (MIN_WITHDRAW_AMOUNT, user_id))
        conn.commit()
        await update.message.reply_text(
            f"✅ Withdrawal request submitted! You will receive 1000 ETB soon.\n"
            f"Your new balance: {balance - MIN_WITHDRAW_AMOUNT} ETB"
            
        )
    else:
        await update.message.reply_text(
        f"""
🎁 ሰላም ወድ {update.effective_user.first_name}, በቅድሚያ እንኳን በደህና መጡ :: 
ገንዘብ ለመቀበል **40 ሰዎችን(1,000 ETB)** ወደዚህ ቦት መጋበዝ አለቦት 


👥 እስካሁን የጋበዙት ሰው መጠን 👉 {get_referral_count(user_id)} ሰው ነው ።

📢 **ማሳሰቢያ:**  
Add አድርገው ከጨረሱ ቦሀላ **ይህን መልዕክት ለ 20 ሰው share** ማድረግ አለቦዎት ።
"""
)


async def handle_buttons(update: Update, context: CallbackContext):
    """Handles button clicks and calls the appropriate function."""
    text = update.message.text
    user_id = str(update.message.from_user.id)
    if text == "ቀሪ ሂሳብ 💰":
        await check_balance(update, context)
    elif text == "💬የጋበዙት ሰው መጠን 💵":
        await get_referrals(update, context)
    elif text == "አሰራር♦️♦️" :
          await show_instructions(update, context)
    elif text == "ሰው ለመጋበዝ 👤":
        await get_referral_link(update, context)
    elif text == "✅ስለ ድርጅቱ ማብራሪያℹ️": # New button response
        await send_about_agency(update, context)
    elif text == "ሽልማት ለመቀበል":
        await withdraw(update, context)
    else:
        await update.message.reply_text("❌ Unknown Command!You have send a Message directly into the Bot's chat\n or\n Menu structure has been modified by Admin.\n ℹ️ Do not send Messages directly to the Bot or\n reload the Menu by pressing /start")


def main():
    print("Starting the bot...")  # Debugging line
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))  # Handles button clicks

    print("Bot is running...")  # Debugging line
    app.run_polling()


if __name__ == "__main__":
    main()
