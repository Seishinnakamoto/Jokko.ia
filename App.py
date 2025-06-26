from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from mangum import Mangum

class ChatRequest(BaseModel):
    message: str
    language: str = "it"
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    language: str
    sources: List[Dict] = []
    category: Optional[str] = None
    confidence: float = 0.0

SUPPORTED_LANGUAGES = {
    "it": "Italiano", "fr": "Français", "en": "English", "wo": "Wolof",
    "bm": "Bambara", "ha": "Hausa", "am": "Amarico", "ti": "Tigrinya",
    "lg": "Lingala", "ff": "Pulaar", "so": "Soninke"
}

SAMPLE_RESPONSES = {
    "it": {
        "permesso_soggiorno": "Per il permesso di soggiorno devi recarti in Questura con passaporto, foto tessera, marca da bollo da €16...",
        "lavoro": "Per cercare lavoro in Italia puoi usare i centri per l'impiego, InfoJobs, agenzie interinali...",
        "casa": "Per trovare casa puoi usare Immobiliare.it, Subito, Idealista o contattare associazioni locali...",
        "sanita": "Il SSN garantisce cure gratuite: chiedi la tessera sanitaria alla ASL e scegli un medico di base...",
        "diritti": "Hai diritto a: assistenza legale gratuita, protezione dalla discriminazione, accesso alla sanità e istruzione...",
        "default": "Ciao! Sono JOKKO AI. Posso aiutarti su: permesso di soggiorno, lavoro, casa, sanità, diritti. Dimmi pure!"
    },
    "en": {
        "permesso_soggiorno": "For residence permit, go to Questura with passport, ID photo, €16 tax stamp...",
        "lavoro": "To find work in Italy: register at job centers, use InfoJobs, temp agencies...",
        "casa": "To find a house, use Immobiliare.it, Idealista, or contact local associations...",
        "sanita": "Italy provides free healthcare: get your health card at ASL and choose a GP...",
        "diritti": "You have the right to free legal aid, education, work and healthcare...",
        "default": "Hello! I’m JOKKO AI. I can help with: residence permit, work, housing, healthcare, rights."
    },
    "fr": {
        "permesso_soggiorno": "Pour le titre de séjour, allez à la Questura avec passeport, photos, timbre fiscal de 16€...",
        "lavoro": "Pour trouver du travail : centres d'emploi, InfoJobs, agences intérimaires...",
        "casa": "Utilisez Immobiliare.it, Idealista ou contactez les associations locales...",
        "sanita": "Le SSN fournit des soins gratuits : demandez votre carte sanitaire à l'ASL...",
        "diritti": "Vous avez droit à : aide juridique, santé, travail régulier, éducation...",
        "default": "Salut ! Je suis JOKKO AI. Je peux vous aider avec : séjour, travail, logement, santé, droits."
    }
}

app = FastAPI(
    title="JOKKO AI",
    description="Chatbot AI multilingue per migranti africani in Italia",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "JOKKO AI - La tua voce, la tua strada",
        "services": list(SAMPLE_RESPONSES["it"].keys()),
        "languages": SUPPORTED_LANGUAGES
    }

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "message": "JOKKO AI funzionante",
        "languages": SUPPORTED_LANGUAGES
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest):
    try:
        message = chat_request.message.lower()
        language = chat_request.language if chat_request.language in SAMPLE_RESPONSES else "it"
        answers = SAMPLE_RESPONSES[language]

        if any(k in message for k in ["permesso", "soggiorno", "séjour", "permit"]):
            response = answers["permesso_soggiorno"]
            category = "permesso_soggiorno"
            confidence = 0.9
        elif any(k in message for k in ["lavoro", "job", "work", "emploi"]):
            response = answers["lavoro"]
            category = "lavoro"
            confidence = 0.85
        elif any(k in message for k in ["casa", "house", "logement", "rent"]):
            response = answers["casa"]
            category = "casa"
            confidence = 0.85
        elif any(k in message for k in ["salute", "health", "santé", "doctor"]):
            response = answers["sanita"]
            category = "sanita"
            confidence = 0.85
        elif any(k in message for k in ["diritti", "rights", "droits", "legal"]):
            response = answers["diritti"]
            category = "diritti"
            confidence = 0.85
        else:
            response = answers["default"]
            category = "generale"
            confidence = 0.7

        return ChatResponse(
            response=response,
            language=language,
            sources=[
                {"title": "JOKKO KB", "url": "https://ym.vercel.app"},
                {"title": "Ministero Interno", "url": "https://www.interno.gov.it"}
            ],
            category=category,
            confidence=confidence
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore: {str(e)}")

handler = Mangum(app)
