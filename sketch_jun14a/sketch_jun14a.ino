/*
 * Motor DC + Sensor Infrarrojo IC-20271
 * Pines Motor: 3 (ENA), 5 (IN1), 6 (IN2)
 * Sensor IR: Pin 2 (digital)
 * El motor se detiene cuando detecta obstáculo
 */

// ===== DEFINICIÓN DE PINES =====
// Motor DC con Driver L298N
#define MOTOR_ENA 3       // Pin 3 - Enable (velocidad PWM)
#define MOTOR_IN1 5       // Pin 5 - IN1 del driver
#define MOTOR_IN2 6       // Pin 6 - IN2 del driver

// Sensor Infrarrojo IC-20271
#define SENSOR_IR 2       // Pin 2 - Señal digital del sensor IR
#define LED_INDICADOR 13  // LED integrado para indicar detección

// ===== VARIABLES GLOBALES =====
int velocidad = 200;           // Velocidad del motor (0-255)
bool obstaculoDetectado = false;
bool motorFuncionando = true;
unsigned long tiempoUltimaDeteccion = 0;
const unsigned long tiempoEspera = 100; // 1 segundo de espera tras detectar obstáculo

void setup() {
  // Configurar pines del motor como salida
  pinMode(MOTOR_ENA, OUTPUT);
  pinMode(MOTOR_IN1, OUTPUT);
  pinMode(MOTOR_IN2, OUTPUT);
  
  // Configurar pines del sensor como entrada
  pinMode(SENSOR_IR, INPUT);
  pinMode(LED_INDICADOR, OUTPUT);
  
  // Inicializar comunicación serial
  Serial.begin(9600);
  Serial.println("=== Motor con Sensor IR IC-20271 ===");
  Serial.println("Pin 3 = ENA, Pin 5 = IN1, Pin 6 = IN2");
  Serial.println("Pin 2 = Sensor IR");
  Serial.println("Motor se detiene al detectar obstáculo");
  Serial.println("=====================================");
  
  // Inicializar motor
  encenderMotor();
  Serial.println("Sistema iniciado - Motor funcionando");
}

void loop() {
  // Leer estado del sensor infrarrojo
  leerSensorIR();
  
  // Controlar motor según detección
  if (obstaculoDetectado) {
    manejarObstaculo();
  } else {
    // Si no hay obstáculo, motor normal
    if (!motorFuncionando) {
      encenderMotor();
      motorFuncionando = true;
      Serial.println("✅ Camino libre - Motor encendido");
    }
  }
  
  // Procesar comandos serie (opcional)
  if (Serial.available()) {
    procesarComando();
  }
  
  delay(30); // Lectura cada 50ms
}

// ===== FUNCIONES DEL SENSOR IR =====
void leerSensorIR() {
  // El sensor IC-20271 da LOW cuando detecta obstáculo
  int lecturaIR = digitalRead(SENSOR_IR);
  
  if (lecturaIR == LOW) {
    // Obstáculo detectado
    if (!obstaculoDetectado) {
      obstaculoDetectado = true;
      tiempoUltimaDeteccion = millis();
      Serial.println("🚨 OBSTÁCULO DETECTADO!");
      digitalWrite(LED_INDICADOR, HIGH); // Encender LED
    }
  } else {
    // No hay obstáculo
    if (obstaculoDetectado) {
      // Verificar si ha pasado el tiempo de espera
      if (millis() - tiempoUltimaDeteccion > tiempoEspera) {
        obstaculoDetectado = false;
        digitalWrite(LED_INDICADOR, LOW); // Apagar LED
        Serial.println("✅ Obstáculo removido");
      }
    }
  }
}

void manejarObstaculo() {
  if (motorFuncionando) {
    apagarMotor();
    motorFuncionando = false;
    Serial.println("🛑 Motor detenido por obstáculo");
  }
  
  // Parpadear LED mientras hay obstáculo
  static unsigned long tiempoParpadeo = 0;
  if (millis() - tiempoParpadeo > 200) {
    digitalWrite(LED_INDICADOR, !digitalRead(LED_INDICADOR));
    tiempoParpadeo = millis();
  }
}

// ===== FUNCIONES DE CONTROL DEL MOTOR =====
void encenderMotor() {
  digitalWrite(MOTOR_IN1, HIGH);     // Pin 5 - IN1 Encendido
  digitalWrite(MOTOR_IN2, LOW);      // Pin 6 - IN2 Apagado
  analogWrite(MOTOR_ENA, velocidad); // Pin 3 - ENA con velocidad PWM
}

void encenderMotorReversa() {
  digitalWrite(MOTOR_IN1, LOW);      // Pin 5 - IN1 Apagado
  digitalWrite(MOTOR_IN2, HIGH);     // Pin 6 - IN2 Encendido
  analogWrite(MOTOR_ENA, velocidad); // Pin 3 - ENA con velocidad PWM
}

void apagarMotor() {
  digitalWrite(MOTOR_IN1, LOW);      // Pin 5 - IN1 Apagado
  digitalWrite(MOTOR_IN2, LOW);      // Pin 6 - IN2 Apagado
  analogWrite(MOTOR_ENA, 0);         // Pin 3 - ENA sin PWM
}

// ===== PROCESAMIENTO DE COMANDOS =====
void procesarComando() {
  char comando = Serial.read();
  
  switch (comando) {
    case 's':
    case 'S':
      // Start/Stop manual
      if (motorFuncionando && !obstaculoDetectado) {
        apagarMotor();
        motorFuncionando = false;
        Serial.println("Motor detenido manualmente");
      } else if (!obstaculoDetectado) {
        encenderMotor();
        motorFuncionando = true;
        Serial.println("Motor encendido manualmente");
      } else {
        Serial.println("❌ No se puede encender - obstáculo detectado");
      }
      break;
      
    case 'r':
    case 'R':
      // Reversa (solo si no hay obstáculo)
      if (!obstaculoDetectado) {
        encenderMotorReversa();
        motorFuncionando = true;
        Serial.println("Motor en REVERSA");
      } else {
        Serial.println("❌ No se puede activar reversa - obstáculo detectado");
      }
      break;
      
    case 'f':
    case 'F':
      // Adelante (solo si no hay obstáculo)
      if (!obstaculoDetectado) {
        encenderMotor();
        motorFuncionando = true;
        Serial.println("Motor ADELANTE");
      } else {
        Serial.println("❌ No se puede mover adelante - obstáculo detectado");
      }
      break;
      
    case '+':
      velocidad = min(255, velocidad + 25);
      Serial.print("Nueva velocidad: ");
      Serial.println(velocidad);
      if (motorFuncionando && !obstaculoDetectado) {
        analogWrite(MOTOR_ENA, velocidad);
      }
      break;
      
    case '-':
      velocidad = max(50, velocidad - 25);
      Serial.print("Nueva velocidad: ");
      Serial.println(velocidad);
      if (motorFuncionando && !obstaculoDetectado) {
        analogWrite(MOTOR_ENA, velocidad);
      }
      break;
      
    case 't':
    case 'T':
      testSensor();
      break;
      
    case 'i':
    case 'I':
      mostrarInfo();
      break;
      
    case 'h':
    case 'H':
      mostrarAyuda();
      break;
      
    default:
      Serial.println("Comando no válido. Usa 'h' para ayuda");
      break;
  }
}

// ===== FUNCIONES DE INFORMACIÓN =====
void mostrarInfo() {
  Serial.println("\n=== ESTADO DEL SISTEMA ===");
  Serial.print("Motor: ");
  Serial.println(motorFuncionando ? "FUNCIONANDO" : "DETENIDO");
  Serial.print("Velocidad: ");
  Serial.print(velocidad);
  Serial.println("/255");
  Serial.print("Sensor IR: ");
  Serial.println(digitalRead(SENSOR_IR) == LOW ? "OBSTÁCULO DETECTADO" : "LIBRE");
  Serial.print("Obstáculo: ");
  Serial.println(obstaculoDetectado ? "SÍ" : "NO");
  Serial.print("LED: ");
  Serial.println(digitalRead(LED_INDICADOR) ? "ENCENDIDO" : "APAGADO");
  Serial.println("==========================\n");
}

void mostrarAyuda() {
  Serial.println("\n=== COMANDOS DISPONIBLES ===");
  Serial.println("s = Start/Stop motor manual");
  Serial.println("f = Forzar adelante");
  Serial.println("r = Forzar reversa");
  Serial.println("+ = Aumentar velocidad");
  Serial.println("- = Disminuir velocidad");
  Serial.println("t = Test del sensor");
  Serial.println("i = Mostrar información");
  Serial.println("h = Mostrar ayuda");
  Serial.println("============================");
  Serial.println("🚨 El motor se detiene automáticamente");
  Serial.println("   cuando se detecta un obstáculo");
  Serial.println("============================\n");
}

void testSensor() {
  Serial.println("\n=== TEST DEL SENSOR IR ===");
  Serial.println("Acerca un objeto al sensor...");
  
  for (int i = 0; i < 50; i++) {
    int lectura = digitalRead(SENSOR_IR);
    Serial.print("Lectura ");
    Serial.print(i + 1);
    Serial.print("/50: ");
    Serial.print(lectura == LOW ? "OBSTÁCULO" : "LIBRE");
    Serial.print(" (");
    Serial.print(lectura);
    Serial.println(")");
    
    digitalWrite(LED_INDICADOR, lectura == LOW ? HIGH : LOW);
    delay(200);
  }
  
  digitalWrite(LED_INDICADOR, LOW);
  Serial.println("=== TEST COMPLETADO ===\n");
}