import telebot
import yt_dlp
import os
import time
from ytmusicapi import YTMusic
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Подключаем правильный токен
TOKEN = "7867908233:AAHPYLVLXZnCWZAsRF8SAj3TdOhcTtX-UNY"  # Обновлённый токен

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

# Подключаем API YouTube Music
ytmusic = YTMusic()

# 📥 Функция для скачивания и конвертации в MP3 (320kbps)
def download_audio(url):
    if not os.path.exists("music"):
        os.makedirs("music")  # Создаём папку, если её нет

    print(f"Подготовка к скачиванию: {url}")  # Отладка, чтобы увидеть правильность URL

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
            print("Запуск скачивания...")  # Отладка
            info = ydl.extract_info(url, download=True)
            filename = f"music/{info['title']}.mp3"
            print(f"Файл скачан: {filename}")  # Отладка
            return filename
    except Exception as e:
        print(f"❌ Ошибка загрузки аудио: {e}")
        return None

# 🚀 Кнопки при старте
@bot.message_handler(commands=['start'])
def send_welcome(message):
    print("Команда /start получена.")  # Отладка
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("🔍 Найти музыку", callback_data="find_music"),
        InlineKeyboardButton("🎵 Скачать по ссылке", callback_data="download_music")
    )
    bot.send_message(message.chat.id, "Привет! Выберите действие:", reply_markup=keyboard)

# Обработчик кнопок
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    print(f"Callback received: {call.data}")  # Отладка
    if call.data == "find_music":
        bot.send_message(call.message.chat.id, "Введите название песни после /find")
    elif call.data == "download_music":
        bot.send_message(call.message.chat.id, "Отправьте ссылку на YouTube")

# 📥 Скачивание музыки по ссылке
@bot.message_handler(func=lambda message: "youtube.com" in message.text or "youtu.be" in message.text or "music.youtube.com" in message.text)
def send_audio(message):
    print(f"Ссылка получена: {message.text}")  # Отладка, чтобы увидеть, какую ссылку отправляет пользователь
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
        print(f"Ошибка при скачивании: {e}")  # Отладка
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

# 🔄 Автоперезапуск бота при сбое
while True:
    try:
        print("Бот запущен и ждёт команды!")
        bot.polling(none_stop=True, timeout=60)
    except Exception as e:
        print(f"⚠️ Сбой в работе бота: {e}")
        time.sleep(5)  # Ждём 5 секунд перед перезапуском
