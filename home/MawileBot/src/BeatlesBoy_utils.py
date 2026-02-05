from email.mime import text
import random
import re
import os
import sys
import pypokedex as poke
if os.path.exists('/home/SableyeBot/src'):
    ENV_PATH = '/home/SableyeBot/src'
    sys.path.insert(0,ENV_PATH) # SableyeBot
else:
    ENV_PATH = './home/MawileBot/src'
    sys.path.insert(0,ENV_PATH) # MawileBot
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
from poke_lib import automatic_card_reader, calculate_bonus_via_types, get_power, poke_cell


tipi_to_types = {
    'Normale': 'Normal','Fuoco': 'Fire','Acqua': 'Water','Erba': 'Grass','Elettro': 'Electric','Ghiaccio': 'Ice','Lotta': 'Fighting','Veleno': 'Poison',
    'Terra': 'Ground','Volante': 'Flying','Psico': 'Psychic','Coleottero': 'Bug','Roccia': 'Rock','Spettro': 'Ghost','Drago': 'Dragon','Buio': 'Dark','Acciaio': 'Steel','Folletto': 'Fairy'
}

async def pokemon_utility(pokemon,lvl):
    #TODO: implement a better utility function
    randran = random.randint(0, 100)
    return 400+ randran if pokemon is not None else 0

async def filter_team(team, remove_100=False):
    if team:
        utilities = []
        lvl_100 = []
        for index, (poke, lvl) in enumerate(team):
            u = await pokemon_utility(poke,lvl)
            if remove_100 and lvl == 100:
                lvl_100.append((poke, lvl, u, get_power(poke, lvl), index+1))
            else:
                utilities.append((poke, lvl, u, get_power(poke, lvl), index+1))
        utilities.sort(key=lambda x: x[2], reverse=True)
        return utilities[:6], utilities[6:], lvl_100
    else:
        return [], [], []

async def extract_pokemon_and_pl(text):
    # Pokémon name: after "hai incontrato", before "selvatico" or comma
    name_match = re.search(
        r"hai incontrato\s+(?:il\s+leggendario\s+)?([A-Za-zÀ-ÿ'’]+)",
        text,
        re.IGNORECASE
    )

    # PL value
    pl_match = re.search(r"PL\s*(\d+)", text)

    pokemon = name_match.group(1) if name_match else None
    pl = int(pl_match.group(1)) if pl_match else None

    return pokemon, pl

async def extract_number_of_pvp_choices(text):
    clean = text.replace("\n", " ")
    words = clean.split()
    i = words.index("schiera")
    num_pokemon = int(words[i + 1])
    return num_pokemon

async def calculate_winning_options(enemy_poke, enemy_pl, team):
    _, _, _, multiplier, _ = poke_cell(0)
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
            if pl + bonus_netto > enemy_pl:
                winning_options.append((your_poke, pl, bonus_netto, index))

    print("Opzioni vincenti calcolate:", winning_options)
    winning_options.sort(key=lambda x: x[1], reverse=False) # ordina per PL crescente
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
                potenziabili.append((your_poke, pl, "nessun tipo", index))

    potenziabili.sort(key=lambda x: x[1], reverse=False) # ordina per PL crescente
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