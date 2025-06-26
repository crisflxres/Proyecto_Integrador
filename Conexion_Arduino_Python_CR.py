import serial #Importamos la libreria serial para la comunicacion con Arduino
import time #Importamos la libreria de tiempo

# Configuración
arduino = serial.Serial('COM5', 9600) 
time.sleep(2)

# Lista para guardar datos
datos = []

#Presiona Ctrl+C para parar

try: #Manejamos excepciones y asi evitamos errores
    while True:  # Hacemos un bucle infinito para leer datos
        if arduino.in_waiting > 0:
            linea = arduino.readline().decode('utf-8').strip()
            
            if "IZQ:" in linea and "DER:" in linea:
                print(linea)  # Mostrar en pantalla
                datos.append(linea)  # Guardar en lista

except KeyboardInterrupt:
    pass

# Guardar en archivo
with open('sensores.txt', 'w') as archivo:
    for linea in datos:
        archivo.write(linea + '\n')

arduino.close()
print(f"\nDatos guardados en sensores.txt ({len(datos)} lecturas)")