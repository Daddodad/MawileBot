import re
import os
import sys
print(sys.path[0])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SRC_PATH = os.path.abspath(os.path.join(BASE_DIR, '..', 'src'))
sys.path.insert(0, SRC_PATH)

from poke_lib import automatic_card_reader

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

async def calculate_winning_options(pokemon, pl, team):
    return None

async def aggiorna_team_da_foto(pil_image):
    secret_data,errors = await automatic_card_reader(pil_image)
    print("Dati segreti estratti:", secret_data)
    print("Errori durante l'estrazione:", errors)