# 🐒 Mosh game

Juego tipo "Chrome Dinosaur" pero con un monito que esquiva componentes electrónicos
(LEDs, resistencias y capacitores). Proyecto para **Programación Orientada a Objetos**.

---

## 🎮 Controles

| Botón del control | Acción en menú | Acción en juego |
| --- | --- | --- |
| **⬆ / ⬇** | Navegar opciones | — |
| **A** | Seleccionar | **Saltar** |
| **B** | Volver | **Pausar / reanudar** |

> Si el control no está conectado, el juego usa el **teclado** como respaldo:
> Espacio = A, P = B, flechas = direcciones.

---

## 📦 Instalación

```bash
pip install pygame pyserial
```

---

## ▶ Cómo ejecutar

1. Conecta tu control físico (Arduino) por USB.
2. Abre `constantes.py` y cambia el puerto si es necesario:
   ```python
   PUERTO_ARDUINO = 'COM6'   # o 'COM7', '/dev/ttyUSB0', etc.
   ```
3. Ejecuta:
   ```bash
   python main.py
   ```

---

## 🗂 Estructura del proyecto

```
monito_runner/
├── constantes.py        # Configuración global (colores, físicas, puerto)
├── control_serial.py    # Comunicación con el Arduino (en un hilo aparte)
├── entidades.py         # Entidad (abstracta), Jugador, Obstáculos y Gestor
├── escenas.py           # Escena (abstracta), Menu, EscenaJuego, GameOver
├── main.py              # Clase Juego y bucle principal
└── README.md
```

---

## 🧱 Pilares de POO aplicados

### 1. **Abstracción**
- `Entidad(ABC)` define la interfaz común de todo lo que aparece en pantalla:
  obliga a implementar `actualizar()` y `dibujar()`.
- `Obstaculo(ABC)` es una abstracción más concreta para los componentes
  electrónicos: además exige una propiedad `nombre`.
- `Escena(ABC)` abstrae el concepto de "pantalla del juego".

### 2. **Herencia**
- `Jugador` y `Obstaculo` heredan de `Entidad`.
- `LED`, `Resistencia` y `Capacitor` heredan de `Obstaculo`.
- `Menu`, `EscenaJuego` y `GameOver` heredan de `Escena`.

### 3. **Polimorfismo**
- En `GestorObstaculos.dibujar()` se recorre una lista de obstáculos y se llama
  a `obs.dibujar(...)` sin importar si es un LED, una resistencia o un capacitor:
  cada uno se dibuja a su manera.
- En el bucle de colisiones, `colisiona_con()` funciona con cualquier subclase
  de `Entidad`.
- El bucle principal llama a `self.__escena.actualizar()` sin saber qué escena
  es.

### 4. **Encapsulamiento**
- Atributos privados (con `__`) en `ControlSerial`, `Jugador`, `Menu`, etc.
- Acceso controlado por `@property` (ej: `Jugador.en_suelo`,
  `EscenaJuego.puntuacion`).
- El control serial expone solo `conectar()`, `obtener_evento()` y `cerrar()`:
  el resto de la implementación (hilo, cola, lectura cruda) queda oculta.

### 5. **Composición (extra)**
- `Juego` **tiene un** `ControlSerial` y **tiene una** `Escena`.
- `EscenaJuego` **tiene un** `Jugador` y **tiene un** `GestorObstaculos`.

---

## 🚀 Aumento de velocidad

En `constantes.py`:

```python
VELOCIDAD_INICIAL    = 6.0
INCREMENTO_VELOCIDAD = 0.0015   # se suma cada cuadro (60 cuadros = 1 s)
VELOCIDAD_MAXIMA     = 18.0
```

La velocidad crece poco a poco, y los obstáculos también empiezan a salir un
poco más seguido conforme avanza el juego (ver `GestorObstaculos.actualizar`).

---

## 🔌 Comunicación con el Arduino

El archivo `control_serial.py` corre en un **hilo separado** (`threading.Thread`)
para que `pygame` nunca se quede esperando datos del puerto.
Los mensajes que envía el Arduino (`"Boton A Presionado"`, `"UP"`, etc.) se
meten en una `queue.Queue` y el juego los va leyendo sin bloqueo en cada cuadro.
