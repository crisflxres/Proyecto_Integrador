import serial  # Importamos la libreria serial para la comunicacion con Arduino
import time # Importamos la libreria de tiempo
import pandas as pd # manejar los datos en forma de DataFrame

# --- Configuración ---
puerto_arduino = 'COM5'
velocidad_arduino = 9600 # Velocidad en baudios
archivo_csv = 'Lecturas_de_los_sensores.csv'

# Conexión serial a Arduino
arduino = None

def conexion_con_arduino():
    global arduino
    try: #Manejamos excepciones para evitar errores
        if arduino is None or not arduino.is_open:
            arduino = serial.Serial(puerto_arduino, velocidad_arduino, timeout=1)
            time.sleep(2)
    except serial.SerialException:
        exit()

def cerrar_conexion_arduino():
    global arduino
    if arduino and arduino.is_open:
        arduino.close()
        print("Conexión con Arduino cerrada.")

def determinar_accion_automatica(izquierda, centro, derecha):
    if centro > 400 and izquierda < 400 and derecha < 400:
        return "adelante"
    elif centro > 400 and izquierda > 400 and derecha < 400:
        return "der" #gira a la derecha
    elif centro > 400 and izquierda < 400 and derecha > 400:
        return "izq" #gira a la izquierda
    elif centro > 400 and izquierda > 400 and derecha > 400:
        return "adelante" # Todos detectan, avanza
    elif izquierda > 400 and centro < 400 and derecha < 400:
        return "der_fuerte" #derecha fuerte
    elif derecha > 400 and centro < 400 and izquierda < 400:
        return "izq_fuerte" #izquierda fuerte
    elif izquierda > 400 and centro < 400 and derecha > 400:
        return "adelante_lento" # Solo izq y der, avanza lento
    else:
        return "parar" # Ninguno detecta

datos = []

if __name__ == "__main__":
    print("-CAPTURA DE DATOS -")
    conexion_con_arduino()
    print("Capturando datos automáticamente. Presiona Ctrl+C para detener.")
    try:
        while True:
            if arduino.in_waiting > 0:
                linea = arduino.readline().decode('utf-8').strip()
                if "IZQ" in linea and "DER" in linea and "CENTRO" in linea:
                    # Parsear los datos de la línea
                    # Formato: "IZQ: 123 CENTRO: 456 DER: 789"
                    try:
                        partes = linea.replace(":", "").split()
                        izquierda = int(partes[1])
                        centro = int(partes[3])
                        derecha = int(partes[5])
                    except (ValueError, IndexError):
                        print("Error en la decodificacion de los datos")
                        continue # Saltar error

                    accion_actual = determinar_accion_automatica(izquierda, centro, derecha)
                    
                    #Agregar los datos a la lista
                    datos.append([izquierda, centro, derecha, accion_actual])

            # Un pequeño delay puede ayudar a evitar la lectura excesiva
            time.sleep(0.1)

    except KeyboardInterrupt:
        print(f"Total de datos capturados: {len(datos)}")
    finally:
        cerrar_conexion_arduino()
        if datos:
            df_captura_de_datos = pd.DataFrame(datos, columns=['izquierda', 'centro', 'derecha', 'accion'])
            df_captura_de_datos.to_csv(archivo_csv, index=False)
            print(f"Datos capturados guardados en '{archivo_csv}'.")
        else:
            print("No se capturaron datos para guardar.")