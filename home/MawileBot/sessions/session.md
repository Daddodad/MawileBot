# Telegram Client Setup

When using BeatlesBoy, TelegramClient requires an api_id and an api_hash.

## First-time login

On first run the client will:
1. Ask for your phone number
2. Send a one-time password (OTP)
3. Create a .session file in:
 home/MawileBot/sessions/ 

## ⚠️ Warning

DO NOT RUN TWO SESSIONS AT THE SAME TIME.
If the same .session is used by multiple processes, it will be invalidated and you will need to log in again.