void setup() {
  pinMode(10,INPUT);
  pinMode(11,INPUT);

  Serial.begin(115200);
}

unsigned long micros_pre = 0;
unsigned long micros_interval = 5000;

void loop() {
  micros_pre = micros();
  
  Serial.print(micros_pre);
  Serial.print("||");
  
  if((digitalRead(10)==1)||(digitalRead(11)==1)){
      Serial.println("Gagal");
  }
  else{
      Serial.println(analogRead(A1));
  }
  
  while(micros() < micros_pre + micros_interval) {
     //waiting 
  }
}

