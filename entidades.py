# entidades.py
# Aquí se demuestran los pilares de POO:
#  - ABSTRACCIÓN: Entidad y Obstaculo son clases abstractas (ABC)
#  - HERENCIA:    Jugador, LED, Resistencia, Capacitor heredan de ellas
#  - POLIMORFISMO: cada obstáculo implementa su propio dibujar()
#  - ENCAPSULAMIENTO: atributos protegidos/privados con @property
#
# === CAMBIO DE ESTÉTICA (gráficos ASCII) =================================
# Antes cada entidad se dibujaba con pygame.draw (círculos, rectángulos,
# arcos...). Ahora, para igualar la versión final en Textual, cada entidad se
# dibuja con un SPRITE ASCII (lista de líneas de texto) renderizado con una
# fuente monoespaciada (Consolas). La LÓGICA del juego (física, colisiones,
# spawn, etc.) NO cambió: solo cambió cómo se ve cada entidad y de dónde sale
# el tamaño de su hitbox (ahora del tamaño real del texto, no de números fijos).
# =========================================================================

import math
import random
import pygame
from abc import ABC, abstractmethod

from constantes import (
    GRAVEDAD, FUERZA_SALTO,
    INTERVALO_OBSTACULO_MIN, INTERVALO_OBSTACULO_MAX,
    ANCHO_VENTANA, VELOCIDAD_INICIAL,
    FUENTE_MONO, TAM_ASCII, Y_LINEA_SUELO,
    BLANCO, GRIS, ROJO, VERDE,
)


# =====================================================================
#  UTILIDADES ASCII  (NUEVO)
#  Sustituyen a pygame.draw: ahora todo se dibuja con texto monoespaciado.
# =====================================================================
_CACHE_FUENTES = {}


def fuente_ascii(tam=TAM_ASCII):
    """
    Devuelve (y memoriza) una fuente monoespaciada Consolas del tamaño dado.
    Se cachea para no recrear la fuente en cada cuadro ni en cada obstáculo.
    """
    if tam not in _CACHE_FUENTES:
        _CACHE_FUENTES[tam] = pygame.font.SysFont(FUENTE_MONO, tam)
    return _CACHE_FUENTES[tam]


def medir_ascii(sprite, fuente):
    """
    Calcula el tamaño REAL (ancho, alto) en píxeles de un sprite ASCII.
    Con esto ajustamos el hitbox de cada entidad al texto renderizado,
    en vez de usar anchos/altos fijos como antes.
    """
    alto_linea = fuente.get_linesize()
    ancho = max((fuente.size(linea)[0] for linea in sprite), default=0)
    return ancho, alto_linea * len(sprite)


def dibujar_ascii(ventana, sprite, x, y, fuente, color):
    """
    Función auxiliar central: dibuja un sprite ASCII (lista de cadenas)
    línea por línea, una debajo de otra, con una fuente monoespaciada.
    Es la que reemplaza a todos los pygame.draw.* de las entidades.
    """
    alto_linea = fuente.get_linesize()
    for i, linea in enumerate(sprite):
        if not linea:
            continue
        ventana.blit(fuente.render(linea, True, color), (x, y + i * alto_linea))


# =====================================================================
#  CLASE ABSTRACTA BASE
# =====================================================================
class Entidad(ABC):
    """Clase abstracta de la que heredan todas las entidades del juego."""

    def __init__(self, x, y, ancho, alto):
        self._x     = x
        self._y     = y
        self._ancho = ancho
        self._alto  = alto

    @property
    def rect(self):
        """Hitbox para colisiones (sigue usando pygame.Rect)."""
        return pygame.Rect(self._x, self._y, self._ancho, self._alto)

    @property
    def x(self): return self._x

    @property
    def y(self): return self._y

    @abstractmethod
    def actualizar(self, *args, **kwargs):
        """Cada entidad define cómo se actualiza por cuadro."""
        pass

    @abstractmethod
    def dibujar(self, ventana):
        """Cada entidad define cómo se dibuja."""
        pass

    def colisiona_con(self, otra):
        # Hitbox más pequeño para que el juego sea justo. Las hitboxes ahora
        # se ajustan solas al tamaño del sprite ASCII (ver __init__ de cada una).
        h1 = self.rect.inflate(-8, -8)
        h2 = otra.rect.inflate(-6, -6)
        return h1.colliderect(h2)


# =====================================================================
#  JUGADOR (el monito)
# =====================================================================
class Jugador(Entidad):
    """El monito que corre y salta."""

    # --- CAMBIO ASCII ---------------------------------------------------
    # Sprite ASCII tomado TAL CUAL de la versión final en Textual.
    # Sustituye a los círculos/rectángulos/arcos que se dibujaban con pygame.draw.
    SPRITE = [
        "  _____  ",
        " /     \\ ",
        "| O   O |",
        "|   ^   |",
        "| \\___/ |",
        " \\_____/ ",
        "    |    ",
        "  / | \\  ",
        " /  |  \\ ",
        "    |    ",
        "   / \\   ",
    ]

    def __init__(self, x, y_pies):
        # y_pies = coordenada Y del suelo (donde quedan los PIES del monito).
        # --- CAMBIO ASCII: el tamaño del hitbox sale del sprite, no de 44x54 ---
        self.__fuente = fuente_ascii()
        ancho, alto = medir_ascii(Jugador.SPRITE, self.__fuente)
        # El borde inferior del sprite (los pies) queda sobre la línea del suelo.
        super().__init__(x, y_pies - alto, ancho, alto)

        self.__velocidad_y = 0
        self.__en_suelo    = True
        self.__y_inicial   = y_pies - alto   # posición de reposo (de pie)

    # --- Encapsulamiento ---
    @property
    def en_suelo(self): return self.__en_suelo

    # --- Comportamiento (LÓGICA SIN CAMBIOS) ---
    def saltar(self):
        if self.__en_suelo:
            self.__velocidad_y = FUERZA_SALTO
            self.__en_suelo = False

    def actualizar(self):
        # Aplicar gravedad
        self.__velocidad_y += GRAVEDAD
        self._y += self.__velocidad_y

        # Aterrizaje
        if self._y >= self.__y_inicial:
            self._y = self.__y_inicial
            self.__velocidad_y = 0
            self.__en_suelo = True

    def reiniciar(self):
        self._y = self.__y_inicial
        self.__velocidad_y = 0
        self.__en_suelo = True

    def dibujar(self, ventana):
        # --- CAMBIO ASCII: el monito ya no se arma con formas, se imprime ---
        dibujar_ascii(ventana, Jugador.SPRITE,
                      int(self._x), int(self._y), self.__fuente, BLANCO)


# =====================================================================
#  CLASE ABSTRACTA DE OBSTÁCULOS
# =====================================================================
class Obstaculo(Entidad):
    """Clase base abstracta para todos los componentes electrónicos."""

    def __init__(self, x, y, ancho, alto):
        super().__init__(x, y, ancho, alto)

    def actualizar(self, velocidad):
        """Se mueve a la izquierda según la velocidad actual del juego."""
        self._x -= velocidad

    def fuera_de_pantalla(self):
        return self._x + self._ancho < 0

    @property
    @abstractmethod
    def nombre(self):
        """Cada obstáculo se identifica con un nombre."""
        pass

    @abstractmethod
    def dibujar(self, ventana):
        pass


# =====================================================================
#  OBSTÁCULOS CONCRETOS (POLIMORFISMO)
#  Cada uno mide su sprite ASCII y se apoya sobre la línea del suelo.
# =====================================================================
class LED(Obstaculo):
    """Un LED (diodo emisor de luz) dibujado en ASCII. Parpadea."""

    # --- CAMBIO ASCII: foco con patitas, en lugar de domo + brillo ---
    SPRITE = [
        "  __  ",
        " /  \\ ",
        "|LED |",
        " \\__/ ",
        "  ||  ",
        "  ||  ",
    ]

    def __init__(self, x):
        self.__fuente = fuente_ascii()
        ancho, alto = medir_ascii(LED.SPRITE, self.__fuente)
        super().__init__(x, Y_LINEA_SUELO - alto, ancho, alto)
        self.__fase = random.random() * 6.28   # se conserva el parpadeo

    @property
    def nombre(self): return "LED"

    def actualizar(self, velocidad):
        super().actualizar(velocidad)
        self.__fase += 0.2

    def dibujar(self, ventana):
        # Parpadeo: alterna verde/blanco (estética terminal, sin colores nuevos).
        color = VERDE if math.sin(self.__fase) >= 0 else BLANCO
        dibujar_ascii(ventana, LED.SPRITE,
                      int(self._x), int(self._y), self.__fuente, color)


class Resistencia(Obstaculo):
    """Resistencia (zig-zag con terminales) en ASCII. Es bajita (se salta fácil)."""

    # --- CAMBIO ASCII: cuerpo corto tipo zig-zag, en lugar de bandas de colores ---
    SPRITE = [
        " ______ ",
        "-|MWMW|-",
        " \\____/ ",
    ]

    def __init__(self, x):
        self.__fuente = fuente_ascii()
        ancho, alto = medir_ascii(Resistencia.SPRITE, self.__fuente)
        super().__init__(x, Y_LINEA_SUELO - alto, ancho, alto)

    @property
    def nombre(self): return "Resistencia"

    def dibujar(self, ventana):
        dibujar_ascii(ventana, Resistencia.SPRITE,
                      int(self._x), int(self._y), self.__fuente, GRIS)


class Capacitor(Obstaculo):
    """Capacitor electrolítico en ASCII. Es alto, hay que saltar bien."""

    # --- CAMBIO ASCII: cilindro alto con marca de polaridad (-), en lugar
    #     de elipses/rectángulos azules ---
    SPRITE = [
        " ____ ",
        "|    |",
        "| -  |",
        "|    |",
        "|____|",
        " |  | ",
        " |  | ",
    ]

    def __init__(self, x):
        self.__fuente = fuente_ascii()
        ancho, alto = medir_ascii(Capacitor.SPRITE, self.__fuente)
        super().__init__(x, Y_LINEA_SUELO - alto, ancho, alto)

    @property
    def nombre(self): return "Capacitor"

    def dibujar(self, ventana):
        dibujar_ascii(ventana, Capacitor.SPRITE,
                      int(self._x), int(self._y), self.__fuente, ROJO)


# =====================================================================
#  GESTOR DE OBSTÁCULOS  (LÓGICA SIN CAMBIOS)
# =====================================================================
class GestorObstaculos:
    """
    Se encarga de generar y mantener la lista de obstáculos en pantalla.
    Aplica COMPOSICIÓN: el juego TIENE un gestor (no hereda de él).
    """

    def __init__(self):
        self.__obstaculos = []
        self.__contador   = 0
        self.__sig_spawn  = random.randint(INTERVALO_OBSTACULO_MIN, INTERVALO_OBSTACULO_MAX)
        self.__tipos      = [LED, Resistencia, Capacitor]

    @property
    def obstaculos(self):
        return self.__obstaculos

    def actualizar(self, velocidad):
        self.__contador += 1

        if self.__contador >= self.__sig_spawn:
            self.__contador = 0
            # Conforme aumenta la velocidad, los obstáculos pueden salir más seguido
            factor = max(0.55, 1.0 - (velocidad - VELOCIDAD_INICIAL) / 25.0)
            self.__sig_spawn = int(
                random.randint(INTERVALO_OBSTACULO_MIN, INTERVALO_OBSTACULO_MAX) * factor
            )
            TipoElegido = random.choice(self.__tipos)
            self.__obstaculos.append(TipoElegido(ANCHO_VENTANA + 60))

        # Mover todos los obstáculos
        for obs in self.__obstaculos:
            obs.actualizar(velocidad)

        # Eliminar los que ya salieron
        self.__obstaculos = [o for o in self.__obstaculos if not o.fuera_de_pantalla()]

    def dibujar(self, ventana):
        for obs in self.__obstaculos:
            obs.dibujar(ventana)

    def reiniciar(self):
        self.__obstaculos.clear()
        self.__contador  = 0
