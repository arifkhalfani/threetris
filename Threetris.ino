// Threetris
// Arif Ismail

enum state {START_SCREEN = 0, GAME, END_SCREEN};

int state = START_SCREEN;
int score = 0;

// inputs
const byte BUTTON = A4;
const byte X_pin = A5;
const int DEBOUNCE_DELAY = 75;
unsigned long last_command_sent = 0;
const int command_rate = 300;

const byte ANODE_PINS[8] = {13, 12, 11, 10, 9, 8, 7, 6};
const byte CATHODE_PINS[8] = {A3, A2, A1, A0, 5, 4, 3, 2};
int grid[8][8];

void setup() {

  pinMode(BUTTON, INPUT_PULLUP);
  pinMode(X_pin, INPUT_PULLUP);

  state = START_SCREEN;
  score = 0;


  // sets every LED off

  for (byte i = 0; i < 8; i++) {
    pinMode(ANODE_PINS[i], OUTPUT);
    pinMode(CATHODE_PINS[i], OUTPUT);
  }

  for (byte i = 0; i < 8; i++) {
    digitalWrite(ANODE_PINS[i], HIGH);
    digitalWrite(CATHODE_PINS[i], HIGH);
  }

  Serial.begin(115200);
  Serial.setTimeout(100);

}

void display() {          // converts matrix to create patterns on the LED board

  for (byte i = 0; i<8; i++) {
    for (byte j = 0; j<8; j++) {
      if (grid[i][j] == 1){
        digitalWrite(CATHODE_PINS[j], LOW);
      }
      else{
        digitalWrite(CATHODE_PINS[j], HIGH);
      }
    }
    digitalWrite(ANODE_PINS[i], LOW);
    delayMicroseconds(150);
    digitalWrite(ANODE_PINS[i], HIGH);
  }

}

void read_python(){       // converts a 64-digit string input to a matrix
  String state_of_LED;
  if (Serial.available()){
    state_of_LED = Serial.readStringUntil('\r');

    if (state_of_LED != "STOP"){                          // if the input isn't a STOP code
      int cnt = 0;
      for (int row = 0; row<8; row++){
        for (int col = 0; col<8; col++){
          
          grid[row][col] = int(state_of_LED[cnt] - '0');  // matrix will consist of 0 and 1
          cnt++;
        }
      }
    }
    else{                                                // if the input is a STOP code
      state = END_SCREEN;                                // change state to end screen
    }
  }
}

void loop() {

  // button debouncing code

  byte reading = digitalRead(BUTTON);
  int button_pressed = 0;

  static byte button_state = HIGH;
  static byte last_reading = HIGH;
  static long last_reading_change = 0;

  unsigned long now = millis();

  // Ignore button_state changes within DEBOUNCE_DELAY milliseconds of the last
  // reading change, otherwise accept.

  if (now - last_reading_change > DEBOUNCE_DELAY) {
    if (reading == LOW && button_state == HIGH) { // button pressed down (HIGH to LOW)
      button_pressed = 1;
    }
    button_state = reading;
  }

  // Prepare for next loop
  if (reading != last_reading){
    last_reading_change = now;
  }
  last_reading = reading;



  // joystick reading code

  unsigned long X_pos = analogRead(X_pin);
  
  bool left = (X_pos < 50);
  bool right = (X_pos > 950);

  now = millis();

  if (state == START_SCREEN){                 // if state = start screen
    // make the start art here
    for(int row = 0; row<8; row++){
      if(row == 0 || row == 1){
        for(int col = 0; col<8; col++){
          grid[row][col] = 1;
        }
      }
      else{
        for(int col = 0; col<8; col++){
          if(col == 3 || col == 4){
            grid[row][col] = 1;
          }
        }
      }
      
    }

    display();                              // show in the LED board

    if(button_pressed == 1){                // if button is pressed
      Serial.print("START\n");              // output START to trigger python code
      for(int row = 0; row<8; row++){
        for(int col = 0; col<8; col++){
          grid[row][col] = 0;
        }
      }
      state = GAME;                        // change state to game
      score = 0;
    }
  }

  else if (state == END_SCREEN){          // if state = end screen
                                          // make everything blank
    for(int row = 0; row<8; row++){
      for(int col = 0; col<8; col++){
        grid[row][col] = 0;
      }
    }

    display();                           // show in the LED board

    if(button_pressed == 1){             // if button is pressed
      state = START_SCREEN;              // change state to start screen
    }
  }

  else{                                             // this is the GAME state

    if(button_pressed == 1){                        // if button is pressed
      Serial.print("button\n");                     // output button to python
    }

    if(now - last_command_sent > command_rate){     // if joystick read cooldown is over

      if(left == 1){                                // if joystick reads left, move piece left
        Serial.print("left\n");
      }

      else if(right == 1){                          // if joystick reads right, move piece right
        Serial.print("right\n");
      }

      last_command_sent = now;                      // update when joystick is read
      
    }
  }

  button_pressed = 0;                               // update button is not pressed



  read_python();                                  // read input from python

  display();                                      // show in the LED board

}
