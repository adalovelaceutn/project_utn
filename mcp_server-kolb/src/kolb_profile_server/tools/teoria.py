from __future__ import annotations

from kolb_profile_server.resources.teoria import KOLB_THEORY_CONTENT


def get_profile_theory(style: str) -> dict:
    """Devuelve las características teóricas del estilo Kolb solicitado.

    Retorna un dict con:
        - nombre          (str):  nombre canónico del estilo.
        - formula         (str):  ejes dominantes (ej. "CA + EA").
        - descripcion     (str):  descripción pedagógica del perfil.
        - estrategia_agente (str): estrategia sugerida para el agente docente.
        - ejes            (dict): descripción de los ejes de percepción y
                                  procesamiento del modelo Kolb.
        - descripcion_modelo (str): descripción general del ciclo de Kolb.
    Lanza ValueError si el estilo no existe.
    """
    normalized = style.strip().lower()
    match = next(
        (
            item
            for item in KOLB_THEORY_CONTENT.get("estilos", [])
            if isinstance(item, dict)
            and str(item.get("nombre", "")).strip().lower() == normalized
        ),
        None,
    )
    if match is None:
        available = [
            str(item.get("nombre", ""))
            for item in KOLB_THEORY_CONTENT.get("estilos", [])
            if isinstance(item, dict)
        ]
        raise ValueError(
            f"Estilo '{style}' no reconocido. Estilos disponibles: {available}"
        )

    return {
        "nombre": match.get("nombre"),
        "formula": match.get("formula"),
        "descripcion": match.get("descripcion"),
        "estrategia_agente": match.get("estrategia_agente"),
        "ejes": KOLB_THEORY_CONTENT.get("ejes", {}),
        "descripcion_modelo": KOLB_THEORY_CONTENT.get("descripcion_modelo"),
    }
