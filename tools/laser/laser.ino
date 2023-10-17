const int outPin = 3;

void setup() {
  Serial.begin(9600);
  pinMode(outPin, OUTPUT);
  Serial.println("Input required pulse width as percentage!");

}

void loop() {
  delay(50);
  int av = Serial.available();
  if(av != 0){
      Serial.println(av);
  }

  if(av == 1){
    int value = Serial.read() - '0';
    analogWrite(outPin, value);
    Serial.println(value);
  }
  if (av == 2) {
    char v1 = Serial.read();
    char v2 = Serial.read();
    char bu[3];
    bu[0] = v1;
    bu[1] = v2;
    bu[2] = '\0';
    int value;
    value = convert(atoi(bu));
    analogWrite(outPin, value);
    Serial.println(value);
  }

  if(av == 3){
    char v1 = Serial.read();
    char v2 = Serial.read();
    char v3 = Serial.read();
    char bu[4];
    bu[0] = v1;
    bu[1] = v2;
    bu[2] = v3;
    bu[3] = '\0';
    int value;
    value = convert(atoi(bu));
    analogWrite(outPin, value);
    Serial.println(value);
  }
}

int convert(int input){
  return (input*255)/100;
}
