# constantes.py
# Configuración global del juego

# Ventana
ANCHO_VENTANA = 900
ALTO_VENTANA = 400
FPS = 60

# Colores (R, G, B)
NEGRO    = (0, 0, 0)
BLANCO   = (250, 250, 250)
GRIS     = (120, 120, 120)
GRIS_OSC = (60, 60, 60)
ROJO     = (220, 50, 50)
VERDE    = (50, 200, 80)
AZUL     = (50, 100, 220)
AZUL_OSC = (30, 60, 150)
AMARILLO = (240, 200, 50)
NARANJA  = (240, 140, 40)
CAFE     = (139, 90, 43)
PIEL     = (210, 180, 140)
CREMA    = (235, 215, 175)

# Suelo (línea donde caminan el monito y los obstáculos)
Y_SUELO = 320

# === Estética ASCII / terminal ===========================================
# (NUEVO) Añadido al convertir los gráficos pygame.draw a sprites ASCII.
# Ya no se dibujan formas: todo el "mundo" se pinta con texto monoespaciado.
FUENTE_MONO   = "Consolas"     # fuente monoespaciada para los sprites ASCII
TAM_ASCII     = 12             # tamaño de la fuente del mundo (monito + obstáculos)
Y_LINEA_SUELO = Y_SUELO + 30   # píxel Y donde se apoyan el monito y los obstáculos (350)

# Física del salto
GRAVEDAD     = 0.8
FUERZA_SALTO = -16

# Velocidad de scroll del juego
VELOCIDAD_INICIAL    = 6.0
INCREMENTO_VELOCIDAD = 0.0015   # por cuadro -> aumenta ~0.09/seg a 60 FPS
VELOCIDAD_MAXIMA     = 18.0

# Spawn de obstáculos (frames entre uno y otro)
INTERVALO_OBSTACULO_MIN = 55
INTERVALO_OBSTACULO_MAX = 110

# Puerto del Arduino (cámbialo según tu equipo)
PUERTO_ARDUINO = 'COM6'
BAUDIOS        = 115200

# Mensajes que envía el Arduino.
# IMPORTANTE: deben coincidir EXACTAMENTE (mayúsculas, minúsculas y espacios)
# con lo que manda el Arduino por serial. NO cambiar estos textos: son el único
# lugar donde se definen y de aquí los usan control_serial, main y escenas.
EV_A     = "Boton A Presionado"
EV_B     = "Boton B Presionado"
EV_UP    = "UP"
EV_DOWN  = "Down"
EV_LEFT  = "Left"
EV_RIGHT = "Right"
EV_LISTO = "Listo para recibir datos..."
