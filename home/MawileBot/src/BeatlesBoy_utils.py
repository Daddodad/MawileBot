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
                        automatic_card_reader, calculate_bonus_via_types, 
                        get_power, poke_cell, similar_pokemon_name,
                        get_poke_bst, EMOJI_TO_TYPE,
                        check_alt_forms
                      )


tipi_to_types = {
    'Normale': 'Normal','Fuoco': 'Fire','Acqua': 'Water','Erba': 'Grass','Elettro': 'Electric','Ghiaccio': 'Ice','Lotta': 'Fighting','Veleno': 'Poison',
    'Terra': 'Ground','Volante': 'Flying','Psico': 'Psychic','Coleottero': 'Bug','Roccia': 'Rock','Spettro': 'Ghost','Drago': 'Dragon','Buio': 'Dark','Acciaio': 'Steel','Folletto': 'Fairy'
}

async def find_evo_at_level_x(pokemon, level_x):

    pokemon = await similar_pokemon_name(pokemon.lower())
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

async def pokemon_utility(pokemon,lvl):
    if pokemon is  None:
        return 0
    #TODO: implement a better utility function

    with open(ENV_PATH+f"/even_evo_file.json", 'r') as ef:
        evo_dict = json.load(ef)  
        
    pokemon = await similar_pokemon_name(pokemon.lower())
    max_bst = await get_poke_bst(await find_evo_at_level_x(pokemon, 100))

    print(f"BST di {await find_evo_at_level_x(pokemon, 100)} a livello 100: {max_bst}")
    utility_bst = max_bst/620*10
    utility_lvl = lvl/10

    utility = utility_bst * 0.7 + utility_lvl * 0.3
    return round(utility, 2)  # 0-10 scale

async def filter_team(team, remove_100=False):
    if team:
        utilities = []
        lvl_100 = []
        for index, (poke, lvl) in enumerate(team):
            #poke = await similar_pokemon_name(poke.lower()) #Sarchiapone
            u = await pokemon_utility(poke,lvl)
            if remove_100 and lvl == 100:
                lvl_100.append((poke, lvl, u, await get_power(poke, lvl), index+1))
            else:
                utilities.append((poke, lvl, u, await get_power(poke, lvl), index+1))
        utilities.sort(key=lambda x: x[2], reverse=True)
        return utilities[:6], utilities[6:], lvl_100
    else:
        return [], [], []

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

        for ch in middle:
            # emoji / symbols live here
            if ord(ch) > 127:
                emojis.append(ch)

    # print(emojis[0])
    # print(emojis[1] if len(emojis)>1 else None)
    pokemon = await similar_pokemon_name(pokemon.lower())
    pokemon = await check_alt_forms(pokemon,
                                    EMOJI_TO_TYPE.get(emojis[0],None),
                                    EMOJI_TO_TYPE.get(emojis[1],None) if len(emojis) >1 else None
                                    )
    print('Letto ',pokemon, pl, EMOJI_TO_TYPE.get(emojis[0],None), EMOJI_TO_TYPE.get(emojis[1],None) if len(emojis) >1 else None)

    return pokemon, pl


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

            types1 = poke.get(name = your_poke).types

            for tipo in tipi:
                if tipi_to_types[tipo].lower() in [t.lower() for t in types1]:
                    potenziabili.append((your_poke, pl, tipo, index))
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
        r[0] = await similar_pokemon_name(r[0].lower())
        print(r)
        r[0] = await check_alt_forms(r[0],r[1],r[2])

    return result

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
    p = await similar_pokemon_name(p)
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

