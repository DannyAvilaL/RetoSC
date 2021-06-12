#include <Adafruit_Sensor.h>
#include <Servo.h>

#include "DHT.h"
#define DHTTYPE DHT11

#define dht_dpin 5
#define outputA 6
#define outputB 7
#define boton 8

DHT dht(dht_dpin, DHTTYPE);

Servo servo;
int pos;

float counter = 0.5;
int aState;
int aLastState;

const int prev = 32;
const int playstop = 34;
const int next = 36;
bool estado = false;
const int ledCount = 10;
               
int scaledCounter = 0;
int sequenceNumber=0;  
int incomingByte = 0;  

int ledPins[] = {
  43, 42, 45, 44, 47, 46, 49, 48, 51, 50
};   // an array of pin numbers to which LEDs are attached
int inputValue = 0;

String control;

void setup()
{
  servo.attach(3);
  pinMode(outputA, INPUT);
  pinMode(outputB, INPUT);
  pinMode(boton, INPUT_PULLUP);
  Serial.begin(9600);
  aLastState = digitalRead(outputA);
  for (int thisLed = 0; thisLed < ledCount; thisLed++) {
    pinMode(ledPins[thisLed], OUTPUT);
  }
}


void loop() {
  volumen();
  botones();
  //servoControl();
  float sensorReading = volumen();
  sensorReading = sensorReading*1000;
  Serial.println(sensorReading);
  int ledLevel = map(sensorReading, 0, 1000, 0, ledCount);
  for (int thisLed = 0; thisLed <= ledCount; thisLed++) {
    if (thisLed <= ledLevel) {
      digitalWrite(ledPins[thisLed], HIGH);
    }
    else {
      digitalWrite(ledPins[thisLed], LOW);
    }
  }
  sensTemp();
  
  if (Serial.available()){
    control = Serial.readStringUntil('\n');
    control.trim();
    if (control.equals("turn_on")) {
      servoControl();
    }
  }
  
}

void botones()
{
  if(digitalRead(prev)){ 
    Serial.println("prev");
    delay(300);
  }

  if(digitalRead(playstop))
  {
    if(estado == true)
    {
      Serial.println("Stop");
      estado = false;
      delay(300);      
    }
    else
    {
      Serial.println("Play");
      estado = true;
      delay(300);
    }

  }

  if(digitalRead(next)){ 
    Serial.println("next"); 
    delay(300);
  }
}

float volumen()
{
  aState = digitalRead(outputA);
  if(aState != aLastState)
  {
    if(digitalRead(outputB) != aState)
    {
      if(counter <= 0.0)
      {
        counter = 0.0;
      }
      else
        counter = counter - 0.1;
    }
    else
    {
      if(counter >=1.0)
      {
        counter = 1.0;
      }
      else
      {
        counter = counter + 0.1;
      }
    }

    //Serial.println(counter);
  }
  aLastState = aState;
  return counter;
}

void sensTemp() {
    float h = dht.readHumidity();
    float t = dht.readTemperature();         
    Serial.print("Current temperature = ");
    Serial.print(t);
    Serial.print("C  ");
    Serial.print("humidity = ");
    Serial.print(h); 
    Serial.print("%");
    Serial.println(" ");
  delay(800);
}

void servoControl() {
  for(pos=0;pos<=180;pos++){
  servo.write(pos);
  delay(15);}
    delay(1000);
    for(pos=180;pos>=0;pos--){
  servo.write(pos);
  delay(15);
  }
    delay(1000); 
}
