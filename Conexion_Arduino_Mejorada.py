import serial #Importamos la libreria serial para la comunicacion con Arduino
import time #Importamos la libreria de tiempo
import pandas as pd #Manejar los datos en forma de DataFrame

# --- Configuración ---
puerto_bluetooth = 'COM8'
velocidad_arduino = 9600 #Velocidad en baudios
archivo_csv = 'Lecturas_de_los_sensores.csv'

# Variable global
arduino = None

def conexion_con_bluetooth():
    global arduino
    try: #Manejamos excepciones para evitar errores
        if arduino is None or not arduino.is_open:
            arduino = serial.Serial(puerto_bluetooth, velocidad_arduino)
            time.sleep(3)
    except serial.SerialException as e:
        print(f"Error conectando Bluetooth: {e}")
        exit()

def cerrar_conexion_bluetooth():
    global arduino
    if arduino and arduino.is_open:
        arduino.close()
        print("Conexión con Arduino cerrada.")

def determinar_accion_automatica(izquierda, centro, derecha):
    if centro > 400 and izquierda < 400 and derecha < 400:
        return "adelante"
    elif centro > 400 and izquierda > 400 and derecha < 400:
        return "der"
    elif centro > 400 and izquierda < 400 and derecha > 400:
        return "izq"
    elif centro > 400 and izquierda > 400 and derecha > 400:
        return "adelante"
    elif izquierda > 400 and centro < 400 and derecha < 400:
        return "der_fuerte"
    elif derecha > 400 and centro < 400 and izquierda < 400:
        return "izq_fuerte"
    elif izquierda > 400 and centro < 400 and derecha > 400:
        return "adelante_lento"
    else:
        return "reversa" #Ninguno detecta

datos = []

if __name__ == "__main__":
    print("- CAPTURA DE DATOS -")
    conexion_con_bluetooth()
    print("Capturando datos automáticamente. Presiona Ctrl+C para detener.")
    
    try:
        while True:
            if arduino.in_waiting > 0:
                linea = arduino.readline().decode('utf-8').strip()
                if "IZQ" in linea and "DER" in linea and "CENTRO" in linea:
                    try:
                        partes = linea.replace(":", "").split()
                        izquierda = int(partes[1])
                        centro = int(partes[3])
                        derecha = int(partes[5])
                    except (ValueError, IndexError):
                        print("Error en la codificación de los datos")
                        continue #Salta el error
                        
                    accion_actual = determinar_accion_automatica(izquierda, centro, derecha)
                    
                    #Agregar los datos a la lista
                    datos.append([izquierda, centro, derecha, accion_actual])
            #Un pequeño delay para ayudar a evitar la lectura excesiva
            time.sleep(0.1)

    except KeyboardInterrupt:
        print(f"\nTotal de datos capturados: {len(datos)}")
    finally:
        cerrar_conexion_bluetooth()
        if datos:
            df_captura_de_datos = pd.DataFrame(datos, columns=['izquierda', 'centro', 'derecha', 'accion'])
            df_captura_de_datos.to_csv(archivo_csv, index=False)
            print(f"Datos guardados en '{archivo_csv}'.")
        else:
            print("No se capturaron datos para guardar.")