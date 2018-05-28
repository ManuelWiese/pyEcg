void setup() {
  pinMode(10,INPUT);
  pinMode(11,INPUT);

  Serial.begin(115200);
}

unsigned long millis_pre = 0;
unsigned long millis_interval = 5;

void loop() {
  millis_pre = millis();
  
  Serial.print(millis_pre);
  Serial.print("||");
  
  if((digitalRead(10)==1)||(digitalRead(11)==1)){
      Serial.println("Gagal");
  }
  else{
      Serial.println(analogRead(A1));
  }
  
  while(millis() < millis_pre + millis_interval) {
     //waiting 
  }
}

