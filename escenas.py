# escenas.py
# Sistema de escenas (Menu, EscenaJuego, EscenaPregunta, GameOver).
# Cada una hereda de Escena y define cómo manejar eventos del control,
# actualizar y dibujar.
#
# === CAMBIO DE ESTÉTICA (gráficos ASCII / terminal) ======================
# Antes el juego se veía "gráfico": fondo blanco, fuente Arial, suelo dibujado
# con pygame.draw.line y entidades con formas. Ahora, para igualar la versión
# final en Textual, todo usa estética de TERMINAL:
#   · Fondo NEGRO y textos en VERDE / BLANCO / ROJO / GRIS.
#   · Fuente monoespaciada (Consolas) en todas las escenas.
#   · El SUELO es una línea de texto ASCII que se desplaza.
#   · Las entidades se dibujan con sprites ASCII (ver entidades.py).
# La LÓGICA (eventos, preguntas con IA, vidas, colisiones, cambios de escena)
# NO cambió: solo cambió la parte visual.
# =========================================================================

import threading
import pygame
from abc import ABC, abstractmethod

from constantes import (
    ANCHO_VENTANA, ALTO_VENTANA, Y_LINEA_SUELO,
    VELOCIDAD_INICIAL, INCREMENTO_VELOCIDAD, VELOCIDAD_MAXIMA,
    FUENTE_MONO,
    NEGRO, BLANCO, GRIS, GRIS_OSC, ROJO, VERDE,
    EV_A, EV_B, EV_UP, EV_DOWN, EV_LEFT, EV_RIGHT,
)
# fuente_ascii viene de entidades para que el suelo use la MISMA rejilla
# monoespaciada que el monito y los obstáculos.
from entidades import Jugador, GestorObstaculos, fuente_ascii


# ---------------------------------------------------------------------
#  Utilidad: partir un texto largo en varias líneas que quepan en 'px'.
#  La usan EscenaPregunta para el enunciado y la explicación de la IA.
# ---------------------------------------------------------------------
def envolver_texto(texto, fuente, ancho_max):
    palabras = texto.split()
    lineas, actual = [], ""
    for palabra in palabras:
        prueba = (actual + " " + palabra).strip()
        if fuente.size(prueba)[0] <= ancho_max:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


# =====================================================================
#  ESCENA ABSTRACTA
# =====================================================================
class Escena(ABC):
    """Clase abstracta base para todas las escenas del juego."""

    def __init__(self, juego):
        self._juego = juego  # Referencia al juego principal

    @abstractmethod
    def manejar_evento(self, evento):
        pass

    @abstractmethod
    def actualizar(self):
        pass

    @abstractmethod
    def dibujar(self, ventana):
        pass


# =====================================================================
#  MENU PRINCIPAL
# =====================================================================
class Menu(Escena):
    """Menú navegable con los botones de dirección + A para seleccionar."""

    # --- CAMBIO ASCII: logo en bloque "MOSH" tomado de la portada de Textual.
    #     Se dibuja línea por línea con Consolas (caracteres de bloque █ ╗ ═...).
    LOGO = [
        "███╗   ███╗ ██████╗ ███████╗██╗  ██╗",
        "████╗ ████║██╔═══██╗██╔════╝██║  ██║",
        "██╔████╔██║██║   ██║███████╗███████║",
        "██║╚██╔╝██║██║   ██║╚════██║██╔══██║",
        "██║ ╚═╝ ██║╚██████╔╝███████║██║  ██║",
        "╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝",
    ]

    def __init__(self, juego):
        super().__init__(juego)
        self.__opciones = ["Jugar", "Cómo jugar", "Salir"]
        self.__sel = 0
        self.__mostrar_ayuda = False

        # --- CAMBIO ASCII: fuente monoespaciada Consolas (antes Arial) ---
        self.__fuente_logo    = pygame.font.SysFont(FUENTE_MONO, 18, bold=True)
        self.__fuente_titulo  = pygame.font.SysFont(FUENTE_MONO, 40, bold=True)
        self.__fuente_opcion  = pygame.font.SysFont(FUENTE_MONO, 28, bold=True)
        self.__fuente_chica   = pygame.font.SysFont(FUENTE_MONO, 18)

    def manejar_evento(self, evento):
        if self.__mostrar_ayuda:
            if evento in (EV_A, EV_B):
                self.__mostrar_ayuda = False
            return

        if evento == EV_UP:
            self.__sel = (self.__sel - 1) % len(self.__opciones)
        elif evento == EV_DOWN:
            self.__sel = (self.__sel + 1) % len(self.__opciones)
        elif evento == EV_A:
            self.__seleccionar()

    def __seleccionar(self):
        op = self.__opciones[self.__sel]
        if op == "Jugar":
            self._juego.cambiar_escena(EscenaJuego(self._juego))
        elif op == "Cómo jugar":
            self.__mostrar_ayuda = True
        elif op == "Salir":
            self._juego.salir()

    def actualizar(self):
        pass

    def dibujar(self, ventana):
        # --- CAMBIO ASCII: fondo negro estilo terminal (antes BLANCO) ---
        ventana.fill(NEGRO)

        if self.__mostrar_ayuda:
            self.__dibujar_ayuda(ventana)
            return

        # --- CAMBIO ASCII: logo en bloque "MOSH" dibujado línea por línea ---
        # Se alinean todas las líneas al mismo borde izquierdo (bloque centrado)
        # para no romper el dibujo de las letras.
        alto_linea = self.__fuente_logo.get_linesize()
        ancho_logo = max(self.__fuente_logo.size(ln)[0] for ln in Menu.LOGO)
        x_logo = ANCHO_VENTANA // 2 - ancho_logo // 2
        y0 = 18
        for i, ln in enumerate(Menu.LOGO):
            ventana.blit(self.__fuente_logo.render(ln, True, VERDE),
                         (x_logo, y0 + i * alto_linea))

        # Subtítulo (debajo del logo)
        y_sub = y0 + len(Menu.LOGO) * alto_linea + 10
        sub = self.__fuente_chica.render(
            "Esquiva LEDs, resistencias y capacitores", True, GRIS)
        ventana.blit(sub, (ANCHO_VENTANA // 2 - sub.get_width() // 2, y_sub))

        # Opciones: la seleccionada en verde con cursor ASCII "> "
        y_op = y_sub + 36
        for i, opcion in enumerate(self.__opciones):
            color = VERDE if i == self.__sel else BLANCO
            prefijo = "> " if i == self.__sel else "  "
            texto = self.__fuente_opcion.render(prefijo + opcion, True, color)
            ventana.blit(texto, (ANCHO_VENTANA // 2 - texto.get_width() // 2,
                                 y_op + i * 44))

        # Pie de página (flechas reemplazadas por texto ASCII)
        pie = self.__fuente_chica.render(
            "W/S Navegar    A Seleccionar    B Pausar (en juego)", True, GRIS_OSC)
        ventana.blit(pie, (ANCHO_VENTANA // 2 - pie.get_width() // 2,
                           ALTO_VENTANA - 30))

    def __dibujar_ayuda(self, ventana):
        titulo = self.__fuente_titulo.render("Cómo jugar", True, VERDE)
        ventana.blit(titulo, (ANCHO_VENTANA // 2 - titulo.get_width() // 2, 30))

        lineas = [
            "El monito corre automáticamente por el circuito.",
            "Presiona  A  para saltar sobre los componentes.",
            "Presiona  B  para pausar / reanudar el juego.",
            "",
            "Si chocas, aparece UNA pregunta: usa W/S para elegir",
            "y A para responder. Si aciertas, no pierdes vida.",
            "",
            "La velocidad aumenta poco a poco. ¡Resiste lo más posible!",
            "",
            "Presiona A o B para volver al menú.",
        ]
        for i, ln in enumerate(lineas):
            t = self.__fuente_chica.render(ln, True, BLANCO)
            ventana.blit(t, (ANCHO_VENTANA // 2 - t.get_width() // 2,
                             120 + i * 26))


# =====================================================================
#  ESCENA DEL JUEGO (el runner del monito)
# =====================================================================
class EscenaJuego(Escena):
    """
    Aquí ocurre la acción: el monito corre y esquiva.

    Cuando choca con un obstáculo NO pierde la vida de inmediato: el runner se
    PAUSA y cambiamos a la escena EscenaPregunta (el "frontend" de la pregunta).
    Esta escena se conserva tal cual (puntuación, velocidad...) para volver a
    ella cuando el jugador termine de responder. Se hace UNA pregunta por
    colisión: tras chocar cambiamos de escena y cortamos con return, así no se
    evalúan más obstáculos ni se lanzan más preguntas.
    """

    def __init__(self, juego):
        super().__init__(juego)
        # Cada partida nueva empieza con las vidas completas.
        self._juego.reiniciar_vidas()

        # --- CAMBIO ASCII: el monito se apoya sobre la línea del suelo ---
        # (Antes: Jugador(80, Y_SUELO - 24) con alto fijo 54.)
        self.__jugador      = Jugador(80, Y_LINEA_SUELO)
        self.__gestor       = GestorObstaculos()
        self.__velocidad    = VELOCIDAD_INICIAL
        self.__puntuacion   = 0.0
        self.__pausado      = False
        self.__offset_suelo = 0.0

        # --- CAMBIO ASCII: suelo como línea de texto en movimiento ---
        self.__fuente_suelo = fuente_ascii()                  # misma rejilla que las entidades
        self.__celda        = max(1, self.__fuente_suelo.size("_")[0])  # ancho de un caracter
        self.__patron       = "_."                            # patrón de suelo (como en Textual)

        # --- CAMBIO ASCII: HUD en Consolas (antes Arial) ---
        self.__fuente_hud   = pygame.font.SysFont(FUENTE_MONO, 22, bold=True)
        self.__fuente_pausa = pygame.font.SysFont(FUENTE_MONO, 56, bold=True)
        self.__fuente_chica = pygame.font.SysFont(FUENTE_MONO, 16)

    # --- Propiedades para que GameOver/EscenaPregunta lean la puntuación ---
    @property
    def puntuacion(self): return int(self.__puntuacion)

    @property
    def velocidad(self): return self.__velocidad

    def reanudar(self):
        """
        Vuelve del cuestionario: reinicia jugador y obstáculos para que el
        monito no choque otra vez al instante con el mismo obstáculo.
        La puntuación y la velocidad se conservan (no se tocan aquí).
        """
        self.__jugador.reiniciar()
        self.__gestor.reiniciar()

    def manejar_evento(self, evento):
        if evento == EV_A and not self.__pausado:
            self.__jugador.saltar()
        elif evento == EV_B:
            self.__pausado = not self.__pausado

    def actualizar(self):
        if self.__pausado:
            return

        self.__jugador.actualizar()
        self.__gestor.actualizar(self.__velocidad)

        # Aumentar velocidad con el tiempo
        if self.__velocidad < VELOCIDAD_MAXIMA:
            self.__velocidad += INCREMENTO_VELOCIDAD

        # Aumentar puntuación
        self.__puntuacion += 0.15 + (self.__velocidad - VELOCIDAD_INICIAL) * 0.02

        # --- CAMBIO ASCII: avanzar el desplazamiento del suelo de texto ---
        # (se acumula en píxeles y se acota al ancho de la rejilla del patrón)
        self.__offset_suelo = (self.__offset_suelo + self.__velocidad) \
            % (len(self.__patron) * self.__celda)

        # Detectar colisiones. Al primer choque cambiamos a EscenaPregunta y
        # cortamos con return -> UNA sola pregunta por colisión.
        for obs in self.__gestor.obstaculos:
            if self.__jugador.colisiona_con(obs):
                # >>> Conexión con el frontend de preguntas <<<
                # Le pasamos esta misma escena para poder volver a ella luego.
                self._juego.cambiar_escena(EscenaPregunta(self._juego, self))
                return

    def dibujar(self, ventana):
        # --- CAMBIO ASCII: fondo negro estilo terminal ---
        ventana.fill(NEGRO)

        # --- CAMBIO ASCII: suelo dibujado como una línea de texto que corre ---
        # (antes: pygame.draw.line + marcas). Cada caracter se elige según el
        # patrón "_." desplazado, dando sensación de movimiento hacia la izq.
        cols = ANCHO_VENTANA // self.__celda + 2
        desplaz = int(self.__offset_suelo) // self.__celda
        linea_suelo = "".join(
            self.__patron[(c + desplaz) % len(self.__patron)]
            for c in range(cols)
        )
        ventana.blit(self.__fuente_suelo.render(linea_suelo, True, VERDE),
                     (0, Y_LINEA_SUELO))

        # Dibujar entidades (ahora son sprites ASCII)
        self.__jugador.dibujar(ventana)
        self.__gestor.dibujar(ventana)

        # HUD (verde/rojo sobre negro)
        punt = self.__fuente_hud.render(
            f"Puntos: {int(self.__puntuacion)}", True, VERDE)
        ventana.blit(punt, (ANCHO_VENTANA - punt.get_width() - 20, 18))

        vel = self.__fuente_hud.render(
            f"Velocidad: {self.__velocidad:.1f}", True, VERDE)
        ventana.blit(vel, (20, 18))

        # Vidas restantes (se leen desde el juego con obtener_vidas())
        vidas = self.__fuente_hud.render(
            f"Vidas: {self._juego.obtener_vidas()}", True, ROJO)
        ventana.blit(vidas, (20, 44))

        hint = self.__fuente_chica.render(
            "A: saltar    B: pausa", True, GRIS)
        ventana.blit(hint, (ANCHO_VENTANA // 2 - hint.get_width() // 2, 22))

        # Capa de pausa (oscurece la pantalla en negro)
        if self.__pausado:
            capa = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA))
            capa.set_alpha(200)
            capa.fill(NEGRO)
            ventana.blit(capa, (0, 0))

            txt = self.__fuente_pausa.render("PAUSA", True, VERDE)
            ventana.blit(txt, (ANCHO_VENTANA // 2 - txt.get_width() // 2,
                               ALTO_VENTANA // 2 - 50))

            sub = self.__fuente_chica.render(
                "Presiona B para continuar", True, GRIS)
            ventana.blit(sub, (ANCHO_VENTANA // 2 - sub.get_width() // 2,
                               ALTO_VENTANA // 2 + 20))


# =====================================================================
#  ESCENA DE PREGUNTA  (el frontend visual del cuestionario con IA)
# =====================================================================
class EscenaPregunta(Escena):
    """
    Pantalla de pregunta de opción múltiple DENTRO del juego (sin consola).

    Flujo (todo con manejar_evento / actualizar / dibujar, sin input ni while):

        GENERANDO  -> se genera UNA pregunta con IA en un hilo (no bloquea).
        PREGUNTA   -> se muestran enunciado + opciones; el jugador navega con
                      W/S y responde con A (o Enter, que el control mapea a A).
        REVISANDO  -> al responder, la IA revisa la respuesta en un hilo.
        RESULTADO  -> se muestra "Correcto/Incorrecto" + explicación de la IA;
                      con A se continúa.

    Reglas de vidas:
      · respuesta correcta -> NO pierde vida.
      · respuesta incorrecta -> pierde 1 vida.
      · al continuar: si vidas == 0 -> GameOver; si no -> vuelve a EscenaJuego.

    La pregunta se genera UNA sola vez (al entrar a la escena), no por cuadro,
    y la revisión solo ocurre cuando el jugador selecciona una opción.
    """

    # Estados internos
    GENERANDO = "generando"
    PREGUNTA  = "pregunta"
    REVISANDO = "revisando"
    RESULTADO = "resultado"

    def __init__(self, juego, escena_juego):
        super().__init__(juego)
        # Guardamos la escena del runner para volver a ella (con su puntuación).
        self.__escena_juego = escena_juego

        # Datos de la pregunta (los llena el hilo de generación).
        self.__enunciado = ""
        self.__opciones  = []     # [(letra, texto), ...]
        self.__correcta  = ""
        self.__sel       = 0

        # Resultado de la respuesta.
        self.__letra_elegida = ""
        self.__respuesta_txt = ""
        self.__acierto       = None
        self.__explicacion   = ""

        # Banderas que comparten los hilos con el bucle principal.
        self.__error      = False   # falló la generación
        self.__gen_listo  = False   # terminó el hilo de generación
        self.__rev_listo  = False   # terminó el hilo de revisión

        self.__estado = EscenaPregunta.GENERANDO

        # --- CAMBIO ASCII: fuentes del frontend en Consolas (antes Arial) ---
        self.__fuente_hud      = pygame.font.SysFont(FUENTE_MONO, 22, bold=True)
        self.__fuente_enun     = pygame.font.SysFont(FUENTE_MONO, 20, bold=True)
        self.__fuente_opcion   = pygame.font.SysFont(FUENTE_MONO, 20)
        self.__fuente_resultado= pygame.font.SysFont(FUENTE_MONO, 26, bold=True)
        self.__fuente_chica    = pygame.font.SysFont(FUENTE_MONO, 16)

        # >>> Conexión IA -> frontend (1) <<<
        # Generamos la pregunta UNA vez, al entrar, en un hilo para no congelar
        # la ventana (el control serial usa la misma idea de hilo aparte).
        self.__hilo_gen = threading.Thread(target=self.__generar_en_hilo,
                                            daemon=True)
        self.__hilo_gen.start()

    # -----------------------------------------------------------------
    #  Hilos que hablan con la IA (no bloquean el bucle de Pygame)
    # -----------------------------------------------------------------
    def __generar_en_hilo(self):
        try:
            # generar_pregunta_estructurada() devuelve enunciado + opciones +
            # letra correcta, y además deja lista la pregunta en el asistente
            # para que revisar_respuesta() funcione después.
            datos    = self._juego.asistente.generar_pregunta_estructurada()
            opciones = datos.get("opciones", [])
            correcta = datos.get("correcta", "")
            letras   = [op[0] for op in opciones]
            if len(opciones) < 2 or correcta not in letras:
                self.__error = True
            else:
                self.__enunciado = datos.get("enunciado", "")
                self.__opciones  = opciones
                self.__correcta  = correcta
        except Exception as e:
            print(f"[IA] Error al generar la pregunta, no se penaliza: {e}")
            self.__error = True
        finally:
            self.__gen_listo = True

    def __revisar_en_hilo(self):
        # >>> Conexión IA -> frontend (2) <<<
        # La IA revisa la respuesta del jugador y devuelve una explicación.
        try:
            self.__explicacion = self._juego.asistente.revisar_respuesta(
                self.__respuesta_txt)
        except Exception as e:
            print(f"[IA] Error al revisar la respuesta: {e}")
            self.__explicacion = "(No se pudo obtener la explicación de la IA.)"
        finally:
            self.__rev_listo = True

    # -----------------------------------------------------------------
    #  EVENTOS
    # -----------------------------------------------------------------
    def manejar_evento(self, evento):
        # Mientras la IA trabaja (genera o revisa) no se acepta entrada.
        if self.__estado in (EscenaPregunta.GENERANDO, EscenaPregunta.REVISANDO):
            return

        if self.__estado == EscenaPregunta.PREGUNTA:
            if evento == EV_UP:
                self.__sel = (self.__sel - 1) % len(self.__opciones)
            elif evento == EV_DOWN:
                self.__sel = (self.__sel + 1) % len(self.__opciones)
            elif evento == EV_A:          # A (y Enter, que el control mapea a A)
                self.__seleccionar()
            return

        if self.__estado == EscenaPregunta.RESULTADO:
            if evento == EV_A:
                self.__continuar()
            return

    def __seleccionar(self):
        """El jugador eligió una opción: se decide la vida y se pide la
        explicación a la IA (en un hilo)."""
        letra, texto = self.__opciones[self.__sel]
        self.__letra_elegida = letra
        self.__respuesta_txt = f"{letra}) {texto}"

        # El veredicto se decide con la letra correcta conocida (100% fiable);
        # la explicación de la IA es solo informativa para el jugador.
        self.__acierto = (letra.lower() == self.__correcta.lower())
        if not self.__acierto:
            self._juego.restar_vida()      # solo se resta si falló

        # Pedimos la explicación a la IA sin bloquear el bucle.
        self.__estado = EscenaPregunta.REVISANDO
        self.__rev_listo = False
        threading.Thread(target=self.__revisar_en_hilo, daemon=True).start()

    def __continuar(self):
        """Cierra la pregunta: GameOver si no quedan vidas; si no, vuelve al
        runner conservando la puntuación."""
        if self._juego.obtener_vidas() <= 0:
            self._juego.cambiar_escena(
                GameOver(self._juego, self.__escena_juego.puntuacion))
        else:
            self.__escena_juego.reanudar()
            self._juego.cambiar_escena(self.__escena_juego)

    # -----------------------------------------------------------------
    #  ACTUALIZACIÓN (solo cambia de estado cuando un hilo termina)
    # -----------------------------------------------------------------
    def actualizar(self):
        if self.__estado == EscenaPregunta.GENERANDO and self.__gen_listo:
            self.__estado = EscenaPregunta.RESULTADO if self.__error \
                else EscenaPregunta.PREGUNTA

        elif self.__estado == EscenaPregunta.REVISANDO and self.__rev_listo:
            self.__estado = EscenaPregunta.RESULTADO

    # -----------------------------------------------------------------
    #  DIBUJO
    # -----------------------------------------------------------------
    def dibujar(self, ventana):
        # --- CAMBIO ASCII: fondo negro + marco verde tipo terminal ---
        ventana.fill(NEGRO)
        # Marco tipo "tarjeta" para que se vea como una capa de pregunta.
        pygame.draw.rect(ventana, VERDE,
                         (16, 8, ANCHO_VENTANA - 32, ALTO_VENTANA - 16), 1)

        # Encabezado + vidas restantes (requisito: mostrar vidas)
        enc = self.__fuente_hud.render("PREGUNTA", True, VERDE)
        ventana.blit(enc, (ANCHO_VENTANA // 2 - enc.get_width() // 2, 16))
        vidas = self.__fuente_hud.render(
            f"Vidas: {self._juego.obtener_vidas()}", True, ROJO)
        ventana.blit(vidas, (32, 16))

        if self.__estado == EscenaPregunta.GENERANDO:
            self.__centrado(ventana, "Generando pregunta...",
                            self.__fuente_enun, VERDE, ALTO_VENTANA // 2 - 14)
            return

        if self.__estado == EscenaPregunta.REVISANDO:
            self.__centrado(ventana, "Revisando tu respuesta con la IA...",
                            self.__fuente_enun, VERDE, ALTO_VENTANA // 2 - 14)
            return

        if self.__estado == EscenaPregunta.RESULTADO and self.__error:
            self.__centrado(ventana, "No se pudo generar la pregunta.",
                            self.__fuente_enun, BLANCO, ALTO_VENTANA // 2 - 28)
            self.__centrado(ventana, "No pierdes vida.  Presiona A para continuar.",
                            self.__fuente_chica, GRIS, ALTO_VENTANA // 2 + 6)
            return

        if self.__estado == EscenaPregunta.PREGUNTA:
            self.__dibujar_pregunta(ventana)
        elif self.__estado == EscenaPregunta.RESULTADO:
            self.__dibujar_resultado(ventana)

    def __dibujar_pregunta(self, ventana):
        margen, ancho_max = 50, ANCHO_VENTANA - 100

        # Enunciado (sin la línea [CORRECTA], que ya no viene en el texto)
        y = 56
        for linea in envolver_texto(self.__enunciado, self.__fuente_enun, ancho_max):
            ventana.blit(self.__fuente_enun.render(linea, True, BLANCO), (margen, y))
            y += 26
        y += 8

        # Opciones a) b) c) -- la seleccionada se resalta con cursor ASCII "> "
        for i, (letra, texto) in enumerate(self.__opciones):
            seleccion = (i == self.__sel)
            color   = VERDE if seleccion else BLANCO
            prefijo = "> " if seleccion else "  "
            for linea in envolver_texto(f"{prefijo}{letra}) {texto}",
                                        self.__fuente_opcion, ancho_max):
                ventana.blit(self.__fuente_opcion.render(linea, True, color),
                             (margen, y))
                y += 24
            y += 4

        pie = self.__fuente_chica.render(
            "W/S  elegir       A / Enter  responder", True, GRIS)
        ventana.blit(pie, (ANCHO_VENTANA // 2 - pie.get_width() // 2,
                           ALTO_VENTANA - 28))

    def __dibujar_resultado(self, ventana):
        margen, ancho_max = 50, ANCHO_VENTANA - 100

        # Resultado: Correcto / Incorrecto
        if self.__acierto:
            verdicto, color = "Resultado: Correcto", VERDE
        else:
            verdicto, color = "Resultado: Incorrecto", ROJO
        ventana.blit(self.__fuente_resultado.render(verdicto, True, color),
                     (margen, 54))

        # Explicación de la IA (envuelta y recortada para que quepa)
        ventana.blit(self.__fuente_chica.render("Explicación:", True, GRIS),
                     (margen, 94))
        y = 116
        pie_y = ALTO_VENTANA - 28
        lineas = envolver_texto(self.__explicacion, self.__fuente_chica, ancho_max)
        max_lineas = max(1, (pie_y - y) // 20)
        for linea in lineas[:max_lineas]:
            ventana.blit(self.__fuente_chica.render(linea, True, BLANCO), (margen, y))
            y += 20

        pie = self.__fuente_chica.render(
            "Presiona A para continuar", True, GRIS)
        ventana.blit(pie, (ANCHO_VENTANA // 2 - pie.get_width() // 2, pie_y))

    def __centrado(self, ventana, texto, fuente, color, y):
        t = fuente.render(texto, True, color)
        ventana.blit(t, (ANCHO_VENTANA // 2 - t.get_width() // 2, y))


# =====================================================================
#  GAME OVER
# =====================================================================
class GameOver(Escena):
    """Pantalla final con la puntuación."""

    def __init__(self, juego, puntuacion):
        super().__init__(juego)
        self.__puntuacion     = puntuacion
        # --- CAMBIO ASCII: fuentes Consolas (antes Arial) ---
        self.__fuente_titulo  = pygame.font.SysFont(FUENTE_MONO, 56, bold=True)
        self.__fuente_punt    = pygame.font.SysFont(FUENTE_MONO, 32, bold=True)
        self.__fuente_chica   = pygame.font.SysFont(FUENTE_MONO, 20)

    def manejar_evento(self, evento):
        if evento == EV_A:
            self._juego.cambiar_escena(EscenaJuego(self._juego))
        elif evento == EV_B:
            self._juego.cambiar_escena(Menu(self._juego))

    def actualizar(self):
        pass

    def dibujar(self, ventana):
        # --- CAMBIO ASCII: fondo negro estilo terminal ---
        ventana.fill(NEGRO)
        t = self.__fuente_titulo.render("GAME OVER", True, ROJO)
        ventana.blit(t, (ANCHO_VENTANA // 2 - t.get_width() // 2, 70))

        p = self.__fuente_punt.render(
            f"Puntuación: {self.__puntuacion}", True, BLANCO)
        ventana.blit(p, (ANCHO_VENTANA // 2 - p.get_width() // 2, 180))

        i1 = self.__fuente_chica.render(
            "Presiona  A  para volver a jugar", True, GRIS)
        ventana.blit(i1, (ANCHO_VENTANA // 2 - i1.get_width() // 2, 260))

        i2 = self.__fuente_chica.render(
            "Presiona  B  para volver al menú", True, GRIS)
        ventana.blit(i2, (ANCHO_VENTANA // 2 - i2.get_width() // 2, 295))
