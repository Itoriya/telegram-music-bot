import telebot
import yt_dlp
import os
import time
from ytmusicapi import YTMusic
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "7867908233:AAE9gISHhGZu1LBlyMxiOmcs6rvnmk_14xc"
bot = telebot.TeleBot(TOKEN)

# Подключаем API YouTube Music
ytmusic = YTMusic()

# 📥 Функция для скачивания и конвертации в MP3 (320kbps)
def download_audio(url):
    if not os.path.exists("music"):
        os.makedirs("music")  # Создаём папку, если её нет

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'outtmpl': 'music/%(title)s.%(ext)s'
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = f"music/{info['title']}.mp3"
            return filename
    except Exception as e:
        print(f"❌ Ошибка загрузки аудио: {e}")
        return None

# 🚀 Кнопки при старте
@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("🔍 Найти музыку", callback_data="find_music"),
        InlineKeyboardButton("🎵 Скачать по ссылке", callback_data="download_music")
    )
    bot.send_message(message.chat.id, "Привет! Выберите действие:", reply_markup=keyboard)

# Обработчик кнопок
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "find_music":
        bot.send_message(call.message.chat.id, "Введите название песни после /find")
    elif call.data == "download_music":
        bot.send_message(call.message.chat.id, "Отправьте ссылку на YouTube")

# 🔍 Поиск музыки и создание кнопок выбора трека
@bot.message_handler(commands=['find'])
def find_music(message):
    query = message.text.replace('/find', '').strip()

    if not query:
        bot.send_message(message.chat.id, "❌ Укажите название песни после /find")
        return

    bot.send_message(message.chat.id, f"🔍 Ищу: {query}...")

    try:
        search_results = ytmusic.search(query, filter="songs", limit=10)  # Увеличено до 10 результатов

        if not search_results:
            bot.send_message(message.chat.id, "⚠️ Ничего не найдено!")
            return

        keyboard = InlineKeyboardMarkup()
        for song in search_results:
            title = song['title']
            artist = song['artists'][0]['name']
            video_id = song.get('videoId')

            if video_id:
                button_text = f"{title} - {artist}"
                keyboard.add(InlineKeyboardButton(button_text, callback_data=f"download_{video_id}"))

        bot.send_message(message.chat.id, "🎶 Выбери песню для загрузки:", reply_markup=keyboard)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка при поиске: {e}")

# 📥 Обработчик нажатий на кнопки выбора трека
@bot.callback_query_handler(func=lambda call: call.data.startswith("download_"))
def handle_download(call):
    video_id = call.data.replace("download_", "")
    youtube_url = f"https://music.youtube.com/watch?v={video_id}"

    bot.send_message(call.message.chat.id, "⏳ Загружаю музыку...")

    filepath = download_audio(youtube_url)

    if filepath and os.path.exists(filepath):
        with open(filepath, 'rb') as audio:
            bot.send_audio(call.message.chat.id, audio)
        os.remove(filepath)  # Удаляем файл после отправки
    else:
        bot.send_message(call.message.chat.id, "❌ Ошибка при загрузке.")

# 🔄 Автоперезапуск бота при сбое
while True:
    try:
        print("Бот запущен и ждёт команды!")
        bot.polling(none_stop=True, timeout=60)
    except Exception as e:
        print(f"⚠️ Сбой в работе бота: {e}")
        time.sleep(5)  # Ждём 5 секунд перед перезапуском
