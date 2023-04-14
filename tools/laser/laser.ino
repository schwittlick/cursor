//sets digital pin 3 to pulse width value

const int outPin = 9;

void setup() {

  Serial.begin(9600);
  pinMode(outPin, OUTPUT);
  Serial.println("Input required pulse width as percentage!");

}

void loop() {

  int mVal; // holds the PWM value as percent
  
  if(Serial.available() > 0){
    mVal = Serial.parseInt();
    if(mVal < 101){
      int tVal = (mVal*255)/100;
      analogWrite(outPin, tVal);
    }
    Serial.print("pulse width = "); Serial.print(mVal); Serial.println("%");
  }
}
