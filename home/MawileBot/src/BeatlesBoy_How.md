### Funzionamento di BeatlesBoy:

##### Keywords: 

> _UTILITY_: 
>>Valore assegnato ad un Pokèmon, rappresenta quanto quel Pokèmon sia "utile". Valore in [0-10].

> _USEFUL, USELESS, LVL100_: 
>>Divisione della squadra in 3 blocchi: 
>>LVL100 contiene i Pokèmon lvl 100 
>>USEFUL massimo 6 tra i rimanenti con utilità più alta
>>USELESS i rimanenti. 

> _NOBODY IS LEFT BEHIND_ 
Protocollo per gestire l'allenamento della squadra: Bypassa le regole generali di allenamento per non lasciare nessun pokemon indietro. 
Si assicura di non lasciare nessun pokemon _USEFUL_ con PL inferiori alla potenza della fascia bassa della casella successiva (eccetto ultimo giorno, in cui è la corrente) (garantendo quindi un minimo aiuto nelle palestre e nelle battaglie, e lasciandolo sempre allenabile. In particolare, è pensato per distribuire potenziamenti e livelli ai pokemon appena catturati per farli arrivare rapidamente al livello degli altri).
In generale, nelle situazioni:
>> CONTRO ALLENATORI: Aggiunge 10 all'utilità, garantendo lo schieramento in caso di parità con altri pokemon.
>> CONTRO CAPOPALESTRA: Aggiunge 10 all'utilità, garantendo lo schieramento in caso di parità con altri pokemon.
>> SELVATICO: Aggiunge 10 all'utilità e bypassa la scelta casuale, venendo sempre schierato in caso di vittoria.
>> DISTRIBUZIONE LIVELLI: Aggiunge 10 all'utilità, garantendo la distribuzione del livello.
>> POTENZIAMENTO: Aggiunge 10 all'utilità e bypassa il controllo del tipo del potenziamento, dandolo al pokemon prioritario.
>>> Se ci sono più di un pokèmon con utilità maggiore di 10, viene data priorità in base all'utilità (bypassa il random choice contro i selvatici.)

##### Funzionamento: 

> **CONTRO ALLENATORI**:
>> Calcola il miglior schieramento percentuale tra gli _USEFUL_. Se uno dei pokemon ha 0% di vincere, aggiunge ad uno ad uno gli USELESS in ordine di utilità e ricalcola finchè nessun pokemon ha 0% o non ha schierato tutti _USEFUL_+_USELESS_. A pari percentuale di vittoria, da priorità ai Pokèmon più utili (Seguendo il protocollo _NOBODY IS LEFT BEHIND_).

> **CONTRO CAPOPALESTRA**:
>> Calcola il miglior schieramento percentuale tra gli USEFUL. Se non ha il 6-0 assicurato, agginge ad uno ad uno gli _USELESS_ in ordine di utilità e ricalcola. Se non ha il 6-0 assicurato, aggiunge ad uno ad uno i LVL100 in ordine di utilità e ricalcola. A pari percentuale di vittoria, da priorità ai Pokèmon più utili, e per ultimi i LVL100 (Seguendo il protocollo _NOBODY IS LEFT BEHIND_).

>**PVP**:
>> Schiera, in ordine di PL, da USEFUL. Se non ha abbastanza _USEFUL_, aggiunge _USELESS_. Se non ha abbastanza USEFUL + _USELESS_, aggiunge LVL100.

>**SELVATICO**:
>>Calcola le opzioni vincenti tra gli _USEFUL_. Se non ci sono opzioni vincenti, aggiunge ad uno ad uno gli _USELESS_ e poi i LVL100 in ordine di utilità. Se non può vincere, restituisce un errore.
>>Tra le opzioni vincenti, sceglie randomicamente pesando la scelta in base all'utilità (Seguendo il protocollo _NOBODY IS LEFT BEHIND_).

>**CATTURA**:
>>Tra gli _USEFUL_, scegli il meno utile. 
>>Se anche la potenza tra *x* livelli dati stimati del Pokèmon da catturare è superiore a quella del Pokèmon meno utile, allora catturalo!
>>+ *x* è (caselle rimanenti) *2 *1.5.
>>+ Se non ci sono nemmeno 6 Pokèmon in squadra, allora cattura a caso (50% di prob.).
>>+ Chi viene tolto dalla squadra? Se ci stanno slot vuoti, uno di quelli. Altrimenti, il meno utile di _USEFUL_+_USELESS_+LVL100 (Assumo che supera la potenza tra *x* livelli stimati, caso limite).
>>+ Non butta mai via Sableye. Cattura sempre Sableye se non ne ha.

>**DISTRIBUZIONE LIVELLI**:
>> Da il livello al pokemon che vince, e al pokemon più utile (se può distribuire, seguendo il protocollo _NOBODY IS LEFT BEHIND_).


>**POTENZIAMENTO**:
>>Dopo aver applicato _NOBODY IS LEFT BEHIND_, controlla se tra gli _USEFUL_ c'è un tipo uguale al potenziamento. Se più di uno, potenzia il più utile.