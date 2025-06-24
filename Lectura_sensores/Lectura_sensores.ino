// Definición de pines
#define M1_ENA 3
#define M1_IN1 5
#define M1_IN2 6
#define M2_ENA 9
#define M2_IN3 7
#define M2_IN4 8
#define IR1 2
#define IR2 4
#define LED1 12
#define LED2 13

// Variables globales
byte vel = 200;                    // Velocidad única para ambos motores
bool obs1, obs2;                   // Estado de obstáculos
unsigned long lastBlink = 0;       // Control de parpadeo LEDs

void setup() {
  // Configurar todos los pines de salida
  pinMode(M1_ENA, OUTPUT); pinMode(M1_IN1, OUTPUT); pinMode(M1_IN2, OUTPUT);
  pinMode(M2_ENA, OUTPUT); pinMode(M2_IN3, OUTPUT); pinMode(M2_IN4, OUTPUT);
  pinMode(LED1, OUTPUT); pinMode(LED2, OUTPUT);
  
  // Configurar pines de entrada
  pinMode(IR1, INPUT); pinMode(IR2, INPUT);
  
  Serial.begin(9600);
  motorOn(1); motorOn(2);           // Encender ambos motores al inicio
}

void loop() {
  // Leer sensores (LOW = obstáculo detectado)
  obs1 = !digitalRead(IR1);
  obs2 = !digitalRead(IR2);
  
  // Control automático de motores
  obs1 ? motorOff(1) : motorOn(1);
  obs2 ? motorOff(2) : motorOn(2);
  
  // Parpadear LEDs cuando hay obstáculo
  if (millis() - lastBlink > 200) {
    digitalWrite(LED1, obs1 ? !digitalRead(LED1) : LOW);
    digitalWrite(LED2, obs2 ? !digitalRead(LED2) : LOW);
    lastBlink = millis();
  }
  
  // Procesar comandos serie
  if (Serial.available()) processCmd();
  
  delay(50);
}

void motorOn(byte m) {
  // Encender motor m (1 o 2) hacia adelante
  if (m == 1) {
    digitalWrite(M1_IN1, HIGH); digitalWrite(M1_IN2, LOW);
    analogWrite(M1_ENA, vel);
  } else {
    digitalWrite(M2_IN3, HIGH); digitalWrite(M2_IN4, LOW);
    analogWrite(M2_ENA, vel);
  }
}

void motorOff(byte m) {
  // Apagar motor m (1 o 2)
  if (m == 1) {
    digitalWrite(M1_IN1, LOW); digitalWrite(M1_IN2, LOW);
    analogWrite(M1_ENA, 0);
  } else {
    digitalWrite(M2_IN3, LOW); digitalWrite(M2_IN4, LOW);
    analogWrite(M2_ENA, 0);
  }
}

void motorRev(byte m) {
  // Motor en reversa
  if (m == 1) {
    digitalWrite(M1_IN1, LOW); digitalWrite(M1_IN2, HIGH);
    analogWrite(M1_ENA, vel);
  } else {
    digitalWrite(M2_IN3, LOW); digitalWrite(M2_IN4, HIGH);
    analogWrite(M2_ENA, vel);
  }
}

void processCmd() {
  char c = Serial.read();
  
  switch (c) {
    case 's': motorOff(1); motorOff(2); break;           // Stop ambos
    case 'f': if(!obs1 && !obs2) {motorOn(1); motorOn(2);} break;  // Forward
    case 'r': if(!obs1 && !obs2) {motorRev(1); motorRev(2);} break; // Reverse
    case 'l': if(!obs2) motorOn(2); motorOff(1); break;  // Left (solo M2)
    case 'd': if(!obs1) motorOn(1); motorOff(2); break;  // Right (solo M1)
    case '1': obs1 ? 0 : motorOn(1); break;              // Toggle M1
    case '2': obs2 ? 0 : motorOn(2); break;              // Toggle M2
    case '+': vel = min(255, vel + 30); break;           // Aumentar velocidad
    case '-': vel = max(80, vel - 30); break;            // Reducir velocidad
    case 'i':                                            // Info
      Serial.print("M1:"); Serial.print(digitalRead(M1_ENA) ? "ON" : "OFF");
      Serial.print(" M2:"); Serial.print(digitalRead(M2_ENA) ? "ON" : "OFF");
      Serial.print(" V:"); Serial.print(vel);
      Serial.print(" IR1:"); Serial.print(obs1 ? "OBS" : "OK");
      Serial.print(" IR2:"); Serial.println(obs2 ? "OBS" : "OK");
      break;
    case 'h':                                            // Help
      Serial.println("s=Stop f=Forward r=Reverse l=Left d=Right");
      Serial.println("1=M1 2=M2 +=Vel+ -=Vel- i=Info h=Help");
      break;
  }