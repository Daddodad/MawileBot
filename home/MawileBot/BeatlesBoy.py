# main.py
import os
from telethon import TelegramClient
import sys
import configparser
import asyncio

#import logging
#logging.basicConfig(level=logging.DEBUG)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.ini")
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

API_ID = int(config["BeatlesBoy"]["api_id"])
API_HASH = config["BeatlesBoy"]["api_hash"]


if os.path.exists('/home/SableyeBot/src'):
    sys.path.insert(0,'/home/SableyeBot/src') # SableyeBot
else:
    sys.path.insert(0,'home/MawileBot/src') # MawileBot
    
from src.BeatlesBoy_handlers import register_handlers, scheduled_job

SESSION_PATH = os.path.join(BASE_DIR, 'sessions', 'userbot')
client = TelegramClient(SESSION_PATH, API_ID, API_HASH)

async def main():
    await client.start()
    print("Logged in successfully!")

    me = await client.get_me()
    print(f"Logged in as: {me.first_name} ({me.username})")

    # Register all event handlers
    register_handlers(client)

    asyncio.create_task(scheduled_job(client))

    print("Press Ctrl+C to stop...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
