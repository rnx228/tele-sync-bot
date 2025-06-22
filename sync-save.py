import os
import zipfile
import asyncio
from telegram import Bot

# Replace with your bot token
BOT_TOKEN = 'x'
GROUP_CHAT_ID = x
TOPIC_ID = x

TARGET_FOLDER = r'C:\Users\x\Saved Games\FALCOM\ed8'
ZIP_FILE = r'C:\Users\x\Saved Games\FALCOM\ed8_backup.zip'

def analyze_folder(folder_path):
    total_files = 0
    total_size = 0
    for root, _, files in os.walk(folder_path):
        for file in files:
            total_files += 1
            total_size += os.path.getsize(os.path.join(root, file))
    print(f"📊 Folder contains {total_files} files, total size {total_size / 1024 / 1024:.2f} MB")

def zip_folder(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                print(f"📝 Adding: {file_path}")
                zipf.write(file_path, arcname)
    print(f"✅ Zipping completed: {zip_path}")

async def main():
    analyze_folder(TARGET_FOLDER)
    print("🔄 Zipping folder, please wait...")
    zip_folder(TARGET_FOLDER, ZIP_FILE)

    bot = Bot(BOT_TOKEN)
    print("📤 Uploading to Telegram...")
    await bot.send_document(
        chat_id=GROUP_CHAT_ID,
        message_thread_id=TOPIC_ID,
        document=open(ZIP_FILE, 'rb'),
        filename='ed8_backup.zip',
        caption="📂 Backup uploaded to #saves topic"
    )
    print("✅ Upload complete!")

if __name__ == "__main__":
    asyncio.run(main())
