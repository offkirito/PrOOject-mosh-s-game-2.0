# main.py
# Punto de entrada del juego "Monito Runner".
# Ejecutar con:  python main.py

import sys
import pygame

from constantes import (
    ANCHO_VENTANA, ALTO_VENTANA, FPS, PUERTO_ARDUINO,
    # Mensajes EXACTOS del Arduino (definidos una sola vez en constantes.py).
    EV_A, EV_B, EV_UP, EV_DOWN, EV_LEFT, EV_RIGHT, EV_LISTO,
)
from control_serial import ControlSerial
from escenas import Menu
from asistente import CiberAsistente  # IA que genera y revisa las preguntas


class Juego:
    """
    Clase principal. Coordina ventana, reloj, escena actual y control serial.
    
    Aplica COMPOSICIÓN: el juego TIENE una escena y TIENE un control.
    También actúa como "Contexto" del patrón State (las escenas cambian
    el comportamiento del juego sin que él tenga que saber detalles).
    """

    def __init__(self):
        pygame.init()
        self.__ventana = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        pygame.display.set_caption("Mosh Game — POO")
        self.__reloj   = pygame.time.Clock()
        self.__corriendo = True
        self.__escena  = None

        # Control físico (Arduino por serial)
        self.__control = ControlSerial(puerto=PUERTO_ARDUINO)
        self.__control.conectar()  # si falla, seguimos con teclado

        # --- Integración con la IA ---
        # UNA sola instancia del asistente para todo el juego.
        # (No se vuelve a crear en cada colisión.)
        self.__asistente = CiberAsistente()

        # Vidas del jugador: empieza con 3.
        self.__vidas = 3

        # Empezamos en el menú
        self.cambiar_escena(Menu(self))

    # --- API pública usada por las escenas ---
    def cambiar_escena(self, nueva_escena):
        self.__escena = nueva_escena

    def salir(self):
        self.__corriendo = False

    # --- Vidas e integración con la IA (lo usa EscenaJuego) ---
    def obtener_vidas(self):
        """Devuelve cuántas vidas le quedan al jugador."""
        return self.__vidas

    def restar_vida(self):
        """Resta una vida al jugador (sin bajar de 0)."""
        if self.__vidas > 0:
            self.__vidas -= 1
        return self.__vidas

    def reiniciar_vidas(self, cantidad=3):
        """Restablece las vidas al empezar una nueva partida."""
        self.__vidas = cantidad

    @property
    def asistente(self):
        """
        Acceso de solo lectura al asistente de IA.

        Lo usa EscenaJuego para generar UNA pregunta cuando el monito choca.
        La pregunta se muestra y se responde DENTRO del juego (no en consola),
        y la generación corre en un hilo aparte para no congelar la ventana.
        """
        return self.__asistente

    # --- Mapeo de teclado a los MISMOS mensajes que manda el Arduino ---
    # El teclado es solo un respaldo: traduce cada tecla al texto serial real
    # (vía las constantes EV_*), así escenas no distingue si vino del Arduino
    # o del teclado.
    @staticmethod
    def __tecla_a_evento(tecla):
        return {
            pygame.K_SPACE:  EV_A,      # Espacio  -> "Boton A Presionado"
            pygame.K_RETURN: EV_A,      # Enter    -> "Boton A Presionado"
            pygame.K_p:      EV_B,      # P        -> "Boton B Presionado"
            pygame.K_ESCAPE: EV_B,      # Escape   -> "Boton B Presionado"
            pygame.K_UP:     EV_UP,     # Flecha arriba -> "UP"
            pygame.K_w:      EV_UP,     # W        -> "UP"
            pygame.K_DOWN:   EV_DOWN,   # Flecha abajo  -> "Down"
            pygame.K_s:      EV_DOWN,   # S        -> "Down"
            pygame.K_LEFT:   EV_LEFT,   # Flecha izquierda -> "Left"
            pygame.K_a:      EV_LEFT,   # A        -> "Left"
            pygame.K_RIGHT:  EV_RIGHT,  # Flecha derecha   -> "Right"
            pygame.K_d:      EV_RIGHT,  # D        -> "Right"
        }.get(tecla)

    # --- Bucle principal ---
    def ejecutar(self):
        while self.__corriendo:
            # 1) Eventos de pygame (ventana + teclado de respaldo)
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.__corriendo = False
                elif evento.type == pygame.KEYDOWN:
                    nombre_evento = self.__tecla_a_evento(evento.key)
                    if nombre_evento:
                        self.__escena.manejar_evento(nombre_evento)

            # 2) Eventos del control serial (Arduino)
            #    Llegan TAL CUAL los manda el Arduino y se reenvían a la escena,
            #    que los compara contra las constantes EV_* (mismos textos).
            while True:
                ev = self.__control.obtener_evento()
                if ev is None:
                    break
                # "Listo para recibir datos..." NO es una acción del juego:
                # solo confirmamos en consola que el Arduino está listo.
                if ev == EV_LISTO:
                    print("[Control] Arduino listo.")
                    continue
                self.__escena.manejar_evento(ev)

            # 3) Lógica + dibujo
            self.__escena.actualizar()
            self.__escena.dibujar(self.__ventana)
            pygame.display.flip()
            self.__reloj.tick(FPS)

        # Cleanup
        self.__control.cerrar()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    juego = Juego()
    juego.ejecutar()
