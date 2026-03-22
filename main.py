import os
import yt_dlp
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ==================== SOZLAMALAR ====================
BOT_TOKEN = "8336585545:AAHEC4wgVcVHE-V5luI6NYk1wlnN0j68aV0"  # Tokeningizni qo'ying!
ARTIST_NAME = "noneedtodiscusss"   # Artist nomi
IMAGE_URL = "https://image2url.com/r2/default/images/1774115756443-981a692d-c4c8-4605-957c-d91f76009e7c.jpg"
# ====================================================

bot = telebot.TeleBot(BOT_TOKEN)

# Yuklab olish formatini saqlash uchun vaqtinchalik ma'lumot
user_choice = {}

def download_audio(url):
    """MP3 yuklab olish"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'audio.%(ext)s',
        'quiet': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return "audio.mp3", info.get('title', 'audio')

def download_video(url):
    """MP4 yuklab olish (eng yaxshi sifat)"""
    ydl_opts = {
        'format': 'best[ext=mp4]/best',  # Eng yaxshi mp4 format
        'outtmpl': 'video.%(ext)s',
        'quiet': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # Yuklab olingan fayl nomini aniqlash
        filename = ydl.prepare_filename(info)
        if not filename.endswith('.mp4'):
            filename = filename.replace('.webm', '.mp4').replace('.mkv', '.mp4')
        return filename, info.get('title', 'video')

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        "🎵 YouTube botiga xush kelibsiz!\n\n"
        "YouTube linkini yuboring, men sizga:\n"
        "🎵 Audio (MP3) yoki\n"
        "🎬 Video (MP4)\n"
        "yuklab beraman!"
    )

@bot.message_handler(func=lambda m: True)
def handle_url(message):
    url = message.text
    
    if 'youtube.com' in url or 'youtu.be' in url:
        # Tanlash uchun tugmalar
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(
            InlineKeyboardButton("🎵 Audio (MP3)", callback_data=f"audio|{url}"),
            InlineKeyboardButton("🎬 Video (MP4)", callback_data=f"video|{url}")
        )
        
        bot.reply_to(message, 
            "Qaysi formatda yuklab olishni tanlang:", 
            reply_markup=markup
        )
    else:
        bot.reply_to(message, "❌ Iltimos, YouTube linkini yuboring!")

@bot.callback_query_handler(func=lambda call: True)
def handle_choice(call):
    format_type, url = call.data.split('|')
    
    # Tanlovni bildirish
    bot.edit_message_text(
        f"⏳ {format_type.upper()} yuklanmoqda... Iltimos kuting.",
        call.message.chat.id,
        call.message.message_id
    )
    
    try:
        if format_type == 'audio':
            filename, title = download_audio(url)
            
            with open(filename, 'rb') as audio:
                bot.send_audio(
                    call.message.chat.id,
                    audio,
                    title=title,
                    performer=ARTIST_NAME,
                    thumb=IMAGE_URL,
                    caption=f"🎵 {title}\n🎤 {ARTIST_NAME}"
                )
            
            os.remove(filename)
            bot.edit_message_text(
                "✅ Audio yuklab olindi!",
                call.message.chat.id,
                call.message.message_id
            )
            
        else:  # video
            filename, title = download_video(url)
            
            with open(filename, 'rb') as video:
                # Video hajmi 50MB dan katta bo'lsa, xabar berish
                if os.path.getsize(filename) > 50 * 1024 * 1024:
                    bot.send_message(
                        call.message.chat.id,
                        f"⚠️ Video hajmi 50MB dan katta ({os.path.getsize(filename) / 1024 / 1024:.1f}MB).\n"
                        f"Telegram faqat 50MB gacha video yubora oladi.\n"
                        f"Link: {url}"
                    )
                else:
                    bot.send_video(
                        call.message.chat.id,
                        video,
                        caption=f"🎬 {title}",
                        supports_streaming=True
                    )
            
            os.remove(filename)
            bot.edit_message_text(
                "✅ Video yuklab olindi!",
                call.message.chat.id,
                call.message.message_id
            )
            
    except Exception as e:
        bot.edit_message_text(
            f"❌ Xatolik yuz berdi: {str(e)[:100]}",
            call.message.chat.id,
            call.message.message_id
        )

if __name__ == "__main__":
    print("Bot ishga tushdi...")
    print("✅ Audio (MP3) va Video (MP4) yuklab olish tayyor!")
    bot.infinity_polling()
