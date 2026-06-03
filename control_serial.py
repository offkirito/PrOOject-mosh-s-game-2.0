# control_serial.py
# Lee el Arduino en un hilo separado y mete los eventos en una cola,
# así pygame no se queda esperando al puerto.

import serial
import threading
import queue
import time

from constantes import PUERTO_ARDUINO, BAUDIOS


class ControlSerial:
    """
    Encapsula la comunicación con el control físico (Arduino).
    
    Demuestra ENCAPSULAMIENTO: todos los atributos son privados (__),
    y se exponen solo los métodos necesarios (conectar, obtener_evento, cerrar).
    """

    def __init__(self, puerto=PUERTO_ARDUINO, baudios=BAUDIOS):
        self.__puerto      = puerto
        self.__baudios     = baudios
        self.__ser         = None
        self.__cola        = queue.Queue()
        self.__hilo        = None
        self.__activo      = False
        self.__conectado   = False

    # --- Propiedades de solo lectura ---
    @property
    def conectado(self):
        return self.__conectado

    @property
    def puerto(self):
        return self.__puerto

    # --- API pública ---
    def conectar(self):
        """Intenta abrir el puerto. Devuelve True/False."""
        try:
            print(f"Conectando al puerto {self.__puerto}...")
            self.__ser = serial.Serial(self.__puerto, self.__baudios, timeout=1)
            # Esperar a que el Arduino termine de reiniciarse
            time.sleep(2)
            self.__conectado = True
            self.__activo = True
            self.__hilo = threading.Thread(target=self.__leer_bucle, daemon=True)
            self.__hilo.start()
            print("Conexión establecida con el control.")
            return True
        except serial.SerialException as e:
            print(f"No se pudo abrir el puerto: {e}")
            print("El juego correrá con teclado como respaldo.")
            self.__conectado = False
            return False

    def obtener_evento(self):
        """Saca un evento de la cola sin bloquear. Devuelve None si está vacía."""
        try:
            return self.__cola.get_nowait()
        except queue.Empty:
            return None

    def cerrar(self):
        """Cierra el hilo y el puerto de forma segura."""
        self.__activo = False
        if self.__ser and self.__ser.is_open:
            try:
                self.__ser.close()
            except Exception:
                pass
        self.__conectado = False

    # --- Privado ---
    def __leer_bucle(self):
        """Se ejecuta en el hilo: lee líneas y las pone en la cola."""
        while self.__activo:
            try:
                if self.__ser and self.__ser.in_waiting > 0:
                    datos = self.__ser.readline().decode('utf-8', errors='ignore').strip()
                    if datos:
                        self.__cola.put(datos)
                else:
                    # pequeña pausa para no quemar CPU
                    time.sleep(0.005)
            except Exception as e:
                print(f"Error de lectura serial: {e}")
                break
