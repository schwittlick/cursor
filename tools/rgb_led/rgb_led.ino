int redPin = 5;
int greenPin = 6;
int bluePin = 7;
String inputString = "";         // string to hold input
boolean stringComplete = false;  // whether the string is complete

void setup() {
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
  Serial.begin(9600);        // initialize serial communication
  inputString.reserve(200);  // reserve 200 bytes for the inputString
}

void loop() {
  // when a complete message arrives, process the RGB values
  if (stringComplete) {
    if (inputString.startsWith("RGB") && inputString.endsWith(";")) {
      // Remove "RGB" prefix and ";" suffix
      String values = inputString.substring(5, inputString.length() - 1);

      // parse the comma-separated values
      int firstComma = values.indexOf(',');
      int secondComma = values.indexOf(',', firstComma + 1);

      if (firstComma != -1 && secondComma != -1) {
        int r = values.substring(0, firstComma).toInt();
        int g = values.substring(firstComma + 1, secondComma).toInt();
        int b = values.substring(secondComma + 1).toInt();

        // constrain values between 0 and 255
        r = constrain(r, 0, 255);
        g = constrain(g, 0, 255);
        b = constrain(b, 0, 255);

        setColor(r, g, b);

        // echo back the received values
        Serial.print("Set RGB to: ");
        Serial.print(r);
        Serial.print(",");
        Serial.print(g);
        Serial.print(",");
        Serial.println(b);
      }
    } else {
      Serial.println("Invalid format. Use: RGB255,0,0;");
    }

    // clear the string for new input
    inputString = "";
    stringComplete = false;
  }
}

void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();

    // if the incoming character is a semicolon, set a flag
    if (inChar == ';') {
      stringComplete = true;
    } else {
      inputString += inChar;
    }
  }
}

void setColor(int r, int g, int b) {
  analogWrite(redPin, r);
  analogWrite(greenPin, g);
  analogWrite(bluePin, b);
}