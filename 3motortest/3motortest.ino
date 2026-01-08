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

#define STEPPERACC 2000
#define STEPPERSPEED 2500

#define HANDOFF 0 // off position of hands
#define NORMAL 70 // single layer position
#define WIDE 110  // double and triple layer position

#define BLOCKOFF 80 // off position of block
#define BLOCKON 3 // on position of block

// #define FULLTURN 1600
// #define HALFTURN 800
// #define QUARTERTURN 400

#define COMPENSATION 50 // compensation for wiggle in the mechanism to ensure turns are complete
#define CW -400 // 90 degrees clockwise rotation
#define CCW 400 // 90 degrees counter clockwise rotation
#define DOUBLE 800 // 180 degree rotation

#define R 0 // motor id for R move
#define U 1 // motor id for U move
#define B 2 // motor id for B move
#define L 0 // motor id for L move (3Rw)
#define D 1 // motor id for D move (3Uw)
#define F 2 // motor id for F move (3Fw)

//Connect the PCA9685 To A4 and A5 pins are SDA/SCL. Also VCC, GND
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// Define the stepper motor and the pins that is connected to
AccelStepper stepper2(1, 3, 2); // U
AccelStepper stepper3(1, 5, 4); // B
AccelStepper stepper1(1, 7, 6); // R
AccelStepper* motor[3] = {&stepper1, &stepper2, &stepper3};
// if motor.position is a multiple of 800 or 0, its default state
// if not, its 90 degrees of default

// [{side, layers, amount, stepper.pos, servo.pos}, ...]
class Move {
  public:
    int side;
    int layers;
    int amount;
    AccelStepper* stepper; // motor[side]->currentPosition() to calculate state
    // tracking for servo state if needed
    Move (int index, int moveLayers, int stepperAmount) {
      side = index;
      layers = moveLayers;
      amount = stepperAmount;
      stepper = motor[index];
    }
};



void setup() {
  Serial.begin(9600);

  pwm.begin(); // start servo motors
  pwm.setPWMFreq(60);

  stepper1.setMaxSpeed(STEPPERSPEED);
  stepper1.setAcceleration(STEPPERACC);
  stepper1.setCurrentPosition(0);
  stepper2.setMaxSpeed(STEPPERSPEED);
  stepper2.setAcceleration(STEPPERACC);
  stepper2.setCurrentPosition(0);

  stepper3.setMaxSpeed(STEPPERSPEED);
  stepper3.setAcceleration(STEPPERACC);
  stepper3.setCurrentPosition(0);

  for (int i = 0; i < 3; i++) { // move all handles to default position
    pwm.setPWM(i, 0, angleToPulse(HANDOFF));
  }
  pwm.setPWM(3, 0, angleToPulse(BLOCKOFF));

  // set default position of steppers
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

    if (move == "S") {
      // (R U R' U') (R' 3Bw U2) (3Rw' 3Bw' U') (3Bw 3Rw U' 3Bw')
      turnFace(R, 1, CW);
      turnFace(U, 1, CW);
      turnFace(R, 1, CCW);
      turnFace(U, 1, CCW);

      turnFace(R, 1, CCW);
      turnFace(B, 3, CW);
      turnFace(U, 1, DOUBLE);

      turnFace(R, 3, CCW);
      turnFace(B, 3, CCW);
      turnFace(U, 1, CCW);

      turnFace(B, 3, CW);
      turnFace(R, 3, CW);
      turnFace(U, 1, CCW);
      turnFace(B, 3, CCW);
    }

    if (move == "R") {
      turnFace(R, 1, CW);
    }
    if (move == "R'") {
      turnFace(R, 1, CCW);
    }

    if (move == "U") {
      turnFace(U, 1, CW);
    }

    if (move == "B") {
      turnFace(B, 1, CW);
    }
  }
}

// 0 = R
// 1 = U
// 2 = B
// 4 = Blocker for wide moves
// turns a side by taking in what side and how many layers to turn
void turnFace(int side, int layers, int amount) { // no functionality for lookahead
  int comp;
  if (amount > 0) {
    comp = COMPENSATION;
  }
  else if (amount < 0) {
    comp = COMPENSATION * -1;
  }
  if (layers == 1 || layers == 2) {
    pwm.setPWM(3, 0, angleToPulse(BLOCKON));
    pwm.setPWM(side, 0, angleToPulse(NORMAL));
    delay(200);

    motor[side]->moveTo(motor[side]->currentPosition() + amount + comp);
    motor[side]->runSpeedToPosition();
    while(motor[side]->distanceToGo() != 0) {motor[side]->run();}
    motor[side]->moveTo(motor[side]->currentPosition() - comp);
    motor[side]->runSpeedToPosition();
    while(motor[side]->distanceToGo() != 0) {motor[side]->run();}

    pwm.setPWM(side, 0, angleToPulse(HANDOFF));
    pwm.setPWM(3, 0, angleToPulse(BLOCKOFF));
    delay(300);
  }
  else if (layers == 2) {
    pwm.setPWM(3, 0, angleToPulse(BLOCKON));
    pwm.setPWM(side, 0, angleToPulse(WIDE));
    delay(200);

    motor[side]->moveTo(motor[side]->currentPosition() + amount + comp);
    motor[side]->runSpeedToPosition();
    while(motor[side]->distanceToGo() != 0) {motor[side]->run();}
    motor[side]->moveTo(motor[side]->currentPosition() - comp);
    motor[side]->runSpeedToPosition();
    while(motor[side]->distanceToGo() != 0) {motor[side]->run();}

    pwm.setPWM(side, 0, angleToPulse(HANDOFF));
    pwm.setPWM(3, 0, angleToPulse(BLOCKOFF));
    delay(300);
  }
  else if (layers == 3) {
    pwm.setPWM(side, 0, angleToPulse(WIDE));
    delay(200);

    motor[side]->moveTo(motor[side]->currentPosition() + amount + comp);
    motor[side]->runSpeedToPosition();
    while(motor[side]->distanceToGo() != 0) {motor[side]->run();}
    motor[side]->moveTo(motor[side]->currentPosition() - comp);
    motor[side]->runSpeedToPosition();
    while(motor[side]->distanceToGo() != 0) {motor[side]->run();}

    pwm.setPWM(side, 0, angleToPulse(HANDOFF));
    delay(200);
  }
}

// prepare > activate > move
// before executing the current move, deactivate the previous, activate the current at the same time and
// prepare the next move at the same time
void movement (int previousMove, int currentMove, int nextMove) {
  // 1.deactivate previous and activate current at the same time
  // (shouldnt cause a collision due to preparation from the previous move)
  // while activating and deactiviating, prepare the next move to prevent collisions
  // (collisions could happen when preparing move while executing move)
  // 2.execute the current move
  // 3.repeat with following moves 

  // moves could be stored as
  // [{side, layers, amount, stepper.pos, servo.pos}, ...]
}

// simultaneous moves
// default position is handles inline with gears
// moved position is 90 degrees of default position
// one handle activates as another deactivates. only possible when both handles involved are matching state
// option 1: keep track of handle positions to move simultaneously when possible
// option 2: keep track of current handle position while activited and position 
//           the next move to match state during the current move 
//           (anticipation of next move should happen before the rotation of the current move)

int angleToPulse(int ang) {
  int pulse = map(ang, 0, 180, SERVOMIN, SERVOMAX);
  return pulse;
}

