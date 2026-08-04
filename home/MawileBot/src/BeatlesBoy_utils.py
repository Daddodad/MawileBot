from email.mime import text
import random
import re
import os
import sys
import json
import pypokedex as poke
from io import BytesIO
from PIL import Image, ImageDraw
from scipy.optimize import linear_sum_assignment
import numpy as np

if os.path.exists('/home/SableyeBot/src'):
    ENV_PATH = '/home/SableyeBot/src'
    sys.path.insert(0,ENV_PATH) # SableyeBot
else:
    ENV_PATH = './home/MawileBot/src'
    sys.path.insert(0,ENV_PATH) # MawileBot
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
from poke_lib import (
                        automatic_card_reader, calculate_bonus, calculate_bonus_via_types, 
                        get_power, poke_cell, similar_pokemon_name,
                        get_poke_bst, EMOJI_TO_TYPE,
                        check_alt_forms, next_gym, poke_cell_gym, generate_all_types_combo,
                        get_casella
                      )


tipi_to_types = {
    'Normale': 'Normal','Fuoco': 'Fire','Acqua': 'Water','Erba': 'Grass','Elettro': 'Electric','Ghiaccio': 'Ice','Lotta': 'Fighting','Veleno': 'Poison',
    'Terra': 'Ground','Volante': 'Flying','Psico': 'Psychic','Coleottero': 'Bug','Roccia': 'Rock','Spettro': 'Ghost','Drago': 'Dragon','Buio': 'Dark','Acciaio': 'Steel','Folletto': 'Fairy'
}

async def dump_x_in_json(x, x_name):
    json_path = os.path.join(ENV_PATH, "BeatlesBoy_info.json")
    print(f"Dumping {x_name} to:", json_path)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data[x_name] = x
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

async def load_x_from_json(x_name):
    json_path = os.path.join(ENV_PATH, "BeatlesBoy_info.json")
    print(f"Loading {x_name} from:", json_path)
    with open(json_path, "r", encoding="utf-8") as f:
        x = (json.load(f))[x_name]
    return x

async def load_team_from_json_simple():
    json_path = os.path.join(ENV_PATH, "BeatlesBoy_info.json")
    print("Loading team from:", json_path)
    with open(json_path, "r", encoding="utf-8") as f:
        team = (json.load(f))["team"]
    return team

async def find_evo_at_level_x(pokemon, level_x):

    pokemon = await similar_pokemon_name(pokemon.lower(), r = False)
    pokemon_x = pokemon.lower()

    with open(ENV_PATH+f"/even_evo_file.json", 'r') as ef:
        evo_dict = json.load(ef)  
    if pokemon in evo_dict:
        if len(evo_dict[pokemon]) >2:
            if evo_dict[pokemon][0] == 'last':
                if level_x < evo_dict[pokemon][1][0]: # Torno indietro?
                    pokemon_x = evo_dict[pokemon][1][1]
                elif level_x < evo_dict[pokemon][2][0]: # Torno indietro?
                    pokemon_x = evo_dict[pokemon][2][1]
            if evo_dict[pokemon][0]=="base":
                if level_x >= evo_dict[pokemon][2][0]:
                    pokemon_x = evo_dict[pokemon][2][1]
                elif level_x >= evo_dict[pokemon][1][0]:
                    pokemon_x = evo_dict[pokemon][1][1]
            elif evo_dict[pokemon][0]=="mid":
                if level_x < evo_dict[pokemon][1][0]: # Torno indietro?
                    pokemon_x = evo_dict[pokemon][1][1]
                elif level_x >= evo_dict[pokemon][2][0]:
                    pokemon_x = evo_dict[pokemon][2][1]
        else:
            if evo_dict[pokemon][0] == 'last':
                if level_x < evo_dict[pokemon][1][0]: # Torno indietro?
                    pokemon_x = evo_dict[pokemon][1][1]
            if evo_dict[pokemon][0]=="base":
                if level_x >= evo_dict[pokemon][1][0]:
                    pokemon_x = evo_dict[pokemon][1][1]

    return pokemon_x

async def pokemon_utility(pokemon,lvl, data = {"lvlup": False, "catch": False, "drop": False}):
    if pokemon is  None:
        return 0
    #TODO: implement a better utility function
        
    pokemon = await similar_pokemon_name(pokemon.lower(), r = False)
    fully_evo = await find_evo_at_level_x(pokemon, 100)
    max_bst = await get_poke_bst(fully_evo)
    if fully_evo in (await load_x_from_json("mega")):
        print('Mega BOOST!')
        max_bst = await get_poke_bst(fully_evo+'-mega')
        #print(f"BST di Mega {await find_evo_at_level_x(pokemon, 100)} a livello 100: {max_bst}")

    else:
        #print(f"BST di {await find_evo_at_level_x(pokemon, 100)} a livello 100: {max_bst}")
        pass


    utility_bst = max_bst/620*10
    utility_lvl = lvl/10

    utility = utility_bst * 0.7 + utility_lvl * 0.3
    print('base utility = ', utility)
    try:
        # bonus fully evo all'inizio
        current_bst = await get_poke_bst(pokemon)
        if current_bst > 450 and get_casella()<=6:
            print("bonus fullyevo = +1")
            utility+=1
        elif current_bst > 450 and get_casella()<=12:
            print("bonus fullyevo = +0.5")
            utility+=0.5
    except Exception as e:
        print(f"Error calculating bonus fullyevo: {e}")

    try:
        malus_in = await malus_inallenabile(pokemon,lvl, **data)
        utility += malus_in
        print('malus inallenabile = ', malus_in)
    except Exception as e:
        print(f"Error calculating malus inallenabile: {e}")

    try:
        next_gym_b = await next_gym_bonus(pokemon, lvl, **data)
        utility += next_gym_b
        print('next gym bonus = ', next_gym_b)
    except Exception as e:
        print(f"Error calculating next gym bonus: {e}")

    return round(utility, 2)  # 0-10 scale (except bonus next gym)

async def malus_inallenabile(pokemon, lvl, **event):

    if event.get("catch") == False:
        return 0

    try:
        _, enemy_powers, capopalestra_powers, multiplier, _ = await poke_cell(1)
    except:
        _, enemy_powers, capopalestra_powers, multiplier, _ = await poke_cell(0)

    low_power = min(enemy_powers)
    power = round(await get_poke_bst(pokemon)*lvl/100)

    malus = 0
    while power < low_power and lvl <= 100:
        malus -=0.05
        lvl +=1
        pokemon = await find_evo_at_level_x(pokemon, lvl)
        power = round(await get_poke_bst(pokemon)*lvl/100)

    return malus

def win_perc_over_gym(gym_type, low_power, pokemon, power, multiplier):
    all_types_combo = generate_all_types_combo(gym_type)
    wins = 0
    for t in all_types_combo:
        types2 = poke.get(name=pokemon).types
        bonus = calculate_bonus_via_types(t, types2 ,multiplier)
        # print(f"Types: {t}, Bonus: {bonus}, Power: {power}, Low Power: {low_power}")
        if power - bonus[0] + bonus[1] > low_power:
            wins += 1
    return wins / len(all_types_combo)

async def next_gym_bonus(pokemon, lvl, **event):

    gym_type,multiplier,casella_gym = (await next_gym())
    _, _, enemy_powers, multiplier, _ = poke_cell_gym(casella_gym-1)
    low_power = min(enemy_powers)
    #print(f"Next gym type: {gym_type}, casella: {casella_gym}, low power: {low_power}, multiplier: {multiplier}")

    # if the average win percentage of the current team is already above 66%, we can skip the bonus calculation for a new catch (don't really need to)
    if event.get("catch") == True:
        try: 
            team = (await load_team_from_json_simple())
        except:
            team = [["chespin",7],["unown",5],["pancham",5],
                    ["sableye",5],["skorupi",5]]
        w_p = []
        for (p, l) in team:
            if p is not None:
                pp = round(await get_poke_bst(await find_evo_at_level_x(p, l+3))*(l+3)/100)
                w_p.append(win_perc_over_gym(gym_type, low_power, p, pp, multiplier))

        w_p = sorted(w_p, reverse=True)[:6]
        w_p += [0] * (6 - len(w_p))
        avg_win_perc = sum(w_p) / len(w_p)
        if avg_win_perc > 0.66:
            return 0

    # IF NOT, we need a new pokemn ASAP!
     
    power = round(await get_poke_bst(pokemon)*lvl/100)
    win_perc = win_perc_over_gym(gym_type, low_power, pokemon, power, multiplier)
    #print(f"{pokemon}: Win percentage against next gym: {win_perc*100:.2f}%")

    power_plus5 = round(await get_poke_bst(await find_evo_at_level_x(pokemon, lvl+5))*(lvl+5)/100)
    win_perc_plus5 = win_perc_over_gym(gym_type, low_power, pokemon, power_plus5, multiplier)
    #print(f"{pokemon} + 5lvl: Win percentage against next gym: {win_perc_plus5*100:.2f}%")

    if win_perc_plus5 > 0.70:
        if win_perc < 0.70 and event.get("lvlup") == True:
            return 8  # This will also boost in training, not only the catches!
                        # Slightly inferior to nilb
        
    if win_perc > 0.70 and event.get("catch") == True:
        return 999  # We need to catch this beast!
    
    if win_perc > 0.70 and event.get("drop") == True:
        return 200 # Do not drop this beast!
    
    return 0

async def lega_utility_core (poke, lvl, power, enemy_team):
    mod = 0
    print('called lega utility')
    # FIGHT A PARI LIVELLO
    for enemy in enemy_team:
        if enemy[0] is None:
            continue
        enemy_power = await get_power(enemy[0], lvl)
        bonus = calculate_bonus(poke,enemy[0],20)
        mod_bonus = bonus[0]-bonus[1]
        print(f"Comparing {poke} vs {enemy[0]} at same level: power {power} vs enemy power {enemy_power}, bonus {mod_bonus}")
        if power + mod_bonus >= enemy_power:
            mod += 10
        else:
            mod -= 10

    # FIGHT A PARI POTENZA  
    for enemy in enemy_team:
        if enemy[0] is None:
            continue
        bonus = calculate_bonus(poke,enemy[0],20)
        mod_bonus = bonus[0]-bonus[1]
        if power + mod_bonus >= power:
            mod += 10
        else:
            mod -= 10

    u = (power + mod)/620
    return round(u*10,2) # 0-10 scale

async def lega_utility(team, enemy_team, first_time = False):
    if first_time:
        team_u = []
        for index, (poke, lvl) in enumerate(team):
            if poke is None:
                team_u.append((None, 0, 0, 0, index+1))
            else:
                power = await get_power(poke, lvl)
                u = await lega_utility_core(poke, lvl, power, enemy_team)

                team_u.append((poke, lvl, u, power, index+1))
        team_u.sort(key=lambda x: x[2], reverse=True)
    else:
        team_u = []
        for (poke, lvl, _ , correct_power, correct_index) in team:
            if poke is None:
                team_u.append((None, 0, 0, 0, correct_index))
            else:
                u = await lega_utility_core(poke, lvl, correct_power, enemy_team)
                team_u.append((poke, lvl, u, correct_power, correct_index))
                
        team_u.sort(key=lambda x: x[2], reverse=True)   
    return team_u

async def filter_team(team, remove_100=False, nilb=False, data_filter={"lvlup": False, "drop": False}):
    if not team:
        return [], [], []

    # 1) Trova i pokemon DELLA TUA SQUADRA, SENZA ALCUN BONUS!
    utilities_clean = []
    lvl_100 = []
    for index, (poke, lvl) in enumerate(team):
        u = await pokemon_utility(poke, lvl, data={"lvlup": False, "catch": False, "drop": False})
        entry = (poke, lvl, u, await get_power(poke, lvl), index + 1)
        if remove_100 and lvl == 100:
            lvl_100.append(entry)
        else:
            utilities_clean.append(entry)
    utilities_clean.sort(key=lambda x: x[2], reverse=True)

    # NEL PRIMO-SECONDO PERCORSO, PUNTA A 4 POKEMON FORTI
    # NEL TERZO-QUARTO, ESPANDI A 5
    # NEL QUINTO-SESTO, ESPANDI A 6
    casella = get_casella()
    if casella <= 12:
        num_utils = 4
    elif casella <= 24:
        num_utils = 5
    else:
        num_utils = 6

    num_utils = max(1, num_utils - len(lvl_100))
    num_utils = min(num_utils, len(utilities_clean))

    # 2) Seleziona il top-N "di default" (nessun bonus) -> questa e' la base
    useful_nilb = [e for e in utilities_clean[:num_utils]]  # shallow copy of the slice

    # 3) Applica il nilb SOLO a questi top-N selezionati
    # Teniamo traccia del delta nilb per indice, cosi' dopo possiamo sommarlo
    # al delta del bonus senza perdere il valore raw originale.
    nilb_delta_by_index = {}
    if nilb:
        try:
            _, enemy_powers, capopalestra_powers, multiplier, _ = await poke_cell(1)
        except Exception:
            _, enemy_powers, capopalestra_powers, multiplier, _ = await poke_cell(0)
        for i in range(len(useful_nilb)):
            p = useful_nilb[i]
            if p[3] < enemy_powers[0]:
                nilb_delta_by_index[p[4]] = 10
                useful_nilb[i] = (p[0], p[1], p[2] + 10, p[3], p[4])
        useful_nilb.sort(key=lambda x: x[2], reverse=True)

    # 4) Ricalcola le utility su TUTTA la squadra applicando data_filter (bonus)
    utilities_bonus = []
    for index, (poke, lvl) in enumerate(team):
        if remove_100 and lvl == 100:
            continue
        u = await pokemon_utility(
            poke, lvl,
            data={"lvlup": data_filter['lvlup'], "catch": False, "drop": data_filter['drop']}
        )
        utilities_bonus.append((poke, lvl, u, await get_power(poke, lvl), index + 1))
    utilities_bonus.sort(key=lambda x: x[2], reverse=True)

    # 5) Guarda TUTTI gli elementi (non solo il top-N) e trova quelli la cui utility
    # e' cambiata per via del bonus (data_filter) rispetto alla versione clean
    clean_by_index = {e[4]: e for e in utilities_clean}
    bonus_by_index = {e[4]: e for e in utilities_bonus}

    changed_indices = {
        idx for idx, bonus_entry in bonus_by_index.items()
        if idx in clean_by_index and bonus_entry[2] != clean_by_index[idx][2]
    }

    if changed_indices:
        # raw + nilb_delta + bonus_delta, cosi' chi prende entrambi i bonus li somma
        stacked_by_index = {}
        for idx in changed_indices:
            raw_entry = clean_by_index[idx]
            raw = raw_entry[2]
            nilb_delta = nilb_delta_by_index.get(idx, 0)
            bonus_delta = bonus_by_index[idx][2] - raw
            stacked_utility = raw + nilb_delta + bonus_delta
            stacked_by_index[idx] = (raw_entry[0], raw_entry[1], stacked_utility, raw_entry[3], idx)

        useful_by_index = {e[4]: e for e in useful_nilb}
        useful_by_index.update(stacked_by_index)  # overwrite existing / add new
        useful_nilb = list(useful_by_index.values())
        useful_nilb.sort(key=lambda x: x[2], reverse=True)

    # 6) I rimanenti = utilities_clean meno quelli gia' selezionati
    final_selected_indices = {e[4] for e in useful_nilb}
    remaining = [e for e in utilities_clean if e[4] not in final_selected_indices]

    return useful_nilb, remaining, lvl_100

async def extract_pokemon_and_pl(text):
    # Pokémon name (unchanged)
    name_match = re.search(
        r"hai incontrato\s+(?:il\s+leggendario\s+)?([A-Za-zÀ-ÿ'’]+)",
        text,
        re.IGNORECASE
    )

    # PL value
    pl_match = re.search(r"PL\s*(\d+)", text)

    pokemon = name_match.group(1) if name_match else None
    pl = int(pl_match.group(1)) if pl_match else None

    # --- Extract emojis ---
    emojis = []

    for line in text.splitlines():
        if "PL" in line:
            stat_line = line.strip()
            break
    else:
        stat_line = ""

    if pokemon and stat_line:
        # Remove name and everything after PL
        middle = stat_line.replace(pokemon, "")
        middle = middle.split("PL")[0]

        emojis = [ch for ch in middle if ch in EMOJI_TO_TYPE]

    # print(emojis[0])
    # print(emojis[1] if len(emojis)>1 else None)
    pokemon = await similar_pokemon_name(pokemon.lower(), r = False)
    #print('\n Emoji 1: ', emojis[0],'Emoji 2', emojis[1] if len(emojis)>1 else None, '\n')
    pokemon = await check_alt_forms(pokemon,
                                    EMOJI_TO_TYPE.get(emojis[0],None),
                                    EMOJI_TO_TYPE.get(emojis[1],None) if len(emojis) >1 else None
                                    )
    print('\nEXTRACT POKEMON AND PL: ',pokemon, pl, EMOJI_TO_TYPE.get(emojis[0],None), EMOJI_TO_TYPE.get(emojis[1],None) if len(emojis) >1 else None)

    return pokemon, pl

async def extract_pokemon_and_pl_lega(text):
    lines = text.splitlines()
    stat_line = ""
    for line in lines:
        if line.strip().startswith("-"):
            stat_line = line.strip()
            break
    
    if not stat_line:
        return None, None
    
    line_match = re.search(r"-\s*([^-]+?)\s*(?:[\U00010000-\U0010ffff]|[\u2600-\u27ff]|\d)", stat_line)
    
    if line_match:
        pokemon_raw = line_match.group(1).strip()
    else:
        pokemon_raw = stat_line.replace("-", "").split()[0]

    all_numbers = re.findall(r"(\d+)", stat_line)
    pl = int(all_numbers[-1]) if all_numbers else None

    pokemon_lower = pokemon_raw.lower().strip()
    if "mega " in pokemon_lower:
        pokemon_final_name = "mega-" + pokemon_lower.replace("mega ", "").strip()
    else:
        pokemon_final_name = pokemon_lower.replace(" ", "-").replace("'", "-")

    emojis = []
    middle = stat_line.replace("-", "").replace(pokemon_raw, "")
    if pl:
        middle = middle.replace(str(pl), "")

    for ch in middle:
        if ord(ch) > 127: # Emoji e simboli speciali
            emojis.append(ch)

    pokemon_cleaned = await similar_pokemon_name(pokemon_final_name, r = False)
    
    type1 = EMOJI_TO_TYPE.get(emojis[0], None) if len(emojis) > 0 else None
    type2 = EMOJI_TO_TYPE.get(emojis[1], None) if len(emojis) > 1 else None

    pokemon_final = await check_alt_forms(pokemon_cleaned, type1, type2)
    
    print(f'Letto: {pokemon_final}, PL: {pl}, Tipi: {type1}, {type2}')

    return pokemon_final.strip(), pl

import re

async def extract_all_matches_lega(text):
    colonna_sinistra = []
    colonna_destra = []
    
    for line in text.splitlines():
        line = line.strip()
        
        if " vs " in line:
            parts = line.split(" vs ")
            if len(parts) < 2: continue
            
            # Sinistra: rimuoviamo l'eventuale trattino iniziale
            left_raw = parts[0].lstrip("- ").strip()
            right_raw = parts[1].strip()
            
            info_sx = await process_pokemon_side(left_raw)
            info_dx = await process_pokemon_side(right_raw)
            
            colonna_sinistra.append(info_sx)
            colonna_destra.append(info_dx)
            
    return colonna_sinistra, colonna_destra

async def extract_all_matches_pvp(text):
    vittorie_sx, vittorie_dx = [], []
    sconfitte_sx, sconfitte_dx = [], []
    pareggi_sx, pareggi_dx = [], []

    section_map = {
        "VITTORIE:":   (vittorie_sx,  vittorie_dx),
        "SCONFITTE:":  (sconfitte_sx, sconfitte_dx),
        "PAREGGI:":    (pareggi_sx,   pareggi_dx),
    }
    current_left, current_right = None, None

    for line in text.splitlines():
        line = line.strip()

        # Detect section headers
        upper = line.upper()
        if upper in section_map:
            current_left, current_right = section_map[upper]
            continue

        # Skip match lines if no section has been declared yet
        if current_left is None:
            continue

        if " vs " in line:
            parts = line.split(" vs ")
            if len(parts) < 2:
                continue

            left_raw  = parts[0].lstrip("- ").strip()
            right_raw = parts[1].strip()

            info_sx = await process_pokemon_side(left_raw)
            info_dx = await process_pokemon_side(right_raw)

            current_left.append(info_sx)
            current_right.append(info_dx)

    return (
        vittorie_sx,  vittorie_dx,
        sconfitte_sx, sconfitte_dx,
        pareggi_sx,   pareggi_dx,
    )

async def process_pokemon_side(side_text):
    side_text = side_text.lstrip("- ").strip()
    
    pl_match = re.search(r"(\d+)\s*\(", side_text)
    pl = int(pl_match.group(1)) if pl_match else None
    
    # 3. NOME: Usiamo una Regex che esclude solo le Emoji 
    # e si ferma prima del valore PL identificato sopra
    # Cattura tutto fino alla prima emoji o fino al numero del PL
    # (Evitiamo di fermarci ai numeri interni al nome come in Porygon2)

    emoji_pattern = r"[\U00010000-\U0010ffff\u2600-\u27ff]"
    
    if pl_match:
        name_and_emojis = side_text[:pl_match.start()].strip()
    else:
        name_and_emojis = side_text

    split_name = re.split(emoji_pattern, name_and_emojis, maxsplit=1)
    pokemon_raw = split_name[0].strip() if split_name else ""

    if not pokemon_raw or pokemon_raw == "":
        print("Attenzione: Nome Pokémon non trovato nella stringa.")
        return None

    p_lower = pokemon_raw.lower().strip()
    
    if p_lower.startswith("mega "):
        p_name = "mega-" + p_lower[5:].strip()
    else:
        p_name = p_lower.replace(" ", "-").replace("'", "-")

    emojis = [ch for ch in side_text if ord(ch) > 127]
    type1 = EMOJI_TO_TYPE.get(emojis[0]) if len(emojis) > 0 else None
    type2 = EMOJI_TO_TYPE.get(emojis[1]) if len(emojis) > 1 else None

    pokemon_cleaned = await similar_pokemon_name(p_name, r = False)
    pokemon_final = await check_alt_forms(pokemon_cleaned, type1, type2)
    
    return pokemon_final

async def extract_number_of_pvp_choices(text):
    clean = text.replace("\n", " ")
    words = clean.split()
    i = words.index("schiera")
    num_pokemon = int(words[i + 1])
    return num_pokemon

async def calculate_winning_options_selvatico(enemy_poke, enemy_pl, team):
    _, _, _, multiplier, _ = await poke_cell(0)
    winning_options = []

    print(' il mio team:', team )
    print("Calcolo delle opzioni vincenti contro", enemy_poke, "PL", enemy_pl)
    for your_poke, lvl, utility, pl, index in team:
        print("Valutazione del Pokémon:", your_poke, "livello", lvl, "utility", utility)

        if your_poke is not None:

            types1 = poke.get(name = your_poke).types
            types2 = poke.get(name = enemy_poke).types

            # print("Tipi del Pokémon:", types1)
            # print("Tipi del nemico:", types2)
            bonus = calculate_bonus_via_types(types1, types2 ,multiplier)

            bonus_netto = bonus[0]-bonus[1]

            # print("Bonus calcolato:", bonus_netto)
            if pl + bonus_netto >= enemy_pl:
                winning_options.append((your_poke, pl, bonus_netto, index, utility))

    print("Opzioni vincenti calcolate:", winning_options)
    winning_options.sort(key=lambda x: x[4], reverse=True) # ordina per utility decrescente
    return winning_options

async def calculate_potenziabili(tipi, team):
    potenziabili = []

    for your_poke, lvl, utility, pl, index in team:
        if your_poke is not None:
            if utility>10: # nilb
                potenziabili.append((your_poke, utility, "nessun tipo", index))
                break

            types1 = poke.get(name = your_poke).types

            for tipo in tipi:
                if tipi_to_types[tipo].lower() in [t.lower() for t in types1]:
                    potenziabili.append((your_poke, utility, tipo, index))
                    break

    if potenziabili == []:
        for your_poke, lvl, utility, pl, index in team:
            if your_poke is not None:
                potenziabili.append((your_poke, utility, "nessun tipo", index))

    potenziabili.sort(key=lambda x: x[1], reverse=True) # ordina per utility decrescente
    return potenziabili

async def aggiorna_team_da_foto(pil_image):
    secret_data,errors = await automatic_card_reader(pil_image)
    #print("Dati segreti estratti:", secret_data)
    #print("Errori durante l'estrazione:", errors)
    # TODO Gestire errori
    return secret_data

async def aggiorna_enemy_team_da_foto(pil_image):
    secret_data,errors = await automatic_card_reader(pil_image, only_name = True)
    #print("Dati segreti estratti:", secret_data)
    #print("Errori durante l'estrazione:", errors)
    # TODO Gestire errori
    return secret_data

async def extract_types(text):
    types = []
    for line in text.splitlines():
        line = line.strip()
        if "+" not in line:
            continue
        if line.startswith("Pokemon Qualsiasi"):
            continue
        # take the first word (type name)
        pokemon_type = line.split()[0]
        types.append(pokemon_type)
    return types

async def read_pokemons_from_trainer(text):
    result = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("-"):
            continue
        row = line[1:]
        name = ""
        types = []
        i = 0
        while i < len(row):
            ch = row[i]
            matched = False
            for emoji, ptype in EMOJI_TO_TYPE.items():
                if row.startswith(emoji, i):
                    types.append(ptype)
                    i += len(emoji)
                    matched = True
                    break

            if not matched:
                name += ch
                i += 1

        name = name.strip()
        if len(types) == 0:
            types = [None, None]
        elif len(types) == 1:
            types.append(None)
        else:
            types = types[:2]
        result.append([name, types[0], types[1]])

    for r in result:
        print(r)
        r[0] = await similar_pokemon_name(r[0].lower(), r = False)
        print(r)
        r[0] = await check_alt_forms(r[0],r[1],r[2])

    return result

def one_vs_team_lega(team, enemy_poke, enemy_pl):
    winners = []
    for pokemon in team:
        if pokemon[0] is not None:
            try:
                types1 = poke.get(name = pokemon[0]).types
                types2 = poke.get(name = enemy_poke).types
            except:
                print(f"Errore nel recuperare i tipi di {pokemon[0]} o {enemy_poke}")
                continue

            bonus = calculate_bonus_via_types(types1, types2 ,multiplier = 20)
            bonus_netto = bonus[0]-bonus[1]

            if pokemon[3] + bonus_netto >= enemy_pl:
                winners.append(pokemon)
    print('Questo lo battono', winners)
    winners.sort(key=lambda x: x[2], reverse=True)  
    print("Team vs enemy_poke: ", enemy_poke, enemy_pl, " - Winners: ", winners)
    return winners[-1] if winners else None

async def calculate_best_strategy(team, enemy_team, enemy_powers,multiplier):
    print('team', team)
    print('enemy_team', enemy_team)
    print('enemy_powers', enemy_powers)
    prob_matrix = []
    base_bonus = 0.010
    for pokemon in team:
        if pokemon[0] is not None:
            base_bonus -= 0.001  
            #print(pokemon)
            pp_of_wins = []
            #print('\n',pokemon[0],'\n')
            types1 = poke.get(name = pokemon[0]).types
            for power in enemy_powers:
                #print(power)
                total = 0
                for enemy_poke in enemy_team:
                    #print(enemy_poke)
                    types2 = poke.get(name = enemy_poke[0]).types

                    bonus = calculate_bonus_via_types(types1, types2 ,multiplier)
                    bonus_netto = bonus[0]-bonus[1]

                    #print("Bonus calcolato:", bonus_netto)

                    if pokemon[3] + bonus_netto >= power:
                        total+=1
                pp_of_wins.append(total/len(enemy_team)*100+base_bonus)
            #print(pokemon, pp_of_wins)
            prob_matrix.append(pp_of_wins)
        else:
            prob_matrix.append([0 for _ in range(len(enemy_powers))])

    print(prob_matrix)
    # Hungarian algorithm minimizes, so negate
    M = np.array(prob_matrix)
    row_ind, col_ind = linear_sum_assignment(-M)  #col_ind è l'indice che ci interessa

    assignment = dict(zip(col_ind, row_ind))  # slot -> pokemon index

    #print(assignment)

    best_schieramento = []
    p_of_victory = []

    for slot in range(len(col_ind)):
        poke_idx = assignment[slot]
        best_schieramento.append(team[poke_idx])
        p_of_victory.append((M[poke_idx, slot]))

    print('p_of_victory', p_of_victory)
    print('best_schieramento', best_schieramento)

    return [int(p) for p in p_of_victory], best_schieramento


async def process_and_reply(event, client, media_list, pokemon_vectors):
    pokemons_found = []
    for c, media in enumerate(media_list):
        file_bytes = await client.download_media(media, file=BytesIO())
        file_bytes.seek(0)

        try:
            img = Image.open(file_bytes).convert("RGB")
        except:
            continue

        mat_gray = img.convert("L")
        mat = np.array(mat_gray)

        h, w = mat.shape
        f = 0.3
        cx, cy = w // 2, h // 2
        dx, dy = int(w * f), int(h * f)

        coords = [
            (cx, cy),
            (cx, max(cy - dy, 0)),
            (cx, min(cy + dy, h - 1)),
            (max(cx - dx, 0), cy),
            (min(cx + dx, w - 1), cy),
            (max(cx - dx//2, 0), max(cy - dy//2, 0)),
            (min(cx + dx//2, w - 1), max(cy - dy//2, 0)),
            (max(cx - dx//2, 0), min(cy + dy//2, h - 1)),
            (min(cx + dx//2, w - 1), min(cy + dy//2, h - 1)),
        ]

        vector = [int(mat[y, x]) for x, y in coords]

        name, dist = await match_vector(vector, pokemon_vectors)
        pokemons_found.append([(await clean_pokemon_name(name)),dist])

    return pokemons_found

async def clean_pokemon_name(p):
    p = p.replace("shiny","")
    p = await similar_pokemon_name(p, r = False)
    return p

async def match_vector(vector, pokemon_vectors):
    v = np.array(vector, dtype=np.float32)
    best_name = None
    best_dist = float("inf")
    exact_match = None
    for name, emb in pokemon_vectors.items():
        e = np.array(emb, dtype=np.float32)

        if np.array_equal(e, v):
            exact_match = name
            break
        diff = e - v
        dist = np.sqrt(np.sum(diff * diff))
        if dist < best_dist:
            best_dist = dist
            best_name = name
    return exact_match if exact_match else best_name, best_dist

#### LEGA UTILS ####
def reset_lega_info(begin = True):
    json_path = os.path.join(ENV_PATH, "BeatlesBoy_info.json")
    print("Dumping JSON to (reset lega):", json_path)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if begin:
        data["fase_lega"] = 1
    else:
        data["fase_lega"] = 0
    data["indizio_chiesto"] = 0
    data["win_1"] = False
    data["win_2"] = False
    data["enemy_team_lega"] = []
    data["team_lega"] = []
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)