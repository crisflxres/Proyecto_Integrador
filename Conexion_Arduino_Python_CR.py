import serial #Importamos la libreria serial para la comunicacion con Arduino
import time #Importamos la libreria de tiempo
import pandas as pd #manejar los datos en forma de DataFrame 
import numpy as np #manejar los datos

# Configuración
arduino = serial.Serial('COM5', 9600) 
time.sleep(2)

# Lista para guardar datos
datos = []

try: #Manejamos excepciones para evitar errores
    while True: #Bucle infinito para capturar los datos
        if arduino.in_waiting > 0:
            linea = arduino.readline().decode('utf-8').strip()
            
            if "IZQ" in linea and "DER" in linea and "CEN" in linea:
                print(linea)
                posiciones = linea.split()
                izquierda = int(posiciones[1])
                centro = int(posiciones[3])
                derecha = int(posiciones[5])

                datos.append((izquierda, centro, derecha))
except KeyboardInterrupt:
    print(f"Datos capturados: {len(datos)}") 

df = pd.DataFrame(datos, columns=['izquierda', 'centro', 'derecha'])
df.to_csv('Lecturas_de_los_sensores.csv', index=False)

sensores_array = np.array(datos)

print(f"Array de los sensores: {sensores_array.shape}")
arduino.close()