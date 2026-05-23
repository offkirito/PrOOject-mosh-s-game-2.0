import serial
import time

# Es el puerto USB de donde se va a realizar la comunicacion, en mi laptop (Armando). COM6 es el de la derecha y COM 7 el de la izquierda
puerto_arduino = 'COM6' #derecha
baudios = 115200

try:
    print(f"Conectando al puerto {puerto_arduino}...")
    
    # serial.Serial(): Abre la "puerta" de comunicación entre Python y el Arduino.
    # timeout=1: Le dice a Python que espere máximo 1 segundo por datos sii no llega nada, sigue adelante. 
    ser = serial.Serial(puerto_arduino, baudios, timeout=1)
    
    # cuando Python abre el puerto, el Arduino se reinicia automáticamente.
    # Se hace una pausa de 2 segundos para darle tiempo de despertar antes de empezar a escuchar.
    time.sleep(2) 
    print("Conexión establecida. Presiona Ctrl+C para salir.")

    # Entra al ciclo
    while True:
        
        # ser.in_waiting, revisa el "buzón" del puerto de tu computadora. 
        if ser.in_waiting > 0: # Si el número es mayor a 0, significa que el Arduino nos dejo un mensaje ahi.
            
            # ser.readline(): lee los bytes crudos que mandó el Arduino hasta encontrar un salto de línea.
            # .decode('utf-8'): traduce los bytes de computadora a texto normal que podemos leer.
            # .strip(): Funciona como tijeras, cortando los espacios invisibles o saltos de línea (\r\n) 
          
            datos_entrantes = ser.readline().decode('utf-8').strip()
            
            # si después de limpiar el texto, realmente hay un mensaje (y no solo una línea en blanco)
            if datos_entrantes:
                
                # MANEJO DE LAS ACCIONES DE LOS BOTONES
                
                # Comparamos el texto exacto que envió el Arduino para ejecutar una acción en Python
                if datos_entrantes == "Boton A Presionado":
                    print("🎮 Acción: ¡Botón A presionado!")
                    # DENTRO DEL IF PONGAN LA ACCION QUE QUIEREN QUE SE EJECUTE EN EL PROGRAMA
                    
                elif datos_entrantes == "Boton B Presionado":
                    print("🎮 Acción: ¡Botón B presionado!")
                    # DENTRO DEL IF PONGAN LA ACCION QUE QUIEREN QUE SE EJECUTE EN EL PROGRAMA
                elif datos_entrantes == "UP":
                    print("⬆️ Acción: ¡Arriba!")
                    # DENTRO DEL IF PONGAN LA ACCION QUE QUIEREN QUE SE EJECUTE EN EL PROGRAMA
                elif datos_entrantes == "Down":
                    print("⬇️ Acción: ¡Abajo!")
                    # DENTRO DEL IF PONGAN LA ACCION QUE QUIEREN QUE SE EJECUTE EN EL PROGRAMA
                elif datos_entrantes == "Right":
                    print("➡️ Acción: ¡Derecha!")
                    # DENTRO DEL IF PONGAN LA ACCION QUE QUIEREN QUE SE EJECUTE EN EL PROGRAMA
                elif datos_entrantes == "Left":
                    print("⬅️ Acción: ¡Izquierda!")
                    # DENTRO DEL IF PONGAN LA ACCION QUE QUIEREN QUE SE EJECUTE EN EL PROGRAMA
                elif datos_entrantes == "Listo para recibir datos...":
                    # Este es el mensaje que manda tu Arduino en el setup()
                    print(" Arduino se ha reiniciado y está listo.")
                    
                else:
                    # Por si llega algo de "ruido" o un texto que no programamos
                    print(f"Dato desconocido recibido: {datos_entrantes}")

# 4. Excepciones
except KeyboardInterrupt:
    # Si presionas Ctrl+C para detener el script en la terminal, entra aquí.
    print("\nCerrando la conexión de forma segura.")
    
    # ser.close():  libera el puerto USB. 
    # Si no haces esto, el puerto se queda bloqueado y el IDE de Arduino no podrá subir nuevo código.
    ser.close()
    
except serial.SerialException as e:
    # Si hay un error al intentar conectarse 
    print(f"\nError al abrir el puerto serial: {e}")
    print(" ¿Olvidaste cerrar el Monitor Serie en el IDE de Arduino?")