# threetris
Tetris game on a custom LED board. Powered with Arduino Nano which reads inputs from a joystick + push button.
(had to make the blocks three units long for ease of gameplay)

The Arduino and Python script runs at the same time and uses the Serial port to communicate. The Arduino sends out the state of the board which then the Python script runs logic on it. The Python script then outputs an updated board state which the Arduino will change the LED board to.

Features of this game include block collisions, move left/right, push down, 90 degrees clockwise rotation, line clears, and scorekeeping (internal data not displayed).