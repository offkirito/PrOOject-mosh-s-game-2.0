// Ejemplo de comunicación serial en Arduino
const byte botonA = 2;
const byte botonB = 3;
const byte botonUp = 4;
const byte botonDown = 5;
const byte botonRight= 6;
const byte botonLeft = 7;

void setup() {
  Serial.begin(115200); // Inicia a 9600 baudios
  Serial.println("Listo para recibir datos...");
  pinMode(botonA, INPUT);
  pinMode(botonB, INPUT);
  pinMode(botonUp, INPUT);
  pinMode(botonDown, INPUT);
  pinMode(botonRight, INPUT);
  pinMode(botonLeft, INPUT);
}

void loop() {
  if (digitalRead(botonA) == LOW) {
    Serial.println("Boton A Presionado");
    delay(20); 
  }
  else if (digitalRead(botonB) == LOW) {
  Serial.println("Boton B Presionado");
    delay(20); 
  }
   else if (digitalRead(botonUp) == LOW) {
  Serial.println("UP");
    delay(20); 
  }
   else if (digitalRead(botonDown) == LOW) {
  Serial.println("Down");
    delay(20); 
  }
   else if (digitalRead(botonRight) == LOW) {
  Serial.println("Right");
    delay(20); 
  }
   else if (digitalRead(botonLeft) == LOW) {
  Serial.println("Left");
    delay(20); 
  }
   
}