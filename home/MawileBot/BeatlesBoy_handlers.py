# handlers.py
from telethon import events

ALLOWED_CHAT_ID = -4998491045
TARGET_CHAT_ID = 454010613

def register_handlers(client):

    @client.on(events.NewMessage)
    async def message_handler(event):
        # Ignore messages not from the desired chat
        if event.chat_id != ALLOWED_CHAT_ID:
            return

        # Ignore your own outgoing messages (VERY important)
        # if event.out:
        #     return

        # ---- TEXT HANDLING ----
        if event.text:
            text = event.text.lower()
            if "non è possibile iscriversi" in text:
                await event.reply("Cos'è, ti prendi gioco di me? 😠")
        await client.send_message(
            TARGET_CHAT_ID,
            f"Trigger received in {ALLOWED_CHAT_ID}:\n\n{text}"
            )

        # ---- IMAGE HANDLING ----
        if event.photo:
            await event.reply("I received an image 📷")
