from dotenv import load_dotenv

# Carica le variabili da .env (in particolare GOOGLE_API_KEY, MISTRAL_API_KEY ecc...).
# Importante: deve avvenire PRIMA degli import di Agno.
load_dotenv()

from pydantic import BaseModel, Field
import json
from pathlib import Path
from agno.agent import Agent

# from agno.models.google import Gemini
from agno.models.mistral import MistralChat
from agno.models.google import Gemini
from agno.models.groq import Groq
from agno.db.sqlite import SqliteDb
from agno.os import AgentOS
from agno.tools import tool
from agno.tools.reasoning import ReasoningTools
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.embedder.google import GeminiEmbedder
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.learn import (
    LearningMachine,
    LearningMode,
    UserProfileConfig,
    UserMemoryConfig,
)

# region Costanti e setup

RECIPES_DB = [
    {
        "name": "Insalata di ceci e zucchine",
        "ingredients": ["ceci", "zucchine", "limone", "olio"],
        "minutes": 15,
        "tags": ["vegetariano", "vegano", "senza-glutine"],
        "servings": 2,
        "quantities": {
            "ceci": (200, "g"),
            "zucchine": (400, "g"),
            "limone": (100, "g"),
            "olio": (45, "ml"),
        },
    },
    {
        "name": "Riso allo yogurt e zucchine",
        "ingredients": ["riso", "zucchine", "yogurt-greco", "olio"],
        "minutes": 25,
        "tags": ["vegetariano", "senza-glutine"],
        "servings": 2,
        "quantities": {
            "riso": (160, "g"),
            "zucchine": (400, "g"),
            "yogurt-greco": (200, "g"),
            "olio": (1, "ml"),
        },
    },
    {
        "name": "Pasta al pesto di rucola",
        "ingredients": ["pasta", "rucola", "parmigiano", "noci"],
        "minutes": 20,
        "tags": ["vegetariano", "contiene-frutta-secca"],
        "servings": 2,
        "quantities": {
            "pasta": (200, "g"),
            "rucola": (80, "g"),
            "parmigiano": (30, "g"),
            "noci": (30, "g"),
        },
    },
    {
        "name": "Hummus express",
        "ingredients": ["ceci", "limone", "tahini", "aglio"],
        "minutes": 10,
        "tags": ["vegetariano", "vegano", "senza-glutine"],
        "servings": 4,
        "quantities": {
            "ceci": (240, "g"),
            "limone": (25, "ml"),
            "tahini": (30, "g"),
            "aglio": (5, "g"),
        },
    },
]

SHOPPING_LIST_FILE = Path("tmp/shopping_list.json")

# endregion

# region Tools


@tool
def find_recipes_by_constraints(
    available_ingredients: list[str],
    dietary_constraints: list[str] = [],
    excluded_ingredients: list[str] = [],
    max_minutes: int = 60,
) -> list[dict]:
    """Trova ricette compatibili con ingredienti disponibili, ingredienti esclusi, vincoli e tempo.

    Tool READ-ONLY (rischio basso): non modifica nessuno stato esterno.

    Args:
        available_ingredients: ingredienti che l'utente ha a disposizione.
        dietary_constraints: tag dietetici richiesti, es. ["vegetariano", "vegano"].
        excluded_ingredients: ingredienti da escludere, es. ["nocciole"].
        max_minutes: tempo massimo di preparazione in minuti.

    Returns:
        Lista di ricette compatibili.
    """
    available_set = set(
        i.lower() for i in available_ingredients if i not in excluded_ingredients
    )
    constraints_set = set(c.lower() for c in dietary_constraints)

    results = []
    for recipe in RECIPES_DB:
        if recipe["minutes"] > max_minutes:
            continue
        if constraints_set and not constraints_set.issubset(set(recipe["tags"])):
            continue
        recipe_ingredients = set(i.lower() for i in recipe["ingredients"])
        if not recipe_ingredients.issubset(available_set):
            missing = recipe_ingredients - available_set
            if len(missing) > 2:
                continue
        results.append(recipe)

    return results


@tool
def save_shopping_list(items: list[str]) -> str:
    """Salva la lista della spesa su file.

    Tool STATE UPDATE (rischio medio): modifica un file persistente.

    Args:
        items: lista di ingredienti da acquistare.

    Returns:
        Messaggio di conferma con il numero di item salvati.
    """
    SHOPPING_LIST_FILE.parent.mkdir(parents=True, exist_ok=True)
    SHOPPING_LIST_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2))
    return f"Lista della spesa salvata con {len(items)} ingredienti in {SHOPPING_LIST_FILE}."


@tool
def scale_recipe(recipe_name: str, target_servings: int) -> dict:
    """Riscala gli ingredienti di una ricetta in base al numero di persone previste.
    Ritorna {} in caso di errore.

    Args:
        recipe_name (str): nome della ricetta
        target_servings (int): numero di persone target
    """
    if target_servings <= 0:
        return {}
    for recipe in RECIPES_DB:
        if recipe["name"].lower() == recipe_name.lower():
            quantities = recipe["quantities"]
            servings = recipe["servings"]
            return dict(
                zip(
                    quantities.keys(),
                    (
                        (quantity[0] / servings * target_servings, quantity[1])
                        for quantity in quantities.values()
                    ),
                )
            )
    return {}


# endregion

# region Models


class RecipeRecommendation(BaseModel):
    """Risposta strutturata di RecipeBot."""

    selected_recipe: str = Field(description="Nome della ricetta scelta.")
    estimated_minutes: int = Field(description="Tempo di preparazione in minuti.")
    missing_ingredients: list[str] = Field(
        default_factory=list,
        description="Ingredienti che l'utente deve comprare per fare questa ricetta.",
    )
    quantitaties: dict = Field(
        description="Quantità degli ingredienti scalate per il numero di persone"
    )
    warnings: list[str] = Field(
        default_factory=list,
        description=(
            "Avvisi rilevanti per l'utente: allergeni potenziali, "
            "vincoli a rischio, conflitti dietetici."
        ),
    )
    reason: str = Field(
        description="Breve spiegazione del perché questa ricetta è stata scelta."
    )


# endregion

# region Knowledge Base

knowledge = Knowledge(
    vector_db=LanceDb(
        table_name="recipebot_knowledge",
        uri="tmp/lancedb",
        search_type=SearchType.vector,
        embedder=GeminiEmbedder(),
    ),
)
# endregion

# Inserimento idempotente: se i file non sono cambiati, è veloce.
knowledge.insert(path="docs/ricettario.md")
knowledge.insert(path="docs/allergeni.md")
knowledge.insert(path="docs/sostituzioni_avanzate.md")
knowledge.insert(path="docs/tecniche_di_cottura.md")

# endregion

db = SqliteDb(db_file="tmp/recipebot.db")

recipebot = Agent(
    name="RecipeBot",
    description="Assistente di cucina che propone ricette e gestisce la lista della spesa.",
    model=Gemini(id="gemini-2.5-flash"),
    # model=MistralChat(id="mistral-small-latest"),
    #model=Groq(id="llama-3.3-70b-versatile"),
    db=db,
    instructions=[
        "Sei RecipeBot, un assistente di cucina.",
        "Distingui i vincoli HARD (allergie, diete) dalle preferenze SOFT (gusti).",
        "Non suggerire mai ingredienti che violino le allergie dichiarate dall'utente.",
        "Quando l'utente non specifica un vincolo, chiedi prima di assumere.",
        "Per richieste con più vincoli, usa think() per decomporli prima di agire.",
        "Dopo aver chiamato find_recipes_by_constraints, usa analyze() per valutare i risultati.",
        "Se nessuna ricetta soddisfa i vincoli, segnala il conflitto in warnings.",
        "Usa find_recipes_by_constraints per cercare ricette compatibili",
        "In find_recipes_by_constraints le allergie vanno passate come excluded_ingredients, non come dietary_constraints.",
        "Usa save_shopping_list quando l'utente chiede di salvare gli ingredienti mancanti.",
        "Usa scale_recipe() per riscalare gli ingredienti di una ricetta in base al numero di persone previste",
        "Restituisci sempre una raccomandazione strutturata secondo lo schema RecipeRecommendation.",
        "Consulta la knowledge base per: tecniche di cottura, allergeni, sostituzioni di ingredienti, sostituzioni di ingredienti con varianti vegane.",
        "Consulta la knowledge base per richieste che riguardano le tecniche di cottura senza olio.",
        "Quando l'utente menziona allergie, preferenze o caratteristiche personali, salva queste informazioni nei tool di learning per ricordarle nelle conversazioni future.",
        "Rispondi sempre in modo conciso.",
    ],
    tools=[
        ReasoningTools(add_instructions=True, enable_analyze=False),
        find_recipes_by_constraints,
        save_shopping_list,
        scale_recipe,
    ],
    knowledge=knowledge,
    search_knowledge=True,
    output_schema=RecipeRecommendation,
    use_json_mode=True,
    learning=LearningMachine(
        user_profile=UserProfileConfig(mode=LearningMode.AGENTIC),
        user_memory=UserMemoryConfig(mode=LearningMode.AGENTIC),
    ),
    add_history_to_context=True,
    num_history_runs=3,
    debug_mode=True,
    markdown=True,
)

agent_os = AgentOS(
    name="RecipeBot OS",
    agents=[recipebot],
    db=db,
    tracing=True,
)

app = agent_os.get_app()
