import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class GroqClient:
    """
    Cliente base para interactuar con la API de Groq.
    Encapsula la configuración de conexión y el historial de conversación.
    """

    def __init__(self, system_prompt: str = "Eres un asistente util."):

        # Atributo privado
        self.__api_key = os.getenv("GROQ_API_KEY")

        if not self.__api_key:
            raise ValueError("No se encontró la API key en el archivo .env")

        # Cliente de conexion
        self.__cliente = OpenAI(
            api_key=self.__api_key,
            base_url="https://api.groq.com/openai/v1"
        )

        # Prompt del sistema
        self.__system_prompt = system_prompt

        # Historial de conversación
        self.historial = []

        # Modelo
        self.modelo = "llama-3.3-70b-versatile"

    def _construir_mensajes(self) -> list:

        return [
            {"role": "system", "content": self.__system_prompt},
            *self.historial
        ]

    def preguntar(self, mensaje: str) -> str:

        # Guardar mensaje usuario
        self.historial.append({
            "role": "user",
            "content": mensaje
        })

        # Peticion API
        respuesta = self.__cliente.chat.completions.create(
            model=self.modelo,
            messages=self._construir_mensajes()
        )

        # Extraer texto
        texto = respuesta.choices[0].message.content

        # Guardar respuesta
        self.historial.append({
            "role": "assistant",
            "content": texto
        })

        return texto

    def limpiar_historial(self):

        self.historial = []

    def __str__(self):

        return f"GroqClient | modelo: {self.modelo} | mensajes en historial: {len(self.historial)}"