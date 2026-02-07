from datetime import datetime, time as dtime, timedelta
from io import BytesIO
import json
import os
from pyexpat.errors import messages
import sys
from random import randrange
from PIL import Image
from telethon import events
import asyncio
import random

from telethon.tl.types import Message

if os.path.exists('/home/SableyeBot/src'):
    ENV_PATH = '/home/SableyeBot/src'
    sys.path.insert(0,ENV_PATH) # SableyeBot
else:
    ENV_PATH = './home/MawileBot/src'
    sys.path.insert(0,ENV_PATH) # MawileBot
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from BeatlesBoy_utils import (
    calculate_winning_options,
    extract_pokemon_and_pl,
    aggiorna_team_da_foto,
    extract_types,
    calculate_potenziabili,
    extract_number_of_pvp_choices,
    filter_team,
    pokemon_utility
)

# if os.path.exists('/home/SableyeBot/src'):
#     ENV_PATH = '/home/SableyeBot/src'
#     sys.path.insert(0,ENV_PATH) # SableyeBot
# else:
#     ENV_PATH = './home/MawileBot/src'
#     sys.path.insert(0,ENV_PATH) # MawileBot
#     sys.path.append(os.path.dirname(os.path.abspath(__file__)))


ALLOWED_CHAT_IDs = [-4998491045, -5272320132]
DAVIDE_CHAT_ID = 454010613

TARGET_TIMES = [
    dtime(15, 0),
    dtime(16, 0),
    dtime(17, 0),
    dtime(17, 30),
    dtime(18, 0),
    dtime(18, 30),
    dtime(19, 0),
    dtime(20, 0),
    dtime(21, 0),
    dtime(22, 0),
    dtime(22, 30),
]

async def scheduled_job(client):

    print("[Scheduler] started")

    local_times = TARGET_TIMES.copy()

    # if TESTING:
    #     now = datetime.now() + timedelta(seconds=20)
    #     injected_time = dtime(now.hour, now.minute, now.second)

    #     if injected_time not in local_times:
    #         local_times.append(injected_time)
    #         local_times.sort()
    #         print(f"[Scheduler] injected start time: {injected_time}")

    while True:
        now = datetime.now()
        print(f"\n[Scheduler] now = {now.time()}")

        next_run = None

        # Cerca il prossimo orario valido oggi
        for t in local_times:
            candidate = now.replace(
                hour=t.hour,
                minute=t.minute,
                second=t.second,  
                microsecond=0,
            )

            print(f"[Scheduler] checking candidate {candidate.time()}")

            if candidate > now:
                next_run = candidate
                print(f"[Scheduler] selected next_run = {next_run.time()}")
                break
            else:
                print(f"[Scheduler] skipped {candidate.time()} (already passed)")

        # Se oggi non c'è nulla, vai a domani
        if next_run is None:
            tomorrow = now + timedelta(days=1)
            t = local_times[0]

            next_run = tomorrow.replace(
                hour=t.hour,
                minute=t.minute,
                second=t.second, 
                microsecond=0,
            )

            print(f"[Scheduler] no slots left today → next_run tomorrow at {next_run.time()}")

        delay = (next_run - now).total_seconds()
        print(f"[Scheduler] sleeping for {int(delay)} seconds")

        await asyncio.sleep(delay)

        print(
            f"\n[Scheduler] 🔔 TRIGGERED "
            f"(target={next_run.time()}, now={datetime.now().time()})"
        )

        try:
            messages = await client.get_messages(ALLOWED_CHAT_IDs[0], limit=2)
            if not messages:
                continue
            last_message: Message = messages[0]
            last_message_text = last_message.text or ""

            # if last_message.photo and TESTING:
            #     last_message: Message = messages[1]
            #     last_message_text = last_message.text or ""
            #     print("The last message is an image")

            if "Ottimo, hai completato tutte le sfide odierne!" in last_message_text:
                await last_message.reply("Finito. Ora posso riposare! 😴💤")
            elif "Finito. Ora posso riposare!" in last_message_text:
                pass
            elif "Giornata di gioco conclusa!" in last_message_text:
                pass
            elif "NON HO FINITO DI LAVORARE!" in last_message_text:
                pass
            else:
                # try: 
                #     answered = await reply_to_text(last_message, last_message_text,client)
                # except Exception as e:
                #     await last_message.reply(f"❗❗ ERRORE ❗❗\n{e}")
                await last_message.reply("⏰⏰ NON HO FINITO DI LAVORARE! ⏰⏰")

        except Exception as e:
            print(f"[Scheduler] ❌ ERROR: {e}")

def register_handlers(client):

    @client.on(events.NewMessage)
    async def message_handler(event):
        # Ignore messages not from the desired chat
        if event.chat_id not in ALLOWED_CHAT_IDs:
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
    elif "Allenatore, sei in una zona potenziament" in text:
        da_allenare = await replies_to_potenziamento(event, text, client)
        await event.reply(str(da_allenare))
        return True
    elif "Buongiorno Allenatore, e benvenuto in questo viaggio nel mondo dei Pokèmon!" in text:
        await event.reply('0')
        return True
    elif "Ottimo, hai completato tutte le sfide odierne!" in text:
        await event.reply("Finito. Ora posso riposare! 😴💤")
        return True
    elif "Allenatore, sfiderai ⚔ un altro Giocatore;" in text:
        da_schierare = await replies_to_pvp(event, text, client)
        await event.reply(str(da_schierare))
        return True
    elif "vuoi aggiungerlo in squadra?" in text:
        dopo_cattura = await replies_to_vittoria(event,text,client)
        await event.reply(str(dopo_cattura))
        return True       
    elif " è salito al livello " in text:
        pass
    elif "Schieramento ricevuto! Attendi che il tuo avversario faccia lo stesso per visualizzare i risultati" in text:
        pass
    else: 
        await event.reply("❓❓")
    return False
    

async def load_team_from_json(event, client):
    await asyncio.sleep(10)  # aspetta 2 minuti

    json_path = os.path.join(ENV_PATH, "BeatlesBoy_team.json")
    print("Loading JSON from:", json_path)

    with open(json_path, "r", encoding="utf-8") as f:
        team = json.load(f)

    # recupera l'ultimo messaggio della chat
    messages = await client.get_messages(
        event.chat_id,
        min_id=event.id,
        limit=5
    )

    success = False

    for msg in messages:
        if not msg.photo:
            continue
        #await msg.reply("Questa è una foto")
        try:
            await msg.reply("Ho ricevuto la foto della squadra, la aggiorno...")  # opzionale
            photo_bytes = await msg.download_media(bytes)
            pil_image = Image.open(BytesIO(photo_bytes))

            team = await aggiorna_team_da_foto(pil_image)
            success = True
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(team, f, indent=2)
            break  # stop at first successful photo
        except Exception as e:
            continue
    if not success:
        await event.reply("Non ho trovato la foto della squadra... continuo comunque.")
    return team

async def replies_to_wild_pokemon(event, text, client):
    pokemon, pl = await extract_pokemon_and_pl(text)
    await event.reply(f"Ho incontrato {pokemon} con PL {pl}.\n\nAspettando la FOTO del team... 2 minuti massimo ⏳")

    team = await load_team_from_json(event, client)
    useful, useless, lvl_100 = await filter_team(team, remove_100 = True)

    try:
        winning_options = await calculate_winning_options(pokemon, pl, useful)
        if winning_options is None or len(winning_options) == 0:
            winning_options = await calculate_winning_options(pokemon, pl, useless)
        if winning_options is None or len(winning_options) == 0:
            winning_options = await calculate_winning_options(pokemon, pl, lvl_100)    
        print("Winning options:", winning_options)
        winning_option = winning_options[0]            
    except Exception as e:
        print("Errore nel calcolo delle opzioni vincenti:", e)
        winning_option = None
    
    print("Winning option:", winning_option)

    if not winning_option:
        return 'Avrei schierato a caso 1' 
    else:
        #return f"avrei schierato {winning_option[3]} ({winning_option[0]}, bonus {winning_option[2]})"
        return winning_option[3]
    
async def replies_to_pvp(event, text, client):
    await event.reply(f"Una PvP! Pronto a schierare i migliori!\n\nAspettando la FOTO del team... 2 minuti massimo ⏳")

    n_schierabili = await extract_number_of_pvp_choices(text)

    team = await load_team_from_json(event, client)
    useful, useless, lvl_100 = await filter_team(team, remove_100 = True)
    useful.sort( key = lambda x: x[3], reverse=True )  # ordina per power decrescente
    lvl_100.sort( key = lambda x: x[3], reverse=True )  # ordina per power decrescente
    useless.sort( key = lambda x: x[3], reverse=True )  # ordina per power decrescente
    # print("Useful:", useful)
    # print("Useless:", useless)
    # print('Lvl 100:', lvl_100)

    da_schierare = ''

    for i in range(len(useful)):
        if len(da_schierare) < n_schierabili:
            if useful[i][0] is not None:
                da_schierare += str(useful[i][4])
        else: 
            return da_schierare
        
    for i in range(len(useless)):
        if len(da_schierare) < n_schierabili: 
            if useless[i][0] is not None:
                da_schierare += str(useless[i][4])
        else:
            return da_schierare
        
    for i in range(len(lvl_100)):
        if len(da_schierare) < n_schierabili: 
            if lvl_100[i][0] is not None:
                da_schierare += str(lvl_100[i][4])
        else:
            return da_schierare
     
    while len(da_schierare) < n_schierabili:
        n = randrange(1,10)
        if n not in [int(x) for x in da_schierare]:
            da_schierare += str(n)

    return da_schierare
    
async def replies_to_potenziamento(event, text, client):
    tipi = await extract_types(text)
    await event.reply(f"Ho incontrato potenziamento coi tipi {tipi}.\n\nAspettando la FOTO del team... 2 minuti massimo ⏳")

    team = await load_team_from_json(event, client)    
    useful, useless, lvl_100 = await filter_team(team, remove_100 = True)

    try:
        potenziabili = await calculate_potenziabili(tipi, useful)
        if potenziabili is None or len(potenziabili) == 0:
            potenziabili = await calculate_potenziabili(tipi, useless)
        if potenziabili is None or len(potenziabili) == 0:
            potenziabili = await calculate_potenziabili(tipi, lvl_100)
        print("Potenziabili:", potenziabili)
    except Exception as e:
        print("Errore nel calcolo dei potenziabili:", e)
        potenziabili = None

    if not potenziabili:
        return 'Avrei schierato a caso 1' 
    else:
        #return f"avrei schierato {potenziabili[3]} ({potenziabili[0]}, bonus {potenziabili[2]})"
        return potenziabili[0][3]

async def drop_the_useless(us, usl, lvl_100):
    occupied_slot = []

    for u in us:
        if u[0] is not None:
            occupied_slot.append(u[4])
    for ul in usl:
        if ul[0] is not None:
            occupied_slot.append(ul[4])
    for l100 in lvl_100:
        if l100[0] is not None:
            occupied_slot.append(l100[4])

    print(occupied_slot)

    if len(occupied_slot) < 9:
        for i in range(1, 10):
            if i not in occupied_slot:
                print("returning", i)
                return i
            
    # No empty slots
    merged = []
    if lvl_100:
        merged.extend(lvl_100)
    if us:
        merged.extend(us)
    if usl:
        merged.extend(usl)

    for p in reversed(merged):
        if p[0] != "sableye":
            return p[4]

    return merged[-1][4]

async def extract_name_and_level_from_vittoria(msg: str):
    lines = msg.splitlines()
    name = None
    level = None
    for line in lines:
        line = line.strip()
        if line.startswith("-Nome:"):
            name = line.split(":", 1)[1].strip()
        elif line.startswith("-Livello:"):
            level = int(line.split(":", 1)[1].strip())
        if name is not None and level is not None:
            break
    return name, level

async def replies_to_vittoria(event, text, client):
    name, level = await extract_name_and_level_from_vittoria(text)

    await event.reply(f"Vittoria! Catturo o no {name} di livello {level}? Decidiamo...")
    #TODO: aggiustare team = await load_team_from_json(event, client)

    await asyncio.sleep(10)  # aspetta 2 minuti

    json_path = os.path.join(ENV_PATH, "BeatlesBoy_team.json")
    print("Loading JSON from:", json_path)

    with open(json_path, "r", encoding="utf-8") as f:
        team = json.load(f)

    print(team)

    useful, useless, lvl_100 = await filter_team(team, remove_100 = True)

    dopo_cattura = "Non ho capito se catturarlo o no.. Aiuto..."
    print('\nUseful', useful)
    print('\nLess useful',useless)
    print('\nlvl100',lvl_100)

    if useful:
        less_useful = next(
            (u for u in reversed(useful) if u[0] is not None),
            None
        )
    else: # Ho solo pokemon al 100?
        less_useful = lvl_100[-1]

    count = 0
    for p in team:
        if p[0] is not None:
            count+=1

    print('Less useful', less_useful)
    print('trovato', await pokemon_utility(name, level))

    if less_useful[0] is not None:

        if name.lower() == 'sableye' and 'sableye' not in [p[0] for p in team]:
            await event.reply(f"Sono io! via {less_useful[0].capitalize()}, non mi servi più!")
            return await drop_the_useless(useful,useless,lvl_100)
    
        if less_useful[2]*1.1< await pokemon_utility(name, level):
            await event.reply(f"È chiaramente più utile di {less_useful[0].capitalize()}, lo prendo!")
            return await drop_the_useless(useful,useless,lvl_100)        

    # Non ho nemmeno 6 pokemon...
    if count<6:
        if random.random() >0.5:
            await event.reply(f"Non ho nemmeno 6 pokémon... ma non mi sembra così utile questo...")
            return 0
        else:
            await event.reply('Non ho nemmeno 6 pokémon... e lui mi piace un sacco!')
            dopo_cattura = await drop_the_useless(useful,useless,lvl_100)
        return dopo_cattura 
    
    return 0
