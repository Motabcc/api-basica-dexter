from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class Personagem(BaseModel):
    id: int
    nome: str
    status: str

class PersonagemCreate(BaseModel):
    nome: str
    status: str

class Temporada(BaseModel):
    season: int
    personagens: Optional[List[int]] = None

class TemporadaResponse(BaseModel):
    season: int


personagens_db: List[Personagem] = [
    Personagem(id=1, nome="Dexter Morgan", status="VIVO"),
    Personagem(id=2, nome="Debra Morgan", status="VIVA"),
    Personagem(id=3, nome="Sargento Doakes", status="VIVO"),
]

temporadas_personagens = {
    1: [1, 2, 3],
    2: [1, 2],
    3: [3],
    4: [1, 3],
    5: [2],
    6: [],
    7: [1],
    8: [2, 3]
}

temporadas_db: List[Temporada] = [
    Temporada(season=season, personagens=personagens if personagens else None)
    for season, personagens in temporadas_personagens.items()
]

@app.get("/")
def root():
    return {
        "welcome": "Bem-vindo à API do Dexter Show!",
        "personagens_endpoint": "/personagens",
        "temporadas_endpoint": "/seasons"
    }

@app.get("/seasons", response_model=List[TemporadaResponse])
def get_seasons():
    return [{"season": t.season} for t in temporadas_db]

@app.get("/seasons/{season_number}/personagens", response_model=List[Personagem])
def get_personagens_by_season(season_number: int):
    temporada = next((t for t in temporadas_db if t.season == season_number), None)
    if not temporada:
        raise HTTPException(status_code=404, detail="Temporada não encontrada!")

    if not temporada.personagens:
        return []

    personagens = [p for p in personagens_db if p.id in temporada.personagens]
    return personagens

@app.get("/personagens", response_model=List[Personagem])
def list_personagens():
    return personagens_db

@app.get("/personagens/{personagem_id}", response_model=Personagem)
def get_personagem_by_id(personagem_id: int):
    personagem = next((p for p in personagens_db if p.id == personagem_id), None)
    if personagem:
        return personagem
    raise HTTPException(status_code=404, detail="Personagem não encontrado!")

@app.post("/personagens", response_model=Personagem)
def create_personagem(new_personagem: PersonagemCreate):
    new_id = max((p.id for p in personagens_db), default=0) + 1
    personagem = Personagem(id=new_id, **new_personagem.dict())
    personagens_db.append(personagem)
    return personagem

@app.put("/personagens/{personagem_id}", response_model=Personagem)
def update_personagem(personagem_id: int, updated_data: PersonagemCreate):
    for i, personagem in enumerate(personagens_db):
        if personagem.id == personagem_id:
            personagens_db[i] = Personagem(id=personagem_id, **updated_data.dict())
            return personagens_db[i]
    raise HTTPException(status_code=404, detail="Personagem não encontrado!")

@app.delete("/personagens/{personagem_id}")
def delete_personagem(personagem_id: int):
    for i, personagem in enumerate(personagens_db):
        if personagem.id == personagem_id:
            del personagens_db[i]
            return {"detail": "Personagem deletado com sucesso!"}
    raise HTTPException(status_code=404, detail="Personagem não encontrado!")
