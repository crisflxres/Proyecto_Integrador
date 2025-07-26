import serial
import time
import joblib
import pandas as pd

# --- Configuración ---
puerto_bluetooth = 'COM3'
velocidad_arduino = 9600
modelo_archivo = 'modelo_carrito.pkl' #Archivo del modelo entrenado

# Variables globales
arduino = None
modelo = None

def conectar_bluetooth():
    global arduino
    try:
        arduino = serial.Serial(puerto_bluetooth, velocidad_arduino, timeout=1)
        time.sleep(3) 
        print("Conectado con Arduino")
        while True:
            if arduino.in_waiting > 0:
                linea = arduino.readline().decode('utf-8').strip()
                if "ARDUINO_LISTO" in linea:
                    print("Arduino listo")
                    break
        return True
    except Exception as e:
        print(f"Error conectando via Bluetooth: {e}")
        return False

def cargar_modelo():
    global modelo
    try:
        modelo = joblib.load(modelo_archivo)
        print("Modelo ML cargado")
        return True
    except FileNotFoundError:
        print(f"No se encontró '{modelo_archivo}'")
        print("Ejecuta primero 'Entrenamiento_ML.py'")
        return False
    except Exception as e:
        print(f"Error cargando modelo: {e}")
        return False

def extraer_valores_sensores(linea):
    try:
        if "IZQ:" in linea and "CENTRO:" in linea and "DER:" in linea:
            partes = linea.replace(":", "").split()
            izquierda = int(partes[1])
            centro = int(partes[3])
            derecha = int(partes[5])
            #Verifica que esta en reversa
            en_reversa = "REVERSA" in linea
            return izquierda, centro, derecha, en_reversa
    except Exception:
        pass
    return None, None, None, False

def predecir_accion(izquierda, centro, derecha):
    try:
        # Crear DataFrame igual que en entrenamiento
        X = pd.DataFrame([[izquierda, centro, derecha]], 
                        columns=['izquierda', 'centro', 'derecha'])
        
        # Hacer predicción
        prediccion = modelo.predict(X)[0]
        
        # Validar que sea un comando válido
        comandos_validos = ['adelante', 'der', 'izq', 'der_fuerte', 
                            'izq_fuerte', 'adelante_lento', 'reversa']
        
        if prediccion not in comandos_validos:
            return "reversa"
        
        return prediccion
    except Exception as e:
        print(f"Error en predicción ML: {e}")
        return "reversa"

def enviar_comando(comando):
    try:
        arduino.write((comando + '\n').encode())
        arduino.flush()  # Asegurar envío inmediato
        return True
    except Exception as e:
        print(f"Error enviando comando: {e}")
        return False

def main():
    print("- ROBOT CON IA -")
    print("Comunicación 100% Bluetooth")
    
    # Cargar modelo ML
    if not cargar_modelo():
        return
    
    # Conectar via Bluetooth
    if not conectar_bluetooth():
        return
    
    print("\n Robot funcionando con IA")
    print("Presiona Ctrl+C para detener")
    
    contador_lecturas = 0
    contador_predicciones = 0
    
    try:
        while True:
            if arduino.in_waiting > 0:
                linea = arduino.readline().decode('utf-8').strip()
                
                if linea:  # Si hay contenido en la línea
                    izquierda, centro, derecha, en_reversa = extraer_valores_sensores(linea)
                    
                    if izquierda is not None:  # Datos de sensores válidos
                        contador_lecturas += 1
                        
                        if not en_reversa:
                            accion_ml = predecir_accion(izquierda, centro, derecha)
                            contador_predicciones += 1
                            
                            if enviar_comando(accion_ml):
                                if contador_lecturas % 8 == 0:
                                    print(f"#{contador_predicciones:03d} | IZQ={izquierda:3d} CEN={centro:3d} DER={derecha:3d} → {accion_ml.upper()}")
                            else:
                                print("Error enviando comando al Arduino")
                        else:
                            if contador_lecturas % 15 == 0:
                                print(f"⬅ REVERSA... | IZQ={izquierda:3d} CEN={centro:3d} DER={derecha:3d}")
                    
                    else:
                        if "INICIANDO_REVERSA" in linea:
                            print("\n⬅ Robot perdió la línea - Maniobra de reversa automática")
                        elif "LINEA_ENCONTRADA" in linea:
                            print("¡Línea recuperada! Volviendo al control ML\n")
                        elif "ARDUINO_LISTO" in linea:
                            print("Arduino confirmó conexión")
                        elif "Robot ML listo" in linea:
                            print("Arduino en modo ML")
                            if contador_lecturas % 20 == 0:  # Mostrar ocasionalmente
                                print(f"Arduino: {linea}")
            time.sleep(0.01)  # Pausa mínima
            
    except KeyboardInterrupt:
        print(f"\nDeteniendo robot...")
        print(f"Estadísticas de la sesión:")
        print(f"   - Lecturas de sensores: {contador_lecturas}")
        print(f"   - Predicciones ML ejecutadas: {contador_predicciones}")
        print(f"   - Precisión: {(contador_predicciones/max(contador_lecturas, 1)*100):.1f}%")
        
        enviar_comando("reversa")
        time.sleep(1)
        
    finally:
        if arduino and arduino.is_open:
            arduino.close()
        print("Desconectado del Bluetooth")

if __name__ == "__main__":
    main()