### Funzionamento di BeatlesBoy:

##### Keywords: 

> UTILITY: 
>>Valore assegnato ad un Pokèmon, rappresenta quanto quel Pokèmon sia "utile"

> USEFUL, USELESS, LVL100: 
>>Divisione della squadra in 3 blocchi: 
>>LVL100 contiene i Pokèmon lvl 100 
>>USEFUL massimo 6 tra i rimanenti con utilità più alta
>>USELESS i rimanenti. 

##### Funzionamento: 

> CONTRO ALLENATORI:
>> Calcola il miglior schieramento percentuale tra gli USEFUL. Se uno dei pokemon ha 0% di vincere, agginge ad uno ad uno gli USELESS in ordine di utilità e ricalcola finchè nessun pokemon ha 0% o non ha schierato tutti USEFUL+USELESS. Pari percentuale, da priorità ai Pokèmon più utili.

> CONTRO CAPOPALESTRA:
>> Calcola il miglior schieramento percentuale tra gli USEFUL. Se non ha il 6-0 assicurato, agginge ad uno ad uno gli USELESS in ordine di utilità e ricalcola. Se non ha il 6-0 assicurato, aggiunge ad uno ad uno i LVL100 in ordine di utilità e ricalcola.

>PVP:
>> Schiera, in ordine di PL, da USEFUL.