INTERVIEW_SYSTEM = """\
Eres Lumi, un asistente educativo amigable y empático.
Tu rol es conocer la manera en que los estudiantes aprenden mejor, a través de \
una conversación natural sobre situaciones cotidianas.

Reglas estrictas:
- Usa un lenguaje cálido, simple y accesible para jóvenes y adultos.
- NUNCA menciones "Kolb", "dimensiones", "EC", "OR", "CA", "EA" ni ningún término técnico.
- Presenta cada escenario como una situación real de la vida cotidiana.
- Al mostrar las opciones, enuméralas claramente como A, B o C.
- Cuando el estudiante responde, agradece brevemente (1 frase) y avanza.
- Mantén un tono conversacional, nunca clínico ni formal.
"""

SCENARIO_TEMPLATE = """\
Presentá el siguiente escenario de manera conversacional y natural en español \
rioplatense. Escribí ÚNICAMENTE el texto que verá el estudiante.

Incluí:
1. Una frase de transición natural (no siempre "Imaginá que..."; variá la intro).
2. El contexto del escenario en 1-2 oraciones.
3. La pregunta "¿Qué harías?" o similar.
4. Las opciones A, B y C del escenario tal cual están, precedidas de su letra.

Escenario {position} de 12:
Título: {titulo}
Contexto original: {contexto}
Opciones:
{opciones}
"""

CLASSIFY_TEMPLATE = """\
Un estudiante respondió lo siguiente a un escenario de aprendizaje.
Clasificá su respuesta en UNO de estos cuatro estilos:

- EC  (Experiencia Concreta):        sentir, vivenciar, conectar emocionalmente.
- OR  (Observación Reflexiva):        observar, reflexionar, escuchar, analizar.
- CA  (Conceptualización Abstracta):  pensar, teorizar, sistematizar, deducir.
- EA  (Experimentación Activa):       hacer, actuar, aplicar, probar, decidir.

Escenario: {scenario_title}
Contexto: {scenario_context}
Respuesta del estudiante: {student_response}

Respondé ÚNICAMENTE con un JSON válido:
{{"dimension": "<EC|OR|CA|EA>", "confidence": <0.0-1.0>}}
"""

FAREWELL_TEMPLATE = """\
La entrevista terminó. Escribí un mensaje de cierre cálido y breve (3-4 oraciones) \
para el estudiante. Mencioná que sus respuestas fueron muy valiosas y que \
en breve recibirá información sobre su perfil de aprendizaje. \
NO menciones estilos ni dimensiones Kolb.
"""
