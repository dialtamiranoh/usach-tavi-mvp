from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
import json
import unicodedata
import requests
import re

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_PATH = BASE_DIR / "knowledge.json"

with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
    KNOWLEDGE = json.load(f)

LLM_URL = "http://127.0.0.1:8001/v1/chat/completions"
LLM_MODEL = "arco-llm"


class Question(BaseModel):
    query: str


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    return text


def clean_model_text(text: str) -> str:
    text = text.replace("\\n", " ")
    text = text.replace("\n", " ")
    text = text.replace("\r", " ")
    text = text.replace('"', "")
    text = text.replace("•", " ")
    text = text.replace("*", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def generate_llm_response(user_query: str, item: dict) -> str:
    system_prompt = (
        "eres ARCO, un asistente para el registro civil y su orientacion. "
        "responde solo con la informacion entregada. "
        "no inventes requisitos, costos, plazos ni pasos. "
        "responde en espanol claro, breve y natural. "
        "usa un solo parrafo, sin listas, sin saltos de linea y con maximo 3 oraciones. "
        "menciona si el tramite requiere atencion presencial, si requiere clave unica y termina con la fuente oficial."
    )

    context = f"""
tramite: {item['titulo']}
respuesta base: {item['respuesta']}
canal: {item['canal']}
presencialidad: {item['presencialidad']}
requiere clave unica: {item['requiere_clave_unica']}
fuente oficial: {item['fuente']}
""".strip()

    user_prompt = f"""
pregunta del usuario: {user_query}

informacion del tramite:
{context}

redacta una respuesta breve de orientacion para el usuario.
""".strip()

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 120
    }

    response = requests.post(LLM_URL, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()

    raw_text = data["choices"][0]["message"]["content"].strip()
    return clean_model_text(raw_text)


@app.get("/")
def read_root():
    return {"message": "ARCO backend funcionando con LLM local"}


@app.post("/ask")
def ask_question(question: Question):
    query = normalize_text(question.query)

    for item in KNOWLEDGE:
        for keyword in item["keywords"]:
            if normalize_text(keyword) in query:
                try:
                    respuesta_ia = generate_llm_response(question.query, item)
                except Exception:
                    respuesta_ia = clean_model_text(item["respuesta"])

                return {
                    "tramite": item["titulo"],
                    "respuesta": respuesta_ia,
                    "canal": item["canal"],
                    "presencialidad": item["presencialidad"],
                    "requiere_clave_unica": item["requiere_clave_unica"],
                    "fuente": item["fuente"]
                }

    if "licencia de conducir" in query or "renovar licencia" in query:
        return {
            "tramite": "Fuera del alcance de ARCO",
            "respuesta": "La renovacion de licencia de conducir no corresponde al Registro Civil. ARCO esta enfocado en tramites del Registro Civil y su orientacion.",
            "canal": None,
            "presencialidad": None,
            "requiere_clave_unica": None,
            "fuente": "https://www.chileatiende.gob.cl/fichas/20592-licencias-de-conducir"
        }

    return {
        "tramite": "No identificado",
        "respuesta": "ARCO todavia no tiene informacion suficiente para orientar ese tramite dentro del alcance actual del demo.",
        "canal": None,
        "presencialidad": None,
        "requiere_clave_unica": None,
        "fuente": None
    }