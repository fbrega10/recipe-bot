# Esercitazione Lezione 10 — "Esplora ed estendi"

**Tempo**: ~75 minuti sul percorso consigliato, 90+ minuti sui task avanzati
— **Tipo**: laboratorio guidato di familiarizzazione — **Modalità**:
individuale o in coppia.

---

## Sommario

1. [Cos'è questa esercitazione](#cosè-questa-esercitazione)
2. [Come leggere questa esercitazione se hai poco tempo](#come-leggere-questa-esercitazione-se-hai-poco-tempo)
3. [Setup](#setup)
4. [Cosa fare](#cosa-fare)
5. [Percorsi consigliati](#percorsi-consigliati)
6. [I quattro task disponibili](#i-quattro-task-disponibili)
   - [Task A — Estendere o sistemare il tool layer](#task-a--estendere-o-sistemare-il-tool-layer)
   - [Task B — Modificare il context engineering](#task-b--modificare-il-context-engineering)
   - [Task C — Estendere la knowledge base](#task-c--estendere-la-knowledge-base)
   - [Task D — Riattivare l'output strutturato](#task-d--riattivare-loutput-strutturato)
7. [Bonus opzionali](#bonus-opzionali)
8. [Trace analysis — esercizio di osservazione](#trace-analysis--esercizio-di-osservazione)
9. [API Crib Sheet — pattern Agno pronti all'uso](#api-crib-sheet--pattern-agno-pronti-alluso)
10. [Se sei bloccato](#se-sei-bloccato)

---

## Cos'è questa esercitazione

Non è un mini-progetto d'esame. Non ti chiediamo di costruire RecipeBot da
zero — l'abbiamo costruito insieme nei sette blocchi della lezione. Ti
chiediamo di **estenderlo in modo mirato**: scegli due task, modifichi il
codice, osservi cosa cambia.

L'obiettivo è che tu **familiarizzi col framework** e con gli strumenti di
osservabilità (Control Plane, trace, debug output). Non ti viene chiesto di
trovare la soluzione "giusta": ti viene chiesto di **provare, osservare,
motivare**. Niente da consegnare: l'esercitazione è per te.

---

## Come leggere questa esercitazione se hai poco tempo

Se hai 75 minuti, leggi solo:

1. [Setup](#setup)
2. [Cosa fare](#cosa-fare)
3. [Percorsi consigliati](#percorsi-consigliati)
4. I due task che hai scelto
5. [Trace analysis](#trace-analysis--esercizio-di-osservazione)

L'API Crib Sheet in fondo è una reference: usala quando ti serve uno snippet
pronto, non leggerla tutta prima di iniziare.

---

## Setup

Clona il repo. Il branch `main` corrisponde allo stato di RecipeBot alla
fine della Lezione 10 (commit `lezione-10`):

```bash
git clone <url-repo> recipebot
cd recipebot
```

Crea il file `.env` con la tua `GOOGLE_API_KEY`:

```bash
cp .env.example .env
# poi modifica .env con la tua chiave
```

Installa le dipendenze (il repo ha già `uv.lock`, quindi `uv sync`
riproduce le versioni esatte usate in classe):

```bash
uv sync
```

Avvia il server:

```bash
fastapi dev recipebot.py
```

Apri `http://localhost:8000` per il Control Plane.

---

## Cosa fare

1. **Scegli due task obbligatori** dalla sezione successiva, rispettando il
   vincolo: **almeno uno dei due deve essere il Task A o il Task C**. La
   combinazione B+D non è ammessa (mancano sia tool che knowledge — sono i
   pilastri della lezione).

   Combinazioni valide:
   - A + B
   - A + C
   - A + D
   - C + B
   - C + D

2. **Lavora sui task scelti**. Per ognuno: leggi l'obiettivo, modifica il
   codice, prova i prompt suggeriti. Annota per te stesso cosa hai osservato
   — ti servirà per discuterne in classe alla prossima lezione.

3. Completa la **trace analysis** (vedi sezione dedicata): analisi completa
   per uno dei due task, versione rapida per l'altro.

4. **(Opzionale)** Affronta uno o entrambi i task bonus.

---

## Percorsi consigliati

Non tutte le varianti hanno lo stesso peso. Per restare dentro 75 minuti,
scegli uno dei percorsi standard. Se scegli un task avanzato, timeboxalo e
accetta che possa richiedere 90 minuti o più.

| Percorso | Quando sceglierlo | Combinazioni consigliate |
|---|---|---|
| **Standard — 75 minuti** | Vuoi completare esercizio, test e trace senza correre | A1 + B1/B3, A3 + B2, C3 + B1/B3 |
| **Intermedio — 90 minuti** | Vuoi toccare due pilastri tecnici con un po' più di margine | A1 + C3, A3 + C3, A1 + B2 |
| **Avanzato / timebox** | Hai già confidenza col codice o lavori in coppia | Qualsiasi combinazione valida con A2, C1, C2 o D |

I task bonus sono davvero opzionali: affrontali solo se hai già completato i
due task scelti e almeno una trace analysis.

---

## I quattro task disponibili

### Task A — Estendere o sistemare il tool layer

**Obiettivo**: aggiungere un nuovo tool a RecipeBot, oppure sistemare un
comportamento problematico di un tool esistente.

**Difficoltà**: variabile — **Tempo stimato**: 15-45 minuti a seconda della
variante scelta.

#### Tre varianti possibili (sceglierne una)

##### Variante A1 — Sistemare la gestione delle allergie

**Difficoltà**: media — **Tempo stimato**: 25-30 minuti.

Durante la demo del Blocco 7 abbiamo osservato un comportamento problematico:
chiedendo "sono allergico alle nocciole" e poi una ricetta, l'agente passa
`dietary_constraints=["vegetariano", "senza nocciole"]` a
`find_recipes_by_constraints`. Ma "senza nocciole" non è un tag presente nelle
ricette di `RECIPES_DB` — i tag sono solo positivi (vegetariano, vegano,
senza-glutine, contiene-frutta-secca). Il filtro fallisce e nessuna ricetta
viene proposta.

**Cosa fare**: separare le allergie dai vincoli dietetici. Aggiungere un
parametro `excluded_ingredients: list[str] = []` al tool, che filtra le
ricette per **ingredienti vietati**, distinto da `dietary_constraints` che
filtra per tag positivi.

**Punti di attenzione**:
- Devi aggiornare anche le instructions dell'agente, dicendo esplicitamente:
  *"Le allergie vanno passate come `excluded_ingredients`, non come
  `dietary_constraints`."*
- Verifica che il tool ora propone l'insalata di ceci e zucchine quando
  l'utente è "vegetariano e allergico alle nocciole" e ha "ceci, zucchine".
- Riflettere sulla **classificazione del rischio** del tool modificato
  (è ancora READ-ONLY?).
- **Decisione di design**: filtri per ingrediente esatto (`"nocciole"`
  esclude solo ricette che contengono `"nocciole"`) o per categoria
  allergenica (`"nocciole"` esclude tutta la frutta secca, come dice
  `docs/allergeni.md`)? Le due strategie producono risultati diversi —
  scegli e motiva. La modalità più semplice è ingrediente-esatto, e
  delegare l'espansione di categoria al ragionamento del modello (che
  legge la knowledge base).

##### Variante A2 — Aggiungere un tool `scale_recipe`

**Difficoltà**: media-alta — **Tempo stimato**: 20-25 minuti per la versione
light, 40-45 minuti per la versione full.

**Versione light**: aggiungi un tool che riceve `recipe_name` e
`target_servings` e ritorna gli ingredienti riscalati per **una sola ricetta**
a tua scelta, usando quantità hardcoded dentro il tool o in una piccola
struttura dedicata.

**Versione full**: estendi il modello dati di tutte le ricette in
`RECIPES_DB` e poi implementa il tool generico.

**Attenzione — modellazione dati richiesta per la versione full**:
`RECIPES_DB` contiene solo *nomi* di ingredienti, senza quantità né numero di
porzioni. Le quantità sono nel markdown `docs/ricettario.md`, e non sono
tutte "per 2" (l'hummus è "per 4 porzioni come antipasto"). Quindi il task
richiede **anche** una piccola estensione del modello dati: aggiungere a ogni
ricetta in `RECIPES_DB` una struttura tipo:

```python
"servings": 2,
"quantities": {"ceci": (200, "g"), "zucchine": (2, "medie"), ...}
```

Nella versione full, solo dopo puoi scrivere il tool che moltiplica per
`target_servings / servings`.

**Punti di attenzione**:
- È un tool calcolatorio puro: classificalo per rischio.
- Aggiungi un'instruction che indichi all'agente quando chiamarlo (es.
  *"Quando l'utente menziona un numero di porzioni diverso da quello
  base della ricetta, usa scale_recipe"*).
- Bonus: gestisci il caso in cui la ricetta non esiste in RECIPES_DB.
- Domanda di design: vale la pena strutturare le quantità in
  `RECIPES_DB`, o è più sensato delegare l'estrazione al modello a
  partire dal markdown della knowledge base?

##### Variante A3 — Aggiungere un tool `convert_units`

**Difficoltà**: bassa-media — **Tempo stimato**: 15-20 minuti.

**Cosa fare**: aggiungere un tool che converte tra unità di misura comuni
in cucina (g ↔ oz, ml ↔ cup, °C ↔ °F).

**Punti di attenzione**:
- READ-ONLY puro, deterministico, nessuna chiamata esterna.
- Domanda: **quando un tool del genere è davvero utile?** Il modello
  potrebbe già saper convertire — ma con quale affidabilità?

#### Prompt di test (Variante A1)

```
Sono vegetariano, allergico alle nocciole.
Ho ceci e zucchine in frigo, qualcosa di veloce?
```

Il prompt deve produrre una ricetta valida (Insalata di ceci e zucchine).

---

### Task B — Modificare il context engineering

**Obiettivo**: cambiare il modo in cui RecipeBot "vede" se stesso e la
conversazione, e osservare l'impatto sul comportamento.

**Difficoltà**: bassa — **Tempo stimato**: 15-20 minuti.

#### Tre varianti possibili (sceglierne una)

##### Variante B1 — Cambia personalità

Modifica `description` e una o due `instructions` per dare a RecipeBot una
**personalità specifica**. Esempi:
- *Chef toscano laconico*: risposte brevi, qualche modo di dire.
- *Nonna scrupolosa*: ricorda sempre di lavare bene le verdure, di fare
  l'ammollo dei legumi, ecc.
- *Coach nutrizionale*: enfatizza l'aspetto proteico/calorico delle scelte.

**Cosa osservare**: la personalità si percepisce solo nel testo finale? O
cambia anche *quali tool chiama* o *quante alternative propone*? Confronta
lo stesso prompt prima e dopo.

##### Variante B2 — Modifica `num_history_runs`

`num_history_runs=3` significa che il modello vede gli ultimi 3 turni di
conversazione. Provalo a `num_history_runs=1` (solo il turno corrente) e
`num_history_runs=10`.

**Cosa osservare**: nel debug output, quanto cambia la lunghezza del prompt?
E il comportamento: l'agente perde context con valori bassi? Diventa "troppo
verbose" con valori alti?

##### Variante B3 — Rimuovere un'instruction critica

Commenta una sola di queste istruzioni e osserva come cambia il
comportamento:
- *"Non suggerire mai ingredienti che violino le allergie..."*
- *"Quando l'utente non specifica un vincolo, chiedi prima di assumere."*
- *"Se i vincoli sono in conflitto, segnala il problema invece di forzare
  una soluzione."*

**Cosa osservare**: l'agente si comporta peggio? Si comporta come se le
instructions non fossero mai state lì? In che modo le instructions contano
davvero?

#### Prompt di test

Per la **Variante B3**, prova:

```
Voglio una cena vegana, proteica, senza comprare nulla.
Ho solo pasta, burro, parmigiano e pomodori.
```

(Lo stesso prompt-conflitto del Blocco 5.)

---

### Task C — Estendere la knowledge base

**Obiettivo**: aggiungere conoscenza al ricettario o cambiare la strategia di
ricerca.

**Difficoltà**: variabile — **Tempo stimato**: 15-40 minuti a seconda della
variante scelta.

#### Tre varianti possibili (sceglierne una)

##### Variante C1 — Aggiungere un nuovo documento

**Difficoltà**: media — **Tempo stimato**: 35-40 minuti.

Crea un file `docs/sostituzioni_avanzate.md` con almeno 30 righe su un tema
specifico: ad esempio sostituzioni per dieta vegana, oppure tecniche di
cottura senza olio, oppure stagionalità degli ingredienti.

**Cosa fare**:
1. Scrivi il documento
2. Aggiungi `knowledge.insert(path="docs/sostituzioni_avanzate.md")` in
   `recipebot.py`
3. **Cancella `tmp/lancedb/`** e riavvia (altrimenti il vector DB non
   reindicizza)
4. Testa con un prompt che richiede esplicitamente la nuova conoscenza

**Punti di attenzione**: il documento deve contenere informazioni *non
ovvie* — se metti "il pomodoro è rosso", il modello la sa già. Cerca cose
specifiche del tuo dominio.

##### Variante C2 — Provare hybrid search

**Difficoltà**: media — **Tempo stimato**: 25-35 minuti.

Modifica `search_type=SearchType.vector` in `search_type=SearchType.hybrid`
nel codice della knowledge.

**Cosa osservare**:
- L'agente cerca ancora correttamente?
- Se vedi errori "no documents found" o "FTS index missing", documentali per
  te! Hybrid search richiede un indice full-text che Agno non crea sempre
  automaticamente.
- Se funziona, prova un prompt molto specifico (con un termine raro tipo
  "tahini") e confrontalo con vector pura: cambia il chunk recuperato?

##### Variante C3 — Disabilitare `search_knowledge`

**Difficoltà**: bassa-media — **Tempo stimato**: 15-20 minuti.

Imposta `search_knowledge=False` nell'Agent (lasciando però
`knowledge=...`).

> **Nota**: in Agno 2.6.4 `search_knowledge` ha default `True`, quindi
> *rimuovere* la riga non disattiva nulla. Per spegnere la KB serve il
> flag esplicito a `False`.

**Cosa osservare**:
- L'agente usa ancora la knowledge base? Spoiler: **no**, anche se è
  configurata.
- Verifica nelle trace: lo span `search_knowledge_base` non compare più.
- **Perché Agno espone il flag** invece di legare l'attivazione alla
  semplice presenza di `knowledge`? Cosa permette questa scelta? (Pensa
  ai casi in cui vuoi tenere la knowledge configurata ma usarla in modo
  manuale, ad esempio precaricarla nel system prompt.)

#### Prompt di test

```
Cosa dice il ricettario sulla cottura dei ceci secchi?
```

(per le varianti C1/C2)

```
Quale ammollo serve per i ceci?
```

(per la variante C3, per vedere che l'agente NON sa rispondere)

---

### Task D — Riattivare l'output strutturato

**Obiettivo**: riattivare `output_schema` (e `use_json_mode=True` per Gemini),
gestire le complicazioni con tool e reasoning attivi.

**Difficoltà**: alta / avanzata — **Tempo stimato**: 35-45 minuti.

Questo task è interessante ma fragile: combina output strutturato, tool,
reasoning, knowledge e Gemini. Sceglilo se vuoi fare debugging avanzato o se
hai almeno 90 minuti; per il percorso standard da 75 minuti è meglio scegliere
un'altra combinazione.

#### Cosa fare

1. Rimuovi i commenti dalle due righe:
   ```python
   output_schema=RecipeRecommendation,
   use_json_mode=True,
   ```

2. Avvia `fastapi dev recipebot.py` e prova un prompt qualunque.

3. **Probabile problema 1**: Gemini ti dà errore *"Function calling with a
   response mime type: 'application/json' is unsupported"*. Hai
   `use_json_mode=True`? Se sì e l'errore continua, prova a disabilitare uno
   degli altri elementi (reasoning? knowledge?) per isolarlo.

4. **Probabile problema 2**: il payload del reasoning (think/analyze) finisce
   dentro la risposta strutturata, in campi sbagliati come `reason`.

#### Punto progettuale aperto

Output structured + tool + reasoning + knowledge è il **caso completo** ma è
anche fragile su Gemini. Tre strategie possibili:

1. **Lasciare structured solo per casi terminali** (l'agente risponde in
   testo durante il reasoning, struttura solo l'output finale).
2. **Pattern a due agenti**: un agente "lavoratore" senza schema, e un
   agente "formatter" che riceve l'output testuale e lo struttura. Lo
   vedremo in Lezione 11 con i Team.
3. **Disabilitare reasoning quando lo schema è attivo**.

Quale di queste tre strategie sceglieresti per RecipeBot v2 e perché?

#### Prompt di test

```
Ho ceci, zucchine e yogurt. Sono vegetariano. Cosa mi consigli?
```

---

## Bonus opzionali

### Bonus F — Reasoning più snello

**Obiettivo**: configurare `ReasoningTools` in modo più mirato, e osservare
il trade-off costo/qualità.

**Tempo stimato**: 15 minuti.

`ReasoningTools` ha due parametri booleani: `enable_think` ed `enable_analyze`.
Per default sono entrambi `True`. Prova:

```python
ReasoningTools(add_instructions=True, enable_analyze=False)
```

Solo `think`, niente `analyze`.

**Cosa osservare**:
- Il numero di tool call nelle trace si riduce?
- La qualità della risposta è peggiore? Per quali tipi di prompt?
- Il tempo totale di run è significativamente più veloce?

Confronta lo stesso prompt nelle due configurazioni (con e senza `analyze`).

---

### Bonus G — LearningMachine: estrarre più storia

**Obiettivo**: aggiungere uno store in più alla LearningMachine, oppure
ispezionare il db.

**Tempo stimato**: 15-20 minuti.

#### Variante G1 — Aggiungi `session_context`

```python
from agno.learn import (
    LearningMachine, LearningMode,
    UserProfileConfig, UserMemoryConfig,
    SessionContextConfig,
)

learning=LearningMachine(
    user_profile=UserProfileConfig(mode=LearningMode.AGENTIC),
    user_memory=UserMemoryConfig(mode=LearningMode.AGENTIC),
    session_context=SessionContextConfig(),
),
```

**Cosa osservare**:
- Dopo qualche turno di conversazione, ispeziona la tabella
  `agno_session_contexts` (o simile) nel db.
- Cosa contiene? Un riassunto della sessione corrente?
- Quando si aggiorna?

#### Variante G2 — Script di ispezione delle memorie

Scrivi uno script Python `inspect_memories.py` che usa Agno per leggere le
memorie del db. `learning_machine` è una **property** sull'Agent (non un
metodo `get_learning_machine()`):

```python
from recipebot import recipebot

lm = recipebot.learning_machine
lm.user_profile_store.print(user_id="marco@test.it")
lm.user_memory_store.print(user_id="marco@test.it")
```

Esegui con `python inspect_memories.py` e osserva cosa hai trovato.

#### Variante G3 — Cambia modalità

Cambia `mode=LearningMode.AGENTIC` in `mode=LearningMode.ALWAYS` per
`UserMemoryConfig`.

**Cosa osservare**:
- Le memorie vengono catturate ugualmente, ma **senza tool call visibili**
  nelle trace.
- C'è una differenza percepibile in quanto vengono catturate? (Always cattura
  più informazioni implicite, Agentic dipende dalla decisione del modello.)

---

## Trace Analysis — esercizio di osservazione

Per uno dei due task che hai scelto, dopo averlo completato e testato con un
prompt, **vai nelle Traces** del Control Plane, apri la trace dell'ultima run,
e rispondi mentalmente (o nei tuoi appunti) a queste tre domande. Le useremo
come spunto di discussione nella prossima lezione.

Per l'altro task fai solo una versione rapida: annota l'ordine dei tool
chiamati e un comportamento interessante.

### 1. Quali tool sono stati chiamati e in che ordine?

Lista cronologica. Esempio: *"think → search_knowledge_base →
find_recipes_by_constraints → analyze"*. Includi anche tool implicitati
(come `search_knowledge_base` se attivo).

### 2. Quanto tempo ha richiesto ciascuno?

Stima in secondi (o decimi). Quale tool è stato il più lento? Per quale
ragione?

### 3. Un comportamento "interessante"

**Almeno una** delle seguenti, a tua scelta:
- Un tool chiamato che non ti aspettavi
- Un tool **non** chiamato che ti aspettavi
- Una query riformulata in modo strano (es. `search_knowledge_base` con
  query molto diversa dal prompt utente)
- Un tempo molto più alto/basso del previsto
- Una decisione del modello (visibile nel reasoning) che ti ha sorpreso

Annota 2-3 righe descrivendo cosa hai notato e una possibile spiegazione.

> **Importante**: la trace analysis non è "trovare il bug". È **osservazione
> strutturata**. Va bene anche concludere con "tutto è andato come mi
> aspettavo, e l'unica cosa interessante è che `analyze` è stato veloce —
> 0.05s — perché il modello aveva già tutto chiaro".

---

## API Crib Sheet — pattern Agno pronti all'uso

Snippet pronti per i pattern visti nei sette blocchi di RecipeBot v1. Tienilo
sotto mano durante l'esercitazione.

### 1 · Setup minimale di un Agent + AgentOS

```python
from dotenv import load_dotenv
load_dotenv()  # PRIMA degli import Agno

from agno.agent import Agent
from agno.models.google import Gemini
from agno.db.sqlite import SqliteDb
from agno.os import AgentOS

db = SqliteDb(db_file="tmp/recipebot.db")

agent = Agent(
    name="MyAgent",
    model=Gemini(id="gemini-2.5-flash"),
    db=db,
    instructions=["..."],
    debug_mode=True,
    markdown=True,
)

agent_os = AgentOS(name="My OS", agents=[agent], db=db, tracing=True)
app = agent_os.get_app()  # ← FastAPI app
```

Avvio: `fastapi dev recipebot.py` → `http://localhost:8000`

### 2 · Tool custom con `@tool`

```python
from agno.tools import tool

@tool
def my_tool(param1: str, param2: int = 10) -> dict:
    """Descrizione concisa di cosa fa il tool.

    Args:
        param1: cosa è
        param2: cosa è (default: 10)

    Returns:
        Dizionario con campi X, Y, Z
    """
    return {"result": ...}

# Nell'Agent:
tools=[my_tool, ...]
```

**Classificazione del rischio**:
- `READ-ONLY`: non modifica nulla all'esterno (es. ricerche, calcoli)
- `STATE UPDATE`: modifica file/db locali (es. salva una shopping list)
- `EXTERNAL CALL`: chiama API esterne (es. invia email, paga)

### 3 · Output strutturato con Pydantic

```python
from pydantic import BaseModel, Field

class MyOutput(BaseModel):
    field_a: str = Field(description="Cosa è il campo A.")
    field_b: list[str] = Field(default_factory=list, description="...")

# Nell'Agent:
output_schema=MyOutput,
use_json_mode=True,  # ← OBBLIGATORIO con Gemini se ci sono anche tool
```

**Trappola Gemini**: senza `use_json_mode=True`, errore 400 INVALID_ARGUMENT
quando `tools` e `output_schema` sono attivi insieme.

### 4 · Reasoning esplicito con `ReasoningTools`

```python
from agno.tools.reasoning import ReasoningTools

tools=[
    ReasoningTools(add_instructions=True),  # ← think() + analyze()
    # ... gli altri tool
]
```

**Configurazioni alternative** (utile per il Bonus F):
```python
ReasoningTools(add_instructions=True, enable_analyze=False)  # solo think
ReasoningTools(add_instructions=True, enable_think=False)    # solo analyze
```

**Importante**: aggiungere `stream_events=True` nell'Agent per evitare che i
payload di `analyze()` finiscano dentro la bubble della risposta finale.

### 5 · Knowledge base con LanceDB + Agentic RAG

```python
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.embedder.google import GeminiEmbedder
from agno.vectordb.lancedb import LanceDb, SearchType

knowledge = Knowledge(
    vector_db=LanceDb(
        table_name="my_knowledge",
        uri="tmp/lancedb",
        search_type=SearchType.vector,  # vector consigliato
        embedder=GeminiEmbedder(),
    ),
)

# Inserimento
knowledge.insert(path="docs/file.md")     # file locale
knowledge.insert(url="https://...")        # URL
knowledge.insert(text_content="testo...")  # stringa

# Nell'Agent (servono ENTRAMBE le righe):
knowledge=knowledge,
search_knowledge=True,  # ← attiva il pattern Agentic RAG
```

**Trappole**:
- `SearchType.hybrid` richiede un indice FTS che spesso non viene creato
  automaticamente. Con `vector` parti senza problemi.
- `search_knowledge=True` è **obbligatorio**: senza, la KB è inerte.
- Se cambi configurazione, **cancella `tmp/lancedb/`** prima di riavviare.

### 6 · LearningMachine (memoria utente cross-sessione)

```python
from agno.learn import (
    LearningMachine, LearningMode,
    UserProfileConfig, UserMemoryConfig,
)

# Nell'Agent:
learning=LearningMachine(
    user_profile=UserProfileConfig(mode=LearningMode.AGENTIC),
    user_memory=UserMemoryConfig(mode=LearningMode.AGENTIC),
),
```

**Trappole**:
- `learning=True` crea una `LearningMachine` di default con `user_profile`
  e `user_memory` attivi (Agno 2.6.4). Va bene per partire, ma se vuoi
  controllare le `mode` o aggiungere altri store devi passare un oggetto
  `LearningMachine` esplicito.
- Per default tutti gli store sono disabilitati quando costruisci tu la
  `LearningMachine`. Se configuri solo `user_profile`, l'agente ricorda
  il nome ma non le osservazioni libere (allergie, preferenze).
- Sia profili che memorie finiscono nella stessa tabella `agno_learnings`,
  distinte dal campo `learning_type` (`user_profile` vs `user_memory`).
  La dashboard "Memory" del Control Plane legge `agno_memories` (sistema
  legacy diverso) — può mostrare "vuoto" anche con la LearningMachine
  funzionante.

**Modes**:

| Mode | Quando salva | Tool visibili in trace |
|---|---|---|
| `LearningMode.ALWAYS` | Dopo ogni run, automatico | No |
| `LearningMode.AGENTIC` | Decide il modello | Sì (`update_user_memory`, ecc.) |
| `LearningMode.PROPOSE` | Modello propone, utente conferma | Sì |

### 7 · I 6 Learning Stores (panoramica)

| Store | Cosa contiene | Scope |
|---|---|---|
| **User Profile** | Campi strutturati (nome, lingua) | Per utente |
| **User Memory** | Osservazioni libere | Per utente |
| **Session Context** | Stato della sessione corrente | Per sessione |
| **Entity Memory** | Fatti su entità esterne | Configurabile |
| **Learned Knowledge** | Insight trasferibili tra utenti | Configurabile |
| **Decision Log** | Decisioni con motivazione | Per agente |

**Decision tree pratico** (cosa va dove):

```
Devo memorizzare un'informazione
  ├─ è un fatto sul mondo? → Knowledge
  └─ è legato a UN utente?
        ├─ sì
        │   ├─ strutturato (nome, ruolo) → User Profile
        │   └─ libero (preferenze, comportamento) → User Memory
        └─ no
              ├─ entità esterne (companies) → Entity Memory
              └─ insight trasferibile → Learned Knowledge
```

### 8 · Ispezione del database SQLite

```bash
# Lista tabelle
sqlite3 tmp/recipebot.db ".tables"

# Tutto ciò che la LearningMachine ha salvato (profili + memorie)
sqlite3 tmp/recipebot.db "SELECT learning_type, user_id, content FROM agno_learnings;" -header -column

# Solo i profili utente
sqlite3 tmp/recipebot.db "SELECT user_id, content FROM agno_learnings WHERE learning_type='user_profile';" -header -column

# Solo le memorie libere
sqlite3 tmp/recipebot.db "SELECT user_id, content FROM agno_learnings WHERE learning_type='user_memory';" -header -column

# Pulizia (per ripartire)
sqlite3 tmp/recipebot.db "DELETE FROM agno_learnings;"
```

> Nota: in Agno 2.6.4 sia profili che memorie vivono nella stessa tabella
> `agno_learnings`, distinti da `learning_type`. I nomi esatti possono
> cambiare tra versioni di Agno.

### 9 · Pattern di lavoro per i task

1. **Modifica `recipebot.py`**, salva.
2. `fastapi dev` ricarica automaticamente.
3. Apri `http://localhost:8000`.
4. **Crea una nuova sessione** (importante: nuova, per ogni test serio).
5. Manda il prompt di test.
6. Vai nelle **Traces** → trace della run più recente.
7. Per memorie cross-sessione: chiudi la sessione, **mantieni lo stesso
   `user_id`**, apri una nuova sessione.

### 10 · Comandi utili

| Cosa | Comando |
|---|---|
| Avvio server | `fastapi dev recipebot.py` |
| Aggiunta dipendenze | `uv add <package>` |
| Reset vector DB | `rm -rf tmp/lancedb/` |
| Reset memorie e profili | `sqlite3 tmp/recipebot.db "DELETE FROM agno_learnings;"` |
| Reset tutto | `rm -rf tmp/` (poi riavvio) |
| Ispezione tabelle | `sqlite3 tmp/recipebot.db ".tables"` |

### 11 · Documentazione di riferimento

- Agno: <https://docs.agno.com>
- Knowledge: <https://docs.agno.com/knowledge>
- Learning: <https://docs.agno.com/learning>
- Reasoning: <https://docs.agno.com/reasoning>
- Tool: <https://docs.agno.com/tools/tools>

---

## Se sei bloccato

Cerca in quest'ordine:

1. **Il debug output** nel terminale di `fastapi dev`. Le sezioni
   `<system_message>`, `<user_profile>`, `<user_memory>` ti dicono *cosa sta
   vedendo il modello*.
2. **Le trace** nel Control Plane. Ogni run ha un albero di span: tool call,
   reasoning, retrieval. Cliccando su uno span vedi argomenti e risultati.
3. **L'API Crib Sheet** qui sopra — pattern pronti per import e
   configurazione.
4. **Il docente o un compagno**. Una mano alzata vale più di 30 minuti di
   muro contro muro.

---

## Cosa NON è questa esercitazione

- **Non è un progetto d'esame**. Il progetto d'esame ti verrà assegnato più
  avanti, e sarà più ampio.
- **Non è una valutazione di "soluzione corretta"**. Quasi tutti i task hanno
  più soluzioni valide.
- **Non è "tutto deve funzionare al primo colpo"**. Se qualcosa rompe il
  comportamento dell'agente, va benissimo: prova a capire perché. Un
  esperimento fallito che capisci vale più di uno riuscito che non sai
  spiegare.