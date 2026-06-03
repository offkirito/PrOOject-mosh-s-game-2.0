import random

from groq_client import GroqClient


class CiberAsistente(GroqClient):

    def __init__(self):

        system_prompt = """
        Eres un profesor de Electrónica Digital I.

        Genera preguntas de opción múltiple claras y correctas.

        Las preguntas deben ser de nivel básico.

        Cuando evalúes respuestas, explica brevemente por qué son correctas o incorrectas.
        """
        self.tema = [
        "Sistemas digitales vs sistemas analógicos",
        "Conceptos y terminología de sistemas digitales",
        "Tecnologías de circuitos electrónicos digitales",
        "Sistemas de numeración y codificación de datos",
        "Introducción al álgebra booleana",
        "Variables booleanas y operaciones básicas",
        "Expresiones algebraicas",
        "Tablas de verdad",
        "Teoremas básicos del álgebra booleana",
        "Suma de productos y producto de sumas",
        "Simplificación algebraica",
        "Introducción a VHDL y Verilog",
        "Introducción al diseño lógico combinacional",
        "Diseños basados en tablas de verdad",
        "Circuitos no completamente especificados",
        "Mapas de Karnaugh",
        "Método Quine-McCluskey",
        "Lógica combinacional modular",
        "Circuitos combinacionales con VHDL y Verilog",
        "Introducción al diseño lógico secuencial",
        "Efectos del tiempo en circuitos digitales",
        "Flip-Flops",
        "Características de Flip-Flops SR, JK y D",
        "Lógica secuencial modular",
        "Circuitos secuenciales con Verilog"
        ]

        self.pregunta_actual = ""
        self.correcta_actual = ""

        super().__init__(system_prompt=system_prompt)

        

    def _prompt_pregunta(self, tema, correcta):
        # Prompt compartido por generar_pregunta() y
        # generar_pregunta_estructurada(). La respuesta correcta SIEMPRE va en
        # el inciso 'correcta' (lo sabemos de antemano y así lo evaluamos).
        return f"""
        Genera una pregunta básica de opción múltiple
        sobre {tema}.
        IMPORTANTE:

        NO expliques la respuesta.
        NO justifiques la respuesta.
        NO escribas frases como:
        "La respuesta correcta es..."
        o similares.

        La respuesta correcta debe estar en el inciso {correcta}.

        Usa EXACTAMENTE este formato:

        Pregunta: ...
        a) ...
        b) ...
        c) ...
        [CORRECTA]{correcta}
        """

    def generar_pregunta(self):

        tema = random.choice(self.tema)
        correcta = random.choice(["a", "b", "c"])

        prompt = self._prompt_pregunta(tema, correcta)

        respuesta = self.preguntar(prompt)

        self.pregunta_actual = respuesta

        lineas = respuesta.splitlines()

        self.correcta_actual = ""

        pregunta_visible = []

        for linea in lineas:
            if linea.startswith("[CORRECTA]"):
                self.correcta_actual = (linea.replace("[CORRECTA]", "").strip())

            else:
                pregunta_visible.append(linea)

        return "\n".join(pregunta_visible)
    
    def generar_pregunta_estructurada(self):
        """
        Genera UNA pregunta de opción múltiple y la devuelve ya separada para
        mostrarla DENTRO del juego (no en consola):

            {
              "enunciado": "texto de la pregunta",
              "opciones":  [("a", "..."), ("b", "..."), ("c", "...")],
              "correcta":  "a"   # la letra correcta
            }

        La corrección se compara localmente contra "correcta": NO se hace otra
        petición a la IA para evaluar, así el juego no se bloquea.
        """
        tema = random.choice(self.tema)
        correcta = random.choice(["a", "b", "c"])

        prompt = self._prompt_pregunta(tema, correcta)

        # Cada pregunta es independiente: limpiamos el historial para que no
        # crezca con la partida (el system prompt se conserva igual).
        self.limpiar_historial()
        respuesta = self.preguntar(prompt)
        self.pregunta_actual = respuesta

        enunciado_partes = []
        opciones = []

        for linea in respuesta.splitlines():
            limpio = linea.replace("*", "").strip()
            if not limpio:
                continue
            if limpio.startswith("[CORRECTA]"):
                # No se muestra; la respuesta correcta ya la conocemos.
                continue
            # ¿Es una opción del tipo "a) ...", "b. ..." o "c- ..."?
            if (len(limpio) >= 2 and limpio[0].lower() in ("a", "b", "c")
                    and limpio[1] in (")", ".", "-")):
                letra = limpio[0].lower()
                texto = limpio[2:].strip()
                opciones.append((letra, texto))
            else:
                enunciado_partes.append(limpio)

        enunciado = " ".join(enunciado_partes)
        for prefijo in ("Pregunta:", "PREGUNTA:", "pregunta:"):
            if enunciado.startswith(prefijo):
                enunciado = enunciado[len(prefijo):].strip()
                break

        self.correcta_actual = correcta
        return {"enunciado": enunciado, "opciones": opciones, "correcta": correcta}

    def revisar_respuesta(self, respuesta_usuario):

        prompt = f"""
        Pregunta original:
        {self.pregunta_actual}

        Respuesta correcta:
        {self.correcta_actual}

        Respuesta del usuario:
        {respuesta_usuario}

        Determina si el usuario entendió el concepto.
        Responde solo:
        - Correcto
        - Incorrecto
        y explica brevemente.
        """

        return self.preguntar(prompt)