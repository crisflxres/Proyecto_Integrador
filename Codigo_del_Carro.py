import serial, time
#Importamos la libreria serial para poder comunicarnos con el Arduino
arduino = serial.Serial('COM5', 9600)
time.sleep(2)  # Esperamos a que se establezca la conexión
def enviar_comando(comando):
    arduino.write(comando.encode())  # Enviamos el comando al Arduino
    time.sleep(0.1)  # Esperamos un poco para asegurarnos de que el comando se envíe correctamente
    respuesta = arduino.readline().decode('utf-8').strip()  # Leemos la respuesta del Arduino
    return respuesta
def mover_adelante():
    respuesta = enviar_comando('adelante')
    print(f"Respuesta del Arduino: {respuesta}")
def mover_atras():
    respuesta = enviar_comando('atras')
    print(f"Respuesta del Arduino: {respuesta}")
def mover_izquierda():
    respuesta = enviar_comando('izquierda')
    print(f"Respuesta del Arduino: {respuesta}")
def mover_derecha():
    respuesta = enviar_comando('derecha')
    print(f"Respuesta del Arduino: {respuesta}")
def detener():
    respuesta = enviar_comando('detener')
    print(f"Respuesta del Arduino: {respuesta}")
def cerrar_conexion():
    arduino.close()  # Cerramos la conexión con el Arduino
    print("Conexión cerrada.")
