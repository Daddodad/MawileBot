import random
import json
import asyncio
from flask import Flask, request
from telegram import Update, BotCommand
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler
import sys
sys.path.insert(0, '/home/SableyeBot/src')

from src.Commands import (
    get_start_conversation_handler, help_command, help_button_handler,
    HELP_START, HELP_BONUS, HELP_BACK, HELP_LEGA, HELP_GYM, HELP_CELL, HELP_TEAM, HELP_ALTRO, HELP_DEX, HELP_HELP, HELP_FIGHT,
    get_bonus_conversation_handler, bonus_button_handler, BONUS_CHANGE_MULT, BONUS_REDO_BONUS,
    gym, gym_button, get_gym_test_conversation_handler,
    team_command, get_team_conversation_handler,
    spy, get_ping_all_handler, dex_command,
    get_cell_handlers,
    lega_command, get_lega_conversation_handler,
    get_fight_conversation_handler,
    card_command,
    auto_team_update,
    auto_text_update,
    get_meme_conversation_handler
)

TOKEN = '7119226556:AAErwxsF7x0rksunnoKp3_ItLcQPfQdlqlM'
app = Flask(__name__)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

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

async def initialize_application():
    application = Application.builder().token(TOKEN).build()
    #await application.initialize()
    #await application.start()

    await set_bot_commands(application)

    application.add_handler(auto_team_update(), group = 666)
    application.add_handler(auto_text_update(), group = 667)

    application.add_handler(get_start_conversation_handler(), group=1)
    application.add_handler(CommandHandler("help", help_command), group=2)
    application.add_handler(CallbackQueryHandler(help_button_handler, pattern=f"^{HELP_START}|{HELP_BONUS}|{HELP_HELP}|{HELP_LEGA}|{HELP_GYM}|{HELP_TEAM}|{HELP_DEX}|{HELP_FIGHT}|{HELP_CELL}|{HELP_ALTRO}|{HELP_BACK}$"), group=2)
    application.add_handler(get_bonus_conversation_handler(), group=3)
    application.add_handler(CallbackQueryHandler(bonus_button_handler, pattern=f"^{BONUS_CHANGE_MULT}|{BONUS_REDO_BONUS}$"), group=3)
    application.add_handler(CommandHandler("gym", gym), group=6)
    application.add_handler(get_gym_test_conversation_handler(), group=6)
    application.add_handler(CallbackQueryHandler(gym_button, pattern="^gym_"), group=6)
    application.add_handler(CommandHandler("team", team_command), group=7)
    application.add_handler(get_team_conversation_handler())
    application.add_handler(CommandHandler("spy", spy), group=8)
    application.add_handler(get_ping_all_handler(), group=9)
    application.add_handler(CommandHandler("dex", dex_command), group=10)
    for handler in get_cell_handlers():
        application.add_handler(handler, group=11)
    application.add_handler(CommandHandler("lega", lega_command), group=12)
    application.add_handler(get_lega_conversation_handler(), group=12)
    application.add_handler(get_fight_conversation_handler(), group=13)
    application.add_handler(CommandHandler("card", card_command), group=99)
    application.add_handler(get_meme_conversation_handler(),group = 100)

    return application

#application = loop.run_until_complete(initialize_application())
application = None

def get_application():
    global application
    if application is None:
        application = loop.run_until_complete(initialize_application())
        loop.run_until_complete(application.initialize())
    return application

@app.route('/sableye_as_a_bot', methods=['POST'])
def webhook():
    #update = Update.de_json(request.get_json(force=True), application.bot)
    app_ = get_application()
    update = Update.de_json(request.get_json(force=True), app_.bot)

    async def process_update():
        await app_.process_update(update)
        #await application.process_update(update)

    loop.run_until_complete(process_update())
    return 'ok'

if __name__ == '__main__':
    app.run(debug=True)