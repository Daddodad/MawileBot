 # MawileBot

 Copia di SableyeBot locale

 ## Struttura

 ```
 📁 MawileBot/                               # Repository
 ├── 📁 home/                                # Su PythonAnywhere, c'è una corrispondente home.
 │   └── 📁 MawileBot/                       # MawileBot. Su PythonAnywhere, c'è un corrispondente SableyeBot.
 │       ├── 📁 src/                         # Su PythonAnywhere, c'è un corrispondente src.
 │       │   └── 📁 images/                 # Contiene immagini utili. Su PythonAnywhere ce ne stanno di più; qui non servono a meno che non stai testando.
 │       │       └── 📁 pokemons/           # Contiene le immagini meme dei Pokémon. Stanno tutte su PythonAnywhere tranne Missingno per evitare bug.
 │       ├── MawileBot.py                  # Main file. Su PythonAnywhere ci sono SableyeBot.py e ./mysite/SableyeBotApp.py.
 │       ├── 📁 old/                        # Roba vecchia per fare ordine.
 │       ├── 📁 output_splits/             # Cartella (locale) per gestire la lettura automatica della squadra.
 │       │                                  # Usarla solo se ci sono bug nella lettura; è tutto dentro.
 │       └── test.ipynb e simili           # Stanno qui per i test. Quando li finisci, o li butti o vanno in /old.
 ├── 📁 images/                             # Il bot crea delle figure. Quelle figure finiscono qui.
 │                                          # Su SableyeBot finiscono in /home/SableyeBot/images/. È un bug ma non ci interessa molto, Sableye funziona e questo funziona.
 ├── README.txt
 └── .gitignore                             # Per non far caricare su GitHub roba inutile
 ```

 ---

 ## Note operative

 1. **SEMPRE PUSHARE SU GITHUB** per evitare branching e casini.  
 2. Ogni modifica a `./src` può **e DEVE** essere spostata su SableyeBot.  
    ➤ **FARE ATTENZIONE ALL'USO DI PATH A FOLDER**: usate sempre *ENV_PATH*.  
 3. Ogni modifica a `MawileBot.py` deve essere trasportata **manualmente** su `SableyeBot.py` **e** `SableyeBotApp.py`.  
    ➤ **NON SONO GLI STESSI FILES. ALCUNE COSE SONO DIVERSE APPOSTA, NON COPIATE E BASTA.**  
 4. Se aggiungete files, **farlo in modo ordinato** nella cartella `src` o in sottocartelle.  
    ➤ Ricordatevi di spostarli poi su SableyeBot.  
 5. Controllare gli errori su SableyeBot (online) è un casino.  
    ➤ Consiglio di aggiungere **molti messaggi di controllo** (poi toglieteli).  
 6. **TESTARE SEMPRE CON MAWILEBOT PRIMA DI CARICARE SU SABLEYE**

 ---

 ## NOTA PER DAVIDE

 **NEW PC:**  
 Per il `.venv` + jupyter-lab:
 ```bash
 ./..\CNR\av-anomaly-detection\av-anomaly-detection\.venv\Scripts\activate 
 jupyter-lab
 ```

 Lanciare da dentro MawileBot con Python:
 ```bash
 python .\home\MawileBot\MawileBot.py
 ```
