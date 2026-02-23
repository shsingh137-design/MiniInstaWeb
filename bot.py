import os
import time
import instaloader
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Telegram bot token
BOT_TOKEN = "8697945721:AAHLozz0MqeSDYlh8Dxg5r51UBSWuJNit9k"

# Instagram login
L = instaloader.Instaloader(dirname_pattern="downloads")
L.login("teretypekabnda", "@haya143")  # Instagram username & password

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! Send me any Instagram username and I will fetch profile options for you."
    )

# When user sends username
async def insta_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip()
    try:
        profile = instaloader.Profile.from_username(L.context, username)

        keyboard = [
            [InlineKeyboardButton("📸 Profile Pic", callback_data=f"pic|{username}")],
            [InlineKeyboardButton("ℹ️ Details", callback_data=f"info|{username}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(f"Select an option for @{username}:", reply_markup=reply_markup)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# Button callback
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action, username = query.data.split("|")

    try:
        profile = instaloader.Profile.from_username(L.context, username)

        if action == "pic":
            # Download profile pic
            L.download_profile(username, profile_pic_only=True)

            folder = f"downloads/{username}"
            pic_file = None
            for file in os.listdir(folder):
                if file.endswith(".jpg"):
                    pic_file = os.path.join(folder, file)
                    while file.endswith(".temp") or not os.path.exists(pic_file):
                        time.sleep(0.5)
                    break

            if pic_file:
                await query.message.reply_photo(photo=open(pic_file, "rb"), caption=f"📸 Profile Pic of @{username}")
            else:
                await query.message.reply_text("⚠️ Profile picture not found!")

        elif action == "info":
            caption = (
                f"👤 Name: {profile.full_name or 'N/A'}\n"
                f"📝 Bio: {profile.biography or 'N/A'}\n"
                f"👥 Followers: {profile.followers}\n"
                f"🔗 Following: {profile.followees}\n"
                f"🖼️ Posts: {profile.mediacount}\n"
                f"🎬 Reels/Highlights: {profile.get_highlights_count()}\n"
                f"🔒 Private: {'Yes' if profile.is_private else 'No'}"
            )
            await query.message.reply_text(caption)

    except Exception as e:
        await query.message.reply_text(f"❌ Error: {e}")

# Telegram bot setup
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, insta_info))
app.add_handler(CallbackQueryHandler(button))

print("Bot is running...")
app.run_polling()