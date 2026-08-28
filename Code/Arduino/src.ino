int RED_PIN = 3;
int GREEN_PIN = 5;
int BLUE_PIN = 6;

void setup() {
  Serial.begin(9600);

  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);

  analogWrite(RED_PIN, 0);
  analogWrite(GREEN_PIN, 0);
  analogWrite(BLUE_PIN, 0);
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    // Connection test
    if (command == "PING") {Serial.println("PONG");}
      
    // RGB color
    else if (command.startsWith("COLOR:")) {
      int first = command.indexOf(':');
      String values = cmd.substring(first + 1);

      int comma1 = values.indexOf(',');
      int comma2 = values.indexOf(',', comma1 + 1);

      if (comma1 != -1 && comma2 != -1) {
        int r = values.substring(0, comma1).toInt();
        int g = values.substring(comma1 + 1, comma2).toInt();
        int b = values.substring(comma2 + 1).toInt();

        r = constrain(r, 0, 255);
        g = constrain(g, 0, 255);
        b = constrain(b, 0, 255);
        
        analogWrite(RED_PIN, r);
        analogWrite(GREEN_PIN, g);
        analogWrite(BLUE_PIN, b);
      }
    }
  }
}
