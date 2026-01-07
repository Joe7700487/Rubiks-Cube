/*
    Controlling two stepper with the AccelStepper library

     by Dejan, https://howtomechatronics.com
*/

#include <string.h>
#include <AccelStepper.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

#define SERVOMIN 125 // 0
#define SERVOMAX 625 // 180

#define HANDOFF 0 // off position of hands
#define NORMAL 70
#define WIDE 110

#define BLOCKOFF 80 // off position of block
#define BLOCKON 5 // on position of block

#define FULLTURN 1600
#define HALFTURN 800
#define QUARTERTURN 400

//Connect the PCA9685 To A4 and A5 pins are SDA/SCL. Also VCC, GND
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// Define the stepper motor and the pins that is connected to
AccelStepper stepper2(1, 3, 2); // (Typeof driver: with 2 pins, STEP, DIR)
AccelStepper stepper3(1, 5, 4);
AccelStepper stepper1(1, 7, 6);
AccelStepper* motor[3] = {&stepper1, &stepper2, &stepper3};

int incomingByte = 0;

void setup() {
  Serial.begin(9600);

  pwm.begin(); // start servo motors
  pwm.setPWMFreq(60);

  stepper1.setMaxSpeed(1000); // Set maximum speed value for the stepper
  stepper1.setAcceleration(500); // Set acceleration value for the stepper
  stepper1.setCurrentPosition(0); // Set the current position to 0 steps

  stepper2.setMaxSpeed(1000);
  stepper2.setAcceleration(500);
  stepper2.setCurrentPosition(0);

  stepper3.setMaxSpeed(1000);
  stepper3.setAcceleration(500);
  stepper3.setCurrentPosition(0);

  for (int i = 0; i < 3; i++) { // move all handles to default position
    pwm.setPWM(i, 0, angleToPulse(HANDOFF));
    delay(200);
  }

  pwm.setPWM(3, 0, angleToPulse(BLOCKOFF));
  delay(200);
  stepper1.moveTo(0); // Set desired move: 800 steps (in quater-step resolution that's one rotation)
  stepper1.runToPosition(); // Moves the motor to target position w/ acceleration/ deceleration and it blocks until is in position
  stepper2.moveTo(0);
  stepper2.runToPosition();
  stepper3.moveTo(0);
  stepper3.runToPosition();

  Serial.println("Done setup");
}

void loop() {
  if (Serial.available() > 0) {
    String move = Serial.readString();
    move.trim();
    // say what you got:
    Serial.print("I received: ");
    Serial.println(move);
    if (move == "i") { 
      Serial.println("Moving motor ");
      turnFace(0, 1);
      turnFace(1, 1);
      turnFace(2, 1);
    }
    if (move == "o") { 
      Serial.println("Moving motor ");
      turnFace(0, 2);
      turnFace(1, 2);
      turnFace(2, 2);
    }
    if (move == "p") { 
      Serial.println("Moving motor ");
      turnFace(0, 3);
      turnFace(1, 3);
      turnFace(2, 3);
    }
    if (move == "[") { 
      Serial.println("Moving motor ");
      pwm.setPWM(0, 0, angleToPulse(WIDE));
      pwm.setPWM(1, 0, angleToPulse(WIDE));
      pwm.setPWM(2, 0, angleToPulse(WIDE));
    }
    if (move == "]") { 
      Serial.println("Moving motor ");
      pwm.setPWM(0, 0, angleToPulse(HANDOFF));
      pwm.setPWM(1, 0, angleToPulse(HANDOFF));
      pwm.setPWM(2, 0, angleToPulse(HANDOFF));
    }
  }
}

void turnFace(int side, int layers) { // turns a side by taking in what side and how many layers to turn
  if (layers == 1) {
    pwm.setPWM(side, 0, angleToPulse(NORMAL));
    delay(200);
    motor[side]->moveTo(motor[side]->currentPosition() + HALFTURN); // Set desired move: 800 steps (in quater-step resolution that's one rotation)
    motor[side]->runToPosition(); // Moves the motor to target position w/ acceleration/ deceleration and it blocks until is in position
    pwm.setPWM(side, 0, angleToPulse(HANDOFF));
    delay(200);
  }
  else if (layers == 2) {
    pwm.setPWM(3, 0, angleToPulse(BLOCKON));
    pwm.setPWM(side, 0, angleToPulse(WIDE));
    delay(200);
    motor[side]->moveTo(motor[side]->currentPosition() + HALFTURN); // Set desired move: 800 steps (in quater-step resolution that's one rotation)
    motor[side]->runToPosition(); // Moves the motor to target position w/ acceleration/ deceleration and it blocks until is in position
    pwm.setPWM(side, 0, angleToPulse(HANDOFF));
    pwm.setPWM(3, 0, angleToPulse(BLOCKOFF));
    delay(200);
  }
  else if (layers == 3) {
    pwm.setPWM(side, 0, angleToPulse(WIDE));
    delay(200);
    motor[side]->moveTo(motor[side]->currentPosition() + HALFTURN); // Set desired move: 800 steps (in quater-step resolution that's one rotation)
    motor[side]->runToPosition(); // Moves the motor to target position w/ acceleration/ deceleration and it blocks until is in position
    pwm.setPWM(side, 0, angleToPulse(HANDOFF));
    delay(200);
  }
}

int angleToPulse(int ang) {
  int pulse = map(ang, 0, 180, SERVOMIN, SERVOMAX);
  // Serial.print("Angle: "); Serial.print(ang);
  // Serial.print(" Pulse: "); Serial.println(pulse);
  return pulse;
}