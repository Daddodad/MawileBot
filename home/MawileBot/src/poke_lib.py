import pypokedex as poke
import numpy as np
import random
from telegram import Update
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import dataframe_image as dfi
import os

import sys
if os.path.exists('/home/SableyeBot/src'):
    PATH = '/home/SableyeBot/src'
    sys.path.insert(0,PATH) # SableyeBot
else:
    PATH = 'home/MawileBot/src'
    sys.path.insert(0,PATH) # MawileBot

from datetime import datetime, date
LvL = [5,6,7,8,10,11,13,13,15,16,17,19,20,22,22,23,25,26,27,29,30,31,33,36,38,41,43,45,46,48,51,54,57,59,62,62,65,67,69,71,73,76]
coeff = [3, 3.5, 4, 4.5, 5, 5.5]
gym_cell = [4,6,8,11,13,16,19,21,23,25,28,30,31,32,34,36,41,42]

pokemon_types = ["normal", "fire", "water", "electric", "grass", "ice",
                 "fighting", "poison", "ground", "flying", "psychic",
                 "bug", "rock", "ghost", "dragon", "dark", "steel", "fairy"]


gym_types = ["rock", "fighting", "dark", "electric", "fairy", "grass",
             "normal", "fire", "bug", "flying", "ghost", "ice", "ground",
             "poison", "psychic", "water", "steel", "dragon"]

# A 2 Dimenstional Numpy Array Of Damage Multipliers For Attacking Pokemon:

damage_array = np.array([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1/2, 0, 1, 1, 1/2, 1],
                    [1, 1/2, 1/2, 1, 2, 2, 1, 1, 1, 1, 1, 2, 1/2, 1, 1/2, 1, 2, 1],
                    [1, 2, 1/2, 1, 1/2, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1/2, 1, 1, 1],
                    [1, 1, 2, 1/2, 1/2, 1, 1, 1, 0, 2, 1, 1, 1, 1, 1/2, 1, 1, 1],
                    [1, 1/2, 2, 1, 1/2, 1, 1, 1/2, 2, 1/2, 1, 1/2, 2, 1, 1/2, 1, 1/2, 1],
                    [1, 1/2, 1/2, 1, 2, 1/2, 1, 1, 2, 2, 1, 1, 1, 1, 2, 1, 1/2, 1],
                    [2, 1, 1, 1, 1, 2, 1, 1/2, 1, 1/2, 1/2, 1/2, 2, 0, 1, 2, 2, 1/2],
                    [1, 1, 1, 1, 2, 1, 1, 1/2, 1/2, 1, 1, 1, 1/2, 1/2, 1, 1, 0, 2],
                    [1, 2, 1, 2, 1/2, 1, 1, 2, 1, 0, 1, 1/2, 2, 1, 1, 1, 2, 1],
                    [1, 1, 1, 1/2, 2, 1, 2, 1, 1, 1, 1, 2, 1/2, 1, 1, 1, 1/2, 1],
                    [1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1/2, 1, 1, 1, 1, 0, 1/2, 1],
                    [1, 1/2, 1, 1, 2, 1, 1/2, 1/2, 1, 1/2, 2, 1, 1, 1/2, 1, 2, 1/2, 1/2],
                    [1, 2, 1, 1, 1, 2, 1/2, 1, 1/2, 2, 1, 2, 1, 1, 1, 1, 1/2, 1],
                    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1/2, 1, 1],
                    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1/2, 0],
                    [1, 1, 1, 1, 1, 1, 1/2, 1, 1, 1, 2, 1, 1, 2, 1, 1/2, 1, 1/2],
                    [1, 1/2, 1/2, 1/2, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1/2, 2],
                    [1, 1/2, 1, 1, 1, 1, 2, 1/2, 1, 1, 1, 1, 1, 1, 2, 2, 1/2, 1]])

def poke_exist(pokea):
    try:
        poke.get(name=pokea)
        return True
    except:
        return False
    return False

def random_pokemon():
    r = int(random.randrange(1025))+1
    return poke.get(dex = r).name.capitalize()

def random_player():
    with open(PATH+'/public_player_data.json', 'r') as file:
        data = json.load(file)
    return random.choice(list(data.keys()))

def calculate_bonus(pokea, pokeb, multiplier):
    p1 = poke.get(name=pokea)
    p2 = poke.get(name=pokeb)
    bonus = [0,0]
    for t1 in p1.types:
        res = 1
        for t2 in p2.types:
            res = res * type_interaction(t1,t2)
        if res == 4:
            bonus[1]-=multiplier*4
        if res == 2:
            bonus[1]-=multiplier*2
        if res == 0.5:
            bonus[1]+=multiplier
        if res == 0.25:
            bonus[1]+=multiplier*2
        if res == 0:
            bonus[1]+=multiplier*2
    for t2 in p2.types:
        res = 1
        for t1 in p1.types:
            res = res * type_interaction(t2,t1)
        if res == 4:
            bonus[0]-=multiplier*4
        if res == 2:
            bonus[0]-=multiplier*2
        if res == 0.5:
            bonus[0]+=multiplier
        if res == 0.25:
            bonus[0]+=multiplier*2
        if res == 0:
            bonus[0]+=multiplier*2
    return(bonus)

def type_interaction(type_att,type_def):
    type_att = pokemon_types.index(type_att)
    type_def = pokemon_types.index(type_def)
    return (damage_array[type_att,type_def])

def calculate_bonus_answer(bonus_pokemon, moltiplicatore):
    try:
        poke1,poke2 = bonus_pokemon.split(" ")
        try:
            [b1,b2] = calculate_bonus(poke1, poke2, moltiplicatore)
            text = f"Moltiplicatore: {moltiplicatore}\n\n{poke1}: {b1}\n{poke2}: {b2}\n\n"
            if b1 > b2:
                text = text + f"{poke1} ha un vantaggio netto di {b1-b2}"
            else:
                text = text + f"{poke2} ha un vantaggio netto di {b2-b1}"
        except:
            text = 'Ku ku ku... Non conosco questi Pokémon...? Riprova.'
    except:
        text = 'Non hai seguito bene le mie istruzioni... Riprova...'
    return text

async def check_route(chat_id):
    jsonFile = open(PATH+"/secret_player_data.json", "r") # Open the JSON file for reading
    data = json.load(jsonFile) # Read the JSON into the buffer
    jsonFile.close() # Close the JSON file

    return data[chat_id]["route"]

async def add_route(chat_id, route):

    jsonFile = open(PATH+"/secret_player_data.json", "r") # Open the JSON file for reading
    data = json.load(jsonFile) # Read the JSON into the buffer
    jsonFile.close() # Close the JSON file

    data[chat_id]["route"] = route

    ## Save our changes to JSON file
    jsonFile = open(PATH+"/secret_player_data.json", "w+")
    jsonFile.write(json.dumps(data))
    jsonFile.close()


def add_new_player(update: Update):

    jsonFile = open(PATH+"/secret_player_data.json", "r") # Open the JSON file for reading
    data = json.load(jsonFile) # Read the JSON into the buffer
    jsonFile.close() # Close the JSON file

    if str(update.effective_user.id) not in data.keys():

        data[str(update.effective_user.id)] = {
        "username" :    update.effective_user.username,
        "first_name" :  update.effective_user.first_name,
        "route" : None,
        "team":         [[None,1],[None,1],[None,1],[None,1],[None,1],[None,1],[None,1],[None,1],[None,1]],
        }

        ## Save our changes to JSON file
        jsonFile = open(PATH+"/secret_player_data.json", "w+")
        jsonFile.write(json.dumps(data))
        jsonFile.close()

        return True
    return False

def get_poke_bst(pokemon):
    if pokemon.lower() == "groudon" or pokemon.lower() == "kyogre":
        bst = 680
    elif pokemon.lower() == "slaking":
        bst = 555
    else:
        bst = sum(poke.get(name=pokemon).base_stats)
    return bst

def poke_lega_single(poke_liv, name,molt):

    try:
        pokemon,liv = poke_liv.split(" ")
        try:
            text = poke_lega_test(pokemon, int(liv), name, molt)
        except:
            text = "Ku ku ku... C'é qualcosa di sbagliato... Riprova."
    except:
        text = 'Non hai seguito bene le mie istruzioni... Riprova...'

    return text

def poke_lega_team(poke_liv, name,molt):
    return poke_lega_single(poke_liv, name,molt)


def has_a_team(chat_id):
    jsonFile = open(PATH+"/secret_player_data.json", "r") # Open the JSON file for reading
    data = json.load(jsonFile) # Read the JSON into the buffer
    jsonFile.close() # Close the JSON file

    team = data[chat_id]["team"]

    for [p,l] in team:
        if p!=None:
            return True
    return False

def poke_lega_test(pokemon, level, name, multiplier ,only_perc = False):

    message = f'Trainer: {name}\n'

    with open(PATH+'/public_player_data.json', 'r') as file:
        enemies = json.load(file)

    pokemon_bst = get_poke_bst(pokemon)
    pokemon_stats = round(level*pokemon_bst/100)

    n_total = 0
    n_pareggi = 0
    n_vittorie = 0
    for enemy in enemies[name]:
        n_total +=1
        message += f"{enemy:<10}"

        bonus = calculate_bonus(pokemon,enemy,multiplier)
        mod_bonus = bonus[0]-bonus[1]
        str_mod_bonus = "("+str(mod_bonus)+")"
        message += f"{str_mod_bonus:<6} "

        if mod_bonus > 0:
            n_vittorie+=1
        if mod_bonus == 0:
            n_pareggi+=1

        enemy_bst = get_poke_bst(enemy)
        enemy_level = round((pokemon_stats + mod_bonus)*100/enemy_bst)
        while pokemon_stats + mod_bonus < round(enemy_level*enemy_bst/100):
            enemy_level -= 1
        if enemy_level < 100:
            message += f"{min(enemy_level,100):<3}\n"
        else:
            message += f"{min(enemy_level,100):<3} ✅ \n"
    n_vittorie = n_vittorie/n_total
    n_pareggi = n_pareggi/n_total


    if only_perc == True:
        message = ''

    if name == 'Generic' or name == 'generic':
        message += f"\n{pokemon} è in vantaggio nel {int(n_vittorie*100)}% dei matchup generici."
        message += f"\n\n{pokemon} è pari forza nel {int(n_pareggi*100)}% dei matchup generici.\n"
    else:
        message += f"\n{pokemon} è in vantaggio nel {int(n_vittorie*100)}% dei matchup."
        message += f"\n\n{pokemon} è pari forza nel {int(n_pareggi*100)}% dei matchup.\n"

    return message[:-1]


def poke_lega_all(multiplier):

    name = 'generic'
    #message = f'Trainer: {name}\n'
    message = ''

    with open(PATH+'/public_player_data.json', 'r') as file:
        enemies = json.load(file)

    order = []
    for pokemon in enemies[name]:

        n_total = 0
        n_pareggi = 0
        n_vittorie = 0
        for enemy in enemies[name]:
            n_total +=1

            bonus = calculate_bonus(pokemon,enemy,multiplier)
            mod_bonus = bonus[0]-bonus[1]

            if mod_bonus > 0:
                n_vittorie+=1
            if mod_bonus == 0:
                n_pareggi+=1

        n_vittorie = n_vittorie/n_total
        n_pareggi = n_pareggi/n_total
        order.append([pokemon,n_vittorie,n_pareggi])

    order = sorted(order, key=lambda x: (x[1], x[2]), reverse=True)

    for pokemon, n_vittorie, n_pareggi in order:
        message += f"\n*{pokemon}* è in vantaggio nel {int(n_vittorie*100)}% e pari forza nel {int(n_pareggi*100)}% dei matchup generici."

    return message


def get_type_emoji(type_name):
    type_emojis = {
        'Normal': '⚪',
        'Fire': '🔥',
        'Water': '💧',
        'Electric': '⚡',
        'Grass': '🍃',
        'Ice': '❄️',
        'Fighting': '👊',
        'Poison': '☠️',
        'Ground': '🟠',
        'Flying': '🦅',
        'Psychic': '🔮',
        'Bug': '🐛',
        'Rock': '⛰️',
        'Ghost': '👻',
        'Dragon': '🐉',
        'Dark': '⚫',
        'Steel': '🔩',
        'Fairy': '🧚'
    }
    return type_emojis.get(type_name, '❓')

def format_types(types):
    formatted_types = [f"{get_type_emoji(t.capitalize())} {t.capitalize()}" for t in types]
    return " / ".join(formatted_types)

def format_types_emoji(types):
    formatted_types = [f"{get_type_emoji(t.capitalize())}" for t in types]
    return " ".join(formatted_types)

def poke_dex1(pokemon_name: str) -> str:
    # This function should return the Pokédex entry for the given Pokémon
    message = ''
    message += poke_lega_test(pokemon_name, level = 100, name = "generic", multiplier = 20 ,only_perc = True)
    return message

def poke_dex2(pokemon_name: str) -> str:
    message = ''
    message += f' Tipo: {format_types(poke.get(name = pokemon_name).types)}\n\n'
    message += f'BST: {get_poke_bst(pokemon_name)}\n'
    message += '\nAttendi il prossimo messaggio...'
    return message

def get_power(pokemon, lvl):
    return round(lvl*get_poke_bst(pokemon)/100)

def save_dataframe_as_image(df, path):

    # Check if df is a Styler object
    if isinstance(df, pd.io.formats.style.Styler):
        styled_df = df
    else:
        styled_df = df.style

    # Save the styled DataFrame as an image
    dfi.export(styled_df.background_gradient(), path, table_conversion='matplotlib')

def extract_first_number(cell):
    try:
        # Extract the first number before the parentheses
        return float(str(cell).split()[0])
    except:
        return None

def style_dataframe_with_thresholds(df, thresholds):
    # Create a copy of the DataFrame to avoid modifying the original
    styled_df = df.style

    # Apply conditional formatting for each column starting from the third column
    for col_idx, (col_name, threshold) in enumerate(zip(df.columns[2:], thresholds), start=2):

        # Define the styling function for this column
        def style_column(val, threshold=threshold):  # Use default argument to capture current threshold
            try:
                first_num = extract_first_number(val)
                if first_num is not None and first_num > threshold:
                    return 'background-color: green'
            except:
                pass
            return ''

        # Apply the styling to this column
        styled_df = styled_df.applymap(style_column, subset=[col_name])

    return styled_df

def save_dataframe_as_image_alt(df, path, thresholds):
    # Apply the conditional formatting
    styled_df = style_dataframe_with_thresholds(df, thresholds)

    # Save the styled DataFrame as an image
    dfi.export(styled_df, path, table_conversion='matplotlib')
    #print(f"Successfully saved styled DataFrame to {path}")

def poke_lega_team_team(chat_id, enemies):
    with open(PATH+'/secret_player_data.json', 'r') as file:
        priv_data = json.load(file)
    team = [[pokemon[0], get_power(pokemon[0], pokemon[1])] for pokemon in priv_data[chat_id]["team"] if pokemon[0]]
    dfs = []
    potenze = []
    for enemy, enemy_powers in enemies:
        potenze.append(get_power(enemy,enemy_powers))
        enemy_powers = [enemy_powers,enemy_powers,enemy_powers]
        enemy = [enemy]
        multiplier = 20
        tab = match_prevision(team, enemy, enemy_powers, multiplier)
        dfs.append(tab)

    # Step 1: Concatenate the data (not styles)
    dfs_data = [df.data for df in dfs]  # Extract data from styled DataFrames

    # Keep the first two columns only in the first DataFrame
    dfs_data[1:] = [df.iloc[:, 2:] for df in dfs_data[1:]]  # Keep only the third column from subsequent DataFrames

    # Concatenate along columns
    concat_data = pd.concat(dfs_data, axis=1)

    # Rename the columns: keep the first two columns' names as is, and update the rest
    new_column_names = list(concat_data.columns[:2])  # Keep the first two column names

    # Append the corresponding threshold value to the name of each subsequent column
    new_column_names += [f"{col} ({potenze[k-2]})" for k, col in enumerate(concat_data.columns[2:], start=2)]
    concat_data.columns = new_column_names

    print(concat_data)
    #print(potenze)
    # Fin qui è corretto. Mi manca lo styling...
    path = PATH+f"/images/{chat_id}_lega_team_team.png"
    save_dataframe_as_image_alt(concat_data, path,potenze)
    return path

def poke_gym(chat_id, gym):
    with open(PATH+'/secret_player_data.json', 'r') as file:
        priv_data = json.load(file)
    team = [[pokemon[0], get_power(pokemon[0], pokemon[1])] for pokemon in priv_data[chat_id]["team"] if pokemon[0]]
    with open(PATH+'/gym_data.json', 'r') as file:
        gym_data = json.load(file)
    if gym_data[gym]["actual_team"] == []:
        enemy = gym_data[gym]["team"]
    else:
        enemy = gym_data[gym]["actual_team"]
    enemy_powers = gym_data[gym]["power"]
    multiplier = gym_data[gym]["multiplier"]
    tab = match_prevision(team, enemy, enemy_powers, multiplier)


    # If tab is a DataFrame and has a 'style' attribute, it means style.apply was used
    if isinstance(tab, pd.DataFrame) and hasattr(tab, 'style'):
        tab = tab.style.apply(highlight_max, subset=tab.columns[2:], args=enemy_powers)


    path = PATH+f"/images/{chat_id}.png"
    save_dataframe_as_image(tab, path)
    return path


def match_prevision(team, enemy, enemy_powers, multiplier):

    limits = None
    if   len(enemy_powers) == 3:
        #print('È un allenatore!')
        limits = enemy_powers
    elif ((len(enemy_powers) == 6) and (enemy_powers[0] == enemy_powers[1]) and (enemy_powers[2] == enemy_powers[3]) and (enemy_powers[4] == enemy_powers[5])):
        #print('È una palestra!')
        limits = [enemy_powers[0],enemy_powers[2],enemy_powers[4]]
    elif (len(enemy_powers) == 1):
        #print('1v1')
        limits = [enemy_powers[0],enemy_powers[0],enemy_powers[0]]

    #print('TABELLA COMPATITIBILITÀ : gli avversari hanno ',enemy_powers)
    bonus_netti,tab = match_table(team,enemy,multiplier,limits = limits)

    return tab


def highlight_max(s,LOW_LIM,MID_LIM,UPP_LIM):
    '''
    highlight the maximum in a Series yellow.
    '''
    # s is the column (i think)
    colors = []
    for el in s:
        n = el.split(' ')
        n = int(n[0])
        if n >= UPP_LIM:
            colors.append('background-color: green')
        else:
            if n >= MID_LIM :
                colors.append('background-color: yellow')
            else:
                if n >= LOW_LIM :
                    colors.append('background-color: red')
                else:
                    colors.append('background-color: grey')
    return colors

def match_table(team,enemy,multiplier,limits = None):
    bonus_netti = []
    tabellone = []
    for p in team:
        bonus_p =[]
        tabella = [p[0],p[1]]
        for t in enemy:
            bonus = calculate_bonus(t, p[0],multiplier)
            bonus_p.append(-bonus[0]+bonus[1])
            tabella.append(str(p[1]-bonus[0]+bonus[1])+' ('+str(-bonus[0]+bonus[1])+')')
        bonus_netti.append(bonus_p)
        tabellone.append(tabella)

    tab = pd.DataFrame(tabellone)
    cols = ['Pokemon', 'Potenza Base']
    for e in enemy:
        if e not in cols:
            cols.append(e)
        else:
            i = 2
            name = e +' '+ str(i)
            while name in cols:
                i+=1
                name = e +' '+ str(i)
            cols.append(name)
    tab.columns = cols
    if limits != None:
        tab = tab.style.apply(highlight_max, subset=cols[2:],args=limits)
    return(bonus_netti,tab)




def poke_cell(cell):
    start = date(2024,7,10)
    today = datetime.now().date()
    offset = cell
    pausa = 5
    casella = int(((today-start).days-pausa)/2) + offset
    multiplier = 5 + 3*int(casella/7)
    if casella < 42:
        aumento = int(casella/14) + 2
        low_power = int((LvL[casella]-aumento)*coeff[int(casella/7)])
        mid_power = int((LvL[casella])*coeff[int(casella/7)])
        high_power = int((LvL[casella]+aumento)*coeff[int(casella/7)])
        super_power = int((LvL[casella]+2*aumento)*coeff[int(casella/7)])
        if casella+1 in gym_cell:
            trainer_power = [low_power,mid_power,high_power]
            gym_power = [mid_power,mid_power,high_power,high_power,super_power,super_power]
            return True, trainer_power, gym_power, multiplier, LvL[casella]
        else:
            encounter_power = [low_power,mid_power]
            boss_power = [int((LvL[casella]+aumento)*coeff[int(casella/7)]),int((LvL[casella]+aumento+10)*coeff[int(casella/7)]),int((LvL[casella]+aumento+18)*coeff[int(casella/7)])]
            return False, encounter_power, boss_power, multiplier
    else:
        return None




async def poke_check_if_evo(chat_id,pokemon,lvl):
    with open(PATH+"/secret_player_data.json", 'r') as f:
        secret = json.load(f)
    route = secret[chat_id]["route"]

    with open(PATH+f"/{route}_evo_file.json", 'r') as ef:
        evo_dict = json.load(ef)

    if pokemon in evo_dict:
        if evo_dict[pokemon][0]=="base":
            if lvl >= evo_dict[pokemon][1][0]:
                pokemon = evo_dict[pokemon][1][1]
        elif evo_dict[pokemon][0]=="mid":
            if lvl <= evo_dict[pokemon][1][0]:
                pokemon = evo_dict[pokemon][1][1]
            elif lvl >= evo_dict[pokemon][2][0]:
                pokemon = evo_dict[pokemon][2][1]
        elif evo_dict[pokemon][0]=="last":
            if lvl <= evo_dict[pokemon][-1][0]:
                pokemon = evo_dict[pokemon][-1][1]

    return pokemon

def poke_check_if_evo_not_async(chat_id,pokemon,lvl):
    with open(PATH+"/secret_player_data.json", 'r') as f:
        secret = json.load(f)
    route = secret[chat_id]["route"]

    with open(PATH+f"/{route}_evo_file.json", 'r') as ef:
        evo_dict = json.load(ef)

    if pokemon in evo_dict:
        if evo_dict[pokemon][0]=="base":
            if lvl >= evo_dict[pokemon][1][0]:
                pokemon = evo_dict[pokemon][1][1]
        elif evo_dict[pokemon][0]=="mid":
            if lvl <= evo_dict[pokemon][1][0]:
                pokemon = evo_dict[pokemon][1][1]
            elif lvl >= evo_dict[pokemon][2][0]:
                pokemon = evo_dict[pokemon][2][1]
        elif evo_dict[pokemon][0]=="last":
            if lvl <= evo_dict[pokemon][-1][0]:
                pokemon = evo_dict[pokemon][-1][1]

    return pokemon

def poke_evo_level(chat_id,pokemon):
    with open(PATH+"/secret_player_data.json", 'r') as f:
        secret = json.load(f)
    route = secret[chat_id]["route"]

    with open(PATH+f"/{route}_evo_file.json", 'r') as ef:
        evo_dict = json.load(ef)

    lvl = '-'
    if pokemon in evo_dict:
        if evo_dict[pokemon][0]=="base":
            lvl = evo_dict[pokemon][1][0]
        elif evo_dict[pokemon][0]=="mid":
            lvl = evo_dict[pokemon][2][0]
        elif evo_dict[pokemon][0]=="last":
            lvl= evo_dict[pokemon][-1][0]

    return lvl

def poke_cell_specific(route,cell,encounters):
    start = date(2024,7,10)
    today = datetime.now().date()
    offset = cell
    pausa = 5
    casella = int(((today-start).days-pausa)/2) + offset
    multiplier = 5 + 3*int(casella/7)

    with open(PATH+f"/{route}_evo_file.json", 'r') as ef:
        evo_dict = json.load(ef)

    if casella < 42:
        aumento = int(casella/14) + 2
        low_power = int((LvL[casella]-aumento)*coeff[int(casella/7)])
        mid_power = int((LvL[casella])*coeff[int(casella/7)])
        encounter_power = [low_power,mid_power]
        for pokemon in encounters:
            if pokemon in evo_dict:
                pokemon = evo_dict[pokemon][-1][1]
            stats = get_poke_bst(pokemon)
            boss_power = max(mid_power,int((LvL[casella]+aumento+int((stats-500)/10))*coeff[int(casella/7)]))
            encounter_power.append(boss_power)
        return encounter_power, multiplier
    else:
        return None


def poke_fight(chat_id,trainer,pokemons):
    if trainer == True:
        path, enemy_powers = poke_trainer(chat_id,pokemons)
    else:
        path, enemy_powers = poke_encounter(chat_id,pokemons)
    return path, enemy_powers


def poke_trainer(chat_id,pokemons):
    with open(PATH+'/secret_player_data.json', 'r') as file:
        priv_data = json.load(file)
    team = [[pokemon[0], get_power(pokemon[0], pokemon[1])] for pokemon in priv_data[chat_id]["team"] if pokemon[0]]


    start = date(2024,7,10)
    today = datetime.now().date()
    pausa = 5
    casella = int(((today-start).days-pausa)/2)

    offset = 0
    while casella+1+offset not in gym_cell:
        offset += 1
    #print(casella, offset)

    _, enemy_powers, _, multiplier, _ = poke_cell(offset)


    tab = match_prevision(team, pokemons, enemy_powers, multiplier)


    # If tab is a DataFrame and has a 'style' attribute, it means style.apply was used
    if isinstance(tab, pd.DataFrame) and hasattr(tab, 'style'):
        tab = tab.style.apply(highlight_max, subset=tab.columns[2:], args=enemy_powers)


    path = PATH+f"/images/{chat_id}.png"
    save_dataframe_as_image(tab, path)
    return path, enemy_powers


def poke_encounter(chat_id,encounter):
    with open(PATH+'/secret_player_data.json', 'r') as file:
        priv_data = json.load(file)
    team = [[pokemon[0], get_power(pokemon[0], pokemon[1])] for pokemon in priv_data[chat_id]["team"] if pokemon[0]]
    route = priv_data[chat_id]["route"]

    start = date(2024,7,10)
    today = datetime.now().date()
    pausa = 5
    casella = int(((today-start).days-pausa)/2)

    offset = 0
    while casella+1+offset in gym_cell:
        offset += 1
    #print(casella, offset)

    enemy_powers, multiplier = poke_cell_specific(route,offset,encounter)

    tab = encounter_prevision(team, encounter, enemy_powers, multiplier)

    # If tab is a DataFrame and has a 'style' attribute, it means style.apply was used
    if isinstance(tab, pd.DataFrame) and hasattr(tab, 'style'):
        tab = tab.style.apply(highlight_max, subset=tab.columns[2:], args=enemy_powers)

    path = PATH+f"/images/{chat_id}.png"
    save_dataframe_as_image(tab, path)
    return path, enemy_powers


def encounter_prevision(team, enemy, enemy_powers, multiplier):

    #print('TABELLA COMPATITIBILITÀ : gli avversari hanno ',enemy_powers)
    bonus_netti,tab = encounter_table(team,enemy,multiplier,limits = enemy_powers)

    return tab



def encounter_highlight_max(s, limits, col_index):
    '''
    highlight the maximum in a Series yellow.
    '''
    colors = []
    for el in s:
        n = el.split(' ')
        n = int(n[0])
        if n >= limits[col_index]:
            colors.append('background-color: green')
        elif n >= limits[1]:
            colors.append('background-color: yellow')
        elif n >= limits[0]:
            colors.append('background-color: red')
        else:
            colors.append('background-color: grey')
    #is_max = s == s.max()
    return colors

def encounter_table(team,enemy,multiplier,limits = None):
    bonus_netti = []
    tabellone = []
    for p in team:
        bonus_p =[]
        tabella = [p[0],p[1]]
        for t in enemy:
            bonus = calculate_bonus(t, p[0],multiplier)
            bonus_p.append(-bonus[0]+bonus[1])
            tabella.append(str(p[1]-bonus[0]+bonus[1])+' ('+str(-bonus[0]+bonus[1])+')')
        bonus_netti.append(bonus_p)
        tabellone.append(tabella)

    tab = pd.DataFrame(tabellone)
    cols = ['Pokemon', 'Potenza Base']
    for e in enemy:
        if e not in cols:
            cols.append(e)
        else:
            i = 2
            name = e +' '+ str(i)
            while name in cols:
                i+=1
                name = e +' '+ str(i)
            cols.append(name)
    tab.columns = cols
    if limits != None:
        # Create a Styler object
        styler = tab.style

        # Apply the highlighting function to each column separately
        for i, col in enumerate(cols[2:], start=2):
            styler = styler.apply(encounter_highlight_max, subset=[col], args=(limits, i))

        # Set the styled DataFrame
        tab = styler
    return(bonus_netti,tab)


def poke_counter(pokemon, level=100):
    counters = []

    multiplier = 20

    with open(PATH+'/public_player_data.json', 'r') as file:
        enemies = json.load(file)['generic']

    pokemon_bst = get_poke_bst(pokemon)
    pokemon_stats = round(pokemon_bst*level/100)

    for enemy in enemies:
        bonus_list = calculate_bonus(enemy,pokemon,multiplier)
        bonus = bonus_list[0] - bonus_list[1]
        enemy_bst = get_poke_bst(enemy)
        if enemy_bst + bonus > pokemon_stats:
            wins = True
        else:
            wins = False
        enemy_level = round((pokemon_stats - bonus)*100/enemy_bst)
        while pokemon_stats - bonus > round(enemy_level*enemy_bst/100):
            enemy_level += 1
        counters.append([enemy,bonus,enemy_bst,wins,enemy_level])

    sorted_counters = sorted(counters, key=lambda x: (x[1], x[2]), reverse=True)

    return sorted_counters

def poke_gym_test(chat_id, pokemon, livello=0, next=4):

    start = date(2024,7,10)
    today = datetime.now().date()
    pausa = 5
    casella = int(((today-start).days-pausa)/2)

    offset = 0
    while casella+1 > gym_cell[offset]:
        offset += 1

    with open(PATH+'/gym_data.json', 'r') as file:
        gym_data = json.load(file)

    with open(PATH+"/secret_player_data.json", 'r') as f:
        secret = json.load(f)
    route = secret[chat_id]["route"]

    with open(PATH+f"/{route}_evo_file.json", 'r') as ef:
        evo_dict = json.load(ef)

    results = []

    end = min(offset + next, len(gym_types))

    for gym in gym_types[offset:end]:
        if gym_data[gym]["actual_team"] == []:
            enemies = gym_data[gym]["team"]
        else:
            enemies = gym_data[gym]["actual_team"]

        enemy_powers = gym_data[gym]["power"]
        limits = [enemy_powers[0],enemy_powers[2],enemy_powers[4]]
        multiplier = gym_data[gym]["multiplier"]

        grey_wins = 0
        red_wins = 0
        yellow_wins = 0
        green_wins = 0

        average = 0
        num = 0
        min_bonus = 1000
        max_bonus = 0
        if livello != 0:
            pokemon_bst = get_poke_bst(pokemon)
            pokemon_stats = round(livello*pokemon_bst/100)
            for enemy in enemies:
                bonuses = calculate_bonus(pokemon, enemy, multiplier)
                bonus = bonuses[0] - bonuses[1]
                average += bonus
                num += 1
                if bonus < min_bonus:
                    min_bonus = bonus
                if bonus > max_bonus:
                    max_bonus = bonus

                if pokemon_stats + bonus >= limits[2]:
                    green_wins += 1
                elif pokemon_stats + bonus >= limits[1]:
                    yellow_wins += 1
                elif pokemon_stats + bonus >= limits[0]:
                    red_wins += 1
                else:
                    grey_wins += 1
        else:
            for enemy in enemies:
                bonuses = calculate_bonus(pokemon, enemy, multiplier)
                bonus = bonuses[0] - bonuses[1]
                average += bonus
                num += 1
                if bonus < min_bonus:
                    min_bonus = bonus
                if bonus > max_bonus:
                    max_bonus = bonus

        average /= num
        average = round(average, 2)

        if livello != 0:
            if grey_wins > 0:
                #print(gym)
                tested_pokemon = []
                k=0
                #print(pokemon)
                necessary_lvl = round((limits[0]-bonus)*100/pokemon_bst)
                while limits[0] - min_bonus > round(necessary_lvl*pokemon_bst/100):
                    necessary_lvl += 1
                #print(necessary_lvl,livello,k)
                new_pokemon = poke_check_if_evo_not_async(chat_id, pokemon, necessary_lvl)
                tested_pokemon.append(pokemon)
                while new_pokemon not in tested_pokemon and necessary_lvl > livello + k:
                    #print(new_pokemon)
                    tested_pokemon.append(new_pokemon)
                    pokemon_bst = get_poke_bst(new_pokemon)
                    necessary_lvl = round((limits[0]-bonus)*100/pokemon_bst)
                    while limits[0] - min_bonus > round(necessary_lvl*pokemon_bst/100):
                        necessary_lvl += 1
                    #print(necessary_lvl,livello,k)
                    evo_lvl = 0
                    if pokemon in evo_dict.keys():
                        for evo in evo_dict[pokemon][1:]:
                            if evo[1] == new_pokemon:
                                evo_lvl = evo[0]
                                break
                    #print(evo_lvl)
                    necessary_lvl = max(necessary_lvl,evo_lvl)
                    new_pokemon = poke_check_if_evo_not_async(chat_id, new_pokemon, necessary_lvl)
                    k+=1
                #print(k)
                results.append([gym, average, min_bonus, max_bonus, grey_wins, red_wins, yellow_wins, green_wins, max(k,necessary_lvl-livello)])
            else:
                results.append([gym, average, min_bonus, max_bonus, grey_wins, red_wins, yellow_wins, green_wins, 0])
        else:
            results.append([gym, average, min_bonus, max_bonus])

    return results