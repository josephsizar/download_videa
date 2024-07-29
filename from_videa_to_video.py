# get the video_url from the upload server link
import telebot
from playwright.sync_api import sync_playwright
import re

# Replace this with your actual Telegram bot token
API_TOKEN = '7445379003:AAEUklI4zCtGQBHSW_tjRxuka2bCAHBf23M'
bot = telebot.TeleBot(API_TOKEN)

def get_video_src(url_website):
    video_src = None
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto(url_website, timeout=120000)
            page.wait_for_selector('video', timeout=60000)
            
            # Wait for a few seconds to ensure video element is fully loaded
            page.wait_for_timeout(5000)

            # Extract video source
            video_src = page.eval_on_selector('video', 'video => video.src')
        except Exception as e:
            print(f"Error retrieving video source: {e}")
        finally:
            browser.close()
    
    return video_src

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, 'Welcome! Send me a website URL, and I will find the video source for you.')

@bot.message_handler(content_types=['text'])
def handle_text(message):
    message_text = message.text
    
    # Basic URL validation
    url_regex = re.compile(r'https?://[^\s]+')
    url_match = url_regex.search(message_text)
    
    if url_match:
        url = url_match.group(0)
        try:
            video_url = get_video_src(url)
            if video_url:
                bot.send_message(
                    message.chat.id, 
                    f"[videa video]({video_url})" or 'No video source found', 
                    parse_mode="MarkdownV2"
                )
            else:
                bot.reply_to(message, 'No video source found.')
        except Exception as e:
            print(f"Error retrieving video source: {e}")
            bot.reply_to(message, 'Error retrieving video source.')
    else:
        bot.reply_to(message, 'Please send a valid website URL.')

print("Bot is running...")
bot.polling()

