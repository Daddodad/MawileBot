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
from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO
from skimage.metrics import structural_similarity as ssim
import base64
import difflib
import requests

import sys
if os.path.exists('/home/SableyeBot/src'):
    ENV_PATH = '/home/SableyeBot/src'
    sys.path.insert(0,ENV_PATH) # SableyeBot
else:
    ENV_PATH = 'home/MawileBot/src'
    sys.path.insert(0,ENV_PATH) # MawileBot

from datetime import datetime, date
LvL = [5, 6, 7, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24, 25, 27, 29, 30, 31, 33, 36, 38, 41, 43, 45, 46, 49, 51, 54, 56, 58, 61, 62, 64, 66, 69, 71, 74, 76]
coeff = [3, 3.5, 4, 4.5, 5, 5.5]

##############################################################################################
#################################   VARIABILI GLOBALI DA CAMBIARE OGNI LEGA ##################
##############################################################################################

STARTING_DATE = date(2025,7,7)  # Data di inizio della lega, da cambiare ogni lega

EVENTUALE_PAUSA = 0  # Giorni di pausa in una lega


###############################################################################################
###############################################################################################
###############################################################################################

pokemon_types = ["normal", "fire", "water", "electric", "grass", "ice",
                 "fighting", "poison", "ground", "flying", "psychic",
                 "bug", "rock", "ghost", "dragon", "dark", "steel", "fairy"]

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
    with open(ENV_PATH+'/public_player_data.json', 'r') as file:
        data = json.load(file)
    return random.choice(list(data.keys()))

def calculate_bonus(pokea, pokeb, multiplier):
    p1 = poke.get(name=pokea)
    p2 = poke.get(name=pokeb)
    return(calculate_bonus_via_types(p1.types, p2.types, multiplier))

def calculate_bonus_via_types(types1, types2, multiplier):
    bonus = [0,0]
    for t1 in types1:
        res = 1
        for t2 in types2:
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
    for t2 in types2:
        res = 1
        for t1 in types1:
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
    jsonFile = open(ENV_PATH+"/secret_player_data.json", "r") # Open the JSON file for reading
    data = json.load(jsonFile) # Read the JSON into the buffer
    jsonFile.close() # Close the JSON file

    return data[chat_id]["route"]

async def add_route(chat_id, route):

    jsonFile = open(ENV_PATH+"/secret_player_data.json", "r") # Open the JSON file for reading
    data = json.load(jsonFile) # Read the JSON into the buffer
    jsonFile.close() # Close the JSON file

    data[chat_id]["route"] = route

    ## Save our changes to JSON file
    jsonFile = open(ENV_PATH+"/secret_player_data.json", "w+")
    jsonFile.write(json.dumps(data))
    jsonFile.close()


def add_new_player(update: Update):

    jsonFile = open(ENV_PATH+"/secret_player_data.json", "r") # Open the JSON file for reading
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
        jsonFile = open(ENV_PATH+"/secret_player_data.json", "w+")
        jsonFile.write(json.dumps(data))
        jsonFile.close()

        return True
    return False

def get_poke_bst(pokemon):
    bst = sum(poke.get(name=pokemon).base_stats)
    if pokemon.lower() == "archeops":
        return 495
    if bst >= 680:
        return 620
    if bst == 600:
        if 'regi' in pokemon.lower():
            return 570
        else:
            return 580
    if bst == 580:
        return 570
    if bst == 570:
        return 555
    non_leg_w_550_bst = ["florges", "arcanine", "arcanine-hisui","ursaluna-bloodmoon","silvally","palafin","palafin-hero","Slaking", ]
    if pokemon.lower() in non_leg_w_550_bst:
        return 550
    if pokemon.lower() == 'archeops':
        return 495
    else:
        return bst
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
    jsonFile = open(ENV_PATH+"/secret_player_data.json", "r") # Open the JSON file for reading
    data = json.load(jsonFile) # Read the JSON into the buffer
    jsonFile.close() # Close the JSON file

    team = data[chat_id]["team"]

    for [p,l] in team:
        if p!=None:
            return True
    return False

def poke_lega_test(pokemon, level, name, multiplier ,only_perc = False):

    message = f'Trainer: {name}\n'

    with open(ENV_PATH+'/public_player_data.json', 'r') as file:
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

    with open(ENV_PATH+'/public_player_data.json', 'r') as file:
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

def extract_first_number(cell):
    try:
        # Extract the first number before the parentheses
        return float(str(cell).split()[0])
    except:
        return None
    
def poke_lega_team_team(chat_id, enemies):
    with open(ENV_PATH+'/secret_player_data.json', 'r') as file:
        priv_data = json.load(file)
    team = [[pokemon[0], get_power(pokemon[0], pokemon[1])] for pokemon in priv_data[chat_id]["team"] if pokemon[0]]
    dfs = []
    potenze = []
    for enemy, enemy_powers in enemies:
        potenze.append(get_power(enemy,enemy_powers))
        enemy_powers = [enemy_powers,enemy_powers,enemy_powers]
        enemy = [enemy]
        multiplier = 20
        tab, limits = match_prevision(team, enemy, enemy_powers, multiplier)
        dfs.append(tab)

    # Step 1: Concatenate the data (not styles)
    dfs_data = [df for df in dfs]  # Extract data from DataFrames
    dfs_data[1:] = [df.iloc[:, 2:] for df in dfs_data[1:]]  # Keep only the third column from subsequent DataFrames
    concat_data = pd.concat(dfs_data, axis=1)
    new_column_names = list(concat_data.columns[:2]) 
    new_column_names += [f"{col} ({potenze[k-2]})" for k, col in enumerate(concat_data.columns[2:], start=2)]
    concat_data.columns = new_column_names

    path = ENV_PATH+f"/images/{chat_id}_lega_team_team.png"
    create_pokemon_collage(concat_data, type = 'lega', path=path, enemy_powers=None)

    #save_dataframe_as_image_alt(concat_data, path,potenze) # OLD IMAGE METHOD

    return path


def gym_cell():
    with open(ENV_PATH+'/gym_data.json', 'r') as file:
        gym_data = json.load(file)
    return gym_data["gym_cell"]

def gym_types():
    with open(ENV_PATH+'/gym_data.json', 'r') as file:
        gym_data = json.load(file)
    return gym_data["order_of_gym_types"]

def poke_gym(chat_id, gym):
    with open(ENV_PATH+'/secret_player_data.json', 'r') as file:
        priv_data = json.load(file)
    team = [[pokemon[0], get_power(pokemon[0], pokemon[1])] for pokemon in priv_data[chat_id]["team"] if pokemon[0]]
    with open(ENV_PATH+'/gym_data.json', 'r') as file:
        gym_data = json.load(file)

    if gym_data[gym]["actual_team"] == []:
            if gym_data[gym]["team"] == ["every type combo"]:
                enemy = ["every type combo", gym] # enemy potrebbe essere ["every type combo"] e questo fa cose in match_prevision->match_table
            else:
                enemy = gym_data[gym]["team"]   
    else:
        enemy = gym_data[gym]["actual_team"]
    enemy_powers = gym_data[gym]["power"]
    multiplier = gym_data[gym]["multiplier"]

    team_with_level = [[pokemon[0], pokemon[1]] for pokemon in priv_data[chat_id]["team"] if pokemon[0]]
    necessary_lvls = {}
    for p in team_with_level:
        try:
            necessary_lvls[p[0]] = get_gym_results(gym, gym_data, p[0], p[1], chat_id)[-1]
        except:
            necessary_lvls[p[0]] = None#Da fixare
    
    #print(f"Team: {team_with_level}\nEnemy: {enemy}\nEnemy Powers: {enemy_powers}\nMultiplier: {multiplier}\nNecessary Levels: {necessary_lvls}")

    tab, limits = match_prevision(team, enemy, enemy_powers, multiplier, necessary_lvls)

    # If tab is a DataFrame and has a 'style' attribute, it means style.apply was used  # OLD IMAGE METHOD
    #if isinstance(tab, pd.DataFrame) and hasattr(tab, 'style'):
        #tab = tab.style.apply(highlight_max, subset=tab.columns[2:], args=enemy_powers)


    path = ENV_PATH+f"/images/{chat_id}.png"
    create_pokemon_collage(tab, type = 'gym', path=path, enemy_powers = limits)

    #save_dataframe_as_image(tab, path)  # OLD IMAGE METHOD
    return path


def match_prevision(team, enemy, enemy_powers, multiplier, necessary_lvls=None):

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

    bonus_netti,tab = match_table(team,enemy,multiplier,limits = limits, necessary_lvls=necessary_lvls)

    return tab, limits

def match_table(team,enemy,multiplier,limits = None, necessary_lvls=None):
    if "every type combo" in enemy:
        bonus_netti = []
        tabellone = []
        all_types_combo = generate_all_types_combo(enemy[1])
        for p in team:
            bonus_p =[]
            tabella = [p[0],p[1]]
            for t in all_types_combo:
                types2 = poke.get(name=p[0]).types
                bonus = calculate_bonus_via_types(t, types2 ,multiplier)
                bonus_p.append(-bonus[0]+bonus[1])
                tabella.append(str(p[1]-bonus[0]+bonus[1])+' ('+str(-bonus[0]+bonus[1])+')')
            if necessary_lvls:
                tabella.append('+'+str(necessary_lvls.get(p[0], 0))+ ' lvl.')
            bonus_netti.append(bonus_p)
            tabellone.append(tabella)

        tab = pd.DataFrame(tabellone)
        cols = ['Pokemon', 'Potenza Base']
        all_types_collapsed = ['Type' + '_' + '_'.join(sublist) for sublist in all_types_combo]
        for e in all_types_collapsed:
            if e not in cols:
                cols.append(e)
            else:
                i = 2
                name = e +' '+ str(i)
                while name in cols:
                    i+=1
                    name = e +' '+ str(i)
                cols.append(name)
        cols.append("Necessary Levels")
        tab.columns = cols
    else:
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
    return(bonus_netti,tab)




def poke_cell(cell):
    start = STARTING_DATE
    today = datetime.now().date()
    print(today, start)
    offset = cell
    pausa = EVENTUALE_PAUSA
    casella = int(((today-start).days-pausa)/2) + offset
    multiplier = 5 + 3*int(casella/7)
    if casella < 42:
        aumento = int(casella/14) + 2
        low_power = int((LvL[casella]-aumento)*coeff[int(casella/7)])
        mid_power = int((LvL[casella])*coeff[int(casella/7)])
        high_power = int((LvL[casella]+aumento)*coeff[int(casella/7)])
        super_power = int((LvL[casella]+2*aumento)*coeff[int(casella/7)])
        if casella+1 in gym_cell():
            trainer_power = [low_power,mid_power,high_power]
            gym_power = [mid_power,mid_power,high_power,high_power,super_power,super_power]
            return True, trainer_power, gym_power, multiplier, LvL[casella]
        else:
            encounter_power = [low_power,mid_power]
            boss_power = [int((LvL[casella]+aumento)*coeff[int(casella/7)]),int((LvL[casella]+aumento+10)*coeff[int(casella/7)]),int((LvL[casella]+aumento+18)*coeff[int(casella/7)])]
            return False, encounter_power, boss_power, multiplier
    else:
        return None

def generate_all_types_combo(type):
    all_types = [[type]]
    not_type = [['normal','ice'],   ['ice','normal'],
                ['normal','bug'],   ['bug','normal'],
                ['normal','rock'],  ['rock','normal'],
                ['normal','steel'], ['steel','normal'],
                ['fire','fairy'],   ['fairy','fire'],
                ['ice','poison'],   ['poison','ice'],
                ['ground','fairy'], ['fairy','ground'],
                ['bug','dragon'],   ['dragon','bug'],
                ['ghost','rock'],   ['rock','ghost'],
                ]
    for t in pokemon_types:
        if [type,t] not in not_type and t!=type:
            #all_types.append(sorted([type,t]))
            all_types.append([type,t])

    # with open(ENV_PATH+'/type_list_frequency.json') as f:
    #     type_list_frequency = json.load(f)
    #     # Define a function to get the frequency
    # def get_frequency(type_combo):
    #     key = str(type_combo)  # Match the format used in the JSON
    #     return type_list_frequency.get(key, 0)
    # # Sort by frequency (descending)
    # all_types = sorted(all_types, key=get_frequency, reverse=True)

    return all_types




async def poke_check_if_evo(chat_id,pokemon,lvl):
    with open(ENV_PATH+"/secret_player_data.json", 'r') as f:
        secret = json.load(f)
    route = secret[chat_id]["route"]

    with open(ENV_PATH+f"/{route}_evo_file.json", 'r') as ef:
        evo_dict = json.load(ef)

    pokemon = pokemon.lower()
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
    with open(ENV_PATH+"/secret_player_data.json", 'r') as f:
        secret = json.load(f)
    route = secret[chat_id]["route"]

    with open(ENV_PATH+f"/{route}_evo_file.json", 'r') as ef:
        evo_dict = json.load(ef)
        
    pokemon = pokemon.lower()
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

def poke_evolve_not_async(chat_id,pokemon,lvl):
    with open(ENV_PATH+"/secret_player_data.json", 'r') as f:
        secret = json.load(f)
    route = secret[chat_id]["route"]

    with open(ENV_PATH+f"/{route}_evo_file.json", 'r') as ef:
        evo_dict = json.load(ef)

    pokemon = pokemon.lower()
    evo_lvl = 0
    if pokemon in evo_dict:
        if evo_dict[pokemon][0]=="base":
            if lvl >= evo_dict[pokemon][1][0]:
                evo_lvl = evo_dict[pokemon][1][0]
                pokemon = evo_dict[pokemon][1][1]
        elif evo_dict[pokemon][0]=="mid":
            if lvl >= evo_dict[pokemon][2][0]:
                evo_lvl = evo_dict[pokemon][2][0]
                pokemon = evo_dict[pokemon][2][1]

    return pokemon, evo_lvl

def poke_evo_level(chat_id,pokemon):
    with open(ENV_PATH+"/secret_player_data.json", 'r') as f:
        secret = json.load(f)
    route = secret[chat_id]["route"]

    with open(ENV_PATH+f"/{route}_evo_file.json", 'r') as ef:
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
    start = STARTING_DATE
    today = datetime.now().date()
    offset = cell
    pausa = EVENTUALE_PAUSA
    casella = int(((today-start).days-pausa)/2) + offset
    multiplier = 5 + 3*int(casella/7)

    with open(ENV_PATH+f"/{route}_evo_file.json", 'r') as ef:
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


async def poke_fight(chat_id,trainer,pokemons):
    if trainer == True:
        path, enemy_powers = await poke_trainer(chat_id,pokemons)
    else:
        path, enemy_powers = await poke_encounter(chat_id,pokemons)
    return path, enemy_powers


async def poke_trainer(chat_id,pokemons):
    with open(ENV_PATH+'/secret_player_data.json', 'r') as file:
        priv_data = json.load(file)
    team = [[pokemon[0], get_power(pokemon[0], pokemon[1])] for pokemon in priv_data[chat_id]["team"] if pokemon[0]]


    start = STARTING_DATE
    today = datetime.now().date()
    pausa = EVENTUALE_PAUSA
    casella = int(((today-start).days-pausa)/2)

    offset = 0
    while casella+1+offset not in gym_cell():
        offset += 1
    #print(casella, offset)

    _, enemy_powers, _, multiplier, _ = poke_cell(offset)

    tab, limits = match_prevision(team, pokemons, enemy_powers, multiplier)

    # If tab is a DataFrame and has a 'style' attribute, it means style.apply was used
    #if isinstance(tab, pd.DataFrame) and hasattr(tab, 'style'):  # OLD IMAGE METHOD
        #tab = tab.style.apply(highlight_max, subset=tab.columns[2:], args=enemy_powers)


    path = ENV_PATH+f"/images/{chat_id}.png"
    create_pokemon_collage(tab, type = 'trainer', path=path, enemy_powers = enemy_powers)

    #save_dataframe_as_image(tab, path) # OLD IMAGE METHOD
    return path, enemy_powers


async def poke_encounter(chat_id,encounter):
    with open(ENV_PATH+'/secret_player_data.json', 'r') as file:
        priv_data = json.load(file)
    team = [[pokemon[0], get_power(pokemon[0], pokemon[1])] for pokemon in priv_data[chat_id]["team"] if pokemon[0]]
    route = priv_data[chat_id]["route"]

    start = STARTING_DATE
    today = datetime.now().date()
    pausa = EVENTUALE_PAUSA
    casella = int(((today-start).days-pausa)/2)

    offset = 0
    while casella+1+offset in gym_cell():
        offset += 1
    #print(casella, offset)

    enemy_powers, multiplier = poke_cell_specific(route,offset,encounter)

    tab = encounter_prevision(team, encounter, enemy_powers, multiplier)
    #print('ooo',enemy_powers)

    # If tab is a DataFrame and has a 'style' attribute, it means style.apply was used
    #if isinstance(tab, pd.DataFrame) and hasattr(tab, 'style'):  # OLD IMAGE METHOD
        #tab = tab.style.apply(highlight_max, subset=tab.columns[2:], args=enemy_powers)

    path = ENV_PATH+f"/images/{chat_id}.png"
    create_pokemon_collage(tab, type = 'encounter', path=path, enemy_powers = enemy_powers)

    # save_dataframe_as_image(tab, path)  # OLD IMAGE METHOD
    return path, enemy_powers


def encounter_prevision(team, enemy, enemy_powers, multiplier):

    #print('TABELLA COMPATITIBILITÀ : gli avversari hanno ',enemy_powers)
    bonus_netti,tab = encounter_table(team,enemy,multiplier,limits = enemy_powers)

    return tab

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

    """  # OLD IMAGE METHOD
    if limits != None:
        # Create a Styler object
        styler = tab.style

        # Apply the highlighting function to each column separately
        for i, col in enumerate(cols[2:], start=2):
            styler = styler.apply(encounter_highlight_max, subset=[col], args=(limits, i))

        # Set the styled DataFrame
        tab = styler

    """
    return(bonus_netti,tab)


def poke_counter(pokemon, level=100):
    counters = []

    multiplier = 20

    with open(ENV_PATH+'/public_player_data.json', 'r') as file:
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

def get_wins(pokemon, livello, all_types_combo, multiplier, limits):

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
        for t in all_types_combo:
            types2 = poke.get(name=pokemon).types
            bonuses = calculate_bonus_via_types(t, types2 ,multiplier)
            bonus = bonuses[1] - bonuses[0]
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
        for t in all_types_combo:
            types2 = poke.get(name=pokemon).types
            bonuses = calculate_bonus_via_types(t, types2, multiplier)
            bonus = bonuses[1] - bonuses[0]
            average += bonus
            num += 1
            if bonus < min_bonus:
                min_bonus = bonus
            if bonus > max_bonus:
                max_bonus = bonus

    average /= num
    average = round(average, 2)

    return average, min_bonus, max_bonus, grey_wins, red_wins, yellow_wins, green_wins

def poke_gym_test(chat_id, pokemon, livello=0, next=4):

    start = STARTING_DATE
    today = datetime.now().date()
    pausa = EVENTUALE_PAUSA
    casella = int(((today-start).days-pausa)/2)

    offset = 0
    while casella+1 > gym_cell()[offset]:
        offset += 1

    with open(ENV_PATH+'/gym_data.json', 'r') as file:
        gym_data = json.load(file)

    results = []

    end = min(offset + next, len(gym_types()))

    for gym in gym_types()[offset:end]:
        results.append(get_gym_results(gym, gym_data, pokemon, livello, chat_id))
    
    return results

def get_gym_results(gym, gym_data, pokemon, livello, chat_id):

    results = []

    if gym_data[gym]["actual_team"] == []:
        if gym_data[gym]["team"] == ["every type combo"]:
            enemy = ["every type combo", gym] # enemy potrebbe essere ["every type combo"] e questo fa cose in match_prevision->match_table
        else:
            enemy = gym_data[gym]["team"]   
    else:
        enemy = gym_data[gym]["actual_team"]
    enemy_powers = gym_data[gym]["power"]
    limits = [enemy_powers[0],enemy_powers[2],enemy_powers[4]]
    multiplier = gym_data[gym]["multiplier"]

    all_types_combo = generate_all_types_combo(enemy[1])

    average, min_bonus, max_bonus, grey_wins, red_wins, yellow_wins, green_wins = get_wins(pokemon, livello, all_types_combo, multiplier, limits)

    if livello != 0:
        if grey_wins > 0:
            bonus = min_bonus
            pokemon_bst = get_poke_bst(pokemon)
            necessary_lvl = round((limits[0]-bonus)*100/pokemon_bst)
            while limits[0] - bonus > round(necessary_lvl*pokemon_bst/100):
                necessary_lvl += 1
            new_pokemon, evo_lvl = poke_evolve_not_async(chat_id, pokemon, necessary_lvl)
            while new_pokemon != pokemon.lower():
                _, bonus, _, _, _, _, _ = get_wins(new_pokemon, livello, all_types_combo, multiplier, limits)
                pokemon_bst = get_poke_bst(new_pokemon)
                necessary_lvl = round((limits[0]-bonus)*100/pokemon_bst)
                while limits[0] - bonus > round(necessary_lvl*pokemon_bst/100):
                    necessary_lvl += 1
                necessary_lvl = max(necessary_lvl,evo_lvl)
                pokemon = new_pokemon
                new_pokemon, evo_lvl = poke_evolve_not_async(chat_id, pokemon, necessary_lvl)
            results = [gym, average, min_bonus, max_bonus, grey_wins, red_wins, yellow_wins, green_wins, max(0,necessary_lvl-livello)]
        else:
            results = [gym, average, min_bonus, max_bonus, grey_wins, red_wins, yellow_wins, green_wins, 0]
    else:
        results = [gym, average, min_bonus, max_bonus]

    return results


#############################################################################################################################################################
#############################################################################################################################################################
#############################################################################################################################################################
#############################################################################################################################################################

# CREAZIONE DELLE IMMAGINI DI GYM, LEGA, FIGHT...

#############################################################################################################################################################
#############################################################################################################################################################
#############################################################################################################################################################
#############################################################################################################################################################


def create_text_image(text, background_color,lines_left_top_right_bottom = (True,True,True,True)):
    image = Image.new('RGB', (250, 98), background_color) #  Create a blank image (250x96) with the specified background color

    draw = ImageDraw.Draw(image) # Prepare to add text
    try: # Load bold font for the text
        if len(text) > 11:
            font = ImageFont.truetype(os.path.join(ENV_PATH, 'arialbd.ttf'), 24)  # Smaller font if text is longer than 8 characters
        else:
            font = ImageFont.truetype(os.path.join(ENV_PATH, 'arialbd.ttf'), 45)  # Regular font for short text
        if 'Encounter' in text:
            font = ImageFont.truetype(os.path.join(ENV_PATH, 'arialbd.ttf'), 32)  # Regular font for short text
    except IOError:
        font = ImageFont.load_default()  # Fallback to default font if custom font isn't available
    position = (30, 25)  # Add the text at a fixed position
    draw.text(position, text, fill="black", font=font)

    border_width = 1
    image_width, image_height = image.size
    if lines_left_top_right_bottom[1]:
        draw.line([(0, 0), (image_width, 0)], fill="black", width=border_width) #Draw top line
    if lines_left_top_right_bottom[3]:
        draw.line([(0, image_height - 1), (image_width, image_height - 1)], fill="black", width=border_width) # Draw bottom line
    if lines_left_top_right_bottom[0]:
        draw.line([(0, 0), (0, image_height)], fill="black", width=border_width) # Draw left line
    if lines_left_top_right_bottom[2]:
        draw.line([(image_width - 1, 0), (image_width - 1, image_height)], fill="black", width=border_width) # Draw right line

    return image

def create_pokemon_name_image(pokemon_name, front = True, shiny_or_default = 'default', lines_left_top_right_bottom = (True,True,True,True)):
    blank_image = Image.new('RGB', (250, 98), (255, 255, 255)) # Create a blank image (250x96) with white background

    sprite_image = Image.new('RGB', (96, 96), (0, 0, 0)).convert("RGBA")
    try:
            pokemon = poke.get(name=pokemon_name.lower())
            if not front:
                try:
                    sprite_url = pokemon.sprites.back[shiny_or_default]
                    response = requests.get(sprite_url)
                except:
                    sprite_url = pokemon.sprites.front[shiny_or_default]
                    response = requests.get(sprite_url)
            else:
                sprite_url = pokemon.sprites.front[shiny_or_default]
                response = requests.get(sprite_url)
            sprite_image = Image.open(BytesIO(response.content)).convert("RGBA")  # Fetch the sprite imag
    except:
        pass

    sprite_image = sprite_image.resize((96, 96)) # Resize sprite if needed to fit the blank image (optional)
    blank_image.paste(sprite_image, (1, 1), sprite_image) # Paste the sprite on the left side of the blank image (use alpha for transparency)
   
    draw = ImageDraw.Draw(blank_image)  # Prepare to add text
    try:
        if len(pokemon_name) > 12:
            font_bold = ImageFont.truetype(os.path.join(ENV_PATH, 'arialbd.ttf'), 14)  # Smaller font if the name is longer than 12 characters
        else:
            font_bold = ImageFont.truetype(os.path.join(ENV_PATH, 'arialbd.ttf'), 24)  # Regular bold font for shorter names
    except IOError:
        font_bold = ImageFont.load_default()  # Fallback to default font if custom font isn't available
    if len(pokemon_name) > 12: # Add the Pokémon name to the right of the sprite
        draw.text((110, 40), pokemon_name.capitalize(), fill="black", font=font_bold)  # Center the name vertically
    else:
        draw.text((110, 35), pokemon_name.capitalize(), fill="black", font=font_bold)  # Center the name vertically

    border_width = 1
    image_width, image_height = blank_image.size
    if lines_left_top_right_bottom[1]:
        draw.line([(0, 0), (image_width, 0)], fill="black", width=border_width) #Draw top line
    if lines_left_top_right_bottom[3]:
        draw.line([(0, image_height - 1), (image_width, image_height - 1)], fill="black", width=border_width) # Draw bottom line
    if lines_left_top_right_bottom[0]:
        draw.line([(0, 0), (0, image_height)], fill="black", width=border_width) # Draw left line
    if lines_left_top_right_bottom[2]:
        draw.line([(image_width - 1, 0), (image_width - 1, image_height)], fill="black", width=border_width) # Draw right line

    return blank_image

def create_type_name_image(pokemon_name, lines_left_top_right_bottom = (True,True,True,True)):
    # Create base blank image
    blank_image = Image.new('RGB', (250, 98), (255, 255, 255))  # White background

    try:
        # Parse types
        type_parts = pokemon_name.lower().split('_')[1:]  # e.g., ['fire'] or ['fire', 'flying']
        type_images = []

        # Load and resize each type image to 144x48
        for type_name in type_parts:
            img_path = ENV_PATH + f"/images/types/{type_name}.png"
            img = Image.open(img_path).convert("RGBA")
            resized = img.resize((144, 48), Image.LANCZOS)
            type_images.append(resized)

        # Total height of stacked images (either 48 or 96)
        total_height = sum(img.height for img in type_images)
        # Assume all type_images have same width (144)
        img_width = type_images[0].width if type_images else 0

        # Calculate top-left corner to center the stack in the blank image
        x_offset = (250 - img_width) // 2
        y_offset = (98 - total_height) // 2
    except Exception as e:
        print('\n\n\n\n\n\n\n\n\n\n')
        print(f"Error loading type images for {pokemon_name}: {e}")
        print('\n\n\n\n\n\n\n\n\n\n')
        type_images = [Image.new('RGB', (5, 5), (255, 0, 0)).convert("RGBA")] # Default
        x_offset = 1
        y_offset = 1

    # Paste images stacked vertically, centered
    for img in type_images:
        blank_image.paste(img, (x_offset, y_offset), img)
        y_offset += img.height

    draw = ImageDraw.Draw(blank_image)  # Prepare to add text

    # TENTATIVO DI SCRIVERE LE FREQUENZE. FALLISCE DATO CHE CI STANNO ALCUNE FORME CHE NON SO COME CONTARE...
    # try:
    #     font_bold = ImageFont.truetype(os.path.join(ENV_PATH, 'arialbd.ttf'), 44)  # Regular bold font for shorter names
    # except IOError:
    #     font_bold = ImageFont.load_default()  # Fallback to default font if custom font isn't available
    # with open(ENV_PATH+'/type_list_frequency.json') as f:
    #     type_list_frequency = json.load(f)
    # draw.text((190, 40), '('+str(type_list_frequency[str(type_parts)])+')', fill="black", font=font_bold)  # Center the name vertically

    border_width = 1
    image_width, image_height = blank_image.size
    if lines_left_top_right_bottom[1]:
        draw.line([(0, 0), (image_width, 0)], fill="black", width=border_width) #Draw top line
    if lines_left_top_right_bottom[3]:
        draw.line([(0, image_height - 1), (image_width, image_height - 1)], fill="black", width=border_width) # Draw bottom line
    if lines_left_top_right_bottom[0]:
        draw.line([(0, 0), (0, image_height)], fill="black", width=border_width) # Draw left line
    if lines_left_top_right_bottom[2]:
        draw.line([(image_width - 1, 0), (image_width - 1, image_height)], fill="black", width=border_width) # Draw right line

    return blank_image

def create_pokemon_image(pokemon_name, power, front = False, shiny_or_default = 'default', lines_left_top_right_bottom = (True,True,True,True)):
    blank_image = Image.new('RGB', (250, 98), (255, 255, 255))  # Create a blank image (250x98) with white background

    sprite_image = Image.new('RGB', (96, 96), (0, 0, 0)).convert("RGBA") # Default Sprite
    try: # Import the Sprite
        pokemon = poke.get(name=pokemon_name.lower())
        if not front:
            try:
                sprite_url = pokemon.sprites.back[shiny_or_default]
                response = requests.get(sprite_url)
            except:
                sprite_url = pokemon.sprites.front[shiny_or_default]
                response = requests.get(sprite_url)
        else:
            sprite_url = pokemon.sprites.front[shiny_or_default]
            response = requests.get(sprite_url)
        sprite_image = Image.open(BytesIO(response.content)).convert("RGBA")  # Fetch the sprite imag
    except:
        pass

    sprite_image = sprite_image.resize((96, 96))  # Resize sprite if needed to fit the blank image (optional)
    blank_image.paste(sprite_image, (1, 1), sprite_image) # Paste the sprite on the left side of the blank image (use alpha for transparency)

    draw = ImageDraw.Draw(blank_image) # Prepare to add text
    try:     # Load bold font for the name and a larger font for the power number
        if len(pokemon_name) > 12:
            font_bold = ImageFont.truetype(os.path.join(ENV_PATH, 'arialbd.ttf'), 14)  # Smaller font if the name is longer than 12 characters
        else:
            font_bold = ImageFont.truetype(os.path.join(ENV_PATH, 'arialbd.ttf'), 24)  # Regular bold font for shorter names
        font_large = ImageFont.truetype(os.path.join(ENV_PATH, 'arialbd.ttf'), 44)  # Larger bold font for power number
    except IOError:
        font_bold = ImageFont.load_default()  # Fallback to default font if custom font isn't available
        font_large = ImageFont.load_default()
    if len(pokemon_name) > 12:  # Add the Pokémon name to the right of the sprite
        draw.text((110, 17), pokemon_name.capitalize(), fill="black", font=font_bold)  # Position (110, 17)
    else:
        draw.text((110, 10), pokemon_name.capitalize(), fill="black", font=font_bold)  # Position (110, 10)
    draw.text((110, 40), str(power), fill="black", font=font_large)  # Add the power number below the name with larger font

    border_width = 1 # Draw lines
    image_width, image_height = blank_image.size
    if lines_left_top_right_bottom[1]:
        draw.line([(0, 0), (image_width, 0)], fill="black", width=border_width) #Draw top line
    if lines_left_top_right_bottom[3]:
        draw.line([(0, image_height - 1), (image_width, image_height - 1)], fill="black", width=border_width) # Draw bottom line
    if lines_left_top_right_bottom[0]:
        draw.line([(0, 0), (0, image_height)], fill="black", width=border_width) # Draw left line
    if lines_left_top_right_bottom[2]:
        draw.line([(image_width - 1, 0), (image_width - 1, image_height)], fill="black", width=border_width) # Draw right line

    return blank_image

def create_pokemon_collage(df, type = 'gym', path=None, enemy_powers=None):

    def randomly_shiny():
        if random.randint(0,1023) == 1:
            return "shiny"
        else:
            return "default"
        
    image_width = 250 # Assuming all images have the same size (250x98)
    image_height = 98

    num_rows, num_cols = df.shape # Create a blank collage image with a grid layout (grid_size is a tuple of (rows, cols))
    collage_width = (num_cols-1) * image_width
    collage_height = (num_rows+1) * image_height
    collage_image = Image.new('RGB', (collage_width, collage_height), (255, 255, 255))  # White background
    
    # Crea prima colonna, squadra.
    name_image = create_text_image(f'{type.title()} →',(255,255,255),(False,False,True,True))
    collage_image.paste(name_image, (0,0))
    for index, (pokemon_name, power) in enumerate(zip(df['Pokemon'].tolist(), df['Potenza Base'].tolist())):
        name_position = (0, (index+1) * image_height) # Position for Pokémon name
        name_image = create_pokemon_image(pokemon_name, power, front = False, shiny_or_default = 'default', lines_left_top_right_bottom = (False,False,True,False))
        collage_image.paste(name_image, name_position)

    # Crea le altre colonne
    for col in range(2, num_cols):
        position = ((col-1) * image_width, 0)
        column_name = df.columns[col]  # Get column name (e.g., "Yanma (195)")
        if column_name == "Necessary Levels":
            header_img = create_text_image("LvLs",
                                   background_color=(255,255,255),
                                   lines_left_top_right_bottom=(False,False,False,True))
            collage_image.paste(header_img, position)

            # 2) draw each row from df["Necessary Levels"]
            for row_idx in range(num_rows):
                val = str(df.loc[row_idx, "Necessary Levels"])
                pos = ((col-1)*image_width, (row_idx+1)*image_height)
                txt_img = create_text_image(val,
                                            background_color=(255,255,255),
                                            lines_left_top_right_bottom=(False,False,False,False))
                collage_image.paste(txt_img, pos)
        else:
            if type == 'lega':
                pokemon_name, power = column_name.split(' ')
                power = int(power.replace('(','').replace(')',''))
                individual_image = create_pokemon_image(pokemon_name,power,True,randomly_shiny(),(False,False,False,True))  # Create the Pokémon image
            else:
                try: # Fixa i pokemon delle palestre tipo (Geodude, Geodude 2, Geodude 3)
                    pokemon_name = column_name.split(' ')[0]
                except:
                    pokemon_name = column_name
                if 'Type_' not in pokemon_name:
                    individual_image = create_pokemon_name_image(pokemon_name,True,randomly_shiny(),lines_left_top_right_bottom = (False,False,False,True))  # Create the Pokémon image
                else:
                    individual_image = create_type_name_image(pokemon_name,lines_left_top_right_bottom = (False,False,False,True))  # Create the Pokémon image
            collage_image.paste(individual_image, position)
            for index in range(num_rows):
                scaled_power = int(df[column_name][index].split(' ')[0].replace('(','').replace(')',''))
                position = ((col-1) * image_width, (index+1) * image_height)
                if type == 'lega':
                    if scaled_power > power:
                        bg = (99, 238, 99)
                    else:
                        bg = (255,255,255)
                elif type == 'encounter':
                    try: #Se enemy_power = None o corto almeno non si blocca
                        if scaled_power >= enemy_powers[0]:
                            bg = (255, 111, 111) # Red
                            if scaled_power >= enemy_powers[1]:
                                bg = (255, 255, 111) # Yellow
                                if scaled_power >= enemy_powers[col]: # nel caso encounter, enemy_powers è [bassa,media,boss1,boss2,boss3 ...],l'indice col ci fa un grand favore partendo da 2
                                    bg = (99, 238, 99) # Green
                        else:
                            bg = (255,255,255)
                    except:
                        bg = (0,0,0)
                else:
                    try: #Se enemy_power = None o corto almeno non si blocca
                        if scaled_power >= enemy_powers[0]:
                            bg = (255, 111, 111) # Red
                            if scaled_power >= enemy_powers[1]:
                                bg = (255, 255, 111) # Yellow
                                if scaled_power >= enemy_powers[2]:
                                    bg = (99, 238, 99) # Green
                        else:
                            bg = (255,255,255)
                    except:
                        bg = (0,0,0)

                text_image = create_text_image(df[column_name][index], bg,(False,False,False,False))  # White text on blue
                collage_image.paste(text_image, position)
        
    # Save or return the final collage image
    if path:
        collage_image.save(path)
    return collage_image


#############################################################################################################################################################
#############################################################################################################################################################
#############################################################################################################################################################
#############################################################################################################################################################

# OLD IMAGE METHOD (Cerca questo tag per le altre parti)

#############################################################################################################################################################
#############################################################################################################################################################
#############################################################################################################################################################
#############################################################################################################################################################


def save_dataframe_as_image(df, path):

    # Check if df is a Styler object
    if isinstance(df, pd.io.formats.style.Styler):
        styled_df = df
    else:
        styled_df = df.style

    # Save the styled DataFrame as an image
    dfi.export(styled_df.background_gradient(), path, table_conversion='matplotlib')

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

# --------------------------------------------------------------------------- AUTOMATIC TEAM UPDATE -------------------------------------------------------------------------------------------

def crop_to_binary(crop, threshold=69):
    gray = crop.convert("L")
    binary = gray.point(lambda p: 1 if p < threshold else 0, mode='1')
    #binary_pixels = list(binary.getdata())
    return binary

def find_vertical_black_lines(image):
    img_array = np.array(image)
    height, width = img_array.shape
    vertical_lines = []
    # Check each column - if all pixels are 0 (black), it's a vertical black line
    for x in range(width):
        column = img_array[:, x]
        if np.all(column == 0):  # All pixels are black
            vertical_lines.append(x)
    
    return vertical_lines

def find_horizontal_black_lines(image):
    # Convert to binary array (0 = black, 255 = white)
    img_array = np.array(image)
    height, width = img_array.shape
    
    horizontal_lines = []
    
    # Check from top (y=0) going down
    for y in range(height):
        row = img_array[y, :]
        if np.all(row == 0):  # All pixels are black
            horizontal_lines.append(y)
        else:
            break  # Stop at first non-black row
    
    # Check from bottom (y=height-1) going up
    for y in range(height - 1, -1, -1):
        if y in horizontal_lines:
            break  # Already found this row from top scan
        row = img_array[y, :]
        if np.all(row == 0):  # All pixels are black
            horizontal_lines.append(y)
        else:
            break  # Stop at first non-black row
    
    return sorted(horizontal_lines)

def split_image_by_vertical_lines(image, vertical_lines):
    if not vertical_lines:
        return [image]
    width, height = image.size
    sub_images = []
    vertical_lines = sorted(set(vertical_lines))     # Sort vertical lines and remove duplicates
    line_groups = [] # Group consecutive vertical lines together
    current_group = [vertical_lines[0]]
    for i in range(1, len(vertical_lines)):
        if vertical_lines[i] == vertical_lines[i-1] + 1:
            current_group.append(vertical_lines[i])
        else:
            line_groups.append(current_group)
            current_group = [vertical_lines[i]]
    line_groups.append(current_group)
    split_points = [0]
    for group in line_groups:
        split_points.append(group[-1] + 1)  # After the last line in the group
    split_points.append(width)
    for i in range(len(split_points) - 1):
        left = split_points[i]
        right = split_points[i + 1]
        if right - left > 0:         # Skip if the section is empty or too narrow
            sub_image = image.crop((left, 0, right, height))
            sub_images.append(sub_image)
    return sub_images

def remove_black_lines_from_image(image):
    vertical_lines = find_vertical_black_lines(image)
    horizontal_lines = find_horizontal_black_lines(image)  
    if not vertical_lines and not horizontal_lines:
        return image
    width, height = image.size
    keep_columns = [x for x in range(width) if x not in vertical_lines]
    keep_rows = [y for y in range(height) if y not in horizontal_lines]
    if not keep_columns or not keep_rows:
        return Image.new('1', (1, 1), 1)
    new_width, new_height = len(keep_columns), len(keep_rows)
    new_image = Image.new('1', (new_width, new_height), 1)  # White background
    for new_y, old_y in enumerate(keep_rows):
        for new_x, old_x in enumerate(keep_columns):
            pixel = image.getpixel((old_x, old_y))
            new_image.putpixel((new_x, new_y), pixel)
    return new_image

def process_image_to_remove_black(image):
    vertical_lines = find_vertical_black_lines(image)
    sub_images = split_image_by_vertical_lines(image, vertical_lines)
    cleaned_images = []
    for i, sub_img in enumerate(sub_images):    
        cleaned_img = remove_black_lines_from_image(sub_img)
        if cleaned_img and cleaned_img.size != (1, 1):
            # Padding step
            width, height = cleaned_img.size
            pad_width = max(5 - width, 0)
            pad_height = max(5 - height, 0)

            left = pad_width // 2
            right = pad_width - left
            top = pad_height // 2
            bottom = pad_height - top

            padded_img = ImageOps.expand(cleaned_img, (left, top, right, bottom), fill=0)

            cleaned_images.append(padded_img)

    return cleaned_images

def calculate_ssim(pil1,pil2):
    #Can be made better by loading arrays directly... but later
    pil1 = pil1.convert('L')
    pil2 = pil2.convert('L')

    img1 = np.array(pil1)
    img2 = np.array(pil2)

    if img1.shape != img2.shape:
        pil2 = pil2.resize(pil1.size)
        img2 = np.array(pil2)

    min_dim = min(img1.shape)
    win_size = min(7, min_dim)
    if win_size % 2 == 0:
        win_size -= 1  # must be odd

    score, _ = ssim(img1, img2, full=True, win_size=win_size)
    return score

def compare_with_saved_data_json(splits, json_name='alphabet.json'):

    # Load JSON file
    with open(ENV_PATH+'/'+json_name, 'r') as f:
        data = json.load(f)

    # Decode base64 strings into PIL images
    alphabet = {}
    for key, img_str in data.items():
        img_bytes = base64.b64decode(img_str)
        img = Image.open(BytesIO(img_bytes))
        alphabet[key] = img
    
    pokemon_probable_name = []
    for sp in splits:
        alph_likeness = [calculate_ssim(sp, alphabet[k]) for k in alphabet.keys()]
        best_match_idx = np.argmax(alph_likeness)
        best_match_key = list(alphabet.keys())[best_match_idx]
        best_match_key = best_match_key.split('_')[0]
        pokemon_probable_name.append(best_match_key)

    try:
        return ''.join(pokemon_probable_name)
    except:
        return ''.join(str(x) for x in pokemon_probable_name)

def most_similar(query, choices):
    matches = difflib.get_close_matches(query, choices, n=1, cutoff=0.0)
    return matches[0] if matches else None
         
async def automatic_card_reader(image):
    # Estrai i nomi e i livelli:
    secret_data =[]
    errors = []

    for row in range(3):
        for col in range(3):
            box_width = 300
            box_height = 50
            left = 596 + col * 345
            upper = 50 + row * 618
            right = left + box_width
            lower = upper + box_height
            name_crop = image.crop((left, upper, right, lower))
            binary_img = crop_to_binary(name_crop)
            
            splits = process_image_to_remove_black(binary_img)
            
            pokemon_probable_name = compare_with_saved_data_json(splits)

            box_width = 120
            box_height = 47
            left = 740 + col * 345
            upper = 561 + row * 613
            right = left + box_width
            lower = upper + box_height
            name_crop = image.crop((left, upper, right, lower))
            binary_img = crop_to_binary(name_crop)
            
            splits = process_image_to_remove_black(binary_img)

            pokemon_probable_level = compare_with_saved_data_json(splits)

            box_width = 120
            box_height = 47
            left = 760 + col * 345
            upper = 510 + row * 613
            right = left + box_width
            lower = upper + box_height
            name_crop = image.crop((left, upper, right, lower))
            binary_img = crop_to_binary(name_crop)
            
            splits = process_image_to_remove_black(binary_img)

            pokemon_probable_power = compare_with_saved_data_json(splits)

            if pokemon_probable_name != '':
                if poke_exist(pokemon_probable_name.lower()):
                    secret_data.append([pokemon_probable_name,int(pokemon_probable_level)])
                    if round(get_poke_bst(pokemon_probable_name.lower())*int(pokemon_probable_level)/100) != int(pokemon_probable_power):
                        errors.append('01')
                    else:
                        errors.append('00')
                else:

                    with open(ENV_PATH+'/pokemon_list.json', 'r', encoding="utf-8") as f:
                        choices = json.load(f)

                    pokemon_name = most_similar(pokemon_probable_name, choices)
                    if round(get_poke_bst(pokemon_name)*int(pokemon_probable_level)/100) != int(pokemon_probable_power):
                        errors.append('11')
                    else:
                        errors.append('10')
                    secret_data.append([pokemon_name,int(pokemon_probable_level)])
            else:
                secret_data.append([None,1])
                errors.append('00')

    return secret_data,errors