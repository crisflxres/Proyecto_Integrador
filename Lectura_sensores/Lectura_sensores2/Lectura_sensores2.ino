/*
 * Seguidor de Línea Minimalista
 * Sensor IR1 (Pin 2) = Izquierda
 * Sensor IR2 (Pin 4) = Derecha
 * Motor Izq: ENA=3, IN1=5, IN2=6
 * Motor Der: ENA=9, IN3=7, IN4=8
 */

#define M1_ENA 3
#define M1_IN1 5
#define M1_IN2 6
#define M2_ENA 9
#define M2_IN3 7
#define M2_IN4 8
#define SENSOR_L 2
#define SENSOR_R 4

uint8_t vel = 150;

void setup() {
  pinMode(M1_ENA, OUTPUT);
  pinMode(M1_IN1, OUTPUT);
  pinMode(M1_IN2, OUTPUT);
  pinMode(M2_ENA, OUTPUT);
  pinMode(M2_IN3, OUTPUT);
  pinMode(M2_IN4, OUTPUT);
  pinMode(SENSOR_L, INPUT);
  pinMode(SENSOR_R, INPUT);
  Serial.begin(9600);
}

void loop() {
  bool izq = digitalRead(SENSOR_L);
  bool der = digitalRead(SENSOR_R);
  
  // Imprimir valores de sensores
  Serial.print("L:");
  Serial.print(izq);
  Serial.print(" R:");
  Serial.println(der);
  
  if (!izq && !der) {        // Ambos detectan línea - Adelante
    adelante();
  } else if (!izq && der) {  // Solo izq detecta línea - Gira izquierda
    izquierda();
  } else if (izq && !der) {  // Solo der detecta línea - Gira derecha
    derecha();
  } 
  
  delay(50);
}

void adelante() {
  digitalWrite(M1_IN1, HIGH); digitalWrite(M1_IN2, LOW);
  digitalWrite(M2_IN3, HIGH); digitalWrite(M2_IN4, LOW);
  analogWrite(M1_ENA, vel); analogWrite(M2_ENA, vel);
}

void izquierda() {
  digitalWrite(M1_IN1, LOW); digitalWrite(M1_IN2, LOW);
  digitalWrite(M2_IN3, HIGH); digitalWrite(M2_IN4, LOW);
  analogWrite(M1_ENA, 0); analogWrite(M2_ENA, vel);
}

void derecha() {
  digitalWrite(M1_IN1, HIGH); digitalWrite(M1_IN2, LOW);
  digitalWrite(M2_IN3, LOW); digitalWrite(M2_IN4, LOW);
  analogWrite(M1_ENA, vel); analogWrite(M2_ENA, 0);
}

