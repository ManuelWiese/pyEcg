void setup() {
  pinMode(10,INPUT);
  pinMode(11,INPUT);

  Serial.begin(115200);
}

void loop() {
  if((digitalRead(10)==1)||(digitalRead(11)==1)){
      Serial.println("Gagal");
  }
  else{
      Serial.println(analogRead(A1));
  }
  delay(5);
}
