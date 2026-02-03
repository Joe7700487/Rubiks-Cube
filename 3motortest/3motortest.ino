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
#define DELAY 75
#define POSTDELAY 75

#define STEPPERACC 8000
#define STEPPERSPEED 6000

#define HANDOFF 0 // off position of hands
#define NORMAL 110 // single layer position
#define WIDE 150 // double and triple layer position

#define BLOCKOFF 75 // off position of block
#define BLOCKON 3 // on position of block

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
AccelStepper stepper1(1, 25, 26); // R
AccelStepper stepper3(1, 27, 14); // U
AccelStepper stepper2(1, 33, 32); // B
AccelStepper* motor[3] = {&stepper1, &stepper2, &stepper3};
// if motor.position is a multiple of 800 or 0, its default state
// if not, its 90 degrees of default

void setup() {
  Serial.begin(115200);

  Wire.begin(21, 22);
  Wire.setClock(400000);
  pwm.begin(); // start servo motors
  pwm.setPWMFreq(50);
  delay(5);

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
    char move[12];
    int n = Serial.readBytesUntil('\n', move, sizeof(move) - 1);
    if (n <= 0) return;
    if (move[n-1] == '\r') n--; // trim CR if present
    move[n] = '\0';

    if (strcmp(move, "S") == 0) {
      String moves[44] = { "B", "Rw", "3Bw", "B", "Bw", "Rw", "3Uw", "3Bw", "Uw'", "B", "3Rw", "Uw2", "Bw'", "3Rw'", "B'", "Uw2", "Bw2", "3Rw", "3Bw2", "U2", "Rw2", "U'", "R", "Uw2", "Bw2", "3Bw'", "3Rw2", "U", "3Rw2", "B2", "R2", "B2", "3Uw2", "3Bw2", "U2", "3Bw", "3Rw2", "U'", "B'", "3Uw'", "3Rw", "R'", "3Bw", "U2" };
      // String tperm[14] = { "R", "U", "R'", "U'", "R'", "3Bw", "U2", "3Rw'", "3Bw'", "U'", "3Bw", "3Rw", "U'", "3Bw'" };

      for (String m : moves ) {
        turnFace(m);
      }
      return;
    }

    turnFace(move);
  }
}

void turnFace(String move) {
  int comp;
  int layers;
  int amount;
  int side = -1;
  if (move.indexOf("3") != -1) {
    layers = 3;
  }
  else if (move.indexOf("w") != -1) {
    layers = 2;
  }
  else {
    layers = 1;
  }
  if (move.indexOf("'") != -1) {
    amount = CCW;
  }
  else if (move.indexOf("2") != -1) {
    amount = DOUBLE;
  }
  else {
    amount = CW;
  }
  if (amount > 0) {
    comp = COMPENSATION;
  }
  else if (amount < 0) {
    comp = COMPENSATION * -1;
  }
  if (move.indexOf("R") != -1) {
    side = R;
  }
  else if (move.indexOf("U") != -1) {
    side = U;
  }
  else if (move.indexOf("B") != -1) {
    side = B;
  }
  if (side == -1) {
    return;
  }
  Serial.println(move);
  if (layers == 1) {
    pwm.setPWM(3, 0, angleToPulse(BLOCKON));
    pwm.setPWM(side, 0, angleToPulse(NORMAL));
    delay(POSTDELAY);

    motor[side]->moveTo(motor[side]->currentPosition() + amount + comp);
    while(motor[side]->distanceToGo() != 0) {
      motor[side]->run();
    }
    motor[side]->moveTo(motor[side]->currentPosition() - comp);
    while(motor[side]->distanceToGo() != 0) {
      motor[side]->run();
    }

    pwm.setPWM(side, 0, angleToPulse(HANDOFF));
    pwm.setPWM(3, 0, angleToPulse(BLOCKOFF));
    delay(DELAY);
  }
  else if (layers == 2) {
    pwm.setPWM(3, 0, angleToPulse(BLOCKON));
    pwm.setPWM(side, 0, angleToPulse(WIDE));
    delay(POSTDELAY);

    motor[side]->moveTo(motor[side]->currentPosition() + amount + comp);
    while(motor[side]->distanceToGo() != 0) {
      motor[side]->run();
    }
    motor[side]->moveTo(motor[side]->currentPosition() - comp);
    while(motor[side]->distanceToGo() != 0) {
      motor[side]->run();
    }

    pwm.setPWM(side, 0, angleToPulse(HANDOFF));
    pwm.setPWM(3, 0, angleToPulse(BLOCKOFF));
    delay(DELAY);
  }
  else if (layers == 3) {
    pwm.setPWM(side, 0, angleToPulse(WIDE));
    delay(POSTDELAY);

    motor[side]->moveTo(motor[side]->currentPosition() + amount + comp);
    while(motor[side]->distanceToGo() != 0) {
      motor[side]->run();
    }
    motor[side]->moveTo(motor[side]->currentPosition() - comp);
    while(motor[side]->distanceToGo() != 0) {
      motor[side]->run();
    }

    pwm.setPWM(side, 0, angleToPulse(HANDOFF));
    delay(DELAY);
  }
}

int angleToPulse(int ang) {
  ang = constrain(ang, 0, 180);
  int pulse = map(ang, 0, 180, SERVOMIN, SERVOMAX);
  return pulse;
}

