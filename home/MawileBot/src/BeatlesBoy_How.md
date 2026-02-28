### Funzionamento di BeatlesBoy:

##### Keywords: 

> UTILITY: 
>>Valore assegnato ad un Pokèmon, rappresenta quanto quel Pokèmon sia "utile". Valore in [0-10].

> USEFUL, USELESS, LVL100: 
>>Divisione della squadra in 3 blocchi: 
>>LVL100 contiene i Pokèmon lvl 100 
>>USEFUL massimo 6 tra i rimanenti con utilità più alta
>>USELESS i rimanenti. 

##### Funzionamento: 

> CONTRO ALLENATORI:
>> Calcola il miglior schieramento percentuale tra gli USEFUL. Se uno dei pokemon ha 0% di vincere, aggiunge ad uno ad uno gli USELESS in ordine di utilità e ricalcola finchè nessun pokemon ha 0% o non ha schierato tutti USEFUL+USELESS. A pari percentuale di vittoria, da priorità ai Pokèmon più utili.

> CONTRO CAPOPALESTRA:
>> Calcola il miglior schieramento percentuale tra gli USEFUL. Se non ha il 6-0 assicurato, agginge ad uno ad uno gli USELESS in ordine di utilità e ricalcola. Se non ha il 6-0 assicurato, aggiunge ad uno ad uno i LVL100 in ordine di utilità e ricalcola. A pari percentuale di vittoria, da priorità ai Pokèmon più utili, e per ultimi i LVL100.

>PVP:
>> Schiera, in ordine di PL, da USEFUL. Se non ha abbastanza USEFUL, aggiunge USELESS. Se non ha abbastanza USEFUL + USELESS, aggiunge LVL100.

>SELVATICO:
>>Calcola le opzioni vincenti tra gli USEFUL. Se non ci sono opzioni vincenti, aggiunge ad uno ad uno gli USELESS e poi i LVL100 in ordine di utilità. Se non può vincere, restituisce un errore.
>>Tra le opzioni vincenti, sceglie randomicamente pesando la scelta in base all'utilità.

>CATTURA:
>>Tra gli USEFUL, scegli il meno utile. 
>>Se anche la potenza tra *x* livelli dati stimati del Pokèmon da catturare è superiore a quella del Pokèmon meno utile, allora catturalo!
>>+ *x* è (caselle rimanenti) *2 *1.5.
>>+ Se non ci sono nemmeno 6 Pokèmon in squadra, allora cattura a caso (50% di prob.).
>>+ Chi viene tolto dalla squadra? Se ci stanno slot vuoti, uno di quelli. Altrimenti, il meno utile di USEFUL+USELESS+LVL100 (Assumo che supera la potenza tra *x* livelli stimati, caso limite).
>>+ Non butta mai via Sableye. Cattura sempre Sableye se non ne ha.

>DISTRIBUZIONE LIVELLI:
>> Da il livello al pokemon che vince


>POTENZIAMENTO:
>>Controlla se tra gli USEFUL c'è un tipo uguale al potenziamento. Se più di uno, potenzia il più utile. Se nessuno, potenzia il più utile tra gli USEFUL. Se non ci sono USEFUL, fa lo stesso con gli USELESS e poi i LVL100.