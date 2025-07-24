import serial
import time
import joblib
import pandas as pd

# --- Configuración ---
puerto_arduino = 'COM5'  # Cambiar si es necesario
velocidad_arduino = 9600
modelo_archivo = 'modelo_carrito.pkl'

# Variables globales
arduino = None
modelo = None

def conectar_arduino():
    global arduino
    try:
        arduino = serial.Serial(puerto_arduino, velocidad_arduino, timeout=1)
        time.sleep(2)
        print("✓ Conectado con Arduino")
        
        # Esperar señal de que Arduino está listo
        while True:
            if arduino.in_waiting > 0:
                linea = arduino.readline().decode('utf-8').strip()
                if "ARDUINO_READY" in linea:
                    print("✓ Arduino listo")
                    break
        return True
    except Exception as e:
        print(f"❌ Error conectando Arduino: {e}")
        return False

def cargar_modelo():
    global modelo
    try:
        modelo = joblib.load(modelo_archivo)
        print("✓ Modelo ML cargado")
        return True
    except FileNotFoundError:
        print(f"❌ No se encontró '{modelo_archivo}'")
        print("   Ejecuta primero 'entrenamiento_modelo.py'")
        return False
    except Exception as e:
        print(f"❌ Error cargando modelo: {e}")
        return False

def parsear_sensores(linea):
    """Extrae valores de sensores de la línea de Arduino"""
    try:
        if "IZQ" in linea and "CENTRO" in linea and "DER" in linea:
            # Formato: "IZQ: 123 CENTRO: 456 DER: 789"
            partes = linea.replace(":", "").split()
            izquierda = int(partes[1])
            centro = int(partes[3])
            derecha = int(partes[5])
            
            # Verificar si está en reversa
            en_reversa = "REVERSA" in linea
            return izquierda, centro, derecha, en_reversa
    except:
        pass
    return None, None, None, False

def predecir_accion(izquierda, centro, derecha):
    """Usa el modelo ML para predecir la acción"""
    try:
        # Crear DataFrame igual que en entrenamiento
        X = pd.DataFrame([[izquierda, centro, derecha]], 
                        columns=['izquierda', 'centro', 'derecha'])
        
        # Hacer predicción
        prediccion = modelo.predict(X)[0]
        return prediccion
    except Exception as e:
        print(f"Error en predicción: {e}")
        return "parar"

def enviar_comando(comando):
    """Envía comando al Arduino"""
    try:
        arduino.write((comando + '\n').encode())
        return True
    except Exception as e:
        print(f"Error enviando comando: {e}")
        return False

def main():
    print("=== ROBOT CON MACHINE LEARNING ===")
    
    # Cargar modelo
    if not cargar_modelo():
        return
    
    # Conectar Arduino
    if not conectar_arduino():
        return
    
    print("\n🤖 Robot funcionando con IA")
    print("📊 Presiona Ctrl+C para detener\n")
    
    contador = 0
    
    try:
        while True:
            if arduino.in_waiting > 0:
                linea = arduino.readline().decode('utf-8').strip()
                
                # Parsear datos de sensores
                izquierda, centro, derecha, en_reversa = parsear_sensores(linea)
                
                if izquierda is not None:
                    if not en_reversa:
                        # Modo normal: ¡AQUÍ ES LA MAGIA! ML predice la acción
                        accion_ml = predecir_accion(izquierda, centro, derecha)
                        
                        # Enviar comando al Arduino
                        enviar_comando(accion_ml)
                        
                        # Mostrar información cada 10 lecturas
                        contador += 1
                        if contador % 10 == 0:
                            print(f"Sensores: IZQ={izquierda:3d} CEN={centro:3d} DER={derecha:3d} → Acción ML: {accion_ml}")
                    else:
                        # Modo reversa: Arduino controla automáticamente
                        if contador % 15 == 0:  # Mostrar menos frecuentemente
                            print(f"⬅️ REVERSA... Sensores: IZQ={izquierda:3d} CEN={centro:3d} DER={derecha:3d}")
                
                # Mostrar mensajes especiales
                elif "INICIANDO_REVERSA" in linea:
                    print("⬅️ Robot perdió la línea - Yendo en reversa")
                elif "LINEA_ENCONTRADA" in linea:
                    print("✅ ¡Línea encontrada! Volviendo al control ML")
            
            time.sleep(0.01)  # Pequeña pausa
            
    except KeyboardInterrupt:
        print("\n\n🛑 Deteniendo robot...")
        enviar_comando("parar")
        time.sleep(0.5)
        
    finally:
        if arduino and arduino.is_open:
            arduino.close()
        print("✓ Desconectado")

if __name__ == "__main__":
    main()