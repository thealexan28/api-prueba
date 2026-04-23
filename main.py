from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal

app = FastAPI(
    title="API de Pruebas - Asistente Unicaja",
    description="API sencilla para simular un asistente con endpoints de consultas generales e hipotecas.",
    version="1.0.0",
)

class PreguntaRequest(BaseModel):
    pregunta: str = Field(..., description="Pregunta exacta del usuario")

class RespuestaResponse(BaseModel):
    respuesta: str
    categoria: Literal["general", "hipotecas"]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/consultas/generales", response_model=RespuestaResponse)
def consultas_generales(body: PreguntaRequest):
    pregunta = body.pregunta.lower().strip()

    if not pregunta:
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía")

    if "tarjeta" in pregunta:
        respuesta = (
            "Unicaja dispone de distintos tipos de tarjetas, como débito, crédito y prepago. "
            "Esta es una respuesta simulada de pruebas."
        )
    elif "cuenta" in pregunta:
        respuesta = (
            "Unicaja ofrece varias modalidades de cuentas corrientes y de ahorro. "
            "Esta es una respuesta simulada de pruebas."
        )
    elif "cajero" in pregunta:
        respuesta = (
            "Puedes localizar cajeros y oficinas desde los canales oficiales de Unicaja. "
            "Esta es una respuesta simulada de pruebas."
        )
    else:
        respuesta = (
            "Consulta general recibida correctamente. "
            "Esta es una respuesta simulada del asistente de Unicaja."
        )

    return {"respuesta": respuesta, "categoria": "general"}

@app.post("/consultas/hipotecas", response_model=RespuestaResponse)
def consultas_hipotecas(body: PreguntaRequest):
    pregunta = body.pregunta.lower().strip()

    if not pregunta:
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía")

    if "fija" in pregunta:
        respuesta = (
            "Unicaja comercializa hipotecas a tipo fijo. "
            "Esta es una respuesta simulada de pruebas."
        )
    elif "variable" in pregunta:
        respuesta = (
            "Unicaja comercializa hipotecas a tipo variable. "
            "Esta es una respuesta simulada de pruebas."
        )
    elif "mixta" in pregunta:
        respuesta = (
            "Unicaja puede ofrecer modalidades de hipoteca mixta según campaña y perfil. "
            "Esta es una respuesta simulada de pruebas."
        )
    elif "requisitos" in pregunta or "document" in pregunta:
        respuesta = (
            "Para una hipoteca suelen solicitarse ingresos, identificación y documentación del inmueble. "
            "Esta es una respuesta simulada de pruebas."
        )
    else:
        respuesta = (
            "Consulta de hipotecas recibida correctamente. "
            "Esta es una respuesta simulada del asistente hipotecario de Unicaja."
        )

    return {"respuesta": respuesta, "categoria": "hipotecas"}