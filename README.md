 # MawileBot

 Copia di SableyeBot locale

 ## Nota sui file mancanti

 ## Struttura

 ```
 📁 MawileBot/                               # Repository
 ├── 📁 home/                                # Su PythonAnywhere, c'è una corrispondente home.
 │   └── 📁 MawileBot/                       # MawileBot. Su PythonAnywhere, c'è un corrispondente SableyeBot.
 │       ├── 📁 sessions/                    # Sessioni di BeatlesBoy.
 │       │   └── session.md                  # Spiegazioni sulle sessions
 │       ├── 📁 src/                         # Su PythonAnywhere, c'è un corrispondente src.
 │       │   └── 📁 images/                  # Contiene immagini utili. Su PythonAnywhere ce ne stanno di più; qui non servono a meno che non stai testando.
 │       │       ├── 📁 templates/           # Templates
 │       │       ├── 📁 types/               # Types per /card
 │       │       └── 📁 pokemons/            # Contiene le immagini meme dei Pokémon. Stanno tutte su PythonAnywhere tranne Missingno per evitare bug.
 │       ├── MawileBot.py                    # Main file. Su PythonAnywhere ci sono SableyeBot.py e ./mysite/SableyeBotApp.py.
 │       ├── BeatlesBoy.py                    # Main file. 
 │       ├── config.ini / config_template.ini # Main file. Su PythonAnywhere ci sono SableyeBot.py e ./mysite/SableyeBotApp.py.
 │       ├── 📁 old/                         # Roba vecchia per fare ordine.
 │       ├── 📁 utils/                       # Roba utile per creare files quando escono nuove gen / nuovi stili del bot.
 │       │   └── 📁 output_splits/           # Cartella (locale) per gestire la lettura automatica della squadra.
 │       │                                   # Usarla solo se ci sono bug nella lettura; è tutto dentro la cartella.
 │       │                                   # L'unica cosa che aggiorna e che va messa anche su SableyeBot è alphabet.json.
 │       │   └── 📁 pokemon_list_creator/    # Crea il file con tutti i pokemon
 │       │   └── 📁 pokemon_type_list_creator/# Crea vari file sui tipi di pokemon esistenti
 │       └── test.ipynb e simili             # Stanno qui per i test. Quando li finisci, o li butti o vanno in /old.
 ├── .gitignore                              # Per non far caricare su GitHub roba inutile
 ├── README.md                               # per i fan delle strutture ricorsive
 └── requirements.txt                        # Può servire? Potrebbe avere roba inutile
 ```

 ---

 ## Note operative (SableyeBot/MawileBot)

 1. **SEMPRE PUSHARE SU GITHUB** per evitare branching e casini.  
 2. Ogni modifica a `./src` può **e DEVE** essere spostata su SableyeBot (copia incolla dei files).  
    ➤ **FARE ATTENZIONE ALL'USO DI PATH A FOLDER**: usate sempre *ENV_PATH*.  
 3. Ogni modifica a `MawileBot.py` deve essere trasportata **manualmente** su `SableyeBot.py` **e** `SableyeBotApp.py`.  
    ➤ **NON SONO GLI STESSI FILES. ALCUNE COSE SONO DIVERSE APPOSTA, NON COPIATE E BASTA.**  
 4. Se aggiungete files, **farlo in modo ordinato** nella cartella `src` o in sottocartelle.  
    ➤ Ricordatevi di spostarli poi su SableyeBot.  
 5. Controllare gli errori su SableyeBot (online) è un casino.  
    ➤ Consiglio di aggiungere **molti messaggi di controllo** (poi toglieteli).  
 6. **TESTARE SEMPRE CON MAWILEBOT PRIMA DI CARICARE SU SABLEYE**

 ---