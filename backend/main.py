from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama
from typing import List, Optional

app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CompanyInfo(BaseModel):
    name: str
    description: str
    key_products: List[str]
    target_audience: List[str]
    pricing_info: str

class ChatMessage(BaseModel):
    message: str
    company_id: str

# Stockage temporaire des données (à remplacer par une vraie base de données)
companies = {}

# Création d'une entreprise par défaut
default_company = CompanyInfo(
    name="Demo Company",
    description="Une entreprise innovante spécialisée dans les solutions B2B",
    key_products=["Solution CRM", "Plateforme d'automatisation", "Analytics"],
    target_audience=["PME", "Grandes entreprises", "Startups"],
    pricing_info="Tarifs à partir de 99€/mois, avec une version gratuite disponible"
)
companies["demo"] = default_company.dict()

@app.post("/api/companies")
async def create_company(company: CompanyInfo):
    company_id = company.name.lower().replace(" ", "_")
    companies[company_id] = company.dict()
    return {"company_id": company_id}

@app.get("/api/companies/{company_id}")
async def get_company(company_id: str):
    if company_id not in companies:
        raise HTTPException(status_code=404, detail="Company not found")
    return companies[company_id]

@app.post("/api/chat")
async def chat(message: ChatMessage):
    if message.company_id not in companies:
        raise HTTPException(status_code=404, detail="Company not found")
    
    company = companies[message.company_id]
    
    # Construction du prompt pour le LLM
    prompt = f"""
    Tu es un assistant spécialisé dans l'entreprise {company['name']}.
    Voici les informations sur l'entreprise :
    Description : {company['description']}
    Produits clés : {', '.join(company['key_products'])}
    Public cible : {', '.join(company['target_audience'])}
    Informations tarifaires : {company['pricing_info']}

    Question de l'utilisateur : {message.message}
    
    Réponds de manière concise et professionnelle en français.
    """
    
    try:
        response = ollama.chat(model='mistral', messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ])
        return {"response": response['message']['content']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 