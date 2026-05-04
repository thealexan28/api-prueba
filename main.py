import contextlib
from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, field_validator

from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolResult, TextContent
from mcp.server.transport_security import TransportSecuritySettings


# ============================================================
# 1. Servidor MCP para ChatGPT Apps
# ============================================================

mcp = FastMCP(
    name="Asistente Unicaja MCP",
    host="0.0.0.0",
    stateless_http=True,
    json_response=True,
    streamable_http_path="/mcp",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[
            "api-prueba-l1sn.onrender.com",
            "api-prueba-l1sn.onrender.com:*",
            "localhost:*",
            "127.0.0.1:*",
        ],
        allowed_origins=[
            "https://chatgpt.com",
            "https://chat.openai.com",
            "http://localhost:*",
            "http://127.0.0.1:*",
        ],
    ),
)


# ============================================================
# 2. Lógica actual de tu API
# ============================================================

_SUFIJO = " Esta es una respuesta simulada de pruebas."

_KEYWORDS_GENERALES: list[tuple[tuple[str, ...], str]] = [
    (
        ("tarjeta",),
        "Unicaja dispone de distintos tipos de tarjetas, como débito, crédito y prepago." + _SUFIJO,
    ),
    (
        ("cuenta",),
        "Unicaja ofrece varias modalidades de cuentas corrientes y de ahorro." + _SUFIJO,
    ),
    (
        ("cajero",),
        "Puedes localizar cajeros y oficinas desde los canales oficiales de Unicaja." + _SUFIJO,
    ),
]

_KEYWORDS_HIPOTECAS: list[tuple[tuple[str, ...], str]] = [
    (
        ("fija",),
        "Unicaja comercializa hipotecas a tipo fijo." + _SUFIJO,
    ),
    (
        ("variable",),
        "Unicaja comercializa hipotecas a tipo variable." + _SUFIJO,
    ),
    (
        ("mixta",),
        "Unicaja puede ofrecer modalidades de hipoteca mixta según campaña y perfil." + _SUFIJO,
    ),
    (
        ("requisitos", "document"),
        "Para una hipoteca suelen solicitarse ingresos, identificación y documentación del inmueble." + _SUFIJO,
    ),
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
    pregunta_normalizada = pregunta.lower().strip()

    for keywords, respuesta in keyword_map:
        if any(kw in pregunta_normalizada for kw in keywords):
            return RespuestaResponse(respuesta=respuesta, categoria=categoria)

    return RespuestaResponse(respuesta=default, categoria=categoria)


def resolver_consulta_general(pregunta: str) -> RespuestaResponse:
    return _resolver(
        pregunta,
        "general",
        _KEYWORDS_GENERALES,
        "Consulta general recibida correctamente. Esta es una respuesta simulada del asistente de Unicaja.",
    )


def resolver_consulta_hipotecas(pregunta: str) -> RespuestaResponse:
    return _resolver(
        pregunta,
        "hipotecas",
        _KEYWORDS_HIPOTECAS,
        "Consulta de hipotecas recibida correctamente. Esta es una respuesta simulada del asistente hipotecario de Unicaja.",
    )


# ============================================================
# 3. Tools MCP que ChatGPT podrá llamar
# ============================================================

@mcp.tool()
def consulta_general_unicaja(pregunta: str) -> CallToolResult:
    """
    Responde consultas generales sobre Unicaja: tarjetas, cuentas, cajeros,
    oficinas, banca digital y servicios generales.

    Usa esta herramienta cuando el usuario pregunte por información general
    de Unicaja que no sea específicamente hipotecaria.
    """
    resultado = resolver_consulta_general(pregunta)

    return CallToolResult(
        content=[
            TextContent(
                type="text",
                text=resultado.respuesta,
            )
        ],
        structuredContent={
            "respuesta": resultado.respuesta,
            "categoria": resultado.categoria,
            "origen": "api_pruebas_unicaja",
        },
        _meta={
            "tool": "consulta_general_unicaja",
            "pregunta_original": pregunta,
        },
    )


@mcp.tool()
def consulta_hipotecas_unicaja(pregunta: str) -> CallToolResult:
    """
    Responde consultas sobre hipotecas de Unicaja: hipoteca fija, variable,
    mixta, requisitos y documentación.

    Usa esta herramienta cuando el usuario pregunte específicamente por
    hipotecas, préstamos hipotecarios, condiciones hipotecarias o requisitos
    para contratar una hipoteca.
    """
    resultado = resolver_consulta_hipotecas(pregunta)

    return CallToolResult(
        content=[
            TextContent(
                type="text",
                text=resultado.respuesta,
            )
        ],
        structuredContent={
            "respuesta": resultado.respuesta,
            "categoria": resultado.categoria,
            "origen": "api_pruebas_unicaja",
        },
        _meta={
            "tool": "consulta_hipotecas_unicaja",
            "pregunta_original": pregunta,
        },
    )


# ============================================================
# 4. FastAPI + lifespan del servidor MCP
# ============================================================

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp.session_manager.run():
        yield


app = FastAPI(
    title="API de Pruebas - Asistente Unicaja",
    description="API sencilla para simular un asistente con endpoints de consultas generales, hipotecas y MCP.",
    version="1.1.0",
    lifespan=lifespan,
)


# Importante para clientes tipo navegador / ChatGPT.
# En producción, cambia allow_origins=["*"] por tus dominios concretos.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],
)


# ============================================================
# 5. Endpoints REST originales
# ============================================================

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
          Esta API es una API de pruebas utilizada por un GPT personalizado o una app de ChatGPT
          para simular respuestas relacionadas con consultas generales e hipotecas.
        </p>

        <h2>Datos que recibimos</h2>
        <p>
          La API puede recibir el texto de la pregunta introducida por el usuario.
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
      </body>
    </html>
    """


@app.post("/consultas/generales", response_model=RespuestaResponse)
def consultas_generales(body: PreguntaRequest):
    return resolver_consulta_general(body.pregunta)


@app.post("/consultas/hipotecas", response_model=RespuestaResponse)
def consultas_hipotecas(body: PreguntaRequest):
    return resolver_consulta_hipotecas(body.pregunta)


# ============================================================
# 6. Montar MCP en /mcp
# ============================================================

app.mount("/", mcp.streamable_http_app())
