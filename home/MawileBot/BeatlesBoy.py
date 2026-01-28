# main.py
import os
from telethon import TelegramClient
import sys
import asyncio

if os.path.exists('/home/SableyeBot/src'):
    sys.path.insert(0,'/home/SableyeBot/src') # SableyeBot
else:
    sys.path.insert(0,'home/MawileBot/src') # MawileBot
    
from src.BeatlesBoy_handlers import register_handlers, scheduled_job

api_id = 32734550
api_hash = '18742bc7269a1e306dce108908ae5291'

client = TelegramClient('sessions/userbot', api_id, api_hash)

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
