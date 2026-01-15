# main.py
from telethon import TelegramClient
from BeatlesBoy_handlers import register_handlers

api_id = 32734550
api_hash = '18742bc7269a1e306dce108908ae5291'

client = TelegramClient('userbot', api_id, api_hash)

async def main():
    await client.start()
    print("Logged in successfully!")

    me = await client.get_me()
    print(f"Logged in as: {me.first_name} ({me.username})")

    # Register all event handlers
    register_handlers(client)

    print("Press Ctrl+C to stop...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
