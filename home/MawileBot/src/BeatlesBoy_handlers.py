from datetime import datetime, time as dtime, timedelta
from io import BytesIO
import json
import os
import ast
from pyexpat.errors import messages
import sys
from random import randrange
from PIL import Image
from telethon import events
import asyncio
import random
import traceback
import configparser
from telethon.tl.types import Message

from poke_lib import get_poke_bst, get_casella, LvL

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "../config.ini")
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

ALLOWED_CHAT_IDs = ast.literal_eval(config["BeatlesBoy"]["allowed_chat_ids"])


if os.path.exists('/home/SableyeBot/src'):
    ENV_PATH = '/home/SableyeBot/src'
    sys.path.insert(0,ENV_PATH) # SableyeBot
else:
    ENV_PATH = './home/MawileBot/src'
    sys.path.insert(0,ENV_PATH) # MawileBot
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from BeatlesBoy_utils import (
    calculate_winning_options_selvatico,
    extract_all_matches_lega,
    extract_pokemon_and_pl,
    aggiorna_team_da_foto,
    aggiorna_enemy_team_da_foto,
    extract_pokemon_and_pl_lega,
    extract_types,
    calculate_potenziabili,
    extract_number_of_pvp_choices,
    filter_team,
    find_evo_at_level_x,
    lega_utility,
    load_team_from_json_simple,
    one_vs_team_lega,
    pokemon_utility,
    read_pokemons_from_trainer,
    poke_cell,
    process_and_reply,
    calculate_best_strategy,
    reset_lega_info,
    extract_all_matches_pvp,
    load_x_from_json,
    dump_x_in_json
)

# if os.path.exists('/home/SableyeBot/src'):
#     ENV_PATH = '/home/SableyeBot/src'
#     sys.path.insert(0,ENV_PATH) # SableyeBot
# else:
#     ENV_PATH = './home/MawileBot/src'
#     sys.path.insert(0,ENV_PATH) # MawileBot
#     sys.path.append(os.path.dirname(os.path.abspath(__file__)))


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

THINK_TIME = 420 #420

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
            elif "Schieramento ricevuto!" in last_message_text:
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
            try:
                outcome, clean_up = await reply_to_text(event, event.text, client)
                if outcome:
                    await dump_x_in_json((await load_x_from_json('clean_up'))+clean_up, "clean_up")
                    # if clean_up>0:
                    #     await delete_messages_after(event, client, limit = clean_up, exclude = "Ecco il resoconto")
                    # elif clean_up<0:
                    #     await delete_messages_before(event, client, limit = clean_up, exclude = "Ecco il resoconto")
            except Exception as e:
                tb = traceback.format_exc()
                await event.reply(
                    f"[Handlers] ❌ ERROR in message_handler:\n"
                    f"{type(e).__name__}: {e}\n\n"
                    f"{tb}"
                )


async def reply_to_text(event, text, client):
    await asyncio.sleep(1)  # wait for 10 seconds before replying
    if "non è possibile iscriversi" in text:
        await event.reply("Cos'è, ti prendi gioco di me? 😠")
        return True, 0
    elif "Allenatore, hai incontrato" in text:

        # ADD POSSIBLE MEGA TO THE MEGA LIST
        # images = []
        # if event.grouped_id:  
        #     album_messages = await client.get_messages(
        #         event.chat_id,
        #         ids=None,
        #         min_id=event.id - 10,
        #         max_id=event.id + 10
        #     )

        #     for msg in album_messages:
        #         if msg.grouped_id == event.grouped_id and msg.media:
        #             images.append(msg.media)
        # else:
        #     if event.media:
        #         images.append(event.media)
        # with open(os.path.join(ENV_PATH, "pokemon_vectors_9.json"), "r", encoding="utf-8") as f:
        #     pokemon_vectors = json.load(f)
        # pokemon_found = (await process_and_reply(event, client, images, pokemon_vectors))[:-1]

        da_schierare = await replies_to_wild_pokemon(event, text, client)
        await event.reply(str(da_schierare))
        return True, 5
    elif "Allenatore, sei in una zona potenziament" in text:
        da_allenare = await replies_to_potenziamento(event, text, client)
        await event.reply(str(da_allenare))
        return True, 6 
    elif "Buongiorno Allenatore, e benvenuto in questo viaggio nel mondo dei Pokèmon!" in text:
        await event.reply('0') 
        await dump_x_in_json([],"mega")
        return True, 3
    elif "Ottimo, hai completato tutte le sfide odierne!" in text:
        await delete_messages_before(event, client, limit = (await load_x_from_json("clean_up")), exclude = "Finito. Ora posso riposare!")
        catt = await load_x_from_json("catture")
        batt = await load_x_from_json("battaglie")
        message = "Finito. Ora posso riposare! 😴💤.\n"
        if catt != []:
            message += "\nHo catturato:\n"+"".join(catt)
        if batt != []:
            message += "\nNelle battaglie, in ordine:\n"+"".join(batt)
        await event.reply(message)
        await dump_x_in_json([], "catture")
        await dump_x_in_json([], "battaglie")
        return True, 2
    elif "Allenatore, sfiderai ⚔ un altro Giocatore;" in text:
        da_schierare = await replies_to_pvp(event, text, client)
        await event.reply(str(da_schierare))
        await dump_x_in_json(len(str(da_schierare)), "num_enemies")
        return True, 5
    elif "vuoi aggiungerlo in squadra?" in text:
        (dopo_cattura, name, poke_u) = (await replies_to_vittoria(event,text,client))
        await event.reply(str(dopo_cattura))
        if "0" not in str(dopo_cattura):
            l = (await load_x_from_json("catture"))
            l.append(f"\t{name} ({poke_u})\n")
            await dump_x_in_json(l,"catture")
        return True, 5      
    elif "Allenatore, dovrai affrontare" in text:
        da_schierare = await replies_to_trainer(event, text, client, is_capopalestra = False)
        await event.reply(str(da_schierare))
        return True, 5 + len(str(da_schierare))
    elif "Allenatore, ora dovrai affrontare il Capopalestra" in text:
        images = []
        if event.grouped_id:  
            album_messages = await client.get_messages(
                event.chat_id,
                ids=None,
                min_id=event.id - 10,
                max_id=event.id + 10
            )

            for msg in album_messages:
                if msg.grouped_id == event.grouped_id and msg.media:
                    images.append(msg.media)
        else:
            if event.media:
                images.append(event.media)
        da_schierare = await replies_to_trainer(event, text, client, is_capopalestra = True, images = images)
        await event.reply(str(da_schierare))
        return True, 12
    

    #### LEGA HANDLERS ####


    elif "Allenatore, benvenuto nella fase" in text:
        reset_lega_info(begin=True)
        await handle_first_lega_message(event, text, client)
        if "Aspetta che il tuo avversario schieri per poter chiedere l'indizio!" in text:
            pass
        else:
            da_schierare = await lega_turn_1_no_hint(event, text, client)
            await event.reply(str(da_schierare))
        return True, 0
    elif "Purtroppo, con le vittorie raggiunte dal tuo avversario, sei stato sconfitto" in text:
        reset_lega_info(begin=False)
        return True, 0
    elif "Congratulazioni, grazie al tuo numero di match vinti e singoli Pokemon battuti hai vinto" in text:
        reset_lega_info(begin=False)
        return True, 0
    elif "Il tuo avversario ha schierato, puoi chiedere l'indizio!" in text:
        fase_lega = await load_x_from_json("fase_lega")
        indizio = None
        if fase_lega == 1:
            indizio = await lega_hint_ask()
        if fase_lega == 2:
            indizio = await lega_hint_ask()
        if fase_lega == 3:
            indizio = await lega_hint_ask()
        await event.reply(str(indizio))
        return True, 0
    elif "Ecco il Pokemon schierato ne" in text:
        fase_lega = await load_x_from_json("fase_lega")
        if fase_lega == 1:
            da_schierare = await lega_turn_1_hint_reply(event, text, client)
        if fase_lega == 2:  
            da_schierare = await lega_turn_2_hint_reply(event, text, client)
        if fase_lega == 3:
            da_schierare = await lega_turn_3_hint_reply(event, text, client)
        await event.reply(str(da_schierare))
        return True, 0
    elif "Bene, via al prossimo match!" in text:
        if "Aspetta che il tuo avversario schieri per poter chiedere l'indizio!" in text:
            pass
        else:
            fase_lega = await load_x_from_json("fase_lega")
            if fase_lega == 2:
                da_schierare = await lega_turn_2_no_hint(event, text, client)
            if fase_lega == 3:
                da_schierare = await lega_turn_3_no_hint(event, text, client)
            await event.reply(str(da_schierare))
        return True, 0
    elif "Match vinto!" in text:
        await compile_answer_lega(event, text, client, vittoria=True)
        return True, 0
    elif "Match perso!" in text:
        await compile_answer_lega(event, text, client, vittoria=False)
        return True, 0

    #### LEGA HANDLERS ####

    elif "Schieramento ricevuto! Attendi che il tuo avversario faccia lo stesso per visualizzare i risultati" in text:
        await delete_messages_before(event, client, limit = (await load_x_from_json("clean_up")), exclude = "Finito. Ora posso riposare!")
        await dump_x_in_json(0, "clean_up")
        return True, ((await load_x_from_json("num_enemies"))+1)
    elif "Giornata di gioco conclusa!" in text:
        return True, 1
    elif "Allenatore, benvenuto nella prossima zona!" in text:
        return True, 1
    elif "Allenatore, benvenuto nella prima zona!" in text:
        return True, 1
    elif "VITTORIE:"  in text or "SCONFITTE:"  in text or "PAREGGI:"  in text:
        (
        vittorie_sx,  vittorie_dx,
        sconfitte_sx, sconfitte_dx,
        pareggi_sx,   pareggi_dx,
        ) =  await extract_all_matches_pvp(text)
        l = await load_x_from_json("battaglie")
        for p in vittorie_dx:
            l.append(f"Ho sconfitto un {p}!\n")
        for p in sconfitte_dx:
            l.append(f"Ho perso contro un {p}...\n")
        for p in pareggi_dx:
            l.append(f"Ho pareggiato contro un {p}?\n")
        l.append('\n')
        await dump_x_in_json(l,"battaglie")
        return True, 0
    
    elif " è salito al livello " in text:
        return True, 0
    elif "Ecco la card del tuo avversario!" in text:
        return True, 0
    elif "Ecco la tua card aggiornata!" in text:
        return True, 0
    elif "Finito. Ora posso riposare!" in text:
        return True, 0
    elif "Complimenti! Hai catturato" in text:
        return True, 0
    elif "Avendogli dimostrato la tua forza" in text:
        return True, 0
    else: 
        await event.reply("❓Non ho capito❓")
    return False, 0
    
async def load_team_from_json(event, client):
    json_path = os.path.join(ENV_PATH, "BeatlesBoy_info.json")
    print("Loading team from:", json_path)
    with open(json_path, "r", encoding="utf-8") as f:
        team = (json.load(f))["team"]
    return team

async def dump_team_in_json(team, event, client):
    json_path = os.path.join(ENV_PATH, "BeatlesBoy_info.json")
    print("Dumping team to:", json_path)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["team"] = team
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)



async def load_team_and_check_card(event, client):
    await asyncio.sleep(20)  # aspetta 20 sec

    team = await load_team_from_json_simple()

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
            photo_bytes = await msg.download_media(bytes)
            pil_image = Image.open(BytesIO(photo_bytes))

            team = await aggiorna_team_da_foto(pil_image)
            success = True
            await msg.reply("Ho ricevuto la foto della squadra, la aggiorno...")  # opzionale
            await dump_team_in_json(team, event, client)
            break  # stop at first successful photo
        except Exception as e:
            continue
    if not success:
        await event.reply("Non ho trovato la foto della squadra... continuo comunque.")
    return team

async def replies_to_wild_pokemon(event, text, client):
    pokemon, pl = await extract_pokemon_and_pl(text)
    
    await event.reply(f"Ho incontrato {pokemon.capitalize()} con PL {pl}.\n\nAspettando la FOTO del team... 20 secondi massimo ⏳")

    team = await load_team_and_check_card(event, client)
    useful, useless, lvl_100 = await filter_team(team, remove_100 = True, nilb = True, data = {"lvlup": True, "catch": False, "drop": False})

    try:
        winning_options = await calculate_winning_options_selvatico(pokemon, pl, useful)
        if winning_options is None or len(winning_options) == 0:
            winning_options = await calculate_winning_options_selvatico(pokemon, pl, useless)
        if winning_options is None or len(winning_options) == 0:
            winning_options = await calculate_winning_options_selvatico(pokemon, pl, lvl_100)    
        print("Winning options:", winning_options)

        if winning_options:
            if winning_options[0][4]>10: # nilb
                winning_option = winning_options[0]
            else:
                winning_option = random.choices(
                    winning_options,
                    weights=[t[-1] for t in winning_options],
                    k=1
                )[0]
        else:
            winning_option = None           
    except Exception as e:
        print("Errore nel calcolo delle opzioni vincenti:", e)
        winning_option = 'Error'
        w_error = e
    
    print("Winning option:", winning_option)

    if winning_option == 'Error':
        return f'Errore: Avrei schierato a caso! C\'è stato un errore! {w_error}'
    elif not winning_option:
        return 'Non posso vincere?!' 
    else:
        #return f"avrei schierato {winning_option[3]} ({winning_option[0]}, bonus {winning_option[2]})"
        return winning_option[3]
    
async def replies_to_pvp(event, text, client):
    await event.reply(f"Una PvP! Pronto a schierare i migliori!\n\nAspettando la FOTO del team... 20 secondi massimo ⏳")

    n_schierabili = await extract_number_of_pvp_choices(text)

    team = await load_team_and_check_card(event, client)
    useful, useless, lvl_100 = await filter_team(team, remove_100 = True, data = {"lvlup": True, "catch": False, "drop": False})
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
            return da_schierare[::-1]
        
    for i in range(len(useless)):
        if len(da_schierare) < n_schierabili: 
            if useless[i][0] is not None:
                da_schierare += str(useless[i][4])
        else:
            return da_schierare[::-1]
        
    for i in range(len(lvl_100)):
        if len(da_schierare) < n_schierabili: 
            if lvl_100[i][0] is not None:
                da_schierare += str(lvl_100[i][4])
        else:
            return da_schierare[::-1]
     
    while len(da_schierare) < n_schierabili:
        n = randrange(1,10)
        if n not in [int(x) for x in da_schierare]:
            da_schierare += str(n)

    return da_schierare[::-1]
    
async def replies_to_potenziamento(event, text, client):
    tipi = await extract_types(text)
    await event.reply(f"Ho incontrato potenziamento coi tipi {tipi}.\n\nAspettando la FOTO del team... 20 secondi massimo ⏳")

    team = await load_team_and_check_card(event, client)    
    useful, useless, lvl_100 = await filter_team(team, remove_100 = True, nilb = True, data = {"lvlup": True, "catch": False, "drop": False})
    print("useful for potenziamento: ",useful)
    try:
        potenziabili = await calculate_potenziabili(tipi, useful)
        # Perchè dovrebbe dare il potenziamento a gente inutile o al 100?!?!
        # if potenziabili is None or len(potenziabili) == 0:
        #     potenziabili = await calculate_potenziabili(tipi, useless)
        # if potenziabili is None or len(potenziabili) == 0:
        #     potenziabili = await calculate_potenziabili(tipi, lvl_100)
        print("Potenziabili:", potenziabili)
    except Exception as e:
        print("Errore nel calcolo dei potenziabili:", e)
        potenziabili = None

    if not potenziabili:
        return 'Qualcosa non ha funzionato, non riesco a capire chi potenziare!' 
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
    #print(occupied_slot)

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
    
    merged.sort(key=lambda x: x[2])

    print('merged', merged)
    for p in merged:
        if p[0] != "sableye":
            return p[4]

    return merged[-1][4]

async def check_if_training_pokemon(less_useful, pokemon_da_catturare):
    print(less_useful, pokemon_da_catturare)
    livelli_rimanenti = (len(LvL) - get_casella()) *2 *1.5
    drop_mon = less_useful[0]
    drop_liv = less_useful[1]+livelli_rimanenti  # Can be over 100
    catch_mon = pokemon_da_catturare[0]
    catch_liv =  pokemon_da_catturare[1]+livelli_rimanenti  # Can be over 100
    scarto_liv = max(0, drop_liv-100, catch_liv-100)
    if scarto_liv > 0:
        drop_liv = max(0, drop_liv - scarto_liv)
        catch_liv = max(0, catch_liv - scarto_liv)

    print(f"livelli rimanenti: {livelli_rimanenti}, drop_liv: {drop_liv}, catch_liv: {catch_liv}")

    drop_mon = await find_evo_at_level_x(drop_mon.lower(), drop_liv)
    catch_mon = await find_evo_at_level_x(catch_mon.lower(), catch_liv)

    print(drop_mon, catch_mon)

    drop_power = round((await get_poke_bst(drop_mon))*int(drop_liv)/100)
    catch_power = round((await get_poke_bst(catch_mon))*int(catch_liv)/100)

    # TODO: FIX (incorporate the level better, do not assume it's mega (or assume it?))
    if catch_mon in (await load_x_from_json("mega")):
        max_bst = await get_poke_bst(catch_mon+'-mega')
        catch_power = (max_bst)*int(catch_liv)/100
   
    print(drop_power, catch_power)

    if catch_power > drop_power:
        return True, livelli_rimanenti
    else:
        return False, livelli_rimanenti

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

    pokemon_u =  await pokemon_utility(name, level, data = {"lvlup": True, "catch": True, "drop": False})

    await event.reply(f"Vittoria! Catturo o no {name} di livello {level} (utility {pokemon_u})? Decidiamo...")

    team = await load_team_from_json_simple()
    useful, useless, lvl_100 =                   await filter_team(team, remove_100 = False,             data = {"lvlup": False, "catch": False, "drop": False}) # Non tolgo i lvl 100 ! UTILITY PURA!
    useful_drop, useless_drop, lvl_100_drop =    await filter_team(team, remove_100 = False,             data = {"lvlup": True,  "catch": False, "drop": True})  # Aggiungo un boost ai pokemon che mi servono per la palestra, anche se altrestì inutili!
    useful_n_100, _u, _100 =                     await filter_team(team, remove_100 = True, nilb = True, data = {"lvlup": True,  "catch": False, "drop": False}) # Tolgo i lvl 100 e aggiungo nilb SOLO per la scelta di distribuzione dei livelli.

    to_return = '0'
    if "te schierato salirà di ben" in text:
        if len(useful_n_100)!=0: # useful è già ordinato
            to_return = '0'+str(useful_n_100[0][4])
    
    message_utility = ''
    for po in useful:
        message_utility+=(f"\n{po[0]} {(po[2])}")
    await event.reply(f"La mia squadra è: {message_utility}")

    dopo_cattura = "Non ho capito se catturarlo o no.. Aiuto..."
    print('\nUseful', useful)
    print('\nLess useful',useless)
    print('\nlvl100',lvl_100)

    if useful:
        less_useful = next(
            (u for u in reversed(useful) if u[0] is not None),
            None
        )
    else: # Ho 9 pokemon al 100?
        less_useful = lvl_100[-1]

    count = 0
    for p in team:
        if p[0] is not None:
            count+=1

    if less_useful[0] is not None:

        if name.lower() == 'sableye' and 'sableye' not in [p[0] for p in team]:
            await event.reply(f"Sono io!")
            return await drop_the_useless(useful_drop,useless_drop,lvl_100_drop), name, pokemon_u
    
        if less_useful[2]<= pokemon_u: # First check utility
            to_be_dropped = await drop_the_useless(useful_drop,useless_drop,lvl_100_drop) 
            if pokemon_u > 99:
                (catch, livelli_rimanenti) = (True, 0)
            else:
                catch, livelli_rimanenti = (await check_if_training_pokemon(less_useful, (name, level)))
            if catch:
                await event.reply(f"È chiaramente più utile di {less_useful[0].capitalize()}, lo prendo!")
                return to_be_dropped  , name, pokemon_u     
            else: 
                await event.reply(f"L'utilità è maggiore, ma non recupera {less_useful[0].capitalize()} in {livelli_rimanenti} livelli (livelli rimanenti stimati / 6).")
                return to_return, name, pokemon_u

    # Non ho nemmeno 6 pokemon...
    if count<6:
        if random.random() >0.5:
            await event.reply(f"Non ho nemmeno 6 pokémon... ma non mi sembra così utile questo...")
            return to_return, name, pokemon_u
        else:
            await event.reply('Non ho nemmeno 6 pokémon... e lui mi piace un sacco!')
            dopo_cattura = await drop_the_useless(useful_drop,useless_drop,lvl_100_drop)
        return dopo_cattura , name, pokemon_u
    
    return to_return, name, pokemon_u

async def replies_to_trainer(event, text, client, is_capopalestra, images = None):
    _, enemy_powers, capopalestra_powers, multiplier, _ = await poke_cell(0)
    if len(enemy_powers) != 3 or len(capopalestra_powers) != 6:
        return("Qualcosa è andato storto con poke_cell...")
    #print(enemy_powers, capopalestra_powers)

    if is_capopalestra:
        with open(os.path.join(ENV_PATH, "pokemon_vectors_9.json"), "r", encoding="utf-8") as f:
            pokemon_vectors = json.load(f)
        pokemon_found = (await process_and_reply(event, client, images, pokemon_vectors))[:-1]

        #TODO add reader of images

        message = "Ho incontrato un Capopalestra con:\n"
        message += "\n".join([f"{name.capitalize()} ({dist:.2f})" for name, dist in pokemon_found])

        await event.reply(message)

        enemy_powers = capopalestra_powers
        enemy_team = [[p[0],None,None] for p in pokemon_found]
    else:
        enemy_team = await read_pokemons_from_trainer(text)
        if len (enemy_team) == 1:
            enemy_powers = [enemy_powers[2]]
        elif len(enemy_team) == 2:
            enemy_powers = [enemy_powers[1], enemy_powers[2]]
        elif len(enemy_team) == 3:
            enemy_powers = [enemy_powers[0], enemy_powers[1], enemy_powers[2]]
        elif len(enemy_team) == 4:
            enemy_powers = [enemy_powers[0], enemy_powers[1], enemy_powers[2], enemy_powers[2]]
        elif len(enemy_team) == 5:
            enemy_powers = [enemy_powers[0], enemy_powers[0], enemy_powers[1], enemy_powers[1], enemy_powers[2]]
        elif len(enemy_team) == 6:
            enemy_powers = [enemy_powers[0], enemy_powers[0], enemy_powers[0], enemy_powers[1], enemy_powers[1], enemy_powers[2]]

        await event.reply(
            f"Ho incontrato {', '.join([e[0].capitalize() for e in enemy_team])}? Capiamo chi schierare..."
        )

    team = await load_team_and_check_card(event, client) 
  
    useful, useless, lvl_100 = await filter_team(team, remove_100 = True, nilb = True, data = {"lvlup": True, "catch": False, "drop": False})
    useful.sort( key = lambda x: x[3], reverse=False )  # ordina per power 
    lvl_100.sort( key = lambda x: x[3], reverse=False )  # ordina per power 
    useless.sort( key = lambda x: x[3], reverse=True )  # ordina per power (do i livelli prima al più forte, non prioritizzo gente indietro) 
    print('\n Incontro Selvatici, le squadre sono:\n', "useful", useful, "\nuseless", useless, "\nlvl_100",lvl_100)
    try:
        p_of_victory, best_schieramento = await calculate_best_strategy(useful,enemy_team, enemy_powers, multiplier)
        if 0 in p_of_victory:   # Si può fare di meglio?
            print('\nprovo a fare di meglio', sum(p_of_victory),'\n')
            new_useful = useful.copy()
            for uls in useless:
                new_useful.append(uls)
                p_of_victory, best_schieramento = await calculate_best_strategy(new_useful,enemy_team, enemy_powers, multiplier)
                if 0 not in p_of_victory:
                    break

        # TODO: migliorare logica di capopalestra (check se il punteggio non migliora, se vengono schierati useful o useless, etc...) 
        if is_capopalestra and sum(p_of_victory)<600:
            new_useful = useful.copy()
            for uls in useless:
                new_useful.append(uls)
                p_of_victory, best_schieramento = await calculate_best_strategy(new_useful,enemy_team, enemy_powers, multiplier)
                if sum(p_of_victory)>=600:
                    break
            for lv100 in lvl_100:
                new_useful.append(lv100)
                p_of_victory, best_schieramento = await calculate_best_strategy(new_useful,enemy_team, enemy_powers, multiplier)
                if sum(p_of_victory)>=600:
                    break
        pos_da_schierare = [str(p[4]) for p in best_schieramento]            
        return ''.join(pos_da_schierare)
    except Exception as e:
        print('Errore nel calcolare la miglior strategia!',e)

    return 'Ho incontrato qualcuno, ma non so che fare.'
    
async def handle_first_lega_message(event, text, client):
    teams = await load_two_teams_from_photos(event, client) 
    team = teams[0] if teams else None
    enemy_team = teams[1] if len(teams) > 1 else None
    print("Team:", team)
    print("Enemy team:", enemy_team)
    
    team = await lega_utility(team,enemy_team,first_time = True)

    await dump_x_in_json(team, "team_lega")
    try:
        await dump_x_in_json(enemy_team, "enemy_team_lega")
    except Exception as e: 
        print(f"Error dumping enemy_team {e}")
    message = ""
    message += "Il team avversario è \n{}".format(''.join([f"\t\t\t{p[0].capitalize()}\n" for p in enemy_team if p[0] is not None]))
    message += "\nIl mio team è \n{}".format(''.join([f"\t\t\t{p[0].capitalize()} ({p[2]})\n" for p in team if p[0] is not None]))
    await event.reply(message)

async def load_two_teams_from_photos(event, client):
    await asyncio.sleep(30)  # aspetta 30 sec
    messages = await client.get_messages(
        event.chat_id,
        min_id=event.id,
        limit=5
    )
    teams = []
    for msg in messages:
        if not msg.photo:
            continue
        try:
            photo_bytes = await msg.download_media(bytes)
            pil_image = Image.open(BytesIO(photo_bytes))

            if msg.text == "Ecco la card del tuo avversario!":
                await msg.reply("Ho ricevuto la foto della squadra avversaria, la aggiorno...")  # opzionale
                team = await aggiorna_enemy_team_da_foto(pil_image)
            elif msg.text == "Ecco la tua card aggiornata!":
                await msg.reply("Ho ricevuto la foto della squadra, la aggiorno...")  # opzionale
                team = await aggiorna_team_da_foto(pil_image)
                await dump_team_in_json(team, event, client)
            else:
                continue  # testo non riconosciuto, salta

            teams.append(team)

            if len(teams) == 2:
                break
        except Exception as e:
            continue

    if len(teams) < 2:
        await event.reply(f"Ho trovato solo {len(teams)} foto su 2 attese... controlla i messaggi.")
    return teams

async def lega_turn_1_no_hint(event, text, client):
    # No need to calculate anything, schiero i 3 più inutili!
    await event.reply("Non ho l'indizio... Aspetto un attimo e poi schiero!")
    await asyncio.sleep(THINK_TIME) # Tempo per pensare... fingi di non essere un bot...
    team = await load_x_from_json("team_lega")

    pos_da_schierare = [str(p[4]) for p in team[-3:]]
    return ''.join(pos_da_schierare)

async def lega_turn_2_no_hint(event, text, client):
    await event.reply("Non ho l'indizio... Aspetto un attimo e poi schiero!")
    await asyncio.sleep(THINK_TIME) # Tempo per pensare... fingi di non essere un bot...
    team = await load_x_from_json("team_lega")
    enemy_team = await load_x_from_json("enemy_team_lega")
    team = await lega_utility(team, enemy_team)

    if (await load_x_from_json("win_1")) == False: # Ho perso il primo match, schiero i 3 più forti
        pos_da_schierare = [str(p[4]) for p in team[:3]]
    else:
        pos_da_schierare = [str(p[4]) for p in team[-3:]]
    return ''.join(pos_da_schierare)

async def lega_turn_3_no_hint(event, text, client):
    await event.reply("Non ho l'indizio... Aspetto un attimo e poi schiero!")
    await asyncio.sleep(THINK_TIME) # Tempo per pensare... fingi di non essere un bot...
    team = await load_x_from_json("team_lega")
    pos_da_schierare = [str(p[4]) for p in team[:3]]
    return ''.join(pos_da_schierare)

async def lega_hint_ask():
    x = random.choice([1,2,3])
    await dump_x_in_json(x, "indizio_chiesto")
    return x

async def lega_turn_1_hint_reply(event, text, client):
    await event.reply("Ho l'indizio... Aspetto un attimo e poi schiero!")
    await asyncio.sleep(THINK_TIME) # Tempo per pensare... fingi di non essere un bot...

    team = await load_x_from_json("team_lega")
    enemy_team = await load_x_from_json("enemy_team_lega")
    indizio_chiesto = await load_x_from_json("indizio_chiesto")
    enemy_poke, enemy_pl = await extract_pokemon_and_pl_lega(text)
    print(indizio_chiesto)
    print(enemy_poke, enemy_pl)

    for i,pp in enumerate(enemy_team):
        if pp[0] == enemy_poke:
            enemy_team.pop(i)
            break

    team = await lega_utility(team, enemy_team)

    vincente = one_vs_team_lega(team, enemy_poke, enemy_pl)

    if vincente == None:
        pos_da_schierare = [str(p[4]) for p in team[-3:]]
        return ''.join(pos_da_schierare)
    else:

        for i,pp in enumerate(team):
            if pp[0] == vincente[0] and pp[4] == vincente[4]:
                team.pop(i)
                break

        pos_vincente = str(vincente[4])
        print("Vincente:", vincente)
        print("Team rimanente:", team)
        print("Indizio chiesto:", indizio_chiesto)
        print("Pos vincente:", pos_vincente)
        if indizio_chiesto == 1:
            pos_da_schierare = pos_vincente + str(team[2][4]) + str(team[4][4])
        if indizio_chiesto == 2:
            pos_da_schierare = str(team[2][4]) + pos_vincente + str(team[4][4])
        if indizio_chiesto == 3:
            pos_da_schierare = str(team[2][4]) + str(team[4][4]) + pos_vincente
        return pos_da_schierare

async def lega_turn_2_hint_reply(event, text, client):
    await event.reply("Ho l'indizio... Aspetto un attimo e poi schiero!")
    await asyncio.sleep(THINK_TIME) # Tempo per pensare... fingi di non essere un bot...

    team = await load_x_from_json("team_lega")
    enemy_team = await load_x_from_json("enemy_team_lega")
    indizio_chiesto = await load_x_from_json("indizio_chiesto")
    enemy_poke, enemy_pl = await extract_pokemon_and_pl_lega(text)
    print(indizio_chiesto)
    print(enemy_poke, enemy_pl)

    for i,pp in enumerate(enemy_team):
        if pp[0] == enemy_poke:
            enemy_team.pop(i)
            break

    team = await lega_utility(team, enemy_team)

    vincente = one_vs_team_lega(team, enemy_poke, enemy_pl)

    if (await load_x_from_json("win_1")) == False: # Ho perso il primo match, schiero i 3 più forti
        print('sono arrivato qui')
        if vincente == None:
            pos_da_schierare = [str(p[4]) for p in team[:3]]
            return ''.join(pos_da_schierare)
        else:

            for i,pp in enumerate(team):
                if pp[0] == vincente[0] and pp[4] == vincente[4]:
                    team.pop(i)
                    break

            pos_vincente = str(vincente[4])
            if indizio_chiesto == 1:
                pos_da_schierare = pos_vincente + str(team[0][4]) + str(team[5][4])
            if indizio_chiesto == 2:
                pos_da_schierare = str(team[0][4]) + pos_vincente + str(team[5][4])
            if indizio_chiesto == 3:
                pos_da_schierare = str(team[0][4]) + str(team[5][4]) + pos_vincente
            return pos_da_schierare
    else:
        if vincente == None:
            pos_da_schierare = [str(p[4]) for p in team[-3:]]
            return ''.join(pos_da_schierare)
        else:

            for i,pp in enumerate(team):
                if pp[0] == vincente[0] and pp[4] == vincente[4]:
                    team.pop(i)
                    break

            pos_vincente = str(vincente[4])
            if indizio_chiesto == 1:
                pos_da_schierare = pos_vincente + str(team[0][4]) + str(team[1][4])
            if indizio_chiesto == 2:
                pos_da_schierare = str(team[0][4]) + pos_vincente + str(team[1][4])
            if indizio_chiesto == 3:
                pos_da_schierare = str(team[0][4]) + str(team[1][4]) + pos_vincente
            return pos_da_schierare        

async def lega_turn_3_hint_reply(event, text, client):
    await event.reply("Ho l'indizio... Aspetto un attimo e poi schiero!")
    await asyncio.sleep(THINK_TIME) # Tempo per pensare... fingi di non essere un bot...

    team = await load_x_from_json("team_lega")
    enemy_team = await load_x_from_json("enemy_team_lega")
    indizio_chiesto = await load_x_from_json("indizio_chiesto")
    enemy_poke, enemy_pl = await extract_pokemon_and_pl_lega(text)
    print(indizio_chiesto)
    print(enemy_poke, enemy_pl)

    for i,pp in enumerate(enemy_team):
        if pp[0] == enemy_poke:
            enemy_team.pop(i)
            break

    team = await lega_utility(team, enemy_team)

    vincente = one_vs_team_lega(team, enemy_poke, enemy_pl)

    if vincente == None:
        pos_da_schierare = [str(p[4]) for p in team[-3:]]
        return ''.join(pos_da_schierare)
    else:

        for i,pp in enumerate(team):
            if pp[0] == vincente[0] and pp[4] == vincente[4]:
                team.pop(i)
                break

        pos_vincente = str(vincente[4])
        if indizio_chiesto == 1:
            pos_da_schierare = pos_vincente + str(team[0][4]) + str(team[1][4])
        if indizio_chiesto == 2:
            pos_da_schierare = str(team[0][4]) + pos_vincente + str(team[1][4])
        if indizio_chiesto == 3:
            pos_da_schierare = str(team[0][4]) + str(team[1][4]) + pos_vincente
        return pos_da_schierare
    
async def compile_answer_lega(event, text, client, vittoria):
    team = await load_x_from_json("team_lega")
    enemy_team = await load_x_from_json("enemy_team_lega")

    out_team, out_enemy_team = await extract_all_matches_lega(text)

    print("Team estratto dal testo:", out_team)
    print("Enemy team estratto dal testo:", out_enemy_team)

    for p in out_team:
        for i,pp in enumerate(team):
            if pp[0] == p:
                team.pop(i)
                break

    for p in out_enemy_team:
        for i,pp in enumerate(enemy_team):
            if pp[0] == p:
                enemy_team.pop(i)
                break

    await dump_x_in_json(team, "team_lega")
    await dump_x_in_json(enemy_team, "enemy_team_lega")
    fase_lega = await load_x_from_json("fase_lega")
    if vittoria:
        await event.reply("Ho vinto! Aggiorno le squadre...")
        if fase_lega == 1:
            await dump_x_in_json(True, "win_1")
        elif fase_lega == 2:
            await dump_x_in_json(True, "win_2")
    else:
        await event.reply("Ho perso! Aggiorno le squadre...")
        if fase_lega == 1:
            await dump_x_in_json(False, "win_1")
        elif fase_lega == 2:
            await dump_x_in_json(False, "win_2")

    await dump_x_in_json(fase_lega+1, "fase_lega")


async def delete_messages_before(event, client, limit=5, exclude=""):
    print(f"[delete] Fetching last {limit} messages BEFORE id={event.id} in chat {event.chat_id}...")

    messages = await client.get_messages(
        event.chat_id,
        max_id=event.id,  # messages BEFORE the event
        limit=limit
    )

    #print(f"[delete] Found {len(messages)} messages")

    to_delete = []
    for msg in messages:
        if exclude and msg.text and exclude in msg.text:
            #print(f"[delete] Skipping protected message id={msg.id}: '{msg.text[:50]}'")
            continue
        #print(f"[delete] Marking for deletion id={msg.id}: '{str(msg.text)[:50]}'")
        to_delete.append(msg.id)

    #print(f"[delete] Deleting {len(to_delete)} messages: {to_delete}")

    if to_delete:
        await client.delete_messages(event.chat_id, to_delete)
        #print("[delete] Done.")
    else:
        print("[delete] Nothing to delete.")


async def delete_messages_after(event, client, limit=5, exclude=""):
    #print(f"[delete] Fetching last {limit} messages AFTER id={event.id} in chat {event.chat_id}...")

    messages = await client.get_messages(
        event.chat_id,
        min_id=event.id,  # messages AFTER the event
        limit=limit
    )

    #print(f"[delete] Found {len(messages)} messages")

    to_delete = []
    for msg in messages:
        if exclude and msg.text and exclude in msg.text:
            #print(f"[delete] Skipping protected message id={msg.id}: '{msg.text[:50]}'")
            continue
        #print(f"[delete] Marking for deletion id={msg.id}: '{str(msg.text)[:50]}'")
        to_delete.append(msg.id)

    #print(f"[delete] Deleting {len(to_delete)} messages: {to_delete}")

    if to_delete:
        await client.delete_messages(event.chat_id, to_delete)
        #print("[delete] Done.")
    else:
        print("[delete] Nothing to delete.")