import json


KOLB_THEORY_CONTENT = {
    "titulo": "Fundamentos Teóricos del Inventario de Estilos de Aprendizaje de Kolb",
    "version": "1.1",
    "enfoque": "Psicopedagogía Constructivista",
    "descripcion_modelo": "El modelo de Kolb sostiene que el aprendizaje es un proceso cíclico basado en la resolución de tensiones entre el sentir vs. pensar y el observar vs. hacer.",
    "ejes": {
        "percepcion": {
            "EC": "Experiencia Concreta (Sentir): Prioriza la vivencia inmediata y la conexión emocional.",
            "CA": "Conceptualización Abstracta (Pensar): Prioriza el análisis lógico y la sistematización teórica."
        },
        "procesamiento": {
            "OR": "Observación Reflexiva (Observar): Prioriza la introspección y la escucha de múltiples perspectivas.",
            "EA": "Experimentación Activa (Hacer): Prioriza la aplicación práctica y el impacto en el entorno."
        }
    },
    "estilos": [
        {
            "nombre": "Divergente",
            "formula": "EC + OR",
            "descripcion": "Especialista en ver situaciones desde múltiples ángulos. Es imaginativo y sensible.",
            "estrategia_agente": "Usa metáforas, lluvias de ideas y valida sus sentimientos sobre los escenarios."
        },
        {
            "nombre": "Asimilador",
            "formula": "CA + OR",
            "descripcion": "Destaca en la creación de modelos teóricos. Valora la precisión lógica sobre la práctica.",
            "estrategia_agente": "Provee estructuras claras, datos y permite tiempo para el análisis antes de responder."
        },
        {
            "nombre": "Convergente",
            "formula": "CA + EA",
            "descripcion": "Busca la aplicación práctica de las teorías. Es eficiente en la resolución de problemas técnicos.",
            "estrategia_agente": "Plantea problemas que requieran una solución única y directa; enfócate en la utilidad."
        },
        {
            "nombre": "Acomodador",
            "formula": "EC + EA",
            "descripcion": "Orientado a la acción y al riesgo. Aprende por ensayo y error en situaciones nuevas.",
            "estrategia_agente": "Anímalo a experimentar y a liderar la toma de decisiones en el escenario planteado."
        }
    ],
    "instrucciones_agente": {
        "objetivo": "Construir un perfil basado en 12 escenarios evitando el lenguaje técnico durante la charla.",
        "metodologia": "Si el alumno da respuestas ambiguas, utiliza la función de 'sampling' para clasificar la intención en uno de los 4 pilares (EC, CA, OR, EA).",
        "andamiaje": "Una vez identificado el perfil, adapta tu lenguaje para que el feedback sea significativo para ese estilo particular."
    }
}


def register_resources(server) -> None:
    """Register MCP resources for the Kolb theory server."""
    
    @server.resource("kolb://teoria", mime_type="application/json")
    def kolb_teoria() -> dict:
        """Teoría fundamental del modelo de estilos de aprendizaje de Kolb."""
        return {
            "uri": "kolb://teoria",
            "mimeType": "application/json",
            "content": KOLB_THEORY_CONTENT
        }
