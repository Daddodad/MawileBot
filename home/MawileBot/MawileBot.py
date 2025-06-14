import random
import json
import asyncio
import os
from telegram import BotCommand, Update
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler

import sys
if os.path.exists('/home/SableyeBot/src'):
    sys.path.insert(0,'/home/SableyeBot/src') # SableyeBot
else:
    sys.path.insert(0,'home/MawileBot/src') # MawileBot

from src.Commands import get_start_conversation_handler
from src.Commands import help_command, help_button_handler, HELP_START, HELP_BONUS, HELP_BACK, HELP_LEGA, HELP_GYM, HELP_CELL, HELP_TEAM, HELP_ALTRO, HELP_DEX,HELP_HELP, HELP_FIGHT
from src.Commands import get_bonus_conversation_handler, bonus_button_handler, BONUS_CHANGE_MULT, BONUS_REDO_BONUS
from src.Commands import gym, gym_button, get_gym_test_conversation_handler
from src.Commands import team_command, get_team_conversation_handler
from src.Commands import spy, get_ping_all_handler, dex_command
from src.Commands import get_cell_handlers
from src.Commands import lega_command, get_lega_conversation_handler
from src.Commands import get_fight_conversation_handler
from src.Commands import card_command

#from src.Commands import
# ------------------------------------------------------------------- LISTA COMANDI ----------------------------------------------------------------

async def set_bot_commands(application: Application) -> None:
    commands = [
        BotCommand("start", "Diamoci dentro..."),
        BotCommand("help", "Cerchi aiuto?"),
        BotCommand("fight", "Simuliamo ogni combattimento..."),
        BotCommand("team", "Tiriamo su questa squadra."),
        BotCommand("bonus", "1v1 al Gyarados?"),
        BotCommand("gym", "Alla conquista di una medaglia."),
        BotCommand("lega", "Solo i migliori vinceranno..."),
        BotCommand("cell", "Vuoi conoscere il futuro?"),
        BotCommand("dex", "Serve un ripasso?"),
    ]
    await application.bot.set_my_commands(commands)

# ------------------------------------------------------------------------- MAIN ------------------------------------------------------------

def main() -> None:
    application = Application.builder().token("8115605790:AAF2BAAGm48-Rt-d5U44Mw7rLD02yo2v1hY").post_init(set_bot_commands).build()

    # Add basic answer
    # application.add_handler(get_edgy_answer(), group = 666)

    application.add_handler(get_start_conversation_handler(), group = 1 )

    application.add_handler(CommandHandler("help", help_command), group = 2 )
    application.add_handler(CallbackQueryHandler(help_button_handler, pattern=f"^{HELP_START}|{HELP_BONUS}|{HELP_HELP}|{HELP_LEGA}|{HELP_GYM}|{HELP_TEAM}|{HELP_DEX}|{HELP_FIGHT}|{HELP_CELL}|{HELP_ALTRO}|{HELP_BACK}$"), group = 2)

    application.add_handler(get_bonus_conversation_handler(), group = 3 )
    application.add_handler(CallbackQueryHandler(bonus_button_handler, pattern=f"^{BONUS_CHANGE_MULT}|{BONUS_REDO_BONUS}$"), group = 3)

    application.add_handler(CommandHandler("gym", gym),group = 6)
    application.add_handler(get_gym_test_conversation_handler(),group = 6)
    application.add_handler(CallbackQueryHandler(gym_button, pattern="^gym_"), group = 6)

    application.add_handler(CommandHandler("team", team_command), group =7)
    application.add_handler(get_team_conversation_handler())

    application.add_handler(CommandHandler("spy", spy) ,group = 8)

    #application.add_handler(CommandHandler("help", help_generic) ,group = 14)

    application.add_handler(get_ping_all_handler(), group = 9 )

    application.add_handler(CommandHandler("dex", dex_command), group = 10)

    #application.add_handler(CommandHandler("cell", cell_command), group = 11)
    for handler in get_cell_handlers():
        application.add_handler(handler,group =11)

    application.add_handler(CommandHandler("lega", lega_command),group = 12)
    application.add_handler(get_lega_conversation_handler(),group = 12)

    #application.add_handler(CallbackQueryHandler(button_callback),group = 12)

    application.add_handler(get_fight_conversation_handler(),group = 13)

    application.add_handler(CommandHandler("card", card_command) ,group = 99)


    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

#Info: per installare librerie, usa in una bash pip3.10 install --user numpy