from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, field_validator
from typing import Literal

app = FastAPI(
    title="API de Pruebas - Asistente Unicaja",
    description="API sencilla para simular un asistente con endpoints de consultas generales e hipotecas.",
    version="1.0.0",
)

_SUFIJO = " Esta es una respuesta simulada de pruebas."

_KEYWORDS_GENERALES: list[tuple[tuple[str, ...], str]] = [
    (("tarjeta",), "Unicaja dispone de distintos tipos de tarjetas, como débito, crédito y prepago." + _SUFIJO),
    (("cuenta",),  "Unicaja ofrece varias modalidades de cuentas corrientes y de ahorro." + _SUFIJO),
    (("cajero",),  "Puedes localizar cajeros y oficinas desde los canales oficiales de Unicaja." + _SUFIJO),
]

_KEYWORDS_HIPOTECAS: list[tuple[tuple[str, ...], str]] = [
    (("fija",),                   "Unicaja comercializa hipotecas a tipo fijo." + _SUFIJO),
    (("variable",),               "Unicaja comercializa hipotecas a tipo variable." + _SUFIJO),
    (("mixta",),                  "Unicaja puede ofrecer modalidades de hipoteca mixta según campaña y perfil." + _SUFIJO),
    (("requisitos", "document"),  "Para una hipoteca suelen solicitarse ingresos, identificación y documentación del inmueble." + _SUFIJO),
]


class PreguntaRequest(BaseModel):
    pregunta: str = Field(..., min_length=1)

    @field_validator("pregunta")
    @classmethod
    def normalizar(cls, v: str) -> str:
        return v.lower().strip()


class RespuestaResponse(BaseModel):
    respuesta: str
    categoria: Literal["general", "hipotecas"]


def _resolver(
    pregunta: str,
    categoria: Literal["general", "hipotecas"],
    keyword_map: list[tuple[tuple[str, ...], str]],
    default: str,
) -> RespuestaResponse:
    for keywords, respuesta in keyword_map:
        if any(kw in pregunta for kw in keywords):
            return RespuestaResponse(respuesta=respuesta, categoria=categoria)
    return RespuestaResponse(respuesta=default, categoria=categoria)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/privacy", response_class=HTMLResponse)
def privacy_policy():
    return """
    <!doctype html>
    <html lang="es">
      <head>
        <meta charset="utf-8" />
        <title>Política de Privacidad</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body style="font-family: system-ui, sans-serif; max-width: 760px; margin: 40px auto; line-height: 1.6; padding: 0 20px;">
        <h1>Política de Privacidad</h1>

        <p>Última actualización: 30 de abril de 2026</p>

        <p>
          Esta API es una API de pruebas utilizada por un GPT personalizado para simular respuestas relacionadas
          con consultas generales e hipotecas.
        </p>

        <h2>Datos que recibimos</h2>
        <p>
          La API puede recibir el texto de la pregunta introducida por el usuario en el GPT personalizado.
          No solicitamos intencionadamente datos personales, bancarios, financieros sensibles ni información confidencial.
        </p>

        <h2>Uso de los datos</h2>
        <p>
          Los datos recibidos se utilizan únicamente para procesar la solicitud del usuario y devolver una respuesta
          simulada a través de la API.
        </p>

        <h2>Almacenamiento</h2>
        <p>
          Esta API de pruebas no almacena de forma permanente las preguntas enviadas por los usuarios.
          Podrían generarse registros técnicos temporales para mantenimiento, seguridad, depuración o funcionamiento del servicio.
        </p>

        <h2>Compartición con terceros</h2>
        <p>
          No vendemos ni compartimos datos personales con terceros, salvo que sea necesario para operar el servicio
          o cumplir obligaciones legales.
        </p>

        <h2>Seguridad</h2>
        <p>
          Aplicamos medidas razonables para proteger la información transmitida a través de la API.
          Aun así, esta API tiene fines de prueba y no debe utilizarse para enviar información sensible.
        </p>

        <h2>Limitación del servicio</h2>
        <p>
          Las respuestas generadas por esta API son simuladas y no constituyen asesoramiento financiero, bancario,
          hipotecario ni legal.
        </p>

        <h2>Contacto</h2>
        <p>
          Para cualquier consulta sobre privacidad, puedes escribir a:
          <a href="mailto:tu-email@dominio.com">tu-email@dominio.com</a>
        </p>

        <h2>Cambios</h2>
        <p>
          Podemos actualizar esta política ocasionalmente. La versión más reciente estará disponible en esta misma URL.
        </p>
      </body>
    </html>
    """


@app.post("/consultas/generales", response_model=RespuestaResponse)
def consultas_generales(body: PreguntaRequest):
    return _resolver(
        body.pregunta,
        "general",
        _KEYWORDS_GENERALES,
        "Consulta general recibida correctamente. Esta es una respuesta simulada del asistente de Unicaja.",
    )


@app.post("/consultas/hipotecas", response_model=RespuestaResponse)
def consultas_hipotecas(body: PreguntaRequest):
    return _resolver(
        body.pregunta,
        "hipotecas",
        _KEYWORDS_HIPOTECAS,
        "Consulta de hipotecas recibida correctamente. Esta es una respuesta simulada del asistente hipotecario de Unicaja.",
    )
