import telebot
import requests
import os
import subprocess

# Replace this with your actual Telegram bot token
API_TOKEN = '7445379003:AAEUklI4zCtGQBHSW_tjRxuka2bCAHBf23M'
bot = telebot.TeleBot(API_TOKEN)

# Define the paths to save the downloaded and compressed video
VIDEO_PATH = "video.mp4"
COMPRESSED_VIDEO_PATH = "compressed_video.mp4"

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

def compress_video(input_path, output_path):
    command = [
        'ffmpeg',
        '-i', input_path,
        '-vf', 'scale=1280:720',
        '-b:v', '1M',
        output_path
    ]
    subprocess.run(command, check=True)

def handle_large_file(input_path, output_path_pattern, segment_time):
    command = [
        'ffmpeg',
        '-i', input_path,
        '-c', 'copy',
        '-map', '0',
        '-f', 'segment',
        '-segment_time', str(segment_time),
        '-segment_format', 'mp4',
        '-reset_timestamps', '1',
        output_path_pattern
    ]
    subprocess.run(command, check=True)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "Send me a video URL to download and send back.")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    url = message.text

    if not url.startswith("http"):
        bot.reply_to(message, "Please send a valid URL.")
        return

    bot.reply_to(message, "Downloading your video...")

    try:
        download_video(url, VIDEO_PATH)
        compress_video(VIDEO_PATH, COMPRESSED_VIDEO_PATH)

        # Check the size of the compressed video
        if os.path.getsize(COMPRESSED_VIDEO_PATH) > 50 * 1024 * 1024:  # 50 MB limit
            # If too large, split the video
            handle_large_file(COMPRESSED_VIDEO_PATH, "segment_%03d.mp4", 30)
            # Send each segment
            for filename in os.listdir("."):
                if filename.startswith("segment_") and filename.endswith(".mp4"):
                    with open(filename, 'rb') as video:
                        bot.send_video(message.chat.id, video)
                    os.remove(filename)
        else:
            # Send the compressed video
            with open(COMPRESSED_VIDEO_PATH, 'rb') as video:
                bot.send_video(message.chat.id, video)
        
    except Exception as e:
        print(f"Error processing request: {e}")
        bot.reply_to(message, "There was an error processing your request.")
    finally:
        # Clean up: delete the video files after sending
        if os.path.exists(VIDEO_PATH):
            os.remove(VIDEO_PATH)
        if os.path.exists(COMPRESSED_VIDEO_PATH):
            os.remove(COMPRESSED_VIDEO_PATH)
        print("Video files deleted.")

print("Bot is running...")
bot.polling()

