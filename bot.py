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

# 🚀 Кнопки (inline-клавиатура)
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

# 🔍 Поиск музыки в YouTube Music с автоматическим скачиванием
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

        # Берём первый найденный трек
        first_song = search_results[0]
        title = first_song['title']
        artist = first_song['artists'][0]['name']
        video_id = first_song.get('videoId')

        if not video_id:
            bot.send_message(message.chat.id, "❌ Ошибка: не удалось найти видео ID.")
            return

        youtube_url = f"https://music.youtube.com/watch?v={video_id}"
        bot.send_message(message.chat.id, f"🎶 Нашёл: {title} - {artist}\n⏳ Загружаю...")

        # Скачиваем и отправляем музыку
        filepath = download_audio(youtube_url)

        if filepath and os.path.exists(filepath):
            with open(filepath, 'rb') as audio:
                bot.send_audio(message.chat.id, audio)
            os.remove(filepath)  # Удаляем файл после отправки
        else:
            bot.send_message(message.chat.id, "❌ Ошибка при загрузке.")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка при поиске: {e}")

# 📥 Скачивание музыки из YouTube по ссылке
@bot.message_handler(func=lambda message: "youtube.com" in message.text or "youtu.be" in message.text or "music.youtube.com" in message.text)
def send_audio(message):
    bot.reply_to(message, "🎵 Загружаю музыку, подожди 1-2 минуты...")
    try:
        filepath = download_audio(message.text)
        if filepath and os.path.exists(filepath):  # Проверяем, скачался ли файл
            with open(filepath, 'rb') as audio:
                bot.send_audio(message.chat.id, audio)
            os.remove(filepath)  # Удаляем файл после отправки
        else:
            bot.reply_to(message, "❌ Ошибка при загрузке. Попробуй другую ссылку.")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

# 🛠 Универсальный обработчик всех сообщений
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    try:
        bot.reply_to(message, "Я пока не знаю эту команду 😕\nПопробуй:\n✅ /find [название песни] — найти музыку\n✅ Отправь ссылку на YouTube — я загружу трек!")
    except Exception as e:
        print(f"Ошибка при обработке сообщения: {e}")

# 🔄 Автоперезапуск бота при сбое
while True:
    try:
        print("Бот запущен и ждёт команды!")
        bot.polling(none_stop=True, timeout=60)
    except Exception as e:
        print(f"⚠️ Сбой в работе бота: {e}")
        time.sleep(5)  # Ждём 5 секунд перед перезапуском
