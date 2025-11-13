
bool newData=false; // flag to indicate if new data is available

// A character variable to store the received command from the serial port.
//char recieved = "idle"; //set to i instead of idle to match type
char recieved = 'i';
int capValue = 0;   // val from analog sensor?
int endstopPin = 2; // pin for endstop signal
const int arraylen=500; // length of the array
int conductance[arraylen]; // array to store conductance values
int idx = 0; // index for the array
int sum =0; // sum of the conductance values
int threshold=100; // threshold value for endstop signal


void setup()
{
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);



  // digitalWrite(LED_BUILTIN, HIGH); // turn on the LED
  // delay(500);
  // digitalWrite(LED_BUILTIN, LOW);
  // delay(500);
  // digitalWrite(LED_BUILTIN, HIGH);
  // delay(500);
  // digitalWrite(LED_BUILTIN, LOW);
  // Serial.setTimeout(50);


  pinMode(endstopPin, OUTPUT); // D2
  digitalWrite(endstopPin, HIGH); // 
 
  for (int i = 0; i < 5; ++i) // can do arrayLen
  { 
    conductance[i]=0;
  }
}



void loop(){
  /*
  loop function that calls the recieve, sendcon, endstopsignal and sendtype functions
  */
  recieve();
  sendcon();
  endstopsignal();
  sendtype();
}

void recieve(){
  /*
  recieves the command from the serial port
  */
  if (Serial.available()>0){
    recieved=Serial.read();
    newData=true;
  }
}

void sendcon(){
  /*
  sends the conductance value to the serial port
  */
  if (newData==true){
    if (recieved=='r'){
      ///Serial.flush();
      capValue = 1023-analogRead(A6); // conductance value
      //reading the value of current taken away from A6

      Serial.println(capValue);
      newData=false;
    }
  }
}


void endstopsignal(){ //threshold problem
  /*
  turns light on if capValue is greater than threshold
  */
  
  capValue = 1023 - analogRead(A6);
  if (capValue > threshold){
    digitalWrite(endstopPin, HIGH);
    }
   else{
    digitalWrite(endstopPin, LOW);
    }
}

void sendtype(){
  if (newData==true){
    if (recieved=='t'){
      ///Serial.flush();
      Serial.println('c');
      newData=false;
    }
  }

}
