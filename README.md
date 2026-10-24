# Hand Gesture Buzzer

Play notes with your hand using a webcam, Python and an Arduino Uno R4 Minima.
MediaPipe tracks the hand, Python sends the finger count and hand position to
the Arduino over USB, and the Arduino plays notes on a passive buzzer and
changes the colour of an RGB LED.

## How it works
Webcam -> Python + MediaPipe -> USB serial -> Arduino -> Buzzer + RGB LED

- Hand position left to right selects one of 8 notes (G4 to G5)
- A fist stops the sound
- LED colour changes with the note

## Hardware
- Arduino Uno R4 Minima
- Passive buzzer on D6
- RGB LED module on D9 (R), D10 (G), D11 (B) with 220 ohm resistors
- Laptop with a webcam

## Setup
1. Install Python 3.11
2. `pip install -r requirements.txt`
3. Upload the sketch in `hand_gesture_notes` to the Arduino
4. In `hand_control.py`, set `USE_ARDUINO = True` and `PORT` to your COM port
5. Run `python hand_control.py` (press q to quit)

## Notes
- Needs MediaPipe 0.10.14, since newer versions removed the `solutions` API
- Close the Arduino Serial Monitor before running the Python script