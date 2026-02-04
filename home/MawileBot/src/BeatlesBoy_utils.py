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

async def pokemon_utility(pokemon):
    return 400

tipi_to_types = {
    'Normale': 'Normal','Fuoco': 'Fire','Acqua': 'Water','Erba': 'Grass','Elettro': 'Electric','Ghiaccio': 'Ice','Lotta': 'Fighting','Veleno': 'Poison',
    'Terra': 'Ground','Volante': 'Flying','Psico': 'Psychic','Coleottero': 'Bug','Roccia': 'Rock','Spettro': 'Ghost','Drago': 'Dragon','Buio': 'Dark','Acciaio': 'Steel','Folletto': 'Fairy'
}

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

async def calculate_winning_options(enemy_poke, enemy_pl, team):
    _, _, _, multiplier, _ = poke_cell(0)
    winning_options = []

    print(' il mio team:', team )
    print("Calcolo delle opzioni vincenti contro", enemy_poke, "PL", enemy_pl)
    for index, poke_and_lvl in enumerate(team):
        print("Valutazione del Pokémon:", poke_and_lvl)

        if None not in poke_and_lvl:
            your_poke, pl = poke_and_lvl[0], get_power( poke_and_lvl[0],  poke_and_lvl[1])

            types1 = poke.get(name = your_poke).types
            types2 = poke.get(name = enemy_poke).types

            print("Tipi del Pokémon:", types1)
            print("Tipi del nemico:", types2)
            bonus = calculate_bonus_via_types(types1, types2 ,multiplier)

            bonus_netto = -bonus[0]+bonus[1]

            print("Bonus calcolato:", bonus_netto)
            if pl + bonus_netto > enemy_pl:
                winning_options.append((your_poke, pl, bonus_netto, index+1))

    print("Opzioni vincenti calcolate:", winning_options)
    winning_options.sort(key=lambda x: x[1], reverse=False) # ordina per PL crescente
    return winning_options

async def calculate_potenziabili(tipi, team):
    potenziabili = []

    for index, poke_and_lvl in enumerate(team):
        if None not in poke_and_lvl:
            your_poke, pl = poke_and_lvl[0], get_power( poke_and_lvl[0],  poke_and_lvl[1])

            types1 = poke.get(name = your_poke).types

            for tipo in tipi:
                if tipi_to_types[tipo].lower() in [t.lower() for t in types1]:
                    potenziabili.append((your_poke, pl, tipo, index+1))
                    break

    if potenziabili == []:
        for index, poke_and_lvl in enumerate(team):
            if None not in poke_and_lvl:
                your_poke, pl = poke_and_lvl[0], get_power( poke_and_lvl[0],  poke_and_lvl[1])
                potenziabili.append((your_poke, pl, "nessun tipo", index+1))

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