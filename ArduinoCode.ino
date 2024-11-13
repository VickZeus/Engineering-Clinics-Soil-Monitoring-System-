void setup() {
    Serial.begin(9600);
}

void loop() {
    int moisture = analogRead(A0);      
    int ph = analogRead(A3);            
    int temperature = analogRead(A5);   
    
    if(moisture>645)moisture=645;
    if(moisture<300)moisture=300;


    Serial.print(moisture);
    Serial.print(",");
    Serial.print(ph);
    Serial.print(",");
    Serial.println(temperature); 
    delay(200);
}
 