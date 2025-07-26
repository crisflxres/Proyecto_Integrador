#include <SoftwareSerial.h>

const int m1_in1 = 5, m1_in2 = 6, m2_in3 = 10, m2_in4 = 11;
const int sensorDer = A0, sensorCen = A1, sensorIzq = A2;

SoftwareSerial bluetooth(2, 3);

bool perdio_linea = false;
unsigned long tiempo_sin_linea = 0;

void setup() {
  pinMode(m1_in1, OUTPUT); pinMode(m1_in2, OUTPUT);
  pinMode(m2_in3, OUTPUT); pinMode(m2_in4, OUTPUT);
  
  Serial.begin(9600);
  bluetooth.begin(9600);
  
  bluetooth.println("ARDUINO_LISTO");
  bluetooth.println("Robot ML listo");
}

void loop() {
  int izq = analogRead(sensorIzq);
  int cen = analogRead(sensorCen);
  int der = analogRead(sensorDer);

  bool hay_linea = (izq > 400 || cen > 400 || der > 400);

  String datos = "IZQ: " + String(izq) + " CENTRO: " + String(cen) + " DER: " + String(der); //enviar datos a ML
  if (perdio_linea) datos += " REVERSA";
  bluetooth.println(datos);
  
  if (!hay_linea) {  // Manejo de pérdida de línea
    if (tiempo_sin_linea == 0) tiempo_sin_linea = millis();
    else if (millis() - tiempo_sin_linea > 500 && !perdio_linea) {
      perdio_linea = true;
      bluetooth.println("INICIANDO_REVERSA");
    }
  } else {
    tiempo_sin_linea = 0;
    if (perdio_linea) {
      perdio_linea = false;
      bluetooth.println("LINEA_ENCONTRADA");
    }
  }

  if (perdio_linea) {   //control
    mover_reversa(); // Reversa
  } else {
    revisar_comandos_ml();
  }
  delay(50);
}

void revisar_comandos_ml() {
  if (bluetooth.available() > 0) {
    String cmd = bluetooth.readStringUntil('\n');
    cmd.trim();
    ejecutar_comando_ml(cmd);
  }
}

void ejecutar_comando_ml(String comando) {
  if (comando == "adelante") mover(100, 100);
  else if (comando == "der") mover(50, 110);
  else if (comando == "izq") mover(110, 50);
  else if (comando == "der_fuerte") mover(120, 0);
  else if (comando == "izq_fuerte") mover(0, 120);
  else if (comando == "adelante_lento") mover(60, 60);
  else if (comando == "reversa") mover(0, 0);
}

void mover(int vel_izq, int vel_der) {
  
  if (vel_izq > 0) {
    analogWrite(m1_in1, vel_izq);
    digitalWrite(m1_in2, LOW);
  } else {
    digitalWrite(m1_in1, LOW);
    digitalWrite(m1_in2, LOW);
  }

  if (vel_der > 0) {
    analogWrite(m2_in3, vel_der);
    digitalWrite(m2_in4, LOW);
  } else {
    digitalWrite(m2_in3, LOW);
    digitalWrite(m2_in4, LOW);
  }
}

void mover_reversa() {
  digitalWrite(m1_in1, LOW);
  analogWrite(m1_in2, 80);
  digitalWrite(m2_in3, LOW);
  analogWrite(m2_in4, 80);
}