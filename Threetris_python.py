# Arif Ismail
# Threetris

import time
import random
import serial

# communicates with arduino in serial monitor
arduinoData = serial.Serial('com6', 115200)

grid = [[0,0,0,0,0,0,0,0],      # 10x8 grid, 10 = 8 + 2 extra 
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0]]      # take these values as an integer 


global frame_rate                   # how fast does the game tick

global current_piece_id             # number associated with the center of the current piece, only odd integers
                                    # a piece has one center, and two edges. these edges has a value of current piece id + 1

global send_new_piece               # if = 1, sends a new piece next tick
global piece_type                   # 0 = line piece, 1 = L piece
global line_piece_direction         # 0 = flat, 1 = vertical
global L_piece_direction            # 0 = L, 1 = r, 2 = backwards r, 3 = J
global output_to_arduino            # a 64 digit string of 1 and 0 to tell arduino what to display
global arduino_input                # string that arduino sends as an input of joystick/button
global game_over                    # checks if game over


def current_piece_movement():               # moves current piece
    global current_piece_id
    global send_new_piece
    global game_over

    # check if current piece is in the last row
    for col in range(0, 8):
        row = 9
        if grid[row][col] == current_piece_id: send_new_piece = 1

    # check every row except last one, move the piece down
    for row in range(8, -1, -1):
        for col in range(0, 8):
            if grid[row][col] == current_piece_id:       # check if it is a center of the new piece

                center_value = grid[row][col]
                down_value = grid[row+1][col]

                should_move_down = 1

                # check left, right, and down direction -> if there is an obstruction do not move

                if col != 0 :
                    left_value = grid[row][col-1]
                    if left_value == center_value+1 and grid[row+1][col-1] != 0 : should_move_down = 0

                if col != 7 :
                    right_value = grid[row][col+1]
                    if right_value == center_value+1 and grid[row+1][col+1] != 0 : should_move_down = 0


                if row == 8 :
                    if down_value == center_value+1 : should_move_down = 0
                    elif down_value != 0 and down_value != center_value+1 : should_move_down = 0     # checks value under center
                        
                else :
                    if down_value == center_value+1 and grid[row+2][col] != 0 : 
                        should_move_down = 0
                    elif down_value != 0 and down_value != center_value+1 : 
                        should_move_down = 0     # checks value under center



                # check complete, move down the whole piece
                if should_move_down == 1 :

                    # move the bottom edge down
                    if down_value == center_value+1 :
                        grid[row+2][col] = down_value
                        grid[row+1][col] = 0

                    # move the center down
                    grid[row+1][col] = center_value
                    grid[row][col] = 0

                    # move the top edge down
                    if grid[row-1][col] == center_value+1 :
                        grid[row][col] = center_value+1
                        grid[row-1][col] = 0

                    # move the left edge down
                    if col != 0 :
                        left_value = grid[row][col-1]
                        if left_value == center_value+1 :
                            grid[row+1][col-1] = left_value
                            grid[row][col-1] = 0

                    # move the right edge down
                    if col != 7 :
                        right_value = grid[row][col+1]
                        if right_value == center_value+1 :
                            grid[row+1][col+1] = right_value
                            grid[row][col+1] = 0


                # if piece is stuck at the top then game over
                elif row <= 2:
                    game_over = 1

                # else, time to send a new piece
                else:
                    send_new_piece = 1

def shift_everything_down():                # shifts everything down when there's a line clear
    print("clear!")

    for row in range(9, 1, -1):             # checks if there's a line to clear
        line_clear = 1
        for col in range(0, 8):             
            if grid[row][col] == 0:
                line_clear = 0
                break

        if line_clear == 1:                                 # if it is clear, then move every row above it down
            for row2 in range(row-1, 1, -1):
                for col in range(0,8):
                    grid[row2+1][col] = grid[row2][col]
                    grid[row2][col] = 0

            row -= 1     

def generate_new_piece():                   # generates new piece and places it on the grid
    global current_piece_id
    global send_new_piece
    global piece_type
    global line_piece_direction
    global L_piece_direction

    spawn_row = 1                      
    spawn_col = 4

    current_piece_id += 2                   # adds 2 to the last piece id 
    piece_type = random.randint(0,1)        # 0 = line piece, 1 = L piece


    # puts the new piece in place


    grid[spawn_row][spawn_col] = current_piece_id       # center value = current piece id
                                                        # edges has a value of current piece id + 1

    if piece_type == 0:
        line_piece_direction = random.randint(0,1) # 0 = vertical, 1 = flat

        if line_piece_direction == 0:
            grid[spawn_row+1][spawn_col] = current_piece_id+1
            grid[spawn_row-1][spawn_col] = current_piece_id+1

        else:
            grid[spawn_row][spawn_col+1] = current_piece_id+1
            grid[spawn_row][spawn_col-1] = current_piece_id+1
    
    else:
        L_piece_direction = random.randint(0,3) # 0 = L, 1 = r, 2 = backwards r, 3 = J

        if L_piece_direction == 0:
            grid[spawn_row-1][spawn_col] = current_piece_id+1
            grid[spawn_row][spawn_col+1] = current_piece_id+1

        elif L_piece_direction == 1:
            grid[spawn_row+1][spawn_col] = current_piece_id+1
            grid[spawn_row][spawn_col+1] = current_piece_id+1

        elif L_piece_direction == 2:
            grid[spawn_row+1][spawn_col] = current_piece_id+1
            grid[spawn_row][spawn_col-1] = current_piece_id+1
        
        else:
            grid[spawn_row-1][spawn_col] = current_piece_id+1
            grid[spawn_row][spawn_col-1] = current_piece_id+1
    

    send_new_piece = 0                      # updates the bool value 

def output():                               # modifies string output and sends it to arduino
    global output_to_arduino

    # if LED is on -> char = 1, else -> char = 0

    for row in range(2, 10):
        for col in range(0, 8):
            on = '1'
            if grid[row][col] == 0: on = '0'

            output_to_arduino += on
    
    print(output_to_arduino)
    output_to_arduino += '\r'
    arduinoData.write(output_to_arduino.encode())      # sends string through serial communication

def loop():                                 # loops every frame rate

        current_piece_movement()            # moves current piece

        if game_over == 1:                  # if game over, stop
            stop_message = "STOP"
            stop_message = '\r'
            arduinoData.write(stop_message.encode())

        
        else:                             
            line_clear = 1
            # check every row if there's a line clear
            for row in range(9, 0, -1): 
                line_clear = 1                  # assume it is clear
                for col in range(0, 8):
                    if grid[row][col] == 0:
                        line_clear = 0
                        break
                if line_clear == 1:
                    break
                    
            print("line clear:", line_clear)
            print("send new piece:", send_new_piece)
            if line_clear == 1 and send_new_piece == 1:         # if there is a line that should be cleared
                                                                # and the current piece has stopped moving
                shift_everything_down()
            
            # send new piece
            if send_new_piece == 1: generate_new_piece()

            # output to arduino
            output()

def rotate():                               # rotates current piece 90 degrees clockwise
    global current_piece_id
    global piece_type
    global line_piece_direction
    global L_piece_direction

    # check if center of new piece, ignore last row
    for row in range(8, 0, -1):
        for col in range(0, 8):
            if grid[row][col] == current_piece_id:       # check if it is a center of the new piece

                up_value = grid[row-1][col]
                center_value = grid[row][col]
                down_value = grid[row+1][col]

                should_rotate = 1

                # check left, right, up, and down direction -> if there is an obstruction do not move

                if col != 0 :
                    left_value = grid[row][col-1]
                    if left_value == center_value+1 and up_value != 0 and up_value != center_value+1: should_rotate = 0

                if col != 7 :
                    right_value = grid[row][col+1]
                    if right_value == center_value+1 and down_value != 0 and down_value != center_value+1: should_rotate = 0

                if up_value == center_value+1:
                    if col == 7: should_rotate = 0
                    else: 
                        if grid[row][col+1] != 0 and grid[row][col+1] != center_value+1: should_rotate = 0
                
                if down_value == center_value+1:
                    if col == 0: should_rotate = 0
                    else: 
                        if grid[row][col-1] != 0 and grid[row][col-1] != center_value+1: should_rotate = 0


                # check complete, rotate it
                if should_rotate == 1:
                    print("rotate is called")

                    if piece_type == 0:

                        if line_piece_direction == 0:   # I
                            grid[row][col+1] = current_piece_id+1
                            grid[row][col-1] = current_piece_id+1

                            grid[row-1][col] = 0
                            grid[row+1][col] = 0
                            line_piece_direction = 1
                        
                        else:                           # flat
                            grid[row-1][col] = current_piece_id+1
                            grid[row+1][col] = current_piece_id+1

                            grid[row][col+1] = 0
                            grid[row][col-1] = 0
                            line_piece_direction = 0
                    
                    else:

                        if L_piece_direction == 0:      # L
                            grid[row+1][col] = current_piece_id+1
                            grid[row-1][col] = 0
                            L_piece_direction = 1

                        elif L_piece_direction == 1:    # r
                            grid[row][col-1] = current_piece_id+1
                            grid[row][col+1] = 0
                            L_piece_direction = 2

                        elif L_piece_direction == 2:    # backwards r
                            grid[row-1][col] = current_piece_id+1
                            grid[row+1][col] = 0
                            L_piece_direction = 3
                        
                        else:                           # J
                            grid[row][col+1] = current_piece_id+1
                            grid[row][col-1] = 0
                            L_piece_direction = 0

    # output new grid to arduino
    output()
                        
def left():                                 # moves piece one pixel left
    global current_piece_id
    global piece_type
    global line_piece_direction
    global L_piece_direction

    for row in range(9, 0, -1):
        # skip first column
        for col in range(1, 8):
            if grid[row][col] == current_piece_id:       # check if it is a center of the new piece

                center_value = grid[row][col]

                if piece_type == 0:
                    
                    if line_piece_direction == 0: # I
                        if grid[row-1][col-1] == 0 and grid[row][col-1] == 0 and grid[row+1][col-1] == 0:

                            grid[row-1][col-1] = center_value+1
                            grid[row][col-1] = center_value
                            grid[row+1][col-1] = center_value+1

                            grid[row-1][col] = 0
                            grid[row][col] = 0
                            grid[row+1][col] = 0

                    elif line_piece_direction == 1 and col != 1: # flat
                        if grid[row][col-2] == 0:

                            grid[row][col-2] = center_value+1
                            grid[row][col-1] = center_value
                            grid[row][col] = center_value+1

                            grid[row][col+1] = 0
                
                else:

                    if L_piece_direction == 0: # L
                        if grid[row-1][col-1] == 0 and grid[row][col-1] == 0:

                            grid[row-1][col-1] = center_value+1
                            grid[row][col-1] = center_value
                            grid[row][col] = center_value+1

                            grid[row-1][col] = 0
                            grid[row][col+1] = 0
                    
                    elif L_piece_direction == 1: # r
                        if grid[row+1][col-1] == 0 and grid[row][col-1] == 0:

                            grid[row+1][col-1] = center_value+1
                            grid[row][col-1] = center_value
                            grid[row][col] = center_value+1

                            grid[row+1][col] = 0
                            grid[row][col+1] = 0
                    
                    elif L_piece_direction == 2 and col != 1: # backwards r
                        if grid[row][col-2] == 0 and grid[row+1][col-1] == 0:

                            grid[row][col-2] = center_value+1
                            grid[row][col-1] = center_value
                            grid[row+1][col-1] = center_value+1

                            grid[row][col] = 0
                            grid[row+1][col] = 0

                    elif L_piece_direction == 3 and col != 1: # J
                        if grid[row][col-2] == 0 and grid[row-1][col-1] == 0:

                            grid[row][col-2] = center_value+1
                            grid[row][col-1] = center_value
                            grid[row-1][col-1] = center_value+1

                            grid[row][col] = 0
                            grid[row-1][col] = 0

    # output new grid to arduino                     
    output()
                    
def right():                                # moves piece one pixel right
    global current_piece_id
    global piece_type
    global line_piece_direction
    global L_piece_direction

    for row in range(9, 0, -1):
        # skip last column
        for col in range(0, 7):
            if grid[row][col] == current_piece_id:       # check if it is a center of the new piece

                center_value = grid[row][col]

                if piece_type == 0:
                    
                    if line_piece_direction == 0: # I
                        if grid[row-1][col+1] == 0 and grid[row][col+1] == 0 and grid[row+1][col+1] == 0:

                            grid[row-1][col+1] = center_value+1
                            grid[row][col+1] = center_value
                            grid[row+1][col+1] = center_value+1

                            grid[row-1][col] = 0
                            grid[row][col] = 0
                            grid[row+1][col] = 0

                    elif line_piece_direction == 1 and col != 6: # flat
                        if grid[row][col+2] == 0:

                            grid[row][col+2] = center_value+1
                            grid[row][col+1] = center_value
                            grid[row][col] = center_value+1

                            grid[row][col-1] = 0
                
                else:

                    if L_piece_direction == 0 and col != 6: # L
                        if grid[row-1][col+1] == 0 and grid[row][col+2] == 0:

                            grid[row-1][col+1] = center_value+1
                            grid[row][col+1] = center_value
                            grid[row][col+2] = center_value+1

                            grid[row-1][col] = 0
                            grid[row][col] = 0
                    
                    elif L_piece_direction == 1 and col != 6: # r
                        if grid[row+1][col+1] == 0 and grid[row][col+2] == 0:

                            grid[row+1][col+1] = center_value+1
                            grid[row][col+1] = center_value
                            grid[row][col+2] = center_value+1

                            grid[row+1][col] = 0
                            grid[row][col] = 0
                    
                    elif L_piece_direction == 2: # backwards r
                        if grid[row][col+1] == 0 and grid[row+1][col+1] == 0:

                            grid[row][col] = center_value+1
                            grid[row][col+1] = center_value
                            grid[row+1][col+1] = center_value+1

                            grid[row][col-1] = 0
                            grid[row+1][col] = 0

                    elif L_piece_direction == 3 and col != 1: # J
                        if grid[row][col+1] == 0 and grid[row-1][col+1] == 0:

                            grid[row][col] = center_value+1
                            grid[row][col+1] = center_value
                            grid[row-1][col+1] = center_value+1

                            grid[row][col-1] = 0
                            grid[row-1][col] = 0

    # output new grid to arduino
    output()


while True:     # runs indefinitely, plays multiple games 

    while arduinoData.inWaiting() == 0: # while serial not available, do nothing
        pass

    # loops every frame rate
    frame_rate = 0.6
    current_piece_id = -1
    send_new_piece = 0
    piece_type = 0
    line_piece_direction = 0
    L_piece_direction = 0
    output_to_arduino = ""
    arduino_input = ""
    game_over = 0

    # set board to empty
    for row in range(9, -1, -1):
        for col in range(0, 8):
            grid[row][col] = 0

    # starts by creating a new piece, first piece id = 1
    generate_new_piece()
    current_piece_id = 1

    # starts timer
    start_time = time.monotonic()

    # for debugging
    cnt = 1                             

    while True:
        if time.monotonic() - start_time > frame_rate :         # if current time - start time > frame rate, then move piece down
            cnt += 1
            print(cnt)
            print(current_piece_id)

            loop()                                              

            start_time = time.monotonic()                       # resets start time

        if game_over == 1:                                      # if game over
            output_to_arduino = "STOP"                          
            output_to_arduino += '\r'
            arduinoData.write(output_to_arduino.encode())       # sends command to arduino to stop
            break

        if arduinoData.inWaiting() > 0 :
            arduino_input = arduinoData.readline()          # three types of string
            arduino_input = str(arduino_input, 'utf-8')     # button, left, right
            print(arduino_input)

            if arduino_input == "button\n": rotate()
        
            elif arduino_input == "left\n" : left()

            elif arduino_input == "right\n": right()


            