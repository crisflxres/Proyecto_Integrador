import serial, time
#Importamos la libreria serial para poder comunicarnos con el Arduino
arduino = serial.Serial('COM5', 9600)
time.sleep(2)  # Esperamos a que se establezca la conexión

while True:
    if arduino.in_waiting > 0:  # Verificamos si hay datos disponibles
        data = arduino.readline().decode('utf-8').rstrip()  # Leemos la línea de datos
        print(data)  # Imprimimos los datos recibidos
    else:
        print("No hay datos disponibles en este momento.")
    time.sleep(1)  # Esperamos un segundo antes de la siguiente lectura