# 🐒 Mosh's Game

Videojuego educativo desarrollado en Python utilizando Programación Orientada a Objetos (POO), comunicación serial con Arduino e Inteligencia Artificial.

El jugador controla a Mosh, quien debe esquivar componentes electrónicos como LEDs, resistencias y capacitores. Cuando ocurre una colisión, el jugador debe responder una pregunta de Electrónica Digital generada por IA para conservar sus vidas y continuar jugando.

---

# 🎯 Objetivo

Combinar conceptos de:

* Programación Orientada a Objetos
* Electrónica Digital
* Inteligencia Artificial
* Comunicación Serial
* Desarrollo de Videojuegos

en una aplicación interactiva y educativa.

---

# 🎮 Controles

## Control Arduino

| Botón | Función                          |
| ----- | -------------------------------- |
| A     | Saltar / Seleccionar / Confirmar |
| B     | Pausar o reanudar                |
| UP    | Navegar hacia arriba             |
| DOWN  | Navegar hacia abajo              |

## Teclado (respaldo)

| Tecla                | Acción  |
| -------------------- | ------- |
| Espacio / Enter      | Botón A |
| P / Escape           | Botón B |
| Flecha Arriba / W    | UP      |
| Flecha Abajo / S     | DOWN    |
| Flecha Izquierda / A | LEFT    |
| Flecha Derecha / D   | RIGHT   |

---

# 🕹️ Mecánica del Juego

1. El jugador controla a Mosh.
2. Mosh corre automáticamente.
3. Debe esquivar obstáculos electrónicos:

   * LED
   * Resistencia
   * Capacitor
4. La velocidad aumenta gradualmente con el tiempo.
5. Cuando ocurre una colisión:

   * Se genera una pregunta de Electrónica Digital.
   * Si responde correctamente, conserva su vida.
   * Si responde incorrectamente, pierde una vida.
6. El juego termina cuando las vidas llegan a cero.

---

# 🤖 Integración con Inteligencia Artificial

El proyecto utiliza la API de Groq para:

* Generar preguntas dinámicas.
* Seleccionar temas aleatoriamente.
* Revisar respuestas.
* Proporcionar explicaciones educativas.

Temas incluidos:

* Álgebra Booleana
* Sistemas Digitales
* Sistemas de Numeración
* Flip-Flops
* Circuitos Combinacionales
* Circuitos Secuenciales
* Karnaugh
* Verilog
* Diseño Lógico

y otros temas de Electrónica Digital I.

---

# 🔌 Comunicación con Arduino

El control físico se comunica mediante puerto serial utilizando PySerial.

Mensajes utilizados:

```text
Boton A Presionado
Boton B Presionado
UP
Down
Left
Right
Listo para recibir datos...
```

La lectura serial se realiza en un hilo independiente utilizando `threading.Thread` para evitar bloqueos durante la ejecución del juego.

---

# 🧱 Aplicación de Programación Orientada a Objetos

## Abstracción

Clases abstractas:

* Entidad
* Obstaculo
* Escena

---

## Herencia

```text
Entidad
│
├── Jugador
│
└── Obstaculo
     ├── LED
     ├── Resistencia
     └── Capacitor

Escena
│
├── Menu
├── EscenaJuego
├── EscenaPregunta
└── GameOver
```

---

## Polimorfismo

Cada obstáculo implementa su propia versión del método:

```python
dibujar()
```

permitiendo que el gestor de obstáculos los trate de forma uniforme.

---

## Encapsulamiento

Uso de atributos privados mediante:

```python
self.__variable
```

en clases como:

* Juego
* ControlSerial
* Jugador
* Menu

---

## Composición

La clase Juego contiene:

* ControlSerial
* Escena
* CiberAsistente

La clase EscenaJuego contiene:

* Jugador
* GestorObstaculos

---

# 🗂️ Estructura del Proyecto

```text
moshs_game/
│
├── main.py
├── constantes.py
├── control_serial.py
├── entidades.py
├── escenas.py
├── asistente.py
├── groq_client.py
├── .env
└── README.md
```

---

# 📦 Instalación

Instalar dependencias:

```bash
pip install pygame pyserial python-dotenv openai
```

---

# 🔑 Configuración

Crear un archivo `.env`:

```env
GROQ_API_KEY=TU_API_KEY
```

---

# ▶️ Ejecución

Configurar el puerto serial en:

```python
PUERTO_ARDUINO = "COM6"
```

Ejecutar:

```bash
python main.py
```

---

# ⚙️ Recursos Externos Utilizados

## 1. Arduino

Dispositivo físico utilizado para controlar el juego mediante comunicación serial.

## 2. Groq API

Servicio de Inteligencia Artificial utilizado para generar y evaluar preguntas dinámicamente.

---

# 🚀 Posibles Mejoras Futuras

* Más tipos de obstáculos.
* Más preguntas y categorías.
* Sistema de récords.
* Niveles de dificultad.
* Estadísticas de rendimiento.
* Base de datos para guardar partidas.

---

# 👥 Equipo

Proyecto desarrollado para la materia de Programación Orientada a Objetos.

**Nombre del proyecto:** Mosh's Game
