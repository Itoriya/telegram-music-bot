
import telebot
import yt_dlp
import os

#7867908233:AAE9gISHhGZu1LBlyMxiOmcs6rvnmk_14xc"
TOKEN = "7867908233:AAE9gISHhGZu1LBlyMxiOmcs6rvnmk_14xc" 
bot = telebot.TeleBot(TOKEN)

# 📥 Функция для скачивания и конвертации в MP3
def download_audio(url):
    if not os.path.exists("music"):
        os.makedirs("music")  # Создаём папку, если её нет

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'music/%(title)s.%(ext)s'
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = f"music/{info['title']}.mp3"
            return filename
    except Exception as e:
        return None

# 🚀 Если человек отправил ссылку на YouTube, бот скачает её
@bot.message_handler(func=lambda message: "youtube.com" in message.text or "youtu.be" in message.text)
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
        import telebot

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я работаю! 🚀")
    import time

@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        bot.reply_to(message, "Привет! Я работаю! 🚀")
    except Exception as e:
        print(f"Ошибка в /start: {e}")

# Универсальный обработчик всех сообщений (чтобы не падал)
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    try:
        bot.reply_to(message, "Я пока не знаю эту команду 😕")
    except Exception as e:
        print(f"Ошибка при обработке сообщения: {e}")

# Автоперезапуск бота при сбое
while True:
    try:
        bot.polling(none_stop=True, timeout=60)
    except Exception as e:
        print(f"Сбой в работе бота: {e}")
        time.sleep(5)  # Ждём 5 секунд перед перезапуском
           # Удаляем файл после отправки
        os.remove(filename)
    except Exception as e:
        bot.send_message(message.chat.id, "❌ Ошибка при скачивании аудио")
        print(f"Ошибка при скачивании: {e}")
        from ytmusicapi import YTMusic

ytmusic = YTMusic()  # Подключаем API YouTube Music

@bot.message_handler(commands=['find'])
def find_music(message):
    query = message.text.replace('/find', '').strip()  # Получаем запрос без команды

    if not query:
        bot.send_message(message.chat.id, "❌ Пожалуйста, укажите название песни после /find")
        return

    bot.send_message(message.chat.id, f"🔍 Ищу: {query}...")

    try:
        # Ищем треки
        search_results = ytmusic.search(query, filter="songs", limit=5)

        if not search_results:
            bot.send_message(message.chat.id, "⚠️ Ничего не найдено!")
            return

        # Формируем список результатов
        response = "🎶 **Вот что я нашёл:**\n\n"
        for i, song in enumerate(search_results, start=1):
            title = song['title']
            artist = song['artists'][0]['name']
            link = f"https://music.youtube.com/watch?v={song['videoId']}"
            response += f"{i}. [{title} - {artist}]({link})\n"

        bot.send_message(message.chat.id, response, parse_mode="Markdown")

    except Exception as e:
        bot.send_message(message.chat.id, "❌ Ошибка при поиске музыки")
        print(f"Ошибка при поиске музыки: {e}")
        print("Бот запущен и ждёт команды!")
bot.polling(none_stop=True)
bot.polling()
