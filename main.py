import telebot
import requests
import os

# Replace this with your actual Telegram bot token
API_TOKEN = '7445379003:AAEUklI4zCtGQBHSW_tjRxuka2bCAHBf23M'
bot = telebot.TeleBot(API_TOKEN)

# Define the path to save the downloaded video
VIDEO_PATH = "video.mp4"

# Function to download video
def download_video(url, output_path):
    try:
        print(f"Starting download from URL: {url}")
        response = requests.get(url, stream=True, timeout=120)
        response.raise_for_status()  # Check if the request was successful
        
        with open(output_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        print("Download completed!")
    except requests.RequestException as e:
        print(f"Error: {e}")
        raise

# Handle /start command
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "Send me a video URL to download and send back.")

# Handle text messages
@bot.message_handler(content_types=['text'])
def handle_text(message):
    url = message.text

    if not url.startswith("http"):
        bot.reply_to(message, "Please send a valid URL.")
        return

    bot.reply_to(message, "Downloading your video...")

    try:
        download_video(url, VIDEO_PATH)
        with open(VIDEO_PATH, 'rb') as video:
            bot.send_video(message.chat.id, video)
    except Exception as e:
        print(f"Error processing request: {e}")
        bot.reply_to(message, "There was an error processing your request.")
    finally:
        # Clean up: delete the video file after sending
        if os.path.exists(VIDEO_PATH):
            os.remove(VIDEO_PATH)
            print("Video file deleted.")

# Start the bot
print("Bot is running...")
bot.polling()
