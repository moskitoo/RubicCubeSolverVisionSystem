Rubik's Cube Solver
===================

This repository contains a Python program for solving a Rubik's Cube using computer vision and an Arduino. The program detects the colors on the Rubik's Cube through a camera and calculates the moves needed to solve it. It can also send these moves to an Arduino to physically solve the cube.

Prerequisites
-------------

Before running the program, make sure you have the following prerequisites installed:

-   Python 3.x
-   OpenCV (cv2)
-   NumPy
-   json
-   keyboard
-   math
-   kociemba
-   serial

You can install the required Python libraries using pip:


`pip install opencv-python numpy keyboard kociemba pyserial`

Usage
-----

1.  Clone the repository:


`git clone <repository_url>`

1.  Navigate to the repository directory:


`cd <repository_directory>`

1.  Run the `main.py` script:


`python main.py`

The program will start capturing video from the specified camera source (usually the default camera) and display the Rubik's Cube on the screen. You can interact with the program using keyboard shortcuts:

-   Press the number keys (1-6) to scan each side of the Rubik's Cube (up, right, front, down, left, back).
-   Press the corresponding letter keys (w, o, b, y, r, g) to calibrate the colors of the Rubik's Cube.
-   Press 'k' to generate the sequence of moves needed to solve the cube.
-   Press 's' to send the generated moves to the Arduino for physical cube manipulation.

Configuration
-------------

You can configure the program by modifying the `config.json` file. Here are some key configuration options:

-   `video`: Specify the camera source and the stop key (key to stop the program).
-   `cube`: Define the size of the Rubik's Cube.
-   `table`: Configure the table and slot dimensions, as well as the table color and line thickness.
-   `arduino`: Set the Arduino port, baud rate, and timeout.
-   `colors`: Define the RGB color values and corresponding codes for each Rubik's Cube color.
-   `buttons`: Configure the keyboard shortcuts for scanning, color calibration, generating moves, and sending moves to the Arduino.
