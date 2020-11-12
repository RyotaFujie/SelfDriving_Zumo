/*
 * This example uses the ZumoMotors library to drive each motor on the Zumo
 * forward, then backward. The yellow user LED is on when a motor should be
 * running forward and off when a motor should be running backward. If a
 * motor on your Zumo has been flipped, you can correct its direction by
 * uncommenting the call to flipLeftMotor() or flipRightMotor() in the setup()
 * function.
 */

#include <Wire.h>
#include <ZumoShield.h>

#define LED_PIN 13

ZumoMotors motors;
byte readByte = 0;
int speed = 0;
int left = 0;
int right = 0;

void setup()
{
  pinMode(LED_PIN, OUTPUT);

  // uncomment one or both of the following lines if your motors' directions need to be flipped
  //motors.flipLeftMotor(true);
  //motors.flipRightMotor(true);
}

void loop() {

  //Get Serial
  if (Serial.available() > 0) {
    readByte = Serial.read();
   int speed = (int)readByte;
   int run = speed / 100;
   speed = speed % 100;
   int left = (speed / 10) * 28;
   int right = (speed % 10) * 28;
   if (run < 1) {
    left = 0;
    right = 0
   }
    //goForward(speed);
   motors.setSpeeds(left, right);
  }else {
    readByte = 0;
  }
  Serial.flush();
}
