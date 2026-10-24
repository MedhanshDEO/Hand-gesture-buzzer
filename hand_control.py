import cv2
import mediapipe as mp
import numpy as np
import time

# ---------- SETTINGS ----------
USE_ARDUINO = True      # set to True when the Arduino is connected
PORT = 'COM5'            # change to your Arduino's port
# ------------------------------

arduino = None
if USE_ARDUINO:
    import serial
    arduino = serial.Serial(PORT, 9600, timeout=1)
    time.sleep(2)  # wait for Arduino to reset after connecting

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1,
                       min_detection_confidence=0.7,
                       min_tracking_confidence=0.6)

def dist(a, b):
    return np.hypot(a.x - b.x, a.y - b.y)

def count_fingers(lm):
    count = 0
    # Four fingers: tip above the middle joint means the finger is up
    for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]:
        if lm[tip].y < lm[pip].y:
            count += 1
    # Thumb: tip farther from the pinky base than the thumb's joint
    if dist(lm[4], lm[17]) > dist(lm[3], lm[17]):
        count += 1
    return count

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

cv2.namedWindow("Hand Control", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Hand Control", 1280, 720)
last_sent = 0

while True:
    ok, frame = cap.read()
    if not ok:
        print("Could not read from camera")
        break

    frame = cv2.flip(frame, 1)  # mirror view
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        hand = result.multi_hand_landmarks[0]
        lm = hand.landmark
        fingers = count_fingers(lm)
        angle = int(np.interp(lm[9].x, [0.1, 0.9], [0, 180]))

        if arduino and time.time() - last_sent > 0.05:
            arduino.write(f"{fingers},{angle}\n".encode())
            last_sent = time.time()

        mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
        cv2.putText(frame, f"Fingers: {fingers}  Angle: {angle}", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
    h, w = frame.shape[:2]
    names = ["G4", "A4", "B4", "C5", "D5", "E5", "F5", "G5"]
    for k in range(9):
        x = int(w * (0.1 + 0.8 * k / 8))
        cv2.line(frame, (x, 0), (x, h), (255, 255, 255), 1)
        if k < 8:
            cv2.putText(frame, names[k], (x + 8, h - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    cv2.imshow("Hand Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
if arduino:
    arduino.close()
cv2.destroyAllWindows()