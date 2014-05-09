// This program can the capacitance values of two programmable capacitors (Intersil X90100) via USB serial communication
// Syntax: Axx will change the value Capacitor A, Bxx will change the value of Capacitor B, where xx is a number between 0 and 31

// Reference: http://arduinobasics.blogspot.com/2012/07/arduino-basics-simple-arduino-serial.html
String inString;  
// Buffer to store incoming commands from serial port; 
// String method can be found at http://arduino.cc/en/Reference/StringObject

int UD = 8;
int INC = 9; 
int CS0 = 10;
int CS1 = 11; 

void setup() {
    pinMode(UD, OUTPUT);
    pinMode(INC, OUTPUT);
    pinMode(CS0, OUTPUT);
    pinMode(CS1, OUTPUT);
    digitalWrite(CS0, HIGH);
    digitalWrite(CS1, HIGH);
    digitalWrite(INC, HIGH);  // INC is negative-edge triggered
    digitalWrite(UD, HIGH);
    Serial.begin(9600);
    Serial.println("Waiting for instructions...");
}

void outputIncPulse(int nCount) {
    // INC always starts with HIGH and ends with HIGH
    int ii; 
    int pulseHalfCycle = 2;  // unit: ms
    digitalWrite(INC, HIGH);
    for(ii=0; ii<nCount; ii++) {
        digitalWrite(INC, LOW);  // Trigger an increment/decrement
        delay(pulseHalfCycle);
        digitalWrite(INC, HIGH);
        delay(pulseHalfCycle);
    }
    Serial.print("Output pulse count of "); Serial.println(nCount); // for debugging purpose
}

void setCap(int nCount, int whichCap) {
    if (whichCap == 0)
        digitalWrite(CS0, LOW); 
    else if (whichCap == 1)
        digitalWrite(CS1, LOW); // Start writing cycle
    delay(2);
    digitalWrite(UD, LOW); delay(2); outputIncPulse(34);  // reset to 0
    digitalWrite(UD, HIGH); delay(2); outputIncPulse(nCount); 
    delay(2);
    if (whichCap == 0)
        digitalWrite(CS0, HIGH);  // end writin cycle
    else if (whichCap == 1)
        digitalWrite(CS1, HIGH); 
    delay(10);  // storage the write when CS is high and INC is high
}
void loop() {
    int nCount;
    while (Serial.available() > 0)
    {
        char received = Serial.read();
        inString += received; 

        // Process message when new line character is recieved
        if (received == '\n')
        {
            Serial.print("Arduino Received: ");
            Serial.print(inString);
            nCount = inString.substring(1).toInt();
            Serial.print("Capacitance count = "); Serial.println(nCount);
            
            if (inString.startsWith("A", 0) || inString.startsWith("a", 0) ){
                Serial.println("Setting Capacitor A");
                setCap(nCount, 0);
            }
            else if (inString.startsWith("B", 0) || inString.startsWith("b", 0) ){
                Serial.println("Setting Capacitor B");
                setCap(nCount, 1);
            }
            else
                Serial.println("Unrecognized command");
                
            inString = ""; // Clear received buffer
        }
    }
}
