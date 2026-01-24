from datetime import datetime, time as dtime, timedelta
from io import BytesIO
import json
import os
import sys
from random import randrange
from PIL import Image
from telethon import events
import asyncio
from src.BeatlesBoy_utils import (
    calculate_winning_options,
    extract_pokemon_and_pl,
    calculate_winning_options,
    aggiorna_team_da_foto,
)
from telethon.tl.types import Message

if os.path.exists('/home/SableyeBot/src'):
    ENV_PATH = '/home/SableyeBot/src'
    sys.path.insert(0,ENV_PATH) # SableyeBot
else:
    ENV_PATH = './home/MawileBot/src'
    sys.path.insert(0,ENV_PATH) # MawileBot
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))


ALLOWED_CHAT_ID = -4998491045
DAVIDE_CHAT_ID = 454010613

TARGET_TIMES = [
    dtime(15, 0),
    dtime(16, 0),
    dtime(17, 0),
    dtime(19, 0),
    dtime(20, 0),
    dtime(21, 0),
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
        last_message_text = last_message.text or ""

        if "Ottimo, hai completato tutte le sfide odierne!" in last_message_text:
            await last_message.reply("Finito. Ora posso riposare! 😴💤")
        else:
            answered = False
            try: 
                answered = await reply_to_text(last_message, last_message_text)
            except Exception as e:
                await last_message.reply(f"❗❗ ERRORE ❗❗\n{e}")
            if not answered:
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
            await reply_to_text(event, event.text, client)

async def reply_to_text(event, text, client):
    await asyncio.sleep(1)  # wait for 10 seconds before replying
    if "non è possibile iscriversi" in text:
        await event.reply("Cos'è, ti prendi gioco di me? 😠")
        return True
    elif "Allenatore, hai incontrato" in text:
        da_schierare = await replies_to_wild_pokemon(event, text, client)
        await event.reply(str(da_schierare))
        return True
    elif "Buongiorno Allenatore, e benvenuto in questo viaggio nel mondo dei Pokèmon!" in text:
        await event.reply('0')
        return True
    else: 
        await event.reply("❓​❓​MA CHE STA DICENDO?​❓​❓​")
    return False
    

async def replies_to_wild_pokemon(event, text, client):
    pokemon, pl = await extract_pokemon_and_pl(text)
    await event.reply(f"Ho incontrato {pokemon} di PL {pl}.")

    with open(ENV_PATH+"/BeatlesBoy_team.json", "r", encoding="utf-8") as f:
        team = json.load(f)

    await event.reply("Aspettando la FOTO del team... 2 minuti massimo ⏳")
    await asyncio.sleep(120)  # aspetta 2 minuti

    # recupera l'ultimo messaggio della chat
    messages = await client.get_messages(event.chat_id, limit=1)
    if not messages:
        await event.reply("Non ci sono messaggi recenti.")
        last_message = None
    else:
        last_message: Message = messages[0]
        if last_message.photo:
            await event.reply("Ho ricevuto la foto, la elaboro...")
            photo_bytes = await last_message.download_media(bytes)
            pil_image = Image.open(BytesIO(photo_bytes))
            await aggiorna_team_da_foto(pil_image)
        else:
            await event.reply("Non è arrivata nessuna foto... continuo comunque.")

    winning_options = await calculate_winning_options(pokemon, pl, team)
    winning_option = winning_options[0] if winning_options else None
    if not winning_option:
        return randrange(1, 10)  # random 1-9
    else:
        return winning_option