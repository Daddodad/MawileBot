from datetime import datetime, time as dtime, timedelta
from random import random
from telethon import events
import asyncio
from src_BB.BeatlesBoy_utils import (
    extract_pokemon_and_pl,
    calculate_winning_options,
)
from telethon.tl.types import Message


ALLOWED_CHAT_ID = -4998491045
DAVIDE_CHAT_ID = 454010613

TARGET_TIMES = [
    dtime(15, 0),
    dtime(18, 0),
    dtime(20, 0),
]

async def scheduled_job(client):
    while True:
        now = datetime.now()

        # find the next target time today or tomorrow
        next_run = None
        for t in TARGET_TIMES:
            candidate = now.replace(
                hour=t.hour,
                minute=t.minute,
                second=0,
                microsecond=0,
            )
            if candidate > now:
                next_run = candidate
                break

        if next_run is None:
            # all times passed → first time tomorrow
            next_run = (now + timedelta(days=1)).replace(
                hour=TARGET_TIMES[0].hour,
                minute=TARGET_TIMES[0].minute,
                second=0,
                microsecond=0,
            )

        delay = (next_run - now).total_seconds()
        await asyncio.sleep(delay)

        # 🔍 get last message
        messages = await client.get_messages(ALLOWED_CHAT_ID, limit=1)
        if not messages:
            continue
        last_message: Message = messages[0]

        if "Ottimo, hai completato tutte le sfide odierne!" in last_message.text:
            await last_message.reply("Finito. Ora posso riposare! 😴💤")
        else:
            await last_message.reply("⏰⏰ NON HO FINITO DI LAVORARE! ⏰⏰")

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
            if "Allenatore, hai incontrato" in text:
                da_schierare = replies_to_wild_pokemon(event, text)
                await event.reply(da_schierare)

def replies_to_wild_pokemon(event, text):
    pokemon, pl = extract_pokemon_and_pl(text)
    team = []  # TODO: load team from somewhere
    winning_options = calculate_winning_options(pokemon, pl, team)
    if not winning_options:
        return random.randrange(9)+1  # random 1-9
    else:
        return best_option(winning_options, [])