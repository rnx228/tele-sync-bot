import os
import sys
import asyncio
import logging
from telegram import Bot
from telegram.error import RetryAfter

# --- CONFIGURATION ---

FOLDER_PATHS = [
    r'C:\Users\x',
]

ALLOWED_EXTENSIONS = {'.jpg', '.png', '.jpeg'}
TELEGRAM_BOT_TOKEN = 'yourbottoken'
TELEGRAM_CHAT_ID = yourchatid  # Integer chat ID
TELEGRAM_TOPIC_ID = yourtopicid           # Integer topic/thread ID

# Destination folder for moved files after upload
DEST_FOLDER = r'C:\Users\x'

# --- SETUP PATHS & LOGGING ---

SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))  # Use sys.argv[0] for .pyw
UPLOADED_FILES_LOG = os.path.join(SCRIPT_DIR, 'uploaded_files.txt')
ERROR_LOG_FILE = os.path.join(SCRIPT_DIR, 'error.log')

logging.basicConfig(
    filename=ERROR_LOG_FILE,
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Make sure destination folder exists
os.makedirs(DEST_FOLDER, exist_ok=True)

# --- MAIN FUNCTION ---

async def upload_files_to_telegram():
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)

        if os.path.exists(UPLOADED_FILES_LOG):
            with open(UPLOADED_FILES_LOG, 'r', encoding='utf-8') as f:
                uploaded_files = set(line.strip() for line in f)
        else:
            uploaded_files = set()

        for folder_path in FOLDER_PATHS:
            if not os.path.exists(folder_path):
                logging.error(f"Folder does not exist: {folder_path}")
                continue

            for filename in os.listdir(folder_path):
                if filename in uploaded_files:
                    continue

                file_path = os.path.join(folder_path, filename)
                ext = os.path.splitext(filename)[1].lower()

                if os.path.isfile(file_path) and ext in ALLOWED_EXTENSIONS:
                    while True:
                        try:
                            with open(file_path, 'rb') as f:
                                if ext in {'.jpg', '.jpeg', '.png'}:
                                    await bot.send_photo(
                                        chat_id=TELEGRAM_CHAT_ID,
                                        message_thread_id=TELEGRAM_TOPIC_ID,
                                        photo=f,
                                        caption=filename
                                    )
                                elif ext == '.mp4':
                                    await bot.send_video(
                                        chat_id=TELEGRAM_CHAT_ID,
                                        message_thread_id=TELEGRAM_TOPIC_ID,
                                        video=f,
                                        caption=filename
                                    )
                                elif ext == '.pdf':
                                    await bot.send_document(
                                        chat_id=TELEGRAM_CHAT_ID,
                                        message_thread_id=TELEGRAM_TOPIC_ID,
                                        document=f,
                                        caption=filename
                                    )
                            # File is closed here (outside 'with')

                            # Mark file as uploaded
                            uploaded_files.add(filename)
                            with open(UPLOADED_FILES_LOG, 'a', encoding='utf-8') as logf:
                                logf.write(filename + '\n')

                            # Move the file after upload
                            dest_path = os.path.join(DEST_FOLDER, filename)
                            if os.path.exists(dest_path):
                                os.remove(dest_path)
                            os.replace(file_path, dest_path)
                            print(f"Moved {filename} to {DEST_FOLDER}")

                            await asyncio.sleep(1.5)  # Flood control buffer
                            break

                        except RetryAfter as e:
                            wait_time = e.retry_after
                            logging.warning(f"Rate limit exceeded. Waiting {wait_time} seconds...")
                            await asyncio.sleep(wait_time)

                        except Exception as e:
                            logging.error(f"Error uploading {filename}: {e}")
                            break

        await bot.close()

    except Exception as e:
        logging.exception(f"Script crashed: {e}")

# --- RUN ---

if __name__ == '__main__':
    asyncio.run(upload_files_to_telegram())
