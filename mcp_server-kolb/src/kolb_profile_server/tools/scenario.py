from __future__ import annotations

from kolb_profile_server.data.scenarios import DIMENSIONS, SCENARIOS_BY_ID, TOTAL_SCENARIOS


# Orden fijo de presentación de los 12 escenarios.
# Los 6 primeros son exploratorios (distribución uniforme de dimensiones),
# los siguientes 3 refuerzan las dimensiones más débiles del perfil parcial,
# y los últimos 3 confirman las dimensiones más fuertes.
_BASE_ORDER = [1, 4, 7, 10, 2, 8, 5, 11, 3, 9, 6, 12]


def _tally(history: list[dict]) -> dict[str, int]:
    """Cuenta cuántas respuestas hay por dimensión en el historial."""
    counts: dict[str, int] = {d: 0 for d in DIMENSIONS}
    for entry in history:
        dim = entry.get("dimension")
        if dim in counts:
            counts[dim] += 1
    return counts


def get_next_scenario(history: list[dict]) -> dict | None:
    """Elige el próximo escenario Kolb en función del historial de respuestas.

    Parámetros
    ----------
    history:
        Lista de dicts con las respuestas dadas hasta ahora. Cada entrada debe
        tener al menos:
            - ``scenario_id`` (int): id del escenario respondido.
            - ``option_id``   (str): id de la opción elegida ("A", "B" o "C").
            - ``dimension``   (str): dimensión de la opción elegida
                                     ("EC", "OR", "CA" o "EA").

    Retorno
    -------
    dict con las claves:
        - ``scenario``      : el escenario completo (id, titulo, contexto, opciones).
        - ``position``      : número de pregunta (1-based).
        - ``remaining``     : escenarios que quedan por responder.
        - ``partial_scores``: conteo parcial de dimensiones hasta el momento.
    Retorna ``None`` si el test ya fue completado (12 escenarios respondidos).
    """
    answered_ids: set[int] = {entry["scenario_id"] for entry in history}

    if len(answered_ids) >= TOTAL_SCENARIOS:
        return None

    position = len(answered_ids) + 1

    # --- Fase exploratoria (primeras 6 preguntas): seguimos el orden base ---
    if position <= 6:
        for sid in _BASE_ORDER:
            if sid not in answered_ids:
                scenario = SCENARIOS_BY_ID[sid]
                break
    else:
        # --- Fase adaptativa (preguntas 7-12) ---
        # Calculamos el perfil parcial y priorizamos escenarios que refuerzan
        # las dimensiones menos exploradas.
        counts = _tally(history)

        # Escenarios pendientes con su «dimensión primaria» (la dimensión
        # mayoritaria entre sus opciones).
        pending: list[tuple[int, str]] = []
        for sid in _BASE_ORDER:
            if sid not in answered_ids:
                sc = SCENARIOS_BY_ID[sid]
                dim_counts: dict[str, int] = {d: 0 for d in DIMENSIONS}
                for opt in sc["opciones"]:
                    d = opt.get("dimension")
                    if d in dim_counts:
                        dim_counts[d] += 1
                primary_dim = max(dim_counts, key=lambda d: dim_counts[d])
                pending.append((sid, primary_dim))

        # Ordenamos: primero los escenarios cuya dimensión primaria tiene menos
        # respuestas acumuladas (equilibrio), conservando el orden base como
        # desempate implícito (lista ya ordenada por _BASE_ORDER).
        pending.sort(key=lambda t: counts.get(t[1], 0))
        scenario = SCENARIOS_BY_ID[pending[0][0]]

    partial_scores = _tally(history)

    return {
        "scenario": scenario,
        "position": position,
        "remaining": TOTAL_SCENARIOS - position,
        "partial_scores": partial_scores,
    }
