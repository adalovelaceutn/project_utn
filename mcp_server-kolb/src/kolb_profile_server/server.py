from mcp.server.fastmcp import FastMCP

from kolb_profile_server.config import setting
from kolb_profile_server.resources.teoria import register_resources
from kolb_profile_server.tools.health import register_tools
from kolb_profile_server.tools.sampling import classify_response
from kolb_profile_server.tools.scenario import get_next_scenario
from kolb_profile_server.tools.teoria import get_profile_theory

server = FastMCP(
    name="kolb-profile-server",
    host=setting.host,
    port=setting.port,
    streamable_http_path=setting.path,
)
register_tools(server)
register_resources(server)

# Expuesto para uvicorn --reload: uvicorn kolb_profile_server.server:asgi_app
asgi_app = server.streamable_http_app()


@server.tool()
def next_scenario(history: list[dict]) -> dict | None:
    """Dado el historial de escenarios respondidos, devuelve el próximo escenario Kolb.

    Parámetros
    ----------
    history:
        Lista de respuestas anteriores. Cada entrada debe contener:
          - scenario_id (int): id del escenario respondido.
          - option_id   (str): id de la opción elegida ("A", "B" o "C").
          - dimension   (str): dimensión de la opción ("EC", "OR", "CA" o "EA").

    Retorna el próximo escenario con su posición y puntajes parciales,
    o null si el test ya fue completado.
    """
    return get_next_scenario(history)


@server.tool()
async def classify_student_response(
    scenario_title: str,
    scenario_context: str,
    student_response: str,
    ctx,
) -> dict:
    """Clasifica una respuesta libre del estudiante en un pilar Kolb usando sampling.

    Útil cuando el alumno responde con texto abierto en lugar de elegir
    la opción A, B o C. Usa el LLM del cliente MCP para inferir la
    dimensión predominante (EC, OR, CA o EA).

    Parámetros
    ----------
    scenario_title:
        Título del escenario (ej. "El electrodoméstico nuevo").
    scenario_context:
        Texto completo del escenario presentado al estudiante.
    student_response:
        Respuesta libre en texto del estudiante.

    Retorna un dict con:
        - dimension  (str | None): pilar Kolb inferido o null si no fue posible.
        - confidence (float):      confianza entre 0.0 y 1.0.
        - raw_response (str):      respuesta cruda del LLM.
    """
    return await classify_response(scenario_title, scenario_context, student_response, ctx)


@server.tool()
def kolb_profile_theory(style: str) -> dict:
    """Devuelve las características teóricas del estilo Kolb solicitado.

    Útil para hidratar componentes de frontend con la descripción completa
    del perfil de aprendizaje del estudiante.

    Parámetros
    ----------
    style:
        Nombre del estilo Kolb: "Divergente", "Asimilador",
        "Convergente" o "Acomodador" (insensible a mayúsculas).

    Retorna un dict con:
        - nombre             (str):  nombre canónico del estilo.
        - formula            (str):  ejes dominantes (ej. "CA + EA").
        - descripcion        (str):  descripción pedagógica del perfil.
        - estrategia_agente  (str):  estrategia sugerida al agente docente.
        - ejes               (dict): descripción de los ejes del modelo.
        - descripcion_modelo (str):  descripción del ciclo de Kolb.
    """
    return get_profile_theory(style)


def main() -> None:
    server.run(transport="streamable-http")


if __name__ == "__main__":
    main()
