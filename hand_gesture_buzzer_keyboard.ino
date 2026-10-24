const int RED_PIN    = 9;
const int GREEN_PIN  = 10;
const int BLUE_PIN   = 11;
const int BUZZER_PIN = 6;

const unsigned long TIMEOUT_MS = 300;

// 8 notes, left to right: G4 A4 B4 C5 D5 E5 F5 G5
const int NOTES[8] = {392, 440, 494, 523, 587, 659, 698, 784};

// LED colour for each note
const int NOTE_COLORS[8][3] = {
  {255, 0,   0},     // G4 red
  {255, 110, 0},     // A4 orange
  {255, 255, 0},     // B4 yellow
  {0,   255, 0},     // C5 green
  {0,   255, 255},   // D5 cyan
  {0,   0,   255},   // E5 blue
  {150, 0,   255},   // F5 violet
  {255, 0,   255}    // G5 magenta
};

int currentZone = -1;        // -1 = silent
unsigned long lastData = 0;

void setColor(int r, int g, int b) {
  analogWrite(RED_PIN, r);
  analogWrite(GREEN_PIN, g);
  analogWrite(BLUE_PIN, b);
}

void playZone(int z) {
  currentZone = z;
  tone(BUZZER_PIN, NOTES[z]);
  setColor(NOTE_COLORS[z][0], NOTE_COLORS[z][1], NOTE_COLORS[z][2]);
}

void silence() {
  currentZone = -1;
  noTone(BUZZER_PIN);
  setColor(0, 0, 0);
}

void setup() {
  Serial.begin(9600);
  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  silence();
}

void loop() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    int comma = line.indexOf(',');
    if (comma > 0) {
      int fingers = constrain(line.substring(0, comma).toInt(), 0, 5);
      int angle = constrain(line.substring(comma + 1).toInt(), 0, 180);
      lastData = millis();

      if (fingers == 0) {
        silence();                         // fist = stop the note
      } else {
        int target = constrain(angle * 8 / 181, 0, 7);
        if (currentZone == -1) {
          playZone(target);                // starting a new note
        } else if (target != currentZone) {
          // hysteresis: only switch once the hand is clearly in the next zone
          float center = (currentZone + 0.5) * 22.5;
          if (abs(angle - center) > 14.25) {
            playZone(target);
          }
        }
      }
    }
  }

  if (millis() - lastData > TIMEOUT_MS) {
    if (currentZone != -1) silence();      // hand left the camera
  }
}