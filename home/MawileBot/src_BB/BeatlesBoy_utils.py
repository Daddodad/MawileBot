import re

def extract_pokemon_and_pl(text):
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

def calculate_winning_options(pokemon, pl, team):
    return None