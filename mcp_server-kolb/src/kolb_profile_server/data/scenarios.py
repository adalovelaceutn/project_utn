KOLB_TEST = {
    "test_metadata": {
        "nombre": "Inventario de Estilos de Aprendizaje (Modelo Kolb)",
        "version": "2.0",
        "metodologia": "Constructivista / Escenarios Cotidianos",
        "total_escenarios": 12,
        "dimensiones": ["EC", "OR", "CA", "EA"],
    },
    "configuracion_calculo": {
        "formula_eje_y": "CA - EC",
        "formula_eje_x": "EA - OR",
        "cuadrantes": {
            "Divergente": "Y < 0, X < 0",
            "Asimilador": "Y > 0, X < 0",
            "Convergente": "Y > 0, X > 0",
            "Acomodador": "Y < 0, X > 0",
        },
    },
    "escenarios": [
        {
            "id": 1,
            "titulo": "El electrodoméstico nuevo",
            "contexto": "Compraste una cafetera digital programable o un Smart TV avanzado. Al sacarlo de la caja, ves que tiene muchísimas funciones que no conoces.",
            "opciones": [
                {"id": "A", "texto": "La enchufo y empiezo a probar los botones de inmediato para ver qué hace cada uno.", "dimension": "EC"},
                {"id": "B", "texto": "Busco un video en YouTube de alguien usándola para ver cómo funciona en la práctica antes de tocar nada.", "dimension": "OR"},
                {"id": "C", "texto": "Me siento a leer el manual de instrucciones para entender la lógica de los menús y las funciones técnicas.", "dimension": "CA"},
            ],
        },
        {
            "id": 2,
            "titulo": "El grupo de estudio",
            "contexto": "Te anotas en un curso presencial. En la primera clase, el profesor dice: 'Formen grupos de tres y decidan qué proyecto van a realizar'.",
            "opciones": [
                {"id": "A", "texto": "Me quedo en silencio un momento, escuchando las propuestas de los demás para ver hacia dónde va la energía del grupo.", "dimension": "OR"},
                {"id": "B", "texto": "Tomo la palabra rápido para proponer una idea concreta y empezar a organizar quién hace cada cosa.", "dimension": "EA"},
                {"id": "C", "texto": "Me presento con una sonrisa y trato de conocer primero a mis compañeros para que trabajemos en un clima de confianza.", "dimension": "EC"},
            ],
        },
        {
            "id": 3,
            "titulo": "La falla técnica",
            "contexto": "Estás en medio de un trabajo importante y, de repente, internet deja de funcionar o el programa que usas se cierra solo.",
            "opciones": [
                {"id": "A", "texto": "Me detengo a pensar qué pudo causar el error y trato de deducir lógicamente dónde está el fallo.", "dimension": "CA"},
                {"id": "B", "texto": "Pruebo lo primero que se me ocurre: reinicio todo o toco los cables basándome en lo que me funcionó otras veces.", "dimension": "EC"},
                {"id": "C", "texto": "Busco soluciones rápidas en el celular y aplico diferentes pasos técnicos para ver cuál lo arregla primero.", "dimension": "EA"},
            ],
        },
        {
            "id": 4,
            "titulo": "La Masterclass",
            "contexto": "Estás escuchando a un experto hablar sobre un tema que te interesa mucho, pero utiliza conceptos muy profundos y técnicos.",
            "opciones": [
                {"id": "A", "texto": "Anoto cómo podría aplicar esa idea en mi propio trabajo o rutina mañana mismo.", "dimension": "EA"},
                {"id": "B", "texto": "Me concentro en entender las definiciones y la estructura del argumento para ver si la teoría tiene coherencia.", "dimension": "CA"},
                {"id": "C", "texto": "Dejo que la mente vuele un poco, relacionando lo que dice con situaciones que yo mismo he vivido.", "dimension": "OR"},
            ],
        },
        {
            "id": 5,
            "titulo": "El viaje espontáneo",
            "contexto": "Unos amigos te proponen ir a pasar el día a un pueblo cercano que no conocen. Hay que decidir qué hacer al llegar.",
            "opciones": [
                {"id": "A", "texto": "Digo que sí de inmediato y propongo que decidamos allá, según lo que tengamos ganas de hacer en el momento.", "dimension": "EC"},
                {"id": "B", "texto": "Busco fotos en redes sociales o reseñas en Google para tener una idea clara de qué lugares valen la pena.", "dimension": "OR"},
                {"id": "C", "texto": "Propongo revisar el mapa, calcular los tiempos de viaje y ver qué opciones son más convenientes.", "dimension": "CA"},
            ],
        },
        {
            "id": 6,
            "titulo": "La discusión ajena",
            "contexto": "Dos conocidos están discutiendo acaloradamente sobre un tema polémico en una cena. La situación se pone incómoda.",
            "opciones": [
                {"id": "A", "texto": "Analizo los puntos de vista de ambos en silencio, tratando de entender el trasfondo de su desacuerdo.", "dimension": "OR"},
                {"id": "B", "texto": "Intervengo para cambiar de tema o proponer algo que hacer para que la reunión siga avanzando.", "dimension": "EA"},
                {"id": "C", "texto": "Trato de mediar usando el humor o haciendo que ambos se sientan escuchados para recuperar la armonía.", "dimension": "EC"},
            ],
        },
        {
            "id": 7,
            "titulo": "El mueble para armar",
            "contexto": "Compraste un estante complejo. Al abrir la caja, hay un montón de tornillos, maderas y un folleto de instrucciones largo.",
            "opciones": [
                {"id": "A", "texto": "Extiendo todas las piezas y estudio el diagrama paso a paso para entender la estructura.", "dimension": "CA"},
                {"id": "B", "texto": "Empiezo a armar las piezas que me resultan obvias, confiando en mi capacidad intuitiva.", "dimension": "EC"},
                {"id": "C", "texto": "Busco la primera instrucción y la ejecuto; voy avanzando paso a paso de forma constante.", "dimension": "EA"},
            ],
        },
        {
            "id": 8,
            "titulo": "Nueva habilidad",
            "contexto": "Decidiste que quieres aprender a tocar un instrumento o a realizar una actividad física nueva por hobby.",
            "opciones": [
                {"id": "A", "texto": "Me paso un buen rato mirando tutoriales o viendo a expertos para captar los detalles del movimiento.", "dimension": "OR"},
                {"id": "B", "texto": "Busco información sobre la técnica correcta o la teoría detrás de la actividad.", "dimension": "CA"},
                {"id": "C", "texto": "Agarro el elemento y empiezo a practicar; prefiero sentir el movimiento aunque me equivoque.", "dimension": "EC"},
            ],
        },
        {
            "id": 9,
            "titulo": "La entrevista de trabajo",
            "contexto": "Mañana tienes una entrevista importante. Solo tienes una hora para prepararte antes de ir a dormir.",
            "opciones": [
                {"id": "A", "texto": "Me paro frente al espejo y ensayo físicamente mi presentación y mis gestos.", "dimension": "EA"},
                {"id": "B", "texto": "Me enfoco en estar tranquilo y visualizo el encuentro como una conexión humana auténtica.", "dimension": "EC"},
                {"id": "C", "texto": "Repaso mentalmente mi trayectoria y anticipo posibles preguntas difíciles para no dudar.", "dimension": "OR"},
            ],
        },
        {
            "id": 10,
            "titulo": "El proyecto laboral",
            "contexto": "Tu superior te propone liderar una iniciativa en un área que no dominas. Es una gran oportunidad.",
            "opciones": [
                {"id": "A", "texto": "Analizo fríamente si mis competencias alcanzan y estudio qué recursos lógicos necesito.", "dimension": "CA"},
                {"id": "B", "texto": "Acepto el reto con ganas, pensando que aprenderé resolviendo los problemas sobre la marcha.", "dimension": "EA"},
                {"id": "C", "texto": "Pido unos días para reflexionar sobre cómo este cambio afectaría mi equilibrio de vida.", "dimension": "OR"},
            ],
        },
        {
            "id": 11,
            "titulo": "El amigo en problemas",
            "contexto": "Un amigo te llama muy angustiado por un problema personal grave y no sabe qué decisión tomar.",
            "opciones": [
                {"id": "A", "texto": "Lo escucho con empatía y le doy mi apoyo emocional para que se sienta acompañado.", "dimension": "EC"},
                {"id": "B", "texto": "Lo escucho y trato de ayudarlo a analizar la situación con lógica para encontrar una salida.", "dimension": "CA"},
                {"id": "C", "texto": "Le hago preguntas para que él mismo pueda pensar por qué pasó esto y qué siente.", "dimension": "OR"},
            ],
        },
        {
            "id": 12,
            "titulo": "Cocina con lo que hay",
            "contexto": "Es tarde, tienes hambre y en la heladera solo hay unos pocos ingredientes sueltos.",
            "opciones": [
                {"id": "A", "texto": "Empiezo a cocinar improvisando una receta nueva para ver si sale algo rico por experimento.", "dimension": "EA"},
                {"id": "B", "texto": "Me quedo mirando los ingredientes, recordando qué combinaciones similares he visto antes.", "dimension": "OR"},
                {"id": "C", "texto": "Busco rápidamente una receta básica que use esos elementos para asegurar el resultado.", "dimension": "CA"},
            ],
        },
    ],
}

SCENARIOS_BY_ID: dict[int, dict] = {s["id"]: s for s in KOLB_TEST["escenarios"]}
TOTAL_SCENARIOS: int = KOLB_TEST["test_metadata"]["total_escenarios"]
DIMENSIONS: list[str] = KOLB_TEST["test_metadata"]["dimensiones"]
