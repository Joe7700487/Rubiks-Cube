# Rubiks-Cube

This repository contains software and hardware work for a Rubik's Cube project: Python-based solvers and visualizers, a C++ solver prototype, firmware for a motorized mechanism, and KiCad PCB files.

## Repository layout

- `Python Solver/`
  - `cube.py`: 3x3 pygame-based cube visualizer and solver experiments. Based off this article https://observablehq.com/@onionhoney/how-to-model-a-rubiks-cube
  - `4x4solver.py`: 4x4 solver work using pruning tables and iterative deepening search.
  - `4x4visual.py`: helper script for converting or visualizing 4x4 facelet states.
  - `MoveConverter.py`: utility script that rewrites move sequences into the move vocabulary used by the robot.
  - `*PruningTable.py`, `g3SolvedStates.py`: precomputed search data and solved-state helpers used by the Python solvers.
- `C++ Cube Solver/`
  - Visual Studio solution for a C++/SDL3 cube renderer and move application prototype.
- `Firmware/`
  - `3motortest.ino`: ESP32/Arduino firmware for driving three steppers and servos to execute cube moves.
- `PCB/Driver/`
  - KiCad design files for the cube driver prototype board.
- `3D models/`
  - Reserved for CAD or printable mechanical parts.

## Python solver tools

The Python code is where most of the cube logic currently lives. It includes:

- Facelet-based move application.
- Geometric sticker representations for cube state conversion.
- Pruning-table-driven search for 3x3 and 4x4 solving stages.
- A move conversion helper for translating notation into the robot-friendly move set.

### Python requirements

Install Python 3.10+ and the runtime dependencies used by the scripts:

```powershell
pip install pygame numpy
```

### Running the Python scripts

From the repository root:

```powershell
cd "Python Solver"
python MoveConverter.py
python cube.py
python 4x4solver.py
python 4x4visual.py
```

Notes:

- `MoveConverter.py` is the simplest standalone utility and prints a converted move sequence.
- `cube.py`, `4x4solver.py`, and `4x4visual.py` open pygame windows and are set up as interactive experiment scripts rather than polished command-line tools.
- The pruning-table modules are committed directly in the repository, so there is no separate generation step required just to run the current Python code.

## C++ solver prototype

The `C++ Cube Solver` folder contains a Visual Studio solution targeting Windows and SDL3. The current code focuses on:

- Representing a 3x3 cube as a fixed-size array.
- Applying face turns efficiently.
- Rendering a cube net with SDL3.
- Basic keyboard-triggered test actions.

### C++ requirements

The Visual Studio project currently references SDL3 from a local path

### Building the C++ project

1. Open `C++ Cube Solver/Cube Solver.sln` in Visual Studio 2022.
2. Install or point the project at a local SDL3 checkout.
3. Select `Debug|x64` or `Release|x64`.
4. Build and run the `Cube Solver` project.

The current SDL application can render the cube net and respond to a few keyboard events for testing moves and performance.

## Firmware

`Firmware/3motortest.ino` is an Arduino-style control program for a three-motor cube turning mechanism. It uses:

- `AccelStepper`
- `Wire`
- `Adafruit_PWMServoDriver`

The firmware appears to target an ESP32-based setup with:

- Three stepper channels for face turns.
- A PCA9685 servo driver.
- Servo-controlled hands and a blocking mechanism.
- Serial move input such as `R`, `U`, `B`, wide moves, triple-layer moves, primes, and double turns.

### Firmware setup

1. Open `Firmware/3motortest.ino` in the Arduino IDE or PlatformIO.
2. Install the required libraries.
3. Select the correct ESP32 board and serial port.
4. Upload the sketch.
5. Send newline-terminated move commands over serial.

The special serial command `S` runs a built-in demonstration sequence.

## PCB files

The `PCB/Driver` directory contains the KiCad project for the driver board, including schematic, PCB layout, footprints, symbols, drill files, and Gerber job data.

Open `PCB/Driver/Driver.kicad_pro` in KiCad to inspect or modify the design.

## Project status

This repository is best understood as an actively developed project workspace rather than a packaged library. The main value is in the implementation details for cube state handling, solver experiments, and the integration path from software to physical hardware.