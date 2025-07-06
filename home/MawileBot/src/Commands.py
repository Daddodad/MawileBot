import asyncio
import time
import json
import random
import requests #test
from PIL import Image, ImageDraw, ImageFont
import os
from io import BytesIO
from telegram import Update, Bot
#from telegram import BotCommand, ForceReply
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.error import BadRequest
import pypokedex as poke

# Custom exception for unauthorized access
class UnauthorizedAccess(Exception):
    pass

import sys
if os.path.exists('/home/SableyeBot/src'):
    ENV_PATH = '/home/SableyeBot/src'
    sys.path.insert(0,ENV_PATH) # SableyeBot
else:
    ENV_PATH = './home/MawileBot/src'
    sys.path.insert(0,ENV_PATH) # MawileBot
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))



from poke_lib import calculate_bonus_answer, random_pokemon, random_player, get_power, poke_evo_level,format_types_emoji
from poke_lib import add_new_player, poke_lega_single, poke_lega_all, poke_gym, poke_exist, poke_dex1, poke_dex2, poke_cell
from poke_lib import add_route,check_route, poke_check_if_evo, poke_fight, poke_counter, has_a_team, poke_gym_test, poke_lega_team_team
from poke_lib import automatic_card_reader
# ----------------------------------------------------------------- GENERIC COMMANDS --------------------------------------------------------------------------------

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Niente da fare, eh")
    context.user_data.clear()
    return ConversationHandler.END

async def end_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    #context.user_data.clear()
    return ConversationHandler.END

def whitelist(chat_id):
    if chat_id in [333178731,454010613]:
        return True
    return False

# Werry = 762058738

async def id_check(update: Update) ->None:

    #####################################################################   ██████╗  ██████╗ ████████╗████████╗ ██████╗ ███╗   ██╗███████╗    ██████╗  ██████╗ ███████╗███████╗ ██████╗ 
    #####################################################################   ██╔══██╗██╔═══██╗╚══██╔══╝╚══██╔══╝██╔═══██╗████╗  ██║██╔════╝    ██╔══██╗██╔═══██╗██╔════╝██╔════╝██╔═══██╗
    deactivate_the_bot = False # True to disable the bot for testing        ██████╔╝██║   ██║   ██║      ██║   ██║   ██║██╔██╗ ██║█████╗      ██████╔╝██║   ██║█████╗  █████╗  ██║   ██║
    #####################################################################   ██╔═══╝ ██║   ██║   ██║      ██║   ██║   ██║██║╚██╗██║██╔══╝      ██╔═══╝ ██║   ██║██╔══╝  ██╔══╝  ██║   ██║
    #####################################################################   ██║     ╚██████╔╝   ██║      ██║   ╚██████╔╝██║ ╚████║███████╗    ██║     ╚██████╔╝██║     ██║     ╚██████╔╝
    #####################################################################   ╚═╝      ╚═════╝    ╚═╝      ╚═╝    ╚═════╝ ╚═╝  ╚═══╝╚══════╝    ╚═╝      ╚═════╝ ╚═╝     ╚═╝      ╚═════╝
    # Ringraziamo chatgpt per la scritta "Bottone Rosso"

    chat_id = update.effective_chat.id
    #print(chat_id)
    if chat_id in []:
        answers = [
            "… i Vassago non dovrebbero affidarsi a tool di Laoconte, potrebbero rimetterci le corna",
            "… chiedilo al tuo guardiano Vassago, cosa vuoi da me",
            "… ancora qui? Tornatene al tuo gate, Vassago",
            "… Vassago infame per te solo le lame",
            "… uh guarda, un bel sacrificio Vassago si è palesato"
            ]
        await update.message.reply_text(random.choice(answers))
    if deactivate_the_bot:
        if not whitelist(chat_id):
            await update.message.reply_text('█▀█ ███ █▀█   ▞▚ █▀█ C ███ ▛▄ ▞▚ . . . \n █▀█ ███ █▀█   ☰   ▞▚ █▀█ C ███ ▛▄ ▞▚   █ █▄▄   █▀█▀█ ███ █▀█▀█ ☰ █▀█ ▀█▀ ███ . . .')
            raise UnauthorizedAccess("You are not authorized to use this bot.") # Soluzione terribile, but it works...

async def manutenzione(update: Update) ->None:
    # infila await manutenzione(update)
    if update.callback_query:
        await update.callback_query.message.reply_text("⚠️🔧 Questa funzione è in manutenzione 🔧⚠️")
    elif update.message:
        await update.message.reply_text("⚠️🔧 Questa funzione è in manutenzione 🔧⚠️")
    else:
        print("No message or callback_query in update")

    raise UnauthorizedAccess("This function is being fixed.")

# ----------------------------------------------------------------- START COMMAND -----------------------------------------------------------------------------------
ROUTE_SELECTION, ADDING_TEAM = range(2)

def get_start_conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ROUTE_SELECTION: [CallbackQueryHandler(route_selection)],
            ADDING_TEAM: [CallbackQueryHandler(adding_team)]
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(filters.COMMAND, end_conversation),
            #MessageHandler(filters.ALL, end_conversation),
        ],
    )

async def curse_player(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cursed_replies = [
            "Ancora tu?! Uff...",
            "Daiii... di nuovo tu?",
            "Ancora qui? Non ti basta mai?",
            "Ma non ce la fai da solo?",
            "Non ti basta mai? Non hai amici?",
            "Proprio non riesci, eh?",
            "Non me lo hai già chiesto?",
            "Sei davvero così disperato?",
        ]
    cursed_stikers = [
                "CAACAgQAAxkBAAE2SQpoTVebbLxq92-_A3-6isFYSzINJAACHRAAAtMaIFJZzabuUDgjbTYE",
                "CAACAgQAAxkBAAE2SQxoTVeqkbq1rZE2mV-8H2c3np0PmgAC4QADgKNGBFpj3sLWH-PsNgQ",
                "CAACAgQAAxkBAAE2SRBoTVfqsadgQv9WYJ4CD1s2vTKS4wAC6g4AApX1MFGvnwdiJDE_EDYE",
                "CAACAgQAAxkBAAE2SRZoTVgZ9Hx9vle53mkjxagGV_PiPgACzgIAAuld0hQGV7PTLBbxhDYE",
                "CAACAgQAAxkBAAE2SSpoTVneOJpmvNpYYY3hb2zKONHWvQAC5QADgKNGBPPD-fs8i4h5NgQ",
                "CAACAgQAAxkBAAE2SSxoTVn1MxBdN87LQP35E_gPAcHcLQAC_QADgKNGBIqshWXCwam8NgQ",
                "CAACAgQAAxkBAAE2STRoTVounHt6Pl5w4v96xpKZ78cLIAACuwkAAg6_-FFqh7ktU56NZzYE",
                "CAACAgQAAxkBAAE2STZoTVo6DJy9k86xgrvUm6kis9rV9gACXQgAAs0T4VN2G8WyqVK6ozYE",
                "CAACAgQAAxkBAAE2SThoTVpI-VUQhGu0pkVEunOJ-9yXgQACpQoAAt1GoVIn2PM9ZiAkmzYE",
                "CAACAgQAAxkBAAE2STxoTVqSWKpJsgABZOMc_Cyqwo5emqkAAn4AA0tp7hATAAFh4WBoDl02BA",
                "CAACAgQAAxkBAAE2STpoTVqElBoxDdzAe3o3NfGHvrch9wACfQAEOuQGGu4twcvDFPs2BA"
            ]
    if random.random() > 0.95:
        await update.message.reply_text(random.choice(cursed_replies))
        await asyncio.sleep(1)
        if random.random() > 0.50:
            await update.message.reply_sticker(random.choice(cursed_stikers))
        await asyncio.sleep(1)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await id_check(update)

    #await curse_player(update, context) # Non lo metterei su start.

    try:
        print(update.effective_chat.username,' (',update.effective_chat.id,',',update.effective_user.first_name,') called /start')
    except:
        pass
    added = add_new_player(update) # IMPORTANTE, anche se non usiamo added
    user = update.effective_user

    replies = [
        "Ku ku ku... Siamo così disperati?",
        'Hi hi hi... Hai scelto il Pokémon giusto per vincere...',
        "Che le s̵̡͕̥̜̞̏̋͝t̶̙̤̑e̴̦̲̳̟̿̃̔̊̈́̋̄̽͜l̵͔͓͉̬̼̮̘̏̈́́̑̉̓͘̕ĺ̸̨̩̝͜͝e̴̬̤̭̫͖̿͛̀̏̅̓͛̐ tremino e l'o̶̻̫̼̒͋̃̀̿̈͜s̵̯̳̗̋͌͛͠c̸̳͂̌͌͘ͅư̵͙̣͑̐̇̀͝͝r̶͙̝̽i̸̛͙̥͈̠̔̋͋t̵̢̝̻̀̄à̶̫̀̓̄͐̑͌̕ risuoni...",
        'Ghihihihi... Pronti per una burla?',
        "Ku ku ku... Stai cercando guai?",
        "Hehehe... Chiedi e sarò il tuo aiutante misterioso!",
        "Ku ku ku... Non temere! S̵͕̒͋͜͜ä̴̧̻͔̟̪̥̞̼́̈́̈́̀̃b̶̡̤͉̍͂̏̒̽͛̚͘l̸͎̙̾͑e̶̫̺͕̻̐y̵̧̨̱͈̰̜͍͗̀̽̿̋e̶̢̙̥͋̈́ è qui...",
        "Vincere la Lega... che cliente ambizioso!",
    ]

    if user["username"]   != None:
        replies.append(f'{user["username"]}... che nome ridicolo... ma un cliente è un cliente...')
    if user["first_name"] != None:
        replies.append(f'Eheh... {user["first_name"]}, non sei in grado di vincere senza di me?')

    route = await check_route(str(update.effective_user.id))

    if route != None and route!= 'Non_detta':
        replies.append(f'Di nuovo qui, {user["username"]}?')
        if random.random() > 0.01:
            await update.message.reply_text(random.choice(replies))
        else:
            await update.message.reply_text('Non so davvero se dovrei aiutarti... lasciamolo decidere al caso, Croce!')
            await asyncio.sleep(2)
            await update.message.reply_text('🪙')
            await asyncio.sleep(3)
            await update.message.reply_text("P̷e̸c̶c̷a̷t̷o̴.̵.̵.̵ ̷C̵o̵s̷a̵ ̴d̴o̶v̷r̴e̴i̸ ̷f̸a̸r̴e̷ ̸c̶o̷n̴ ̷t̷e̷ ̴a̵d̷e̵s̵s̴o̴.̴.̶.̵")

    if route == None:
        text = "Benvenuto! Questa è la prima volta che ci incontriamo, no?\n\n" \
        f'Il mio nome è SableyeBot, e sono un Bot creato al solo scopo di aiutarti a vincere la Lega.\n' \
        'La mia esistenza oramai non è più un segreto, sentitene libero di parlare anche con altri giocatori! Ma veniamo al dunque...\n\n'\
        "Questo bot è costruito indipendentemente dal bot della Lega (qualunque nome esso abbia adesso...). Le informazioni che ha a disposizione sono tutte pubbliche.\n"\
        "Ciò significa che, per quanto mi riguarda, puoi rimpiazzarmi con un pezzo di carta e una matita. Ma non credo ti convenga...\n\n"\
        "Per informazioni sui comandi dei bot, dai uno sguardo al comando /help. Sono troppi per spiegarli tutti qui...\n\nIntanto, tieni a mente solo qualche cosa:\n\n"
        await update.message.reply_text(text)
        await asyncio.sleep(5)
        text = "Se il bot non risponde ad un comando, prova ad inviarlo di nuovo. Ogni tanto, potrebbe 'perdersi' qualche richiesta. O ignorarti di proposito... Ehehehe...\n\nIl bot potrebbe chiedere di aspettare un attimo... In quel caso, evita di scrivere comandi fin quando non manderà un altro messaggio."
        await update.message.reply_text(text)
        await asyncio.sleep(5)
        text = "Se il bot continua a non rispondere, potrebbe essere spento o bloccato. In quel caso, prova scriverlo sul gruppo per confrontarti. Gli sviluppatori provvederanno a fare qualcosa.\n\nAnche quando chiede di aspettare, solitamente si tratta di un minuto al massimo. Se dovesse non rispondere per più tempo, prova a ricominciare da capo."
        await update.message.reply_text(text)
        await asyncio.sleep(5)
        text = "Come ripetuto prima, il bot è indipendente dalla lega e le sue informazioni sono limitate. Controlla sempre quanto Sableye ti dice, non fidarti alla cieca. E se commette errori, o ci sono bug, puoi farlo presente sul gruppo ufficiale, ma se sbagli la colpa sarà tua..."
        await update.message.reply_text(text)
        await asyncio.sleep(5)
        text = "🎉🎉NOVITÀ🎉🎉 \n\n Sto imparando a leggere, quindi adesso, invece di usare il comando /team, puoi inviarmi direttamente il messaggio contentente la tua card... \n\nControlla sempre che quel che leggo ia corretto! Un ⚠️ accanto al nome significa che non ho capito bene qualcosa, ma non è detto che abbia sbagliato..."
        await update.message.reply_text(text)
        await asyncio.sleep(5)
        await add_route(str(update.effective_user.id), "Non_detta")
        keyboard = [
            [InlineKeyboardButton("Pari", callback_data='even'),
            InlineKeyboardButton("Dispari", callback_data='odd')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Quindi, bando alle ciance e iniziamo! Per prima cosa, dimmi il percorso su cui ti trovi",
            reply_markup=reply_markup
        )
        return ROUTE_SELECTION
    
    elif route == "Non_detta":
        keyboard = [
            [InlineKeyboardButton("Pari", callback_data='even'),
            InlineKeyboardButton("Dispari", callback_data='odd')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Prima mi hai ignorato... dimmi il tuo percorso... Guarda che altrimenti non posso funzionare per bene...",
            reply_markup=reply_markup
        )
        return ROUTE_SELECTION
    return ConversationHandler.END

async def route_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    route = query.data  # 'pari' or 'dispari'
    await add_route(str(update.effective_user.id), route)

    keyboard = [
            [InlineKeyboardButton("Sì", callback_data='add_team'),
             InlineKeyboardButton("No", callback_data='no_add_team')]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Grazie dell'informazione... Vuoi anche aggiungere subito la tua squadra?",reply_markup=reply_markup)
    return ADDING_TEAM


async def adding_team(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    add_ = query.data  # 'add_team' or 'no_add_team'

    if add_ == 'no_add_team':
        await query.edit_message_text("Va bene... Ricordati che potrai sempre farlo usando /team...")
    else:
        await team_command(update, context)
    return ConversationHandler.END

# ------------------------------------------------------- BONUS COMMAND -----------------------------------------------------------------------------------

BONUS_READ_POKEMONS = range(1)
BONUS_CHANGE_MULT = "change_mult"
BONUS_REDO_BONUS = "redo_bonus"
BONUS_MULT_PREFIX = "mult_"


def get_bonus_conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("bonus", bonus)],
        states={
            BONUS_READ_POKEMONS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, show_main_bonus_menu),
                MessageHandler(filters.COMMAND, end_conversation),
                CallbackQueryHandler(bonus_button_handler),
            ],
        },
        # Gestire i fallback così è terribile ma non riesco a fare di meglio...
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(filters.COMMAND, end_conversation),
            #MessageHandler(filters.ALL, end_conversation),
        ],
        allow_reentry = True
    )
async def bonus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await id_check(update)
    await curse_player(update, context)
    try:
        print(update.effective_chat.username,' (',update.effective_chat.id,',',update.effective_user.first_name,') called /bonus')
    except:
        pass
    context.user_data.clear()
    context.user_data['bonus_fallito'] = False
    context.user_data['first time'] = True
    await update.message.reply_text("""Uno contro uno, eh?... Dimmi un po' chi sono i due pokemon.\n\n Scrivi "Pokemon1 Pokemon2"...""")
    return BONUS_READ_POKEMONS

async def show_main_bonus_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    MULT = 20
    if  context.user_data.get('bonus_fallito') == True:      # Se ho già fallito a dire pokemon, rileggi
        context.user_data['moltiplicatore'] = MULT
        context.user_data['bonus_pokemon'] = update.message.text
    elif 'bonus_pokemon' not in context.user_data.keys():   # Se non sto cambiando moltiplicatore, leggi:
        context.user_data['moltiplicatore'] = MULT
        context.user_data['bonus_pokemon'] = update.message.text
    text = calculate_bonus_answer(context.user_data.get('bonus_pokemon'), context.user_data.get('moltiplicatore') )
    if text[0] == 'M': # Da fixare
        context.user_data['bonus_fallito'] = False
        keyboard = [
        [InlineKeyboardButton("Cambia Moltiplicatore", callback_data=BONUS_CHANGE_MULT)],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
        elif context.user_data['first time'] == True:
            context.user_data['first time'] = False
            await update.message.reply_text(text=text, reply_markup=reply_markup)
    else:
        context.user_data['bonus_fallito'] = True
        await update.message.reply_text(text)
        return BONUS_READ_POKEMONS

async def show_command_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # Create a 3x2 grid of numbers
    numbers = [5, 8, 11, 14, 17, 20]
    keyboard = [
        [InlineKeyboardButton(str(num), callback_data=f"{BONUS_MULT_PREFIX}{num}") for num in numbers[i:i+3]]
        for i in range(0, len(numbers), 3)
    ]

    # Add the "Indietro" button below the grid
    keyboard.append([InlineKeyboardButton("Indietro", callback_data=BONUS_REDO_BONUS)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Seleziona un moltiplicatore:", reply_markup=reply_markup)

async def bonus_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data.startswith(BONUS_MULT_PREFIX):
        # Extract the number from the callback data and update the multiplier
        selected_mult = int(query.data.split('_')[1])
        context.user_data['moltiplicatore'] = selected_mult
        # Immediately show the main bonus menu with the updated multiplier
        await show_main_bonus_menu(update, context)
    elif query.data == BONUS_CHANGE_MULT:
        await show_command_bonus(update, context)
    elif query.data == BONUS_REDO_BONUS:
        await show_main_bonus_menu(update, context)


# ----------------------------------------------------------------- HELP COMMAND -----------------------------------------------------------------------------------

# Define callback data
HELP_START = "help_start"
HELP_BONUS = "help_bonus"
HELP_BACK = "help_back"
HELP_LEGA = "help_lega"
HELP_GYM = "help_gym"
HELP_TEAM = "help_team"
HELP_ALTRO = "help_altro"
HELP_DEX = "help_dex"
HELP_CELL = "help_cell"
HELP_FIGHT = "help_fight"
HELP_HELP = "help_help"

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await id_check(update)
    try:
        print(update.effective_chat.username,' (',update.effective_chat.id,',',update.effective_user.first_name,') called /help')
    except:
        pass
    await show_main_help_menu(update, context)

async def show_main_help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("/start", callback_data=HELP_START)],
        [InlineKeyboardButton("/help", callback_data=HELP_HELP)],
        [InlineKeyboardButton("/fight", callback_data=HELP_FIGHT)],
        [InlineKeyboardButton("/team", callback_data=HELP_TEAM)],
        [InlineKeyboardButton("/bonus", callback_data=HELP_BONUS)],
        [InlineKeyboardButton("/gym", callback_data=HELP_GYM)],
        [InlineKeyboardButton("/lega", callback_data=HELP_LEGA)],
        [InlineKeyboardButton("/cell", callback_data=HELP_CELL)],
        [InlineKeyboardButton("/dex", callback_data=HELP_DEX)],
        [InlineKeyboardButton("Altro e FAQ", callback_data=HELP_ALTRO)],

    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = ("Ku ku ku ku... Benvenuto nel covo di Sableye... Dove tutto può essere realizzato! Al giusto prezzo ovviamente...\n\n Questo è tutto l'aiuto che puoi avere. Se non ti basta, non è un mio problema...")

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text=text, reply_markup=reply_markup)

async def show_command_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == HELP_START:
        text = "Il comando /start inizia la conversazione principale con Sableye\. ma se sei già qui non credo serva spiegartelo\."
    elif query.data == HELP_BONUS:
        text = "Il comando /bonus calcola i bonus nel combattimento tra due Pokémon\.\nQuando usi /bonus, ti verranno chiesti i Pokémon\.\n" \
        f'Per esempio, rispondigli "{random_pokemon()} {random_pokemon()}" per sapere chi la spunterebbe\.' \
        '\nIl moltiplicatore usato dipende dalla giornata, ma può essere cambiato seguendo le istruzioni\.\nE attento a non sbagliare i nomi\.'
    elif query.data == HELP_LEGA:
        text = "Il comando /lega da varie possibilità utili per combattimenti in endgame\." \
        """\n\nL'opzione "Migliori Pokémon" restituisce il matchup dei pokemon con 500\+ BST con loro stessi\. In pratica, mostra quanto ogni pokemon \(tra i più forti\)""" \
        " sia avvantaggiato o svantaggiato dal proprio typing\."
        text += """\n\n L'opzione "Team vs Team" è lo state\-of\-the\-art di una lega a carte scoperte\. Comunica la squadra che strai fronteggiando, e ti darà informazioni su come battere il tuo nemico\!"""
    elif query.data == HELP_GYM:
        text = """Il comando /gym ti permette di testare la tua squadra contro le varie palestre del gioco\. Puoi selezionare una palestra e fronteggiarla con la tua squadra\.\n\nAltrimenti, la funzione "Testa un Pokémon" ti permette di controllare la prestazione di un Pokémon contro varie palestre senza doverlo aggiungere al Team\. Geniale, no\?"""
    elif query.data == HELP_TEAM:
        text = "Il comando /team ti permette di creare e modificare a tuo piacimento la tua squadra, così da poterla testare contro palestre, selvatici, allenatori e altri giocatori\."
    elif query.data == HELP_DEX:
        r = random_pokemon()
        text =f'La sintassi del comando /dex è, per esempio, "/dex {r}"'
    elif query.data == HELP_FIGHT:
        text = "Il comando /fight ti permette di testare la tua squadra contro le prossime ostilità\." \
        """\n\nL'opzione "Selvatici" permette di mettere alla prova la tua squadra contro dei Pokémon della potenza pari alla prossima casella cattura \(nel caso ci si trovi su una, quella attuale\)\.""" \
        """\n\nL'opzione "Allenatore" permette di mettere alla prova la tua squadra contro i Pokémon di un allenatore dalla potenza pari alla prossima casella palestra \(nel caso ci si trovi su una, quella attuale\)\."""
    elif query.data == HELP_CELL:
        text = "Il comando /cell ti permette di verificare potenze e livelli dei Pokémon presenti nella casella Corrente, Prossima o tra x Caselle\."
    elif query.data == HELP_HELP:
        await query.edit_message_text(text="◉‿◉")
        for _ in range(random.randint(0,6)):
            chat_id = query.message.chat_id  # Get the chat ID to send the message to
            await context.bot.send_message(chat_id=chat_id, text="◉‿◉")
            await asyncio.sleep(1)
        keyboard = [[InlineKeyboardButton("Indietro", callback_data=HELP_BACK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat_id, text="◉‿◉", reply_markup=reply_markup)
    elif query.data == HELP_ALTRO:
        text = '"/cancel" è il comando per uscire da ogni funzione\. Se una funzione non si comporta come dovrebbe, prova ad inviare "/cancel" e ricominciare\.' \
        '\n\nSe il bot non risponde a nessun comando, non spammare\. Alcune funzioni sono lente, o è semplicemente spento\. \n\nSe incontri un bug, o una funzione non si comporta come dovrebbe, sentiti libero di comunicarlo agli sviluppatori\.' \
        '\n\nSableyeBot ha 3 comandi segreti\. Alcuni possono usarli solo chi voglio io\. Però magari ci sono delle sorprese\.\.\.'\
        "\n\n\n*FAQ*\n\n"\
        "*Q: Gli sviluppatori hanno accesso in chiaro alle informazioni della mia squadra?*\n*A:* Sì\n\n"\
        "*Q: Come si chiama Farfetch\'d?*\n*A:* Farfetchd\n\n"\
        "*Q: Come si chiama Mega Sableye? E Mega Sableye Y?*\n*A:* Sableye\-mega e Sableye\-mega\-y\n\n"

    else:
        text = "Cosa hai detto\? Non saresti dovuto finire qui\."

    keyboard = [[InlineKeyboardButton("Indietro", callback_data=HELP_BACK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if query.data != HELP_HELP:
        await query.edit_message_text(text=text, parse_mode='MarkdownV2', reply_markup=reply_markup)


async def help_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    if query.data in [HELP_START, HELP_BONUS, HELP_FIGHT, HELP_LEGA, HELP_GYM, HELP_TEAM, HELP_ALTRO, HELP_DEX, HELP_CELL,HELP_HELP]:
        await show_command_help(update, context)
    elif query.data == HELP_BACK:
        await show_main_help_menu(update, context)

# ------------------------------------------------------------------- EDGY ANSWER ----------------------------------------------------------------------------------

'''
async def edgy_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    await update.message.reply_text(f" Data: {type(user_data)}")

    if user_data == {}:
        await update.message.reply_text('Coglione che scrivi ' + str(update.message.text)+', mica è un comando')
    return ConversationHandler.END

def get_edgy_answer():
    return ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, edgy_answer)],
        states={},
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(filters.COMMAND, end_conversation),
        ],
        per_message = False
    )
'''

# ---------------------------------------------------------------------- GYM ------------------------------------------------------------------

POKEMON_TYPES = [
    "Rock", "Fighting", "Dark", "Electric", "Fairy", "Grass",
    "Normal", "Fire", "Bug", "Flying", "Ghost", "Ice",
    "Ground", "Poison", "Psychic", "Water", "Steel", "Dragon"
]

CHOOSING_POKEMON_GYM, CHOOSING_GYM_COUNT, CHOOSING_CUSTOM_GYM_COUNT = range(3)

async def gym(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await id_check(update)
    await curse_player(update, context)
    try:
        print(update.effective_chat.username,' (',update.effective_chat.id,',',update.effective_user.first_name,') called /gym')
    except:
        pass

    chat_id=str(update.effective_chat.id)
    if has_a_team(chat_id):

        keyboard = [
            [InlineKeyboardButton(type, callback_data=f"gym_{type.lower()}") for type in POKEMON_TYPES[i:i+3]]
            for i in range(0, len(POKEMON_TYPES), 3)
        ]
        row = [
                    InlineKeyboardButton("Testa un Pokémon",callback_data="gym_test")
        ]
        keyboard.append(row)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Scegli che palestra affrontare.", reply_markup=reply_markup)

    else:
        if random.random()>0.05:
            await update.message.reply_text("Non hai un team... come pensi di battere una palestra!")
        else:
            await update.message.reply_text("Che cazzo mi chiedi la palestra se non so che Pokémon hai.")

async def gym_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "gym_test":
        await manutenzione(update)  # fixa con nuove palestre per tipo
        await query.edit_message_text("Dimmi un Pokémon e il suo livello...\n\nScrivi \"Pokémon Livello\".\n\nPuoi inserire livello 0 per ottenre una valutazione dei soli bonus.")
        return CHOOSING_POKEMON_GYM
    else:
        # Rest of your existing code for handling other gym types
        gym_type = query.data.split('_')[1]
        chat_id = update.effective_chat.id
        with open(ENV_PATH+'/gym_data.json', 'r') as file:
            gym_data = json.load(file)
        enemy_powers = gym_data[gym_type]["power"]
        temp_multi   = gym_data[gym_type]["multiplier"]
        await query.edit_message_text(f"Il moltiplicatore della palestra sarà {temp_multi}\n\nAttendi per la foto...")
        # Call the poke_gym function
        image_path = poke_gym(str(chat_id), gym_type)
        # Open the image file
        cap = f"Ecco il risultato del tuo team contro la palestra {gym_type.capitalize()}.\n\n🔴: batte la fascia bassa ({enemy_powers[0]})\n🟡: batte la fascia media ({enemy_powers[2]})\n🟢: batte la fascia alta ({enemy_powers[4]})"
        with open(image_path, 'rb') as image_file:
            # Send a new message with the image
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=image_file,
                caption=cap
            )
        return ConversationHandler.END

async def choose_pokemon_gym(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pokemon_name = update.message.text.strip().capitalize()
    #print('Pokémon received:', pokemon_name)
    if " " not in pokemon_name:
        if poke_exist(pokemon_name):
            await update.message.reply_text("Assumerò il livello sia 0...")
            pokemon_name += ' 0'
        else:
            await update.message.reply_text("Ignori le istruzioni, e sbagli pure a scrivere il Pokémon? Riprova.")
            return CHOOSING_POKEMON_GYM
    if poke_exist(pokemon_name.split(" ")[0]):
        context.user_data['test_pokemon'] = pokemon_name
        keyboard = [
            [InlineKeyboardButton("Bastano 4", callback_data="gggg_test_4")],
            [InlineKeyboardButton("Decido io", callback_data="gggg_test_custom")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Vuoi decidere quante palestre nel futuro vedere? O bastano 4?",
            reply_markup=reply_markup
        )
        return CHOOSING_GYM_COUNT
    else:
        await update.message.reply_text("Non conosco questo Pokémon... Riprova.")
        return CHOOSING_POKEMON_GYM

async def handle_gym_count_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    pokemon_name,livello = context.user_data.get('test_pokemon').split(" ")

    if query.data == "gggg_test_4":
        await query.edit_message_text("Attendi il prossimo messaggio...")
        chat_id = query.message.chat_id
        result = poke_gym_test(str(chat_id),pokemon_name,int(livello), 4)
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Ecco i risultati per {pokemon_name} al {livello}\n(4 palestre future):\n\n{format_gym_test(result)}"
        )
        #await update.message.reply_text(f"Ecco i risultati per {pokemon_name} al {livello}\n(4 palestre future):\n\n{format_gym_test(result)}")

        return ConversationHandler.END
    elif query.data == "gggg_test_custom":
        await query.edit_message_text("Quante palestre future vuoi vedere? Inserisci un numero.")
        return CHOOSING_CUSTOM_GYM_COUNT

    return ConversationHandler.END

async def handle_custom_gym_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        gym_count = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Pensi di essere divertente?")
        return CHOOSING_CUSTOM_GYM_COUNT
    if gym_count <= 0:
        await update.message.reply_text("Ho detto nel futuro...")
        return CHOOSING_CUSTOM_GYM_COUNT

    await update.message.reply_text("Attendi il prossimo messaggio...")
    pokemon_name,livello = context.user_data.get('test_pokemon').split(" ")
    chat_id = update.effective_chat.id
    result = poke_gym_test(str(chat_id),pokemon_name,int(livello), int(gym_count))
    await update.message.reply_text(f"Ecco i risultati per {pokemon_name} al {livello}\n({gym_count} palestre future):\n\n{format_gym_test(result)}")
    return ConversationHandler.END


def get_gym_test_conversation_handler():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(gym_button, pattern='^gym_')],
        states={
            CHOOSING_POKEMON_GYM: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_pokemon_gym)],
            CHOOSING_GYM_COUNT: [CallbackQueryHandler(handle_gym_count_choice)],
            CHOOSING_CUSTOM_GYM_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_gym_count)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(filters.COMMAND, end_conversation),
        ],
        allow_reentry=True
    )

def format_gym_test(result):
    message = ''
    for p in result:
        text = f"- {p[0].capitalize()}: ~: {p[1]} >: {p[2]} <: {p[3]}"
        if len(p)!=4:
            if p[8]!=0:
                text += f" (+{p[8]} lvl.)"
            text += f"\n⬜: {p[4]}, 🟥: {p[5]}, 🟨: {p[6]}, 🟩: {p[7]}"
        text+= "\n"
        message+=text
    return message

# ---------------------------------------------------------------------- TEAM ----------------------------------------------------------

CONFIRM_EDIT, CHOOSING_POKEMON, CHOOSING_LEVEL = range(3)

def change_secret_player_data_team(update: Update, index, pl, new_value): # index is the pokemon index (0-9), pl is 0-1 (0 = pokemon, 1 = livello)

    with open(ENV_PATH+'/secret_player_data.json', 'r') as file:
        data = json.load(file)

    data[str(update.effective_user.id)]["team"][index][pl] = new_value

    ## Save our changes to JSON file
    jsonFile = open(ENV_PATH+"/secret_player_data.json", "w+")
    jsonFile.write(json.dumps(data))
    jsonFile.close()

async def team_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await id_check(update)
    await curse_player(update, context)
    try:
        print(update.effective_chat.username,' (',update.effective_chat.id,',',update.effective_user.first_name,') called /team')
    except:
        pass
    chat_id = update.effective_chat.id
    with open(ENV_PATH+'/secret_player_data.json', 'r') as file:
        data = json.load(file)
        current_team = data[str(chat_id)]["team"]
    keyboard = create_team_keyboard(current_team)
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(text="Ecco qui il messaggio per modificare il tuo team... Ricorda che lo puoi sempre chiamare usando /team", reply_markup=reply_markup)
    else:
        await update.message.reply_text(text="Questo è il tuo team... Non male.", reply_markup=reply_markup)

        #await update.message.reply_text("Questo è il tuo team... Non male.", reply_markup=reply_markup)

def create_team_keyboard(team):
    keyboard = []
    for i, pokemon in enumerate(team):
        row = []
        if pokemon[0] is not None:
            row.append(InlineKeyboardButton("➖", callback_data=f"team_minus_{i}"))
            row.append(InlineKeyboardButton(f"Lv.{pokemon[1]} {pokemon[0]}", callback_data=f"team_info_{i}"))
            row.append(InlineKeyboardButton("➕", callback_data=f"team_plus_{i}"))
            #keyboard.append(row)
        else:
            row = [
                InlineKeyboardButton("❌", callback_data=f"team_nolevel_{i}"),
                InlineKeyboardButton("🆕", callback_data=f"team_empty_{i}"),
                InlineKeyboardButton("❌", callback_data=f"team_nolevel_{i}")
            ]
        keyboard.append(row)
    row = [InlineKeyboardButton("Chiudi", callback_data="team_end_0")]
    keyboard.append(row)
    return keyboard

async def choose_pokemon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pokemon_name = update.message.text
    if poke_exist(pokemon_name) == True:
        index = context.user_data['editing_index']
        #current_team[index][0] = pokemon_name
        change_secret_player_data_team(update, index, 0, pokemon_name)
        await update.message.reply_text(f"Quindi il tuo nuovo Pokémon è {pokemon_name}... A che livello?")
        return CHOOSING_LEVEL
    else:
        await update.message.reply_text("Non conosco questo Pokémon... Riprova.")
        return CHOOSING_POKEMON

async def choose_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        level = int(update.message.text)
        if level < 1 or level > 100:
            raise ValueError
        index = context.user_data['editing_index']
        #current_team[index][1] = level
        change_secret_player_data_team(update, index, 1, level)
        await update.message.reply_text(f"Capito, capito... Livello {level}.")

        # Read updated team to show
        chat_id = update.effective_chat.id
        with open(ENV_PATH+'/secret_player_data.json', 'r') as file:
            data = json.load(file)
            current_team = data[str(chat_id)]["team"]

        keyboard = create_team_keyboard(current_team)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Questo è il tuo team aggiornato...", reply_markup=reply_markup)

        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("... Riprova.")
        return CHOOSING_LEVEL

async def team_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    action, index = query.data.split('_')[1], int(query.data.split('_')[2])

    # Qui ci stanno un botto di cambi di valori. Quindi modifico direttamente il file. Brutto ma chissene...
    if action in ['minus', 'plus']:

        with open(ENV_PATH+'/secret_player_data.json', 'r') as file:
            data = json.load(file)

        current_team = data[str(update.effective_user.id)]["team"]

        if current_team[index][0] is not None:
            if action == 'minus' and current_team[index][1] > 1:
                current_team[index][1] -= 1
                # Recreate the keyboard with updated information
                current_team[index][0] = await poke_check_if_evo(str(update.effective_user.id),current_team[index][0],current_team[index][1])
                keyboard = create_team_keyboard(current_team)
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_reply_markup(reply_markup=reply_markup)
            elif action == 'plus' and current_team[index][1] < 100:
                current_team[index][1] += 1
                # Recreate the keyboard with updated information
                current_team[index][0] = await poke_check_if_evo(str(update.effective_user.id),current_team[index][0],current_team[index][1])
                keyboard = create_team_keyboard(current_team)
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_reply_markup(reply_markup=reply_markup)

        data[str(update.effective_user.id)]["team"] = current_team
        ## Save our changes to JSON file
        jsonFile = open(ENV_PATH+"/secret_player_data.json", "w+")
        jsonFile.write(json.dumps(data))
        jsonFile.close()

    elif action == 'info' or action == 'empty':
        context.user_data['editing_index'] = index
        keyboard = [
            [
                InlineKeyboardButton("Sì", callback_data="edit_confirm_yes"),
                InlineKeyboardButton("No", callback_data="edit_confirm_no")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Vuoi modificare questo Pokémon?", reply_markup=reply_markup)
        return CONFIRM_EDIT
    elif action == 'nolevel':
        # Do nothing for "No level" buttons
        pass
    elif action == 'end':
        await query.edit_message_text("Squadra modificata con successo!")
    return ConversationHandler.END

async def confirm_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "edit_confirm_yes":
        await query.edit_message_text("Dimmi il nome del Pokémon:")
        return CHOOSING_POKEMON
    elif query.data == "edit_confirm_no":
        # Read the current team data
        chat_id = update.effective_chat.id
        with open(ENV_PATH+'/secret_player_data.json', 'r') as file:
            data = json.load(file)
            current_team = data[str(chat_id)]["team"]

        # Create the team keyboard
        keyboard = create_team_keyboard(current_team)
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Edit the message to show the team again
        await query.edit_message_text("Questo è il tuo team.", reply_markup=reply_markup)

        return ConversationHandler.END

def get_team_conversation_handler():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(team_button, pattern="^team_")],
        states={
            CONFIRM_EDIT: [CallbackQueryHandler(confirm_edit, pattern="^edit_confirm_")],
            CHOOSING_POKEMON: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_pokemon)],
            CHOOSING_LEVEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_level)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(filters.COMMAND, end_conversation),
            #MessageHandler(filters.ALL, end_conversation),
        ],
    )

# ----------------------------------------------------------------------- PING_ALL -----------------------------------------------------------------

WAITING_FOR_MESSAGE = 1

def get_ping_all_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("ping_all", ping_all_start)],
        states={
            WAITING_FOR_MESSAGE: [MessageHandler(filters.ALL & ~filters.COMMAND, send_ping_all)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(filters.COMMAND, end_conversation),
            #MessageHandler(filters.ALL, end_conversation),
        ]
    )

async def ping_all_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await id_check(update)
    try:
        print(update.effective_chat.username,' (',update.effective_chat.id,',',update.effective_user.first_name,') called /ping_all')
    except:
        pass
    chat_id = update.effective_chat.id
    if whitelist(chat_id):
        await update.message.reply_text("Dimmi quale messaggio vuoi inviare a tutte le chats...")
        return WAITING_FOR_MESSAGE
    else:
        await update.message.reply_text("Ehehehe... Ma chi ti credi di essere...")
        return ConversationHandler.END

async def send_ping_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #bot = Bot(token="7119226556:AAErwxsF7x0rksunnoKp3_ItLcQPfQdlqlM")
    with open(ENV_PATH+'/secret_player_data.json', 'r') as file:
        accounts = json.load(file)
        if update.message.text:
            content = update.message.text
            for idd in accounts.keys():
                try:
                    await context.bot.send_message(chat_id=idd, text = content)
                except:
                    print(f'ping_all to id : {idd} failed. (Probably no chat existing with the bot)')
        elif update.message.photo:
            content = update.message.photo[-1].file_id  # Get the largest photo
            for idd in accounts.keys():
                try:
                    await context.bot.send_photo(chat_id=idd, photo=content)
                except:
                    print(f'ping_all to id : {idd} failed. (Probably no chat existing with the bot)')
        elif update.message.document:
            content = update.message.document.file_id
            for idd in accounts.keys():
                try:
                    await context.bot.send_document(chat_id=idd, document=content)
                except:
                    print(f'ping_all to id : {idd} failed. (Probably no chat existing with the bot)')
        elif update.message.audio:
            content = update.message.audio.file_id
            for idd in accounts.keys():
                try:
                    await context.bot.send_audio(chat_id=idd, audio=content) # File audio, non messaggi audio
                except:
                    print(f'ping_all to id : {idd} failed. (Probably no chat existing with the bot)')
        elif update.message.video:
            content = update.message.video.file_id
            for idd in accounts.keys():
                try:
                    await context.bot.send_video(chat_id=idd, video=content)
                except:
                    print(f'ping_all to id : {idd} failed. (Probably no chat existing with the bot)')
        else:
            await update.message.reply_text("Nah... Questo non lo posso inviare... Per adesso...")
    return ConversationHandler.END



# ----------------------------------------------------------------------- SPY -----------------------------------------------------------------

async def spy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await id_check(update)
    try:
        print(update.effective_chat.username,' (',update.effective_chat.id,',',update.effective_user.first_name,') called /spy')
    except:
        pass
    chat_id = update.effective_chat.id
    if whitelist(chat_id):
        with open(ENV_PATH+'/secret_player_data.json', 'r') as file:
            accounts = json.load(file)
            for id in accounts.keys():
                await update.message.reply_text(f'Id: {id}, username: {accounts[id]["username"]}, first_name: {accounts[id]["first_name"]}')
    else:
        text = "*Terms of Service di SableyeBot*\n\n" \
            "Benvenuti nei Termini di Servizio per l'utilizzo di SableyeBot. Utilizzando il Bot, l'utente accetta di essere vincolato dai presenti Termini. Se non accetti questi Termini, ti preghiamo di non utilizzare il Bot.\n" \
            "\n\n*1. Descrizione del Servizio*\n" \
            "SableyeBot offre informazioni e consigli sul gioco. Il Bot include comandi che gli utenti possono utilizzare per ricevere suggerimenti, strategie e altre informazioni utili.\n" \
            "\n\n*2. Uso Accettabile*\n" \
            "Gli utenti devono utilizzare il Bot solo per scopi leciti e conformi ai presenti Termini." \
            "Gli utenti non possono utilizzare il Bot in modo da disturbare altri utenti, inviare contenuti offensivi, o in violazione delle leggi applicabili." \
            """Il comando "spy" è riservato esclusivamente ai proprietari del Bot e consente di monitorare l'attività degli utenti. L'uso di questo comando è soggetto a restrizioni e linee guida interne ai proprietari, che si impegnano a rispettare la privacy degli utenti.\n""" \
            "\n\n*3. Privacy*\n" \
            "SableyeBot raccoglie attivamente informazioni personali identificabili dagli utenti. Informazioni come username e ID possono essere visibili ai proprietari del Bot." \
            """L'uso del comando "spy" consente ai proprietari di vedere l'attività degli utenti all'interno del Bot. Questa funzionalità è utilizzata esclusivamente per migliorare il servizio e monitorare l'uso del Bot, nel rispetto della privacy degli utenti.\n""" \
            "\n\n*4. Limitazioni di Responsabilità*\n" \
            """SableyeBot è fornito "così com'è", senza garanzie di alcun tipo. Non garantiamo che il Bot sia privo di errori o interruzioni.""" \
            "I proprietari di Sableye Bot non sono responsabili per eventuali danni diretti o indiretti derivanti dall'uso del Bot." \
            "\n\n*5. Modifiche ai Termini*\n" \
            "Ci riserviamo il diritto di modificare questi Termini in qualsiasi momento. Gli utenti saranno informati di eventuali modifiche importanti, e l'uso continuato del Bot dopo la pubblicazione delle modifiche costituirà accettazione delle stesse.\n" \
            "\n\n*6. Risoluzione*\n" \
            "I proprietari si riservano il diritto di sospendere o terminare l'accesso al Bot per qualsiasi utente che violi questi Termini." \
            "\n\n*7. Contatti*\n" \
            "Per qualsiasi domanda riguardante questi Termini, si prega di contattare i proprietari del Bot direttamente su Telegram."
        text = text.replace(".", "\.").replace("-", "\-").replace("!", "\!")
        await update.message.reply_text(text, parse_mode='MarkdownV2')



# ----------------------------------------------------------------------- DEX ----------------------------------------------------------------

async def dex_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await id_check(update)
    await curse_player(update, context)
    try:
        print(update.effective_chat.username,' (',update.effective_chat.id,',',update.effective_user.first_name,') called /dex')
    except:
        pass
    if not context.args:
        await update.message.reply_text("Devi specificare un Pokémon... guarda /help...")
        return

    pokemon_name = ' '.join(context.args)
    dex_entry = poke_dex2(pokemon_name)
    await update.message.reply_text(dex_entry)
    dex_entry = poke_dex1(pokemon_name)
    await update.message.reply_text(dex_entry)


# -------------------------------------------------------------------------- CELL --------------------------------------------------------

WAITING_FOR_X = 0

async def cell_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await id_check(update)
    await curse_player(update, context)
    try:
        print(update.effective_chat.username,' (',update.effective_chat.id,',',update.effective_user.first_name,') called /cell')
    except:
        pass
    keyboard = [
        [InlineKeyboardButton("Corrente", callback_data="cell_current")],
        [InlineKeyboardButton("Prossima", callback_data="cell_next")],
        [InlineKeyboardButton('Tra "x" caselle', callback_data="cell_custom")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Scegli la cella", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "cell_current":
        content = poke_cell(0)
        if content == None:
            text = "Non siamo più su una casella..."
        else:
            text = ''
            if content[0] == True:
                text += 'La casella di oggi è una palestra.\n\n'
                text+= f'La potenza degli scontri di oggi è {content[1]}.\n\n'
                text+= f'La potenza del capopalestra di oggi è {content[2]}.'
            else:
                text+= f'La potenza degli scontri di oggi è {content[1]}.\n\n'
                text+= f'La potenza del boss di oggi è {content[2]}.'
        await query.edit_message_text(text)
    elif query.data == "cell_next":
        content = poke_cell(1)
        if content == None:
            text = "Non ci sono prossime caselle."
        else:
            text = ''
            if content[0] == True:
                text += 'La prossima casella è una palestra.\n\n'
                text+= f'La potenza degli scontri della prossima casella è {content[1]}.\n\n'
                text+= f'La potenza dei Pokémon del capopalestra della prossima casella è {content[2]}.'
            else:
                text+= f'La potenza dei selvatici della prossima casella è {content[1]}.\n\n'
                text+= f'Il livello dei pokemon selvatici sara {int(content[3])-1} o {int(content[3])+1}.\n\n'
                text+= f'La potenza del boss della prossima casella sarà tra {content[2][0]} e {content[2][1]}. Se il boss è un leggendario di copertina, la sua potenza sarà {content[2][2]}'
        await query.edit_message_text(text)
    elif query.data == "cell_custom":
        await query.edit_message_text('Dimmi "x"')
        return WAITING_FOR_X

async def get_custom_x(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        x = int(update.message.text)
        if x > 0:
            content = poke_cell(x)
            if content == None:
                text = """Non c'è nessuna casella così avanti. Dimmi un altro "x" """
                await update.message.reply_text(text)
                return WAITING_FOR_X
            else:
                text = ''
                if content[0] == True:
                    text += f'La casella tra {x} è una palestra.\n\n'
                    text+= f'La potenza degli scontri della casella tra {x} è {content[1]}.\n\n'
                    text+= f'La potenza del capopalestra della casella tra {x} è {content[2]}.'
                else:
                    text+= f'La potenza dei selvatici della casella tra {x} è {content[1]}.\n\n'
                    text+= f'Il livello dei pokemon selvatici sara {int(content[3])-1} o {int(content[3])+1}.\n\n'
                    text+= f'La potenza del boss della casella tra {x} è {content[2]}. Se il boss è un leggendario di copertina, la sua potenza sarà {content[2][2]}'
                await update.message.reply_text(text)
                return ConversationHandler.END
        else:
            await update.message.reply_text('Non posso guardare alle caselle passate. Dimmi un altro "x"')
            return WAITING_FOR_X
    except ValueError:
        await update.message.reply_text("""Valgono solo "x" numerici. Dimmi un altro "x" """)
        return WAITING_FOR_X

def get_cell_handlers():
    cell_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_callback, pattern="^cell_")],
        states={
            WAITING_FOR_X: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_custom_x)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(filters.COMMAND, end_conversation),
            #MessageHandler(filters.ALL, end_conversation),
        ],
    )

    return [
        CommandHandler("cell", cell_command),
        cell_conv_handler,
    ]

# ---------------------------------------------------------------------------- LEGA ----------------------------------------------------------------------------------

READ_POKEMON, READ_TRAINER, COUNTER_READ_POKEMON, READ_LEGA_TEAM = range(4)

# Define callback data
BEST_POKEMON = 'best_pokemon'
ONE_VS_TEAM = 'one_vs_team'
LEGA_COUNTERS = 'lega_counters'
LEGA_TEAM_VS_TEAM = 'lega_team_vs_team'
CHANGE_MULT = "change_mult"
REDO_LEGA_SINGLE = "redo_lega"
MULT_PREFIX = "mult_"
CHANGE_POKEMON = "change_pokemon"

async def lega_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await id_check(update)
    await curse_player(update, context)
    try:
        print(update.effective_chat.username,' (',update.effective_chat.id,',',update.effective_user.first_name,') called /lega')
    except:
        pass
    keyboard = [
        [InlineKeyboardButton("I Migliori Pokèmon", callback_data=BEST_POKEMON)],
        [InlineKeyboardButton("Counters", callback_data=LEGA_COUNTERS)],
        #[InlineKeyboardButton("1 vs Team", callback_data=ONE_VS_TEAM)],
        [InlineKeyboardButton("Team vs Team", callback_data=LEGA_TEAM_VS_TEAM)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Scegli cosa calcolare:", reply_markup=reply_markup)

async def lega_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    if query.data == BEST_POKEMON:
        await manutenzione(update)
        await query.edit_message_text("Attendi il prossimo messaggio...")
        text = poke_lega_all(20)
        #await query.edit_message_text(text)
        text = text.replace(".", "\\.").replace("-", "\\-").replace("!", "\\!")
        await query.edit_message_text(text=text, parse_mode='MarkdownV2')
    elif query.data == ONE_VS_TEAM:
        await query.edit_message_text("Dimmi il nome di un allenatore della lega...")
        context.user_data.clear()
        context.user_data['lega_single_fallito'] = False
        context.user_data['first time'] = True
        return READ_TRAINER
    elif query.data == LEGA_COUNTERS:
        await manutenzione(update)
        await query.edit_message_text("Di quale Pokémon vuoi conoscere i counter?")
        context.user_data.clear()
        return COUNTER_READ_POKEMON
    elif query.data == LEGA_TEAM_VS_TEAM:
        text = 'Dimmi una lista di pokemon (coi livelli). La struttura deve essere come nel seguente esempio:\n'
        for i in range(random.randint(3, 9)):
            text += f'\n{random_pokemon()} {random.randint(1, 101)}'
        await query.edit_message_text(text)
        context.user_data.clear()
        return READ_LEGA_TEAM

async def lega_single_get_trainer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['enemy_trainer'] = update.message.text
    with open(ENV_PATH+'/public_player_data.json', 'r') as file:
        enemies = json.load(file)
    if context.user_data['enemy_trainer'] in enemies.keys():
        await update.message.reply_text("Dimmi un Pokémon e un livello.\n\nScrivi \"Pokémon Livello\"... ")
        return READ_POKEMON
    else:
        await update.message.reply_text("Non lo conosco! Riprova.")
        return READ_TRAINER

async def show_main_lega_single_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('lega_single_fallito') == True:
        context.user_data['moltiplicatore'] = 20
        context.user_data['lega_single_pokemon'] = update.message.text
    elif 'lega_single_pokemon' not in context.user_data.keys():
        context.user_data['moltiplicatore'] = 20
        context.user_data['lega_single_pokemon'] = update.message.text
    text = poke_lega_single(context.user_data.get('lega_single_pokemon'), context.user_data.get('enemy_trainer'), context.user_data.get('moltiplicatore'))

    if text[0] == 'T':  # Da fixare
        context.user_data['lega_single_fallito'] = False
        keyboard = [
            [InlineKeyboardButton("Cambia Moltiplicatore", callback_data=CHANGE_MULT)],
            [InlineKeyboardButton("Cambia Pokemon", callback_data=CHANGE_POKEMON)],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
        elif context.user_data['first time'] == True:
            context.user_data['first time'] = False
            await update.message.reply_text(text=text, reply_markup=reply_markup)
    else:
        context.user_data['lega_single_fallito'] = True
        await update.message.reply_text(text)
        return READ_POKEMON

async def counter_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    context.user_data['counter_pokemon'] = update.message.text

    if poke_exist(context.user_data['counter_pokemon']) == False:
        await update.message.reply_text(f"Mh... Sei sicuro {context.user_data['counter_pokemon']} esista? Prova a ridirmelo...")
        return COUNTER_READ_POKEMON

    await update.message.reply_text('Il messaggio si legge come:\nPokémon avversario\n(Bonus)\nBST\nCheck se può batterti\nLivello a cui può batterti\n\nAttendi il prossimo messaggio...')
    try:
        content = poke_counter(context.user_data['counter_pokemon'])

        text = f"I counters di {context.user_data['counter_pokemon']} sono:\n\n"
        for c in content:
            if random.random()<0.02 and c[1] == 120:
                text +='Totti (+120) 680 BST ✅ [82]\n'
            if random.random()<0.02 and c[1] == 80:
                text +='Batistuta (+80) 600 BST ✅ [95]\n'
            if random.random()<0.02 and c[1] == 80:
                text +='Montella (+80) 560 BST ❌\n'
            p = ''
            if c[1]>0:
                p='+'
            if c[3] == True:
                    text +=f'{c[0]} ({p}{c[1]}) {c[2]} BST ✅ [{c[4]}]\n'
            else:
                text +=f'{c[0]} ({p}{c[1]}) {c[2]} BST ❌\n'

        await update.message.reply_text(text=text)
    except:
        await update.message.reply_text(text='Qualcosa è andato storto con poke_counters...')
        return ConversationHandler.END


def parse_pokemon_message(message):
    parts = message.strip().split()  # Split message by any whitespace
    pokemon_list = []

    # Loop through the message with a step of 2 (name, level pairs)
    for i in range(0, len(parts), 2):
        name = parts[i]  # Pokémon name
        level = int(parts[i + 1])  # Pokémon level, converted to an integer
        pokemon_list.append([name, level])  # Add to the list

    return pokemon_list

async def lega_team_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    context.user_data['counter_team'] = parse_pokemon_message(update.message.text)

    for pokeee,liv in context.user_data['counter_team']:
        if poke_exist(pokeee) == False:
            await update.message.reply_text(f'Mh... Sei sicuro {pokeee} esista? Prova a ripetermi la lista...')
            return READ_LEGA_TEAM

    await update.message.reply_text('Buona fortuna per lo scontro. E attendi il prossimo messaggio...')

    #TEST PART
    #print('OK', context.user_data['counter_team'])
    chat_id = update.effective_chat.id

    image_path = poke_lega_team_team(str(chat_id), context.user_data['counter_team'])
    
    # Open the image file
    cap = "Ecco il risultato del tuo team contro la squadra che mi hai inviato"
    with open(image_path, 'rb') as image_file:
        # Send a new message with the image
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=image_file,
            caption=cap
        )
    return ConversationHandler.END
    # END TEST
    """
    try:
        #print('OK', context.user_data['counter_team'])
        chat_id = update.effective_chat.id

        image_path = poke_lega_team_team(str(chat_id), context.user_data['counter_team'])
        # Open the image file
        cap = "Ecco il risultato del tuo team contro la squadra avversaria inserita"
        with open(image_path, 'rb') as image_file:
            # Send a new message with the image
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=image_file,
                caption=cap
            )
        return ConversationHandler.END
    except:
        await update.message.reply_text(text='Qualcosa è andato storto con poke_lega_team_vs_team...')
        return ConversationHandler.END
    """

async def show_command_lega_single(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    numbers = [5, 8, 11, 14, 17, 20]
    keyboard = [
        [InlineKeyboardButton(str(num), callback_data=f"{MULT_PREFIX}{num}") for num in numbers[i:i+3]]
        for i in range(0, len(numbers), 3)
    ]
    keyboard.append([InlineKeyboardButton("Indietro", callback_data=REDO_LEGA_SINGLE)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Seleziona un moltiplicatore:", reply_markup=reply_markup)

async def lega_single_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data.startswith(MULT_PREFIX):
        selected_mult = int(query.data.split('_')[1])
        context.user_data['moltiplicatore'] = selected_mult
        await show_main_lega_single_menu(update, context)
    elif query.data == CHANGE_MULT:
        await show_command_lega_single(update, context)
    elif query.data == CHANGE_POKEMON:
        context.user_data['first time'] = True
        del context.user_data['lega_single_pokemon']
        await query.edit_message_text("Dimmi un altro Pokémon.\n\nScrivi \"Pokémon Livello\"... ")
        return READ_POKEMON
    elif query.data == REDO_LEGA_SINGLE:
        await show_main_lega_single_menu(update, context)

def get_lega_conversation_handler():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(lega_button_callback, pattern=f"^{BEST_POKEMON}|{LEGA_COUNTERS}|{ONE_VS_TEAM}|{LEGA_TEAM_VS_TEAM}$")],
        states={
            READ_TRAINER: [MessageHandler(filters.TEXT & ~filters.COMMAND, lega_single_get_trainer)],
            READ_POKEMON: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, show_main_lega_single_menu),
                CallbackQueryHandler(lega_single_button_handler),
            ],
            COUNTER_READ_POKEMON: [MessageHandler(filters.TEXT & ~filters.COMMAND, counter_main)],
            READ_LEGA_TEAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, lega_team_main)]
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(filters.COMMAND, end_conversation),
            #MessageHandler(filters.ALL, end_conversation),
        ],
        allow_reentry=True
    )

# ----------------------------------------------------------------------------- FIGHT --------------------------------------------------------------
CHOOSE_FIGHT_TYPE, ENTER_POKEMONS = range(2)
WILD = 'wild'
TRAINER = 'trainer'

async def fight_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await id_check(update)
    await curse_player(update, context)
    try:
        print(update.effective_chat.username,' (',update.effective_chat.id,',',update.effective_user.first_name,') called /fight')
    except:
        pass

    chat_id=str(update.effective_chat.id)
    if has_a_team(chat_id):

        keyboard = [
            [InlineKeyboardButton("Selvatici", callback_data=WILD)],
            [InlineKeyboardButton("Allenatore", callback_data=TRAINER)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Dimmi il tipo di incontro", reply_markup=reply_markup)
        return CHOOSE_FIGHT_TYPE
    else:
        if random.random()>0.05:
            await update.message.reply_text("Non hai un team... contro chi pensi di combattere!")
        else:
            await update.message.reply_text("Che cazzo mi chiedi di combattere se non so che Pokémon hai.")


async def fight_type_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data['fight_type'] = query.data
    await query.edit_message_text("Inserisci una lista di Pokémon:")
    return ENTER_POKEMONS

async def enter_pokemons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    poke_list = message_text.split()
    for p in poke_list:
        if poke_exist(p) == False:
            await update.message.reply_text(f'Mhh... Non mi risulta nessun "{p}"... Riprova a dirmi la lista.')
            return ENTER_POKEMONS

    # Call the poke_Fight function
    await update.message.reply_text("Attendi un attimo per l'immagine...")
    try:
        if context.user_data['fight_type'] == 'trainer':
            image_path,e_p = await poke_fight(str(update.effective_chat.id),
                                  True,
                                  poke_list
                                  )
            cap = f"Ecco il risultato del tuo team contro questo allenatore.\n\n🔴: batte la fascia bassa ({e_p[0]})\n🟡: batte la fascia media ({e_p[1]})\n🟢: batte la fascia alta ({e_p[2]})"
        else:
            image_path,e_p = await poke_fight(str(update.effective_chat.id),
                                  False,
                                  poke_list
                                  )
            if len(poke_list)==1:
                cap = "Ecco il risultato del tuo team contro questo Pokémon selvatico."
                cap+= f"\n\n🔴: batte la fascia bassa ({e_p[0]})\n🟡: batte la fascia alta ({e_p[1]})\n"
                cap+= f"🟢: batte {poke_list[0]} se boss ({e_p[2]})"
            else:
                cap = "Ecco il risultato del tuo team contro questi Pokémon selvatici."
                cap+= f"\n\n🔴: batte la fascia bassa ({e_p[0]})\n🟡: batte la fascia alta ({e_p[1]})\n"
                for i, pk in enumerate(poke_list):
                    cap+= f"🟢: batte {pk} se boss ({e_p[2+i]})\n"

        # Open the image file
        with open(image_path, 'rb') as image_file:
            # Send a new message with the image
            await context.bot.send_photo(
                chat_id=str(update.effective_chat.id),
                photo=image_file,
                caption=cap
            )
    except:
        await update.message.reply_text("Qualcosa è andato storto... ti chiedo di ricominciare chiamando /fight.")
    return ConversationHandler.END

def get_fight_conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('fight', fight_command)],
        states={
            CHOOSE_FIGHT_TYPE: [CallbackQueryHandler(fight_type_callback)],
            ENTER_POKEMONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_pokemons)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(filters.COMMAND, end_conversation),
            #MessageHandler(filters.ALL, end_conversation),
        ],
        allow_reentry=True
    )

# --------------------------------------------------------------------------- CARD -------------------------------------------------------------------------------------------
def get_pokemon_image_path(pokemon_name):

    """
    Returns the path for the Pokemon image based on the Pokemon name.
    Searches for the image in the /images/pokemons folder.
    Returns 'Missing.png' if the specific Pokemon image is not found.
    """
    base_path = ENV_PATH+"/images/pokemons"
    pokemon_image = f"{pokemon_name}.png"
    full_path = os.path.join(base_path, pokemon_image)

    if os.path.exists(full_path):
        return full_path
    else:
        return os.path.join(base_path, "Missing.png")

async def card_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await id_check(update)
    try:
        print(update.effective_chat.username,' (',update.effective_chat.id,',',update.effective_user.first_name,') called /card')
    except:
        pass
    text = "Nah, hai sbagliato bot... Però posso provare..."
    await update.message.reply_text(text)
    # Read updated team to show
    chat_id = str(update.effective_chat.id)
    with open(ENV_PATH+'/secret_player_data.json', 'r') as file:
        data = json.load(file)
        team = data[str(chat_id)]["team"]

    # Image dimensions
    image_width = 700
    image_height = 1000
    image = Image.new('RGB', (image_width, image_height), color='white')
    draw = ImageDraw.Draw(image)

    # Calculate cell dimensions
    cell_width = image_width // 3
    cell_height = image_height // 3

    # Load fonts
    title_font = ImageFont.load_default()
    text_font = ImageFont.load_default()

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    except IOError:
        try: 
            font = ImageFont.truetype(ENV_PATH+'/arialbd.ttf',20)
        except:
            font = ImageFont.load_default()
    try:
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 17)
    except IOError:
        try: 
            font_small = ImageFont.truetype(ENV_PATH+'/arialbd.ttf',17)
        except:
            font_small = ImageFont.load_default()

    # Draw grid
    for i in range(1, 3):
        draw.line([(i * cell_width, 0), (i * cell_width, image_height)], fill='black', width=4)
        draw.line([(0, i * cell_height), (image_width, i * cell_height)], fill='black', width=4)

    # Fill each cell
    for i in range(min(9, len(team))):
        row = i // 3
        col = i % 3
        x = col * cell_width
        y = row * cell_height

        # Get Pokemon name and image path
        pokemon_name = team[i][0]
        pokemon_image_path = get_pokemon_image_path(pokemon_name)
        if pokemon_name:
            # Draw title
            draw.text((x + 10, y + 5), pokemon_name, fill='black', font=font)

            # Draw separator line
            draw.line([(x, y + 30), (x + cell_width, y + 30)], fill='black', width=2)

            # Load and draw Pokemon image
            try:
                pokemon_image = Image.open(pokemon_image_path)
                resized_pokemon = pokemon_image.resize((cell_width - 20, cell_height - 140))
                image.paste(resized_pokemon, (x + 10, y + 40), resized_pokemon.convert('RGBA'))
            except Exception as e:
                #print(f"Error loading image for {pokemon_name}: {e}")
                placeholder = Image.new('RGB', (cell_width - 20, cell_height - 140), color='lightgray')
                draw.text((x + 15, y + 45), f"No image for {pokemon_name}", fill='black', font=font)
                image.paste(placeholder, (x + 10, y + 40))

            # Draw bottom text
            texts = [["Tipo:",50,f'{format_types_emoji(poke.get(name = pokemon_name).types)}'], ["Potenza:",90,f"{get_power(team[i][0],team[i][1])}"], ["Livello:",80,f"{team[i][1]}"], ["Livello Evo:",110,f"{poke_evo_level(chat_id,pokemon_name)}"]]
            for j, text in enumerate(texts):
                text_y = y + cell_height - 108 + j * 22
                text_y_text = y + cell_height - 108 + j * 23
                # Draw line above each text, including "Tipo"
                draw.line([(x, text_y + 15), (x + cell_width, text_y + 15)], fill='black', width=1)
                draw.text((x + 10, text_y_text + 15), text[0], fill='black', font=font_small)
                draw.text((x + text[1], text_y_text + 14), text[2], fill='black', font=font)

    # Save the image
    os.makedirs('./images', exist_ok=True)
    image_path = f'./images/{chat_id}_card.png'
    image.save(image_path)

    with open(image_path, 'rb') as image_file:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=image_file,
        )

# --------------------------------------------------------------------------- AUTOMATIC TEAM UPDATE -------------------------------------------------------------------------------------------

async def team_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await id_check(update)
    message = update.message
    caption = message.caption  # for media messages (photo, video, etc.)
    photo = message.photo  # list of PhotoSize objects, from smallest to largest

    if photo and not caption:
        await update.message.reply_text("Stai provando ad inviarmi la tua card? Devi girarmi l'intero messaggio...\n\nAltrimenti che fai, mi mandi i meme?")

    elif photo and caption:
        if caption.strip() == "Ecco la tua card aggiornata!":
            try:
                print(update.effective_chat.username,' (',update.effective_chat.id,',',update.effective_user.first_name,') sent a card')
            except:
                pass
            await update.message.reply_text("Attendi il prossimo messaggio...")

            photo_file = photo[-1] # Get the last photo.
            file = await context.bot.get_file(photo_file.file_id)
            photo_bytes = await file.download_as_bytearray()
            pil_image = Image.open(BytesIO(photo_bytes))
            
            secret_data,errors = await automatic_card_reader(pil_image)

            message = 'Team aggiornato:\n\n'
            for x,y in zip(secret_data,errors):
                if x[0] != None:
                    message+=f'{x[0]}'
                    if y == 1:
                        message += " (⚠️)"   
                    message +=  f' lvl: {x[1]}\n'       
            await update.message.reply_text(message)

            with open(ENV_PATH+'/secret_player_data.json', 'r') as file:
                 data = json.load(file)
            data[str(update.effective_user.id)]["team"] = secret_data
            ## Save our changes to JSON file
            jsonFile = open(ENV_PATH+"/secret_player_data.json", "w+")
            jsonFile.write(json.dumps(data))
            jsonFile.close()

        return ConversationHandler.END

    return ConversationHandler.END  # Fallback



def auto_team_update():   # prende solo le immagini (spero)
    return ConversationHandler(
        entry_points=[MessageHandler(
            (filters.Caption() | filters.PHOTO) & ~filters.COMMAND,
            team_update
        )],
        states={},
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(filters.COMMAND, end_conversation),
        ],
        per_message = False
    )