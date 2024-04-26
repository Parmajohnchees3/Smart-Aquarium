// Define pH sensor pin
#define analog_in A0

// Define actuator I/O pins
const int in1 = 2; 
const int in2 = 3; 
const int in3 = 4; 

const int out1 = 7;
const int out2 = 8;
const int out3 = 9;


void setup() {
  Serial.begin(9600); // Initialize serial communication
  
  pinMode(in1, INPUT);
  pinMode(in2, INPUT);
  pinMode(in3, INPUT);

  pinMode(out1, OUTPUT);
  pinMode(out2, OUTPUT);
  pinMode(out3, OUTPUT);
}

void loop() {

  int sensorValue = analogRead(analog_in); // Read analog voltage from pin A0
  float voltage = sensorValue * (5.0 / 1023.0); // Convert ADC reading to voltage (assuming 5V reference voltage)
//  float dataToSend = mapFloat(sensorValue, 0.0, 1023.0, 14.0, 0.0); // Scale the sensor value to fit into 8-bit range

  float dataToSend = sensorValue * -3.0 / 144 + 13.15;  // Scale sensor value via linear interpolation of known pH readings

  Serial.flush();
  Serial.println(dataToSend);   // Send pH data via serial communication


  // Define actuator behavior based on system inputs
  if (digitalRead(in1) == HIGH) {
    digitalWrite(out1, HIGH);
  }
  else {
    digitalWrite(out1, LOW);
  }
  
  if (digitalRead(in2) == HIGH) {
    digitalWrite(out2, HIGH);
  }
  else {
    digitalWrite(out2, LOW);
  }
  
  if (digitalRead(in3) == HIGH) {
    digitalWrite(out3, HIGH);
  }
  else {
    digitalWrite(out3, LOW);
  }

  delay(1000);

}

float mapFloat(float x, float in_min, float in_max, float out_min, float out_max) {
  // Map the input value x from the input range to the output range
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}
