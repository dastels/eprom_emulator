"""
EPROM emulator UI in CircuitPython.
Targeted for the SAMD51 boards.

by Dave Astels
"""

import time
import digitalio
import board
import busio
import adafruit_ssd1306
import os
import storage
import adafruit_sdcard
from directory_node import DirectoryNode
from emulator import Emulator


#--------------------------------------------------------------------------------
# Initialize Rotary encoder

# Encoder button is a digital input with pullup on D2
button = digitalio.DigitalInOut(board.D2)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP
 
# Rotary encoder inputs with pullup on D3 & D4
rot_a = digitalio.DigitalInOut(board.D4)
rot_a.direction = digitalio.Direction.INPUT
rot_a.pull = digitalio.Pull.UP

rot_b = digitalio.DigitalInOut(board.D3)
rot_b.direction = digitalio.Direction.INPUT
rot_b.pull = digitalio.Pull.UP

#--------------------------------------------------------------------------------
# Initialize I2C and OLED

i2c = busio.I2C(board.SCL, board.SDA)

oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
oled.fill(0)
oled.text("Initializing SD", 0, 10)
oled.show()

#--------------------------------------------------------------------------------
# Initialize SPI and SD card

#SD_CS = board.D10
# Connect to the card and mount the filesystem.
spi = busio.SPI(board.D13, board.D11, board.D12)   # SCK, MOSI, MISO
cs = digitalio.DigitalInOut(board.D10)
sdcard = adafruit_sdcard.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

oled.fill(0)
oled.text("Done", 0, 10)
oled.show()


#--------------------------------------------------------------------------------
# Initialize globals

encoder_counter = 0
encoder_direction = 0
 
# constants to help us track what edge is what
A_POSITION = 0
B_POSITION = 1
UNKNOWN_POSITION = -1  # initial state so we know if something went wrong
 
rising_edge = falling_edge = UNKNOWN_POSITION

PROGRAM_MODE = 0
ICE_MODE = 1

current_mode = PROGRAM_MODE

emulator = Emulator(i2c)


#--------------------------------------------------------------------------------
# Helper functions

def is_binary_name(filename):
    return filename[-4:] == ".bin"


def load_file(filename):
    data = []
    with open(filename, "rb") as f:
        data = f.read()
    return data


def enter_run_mode():
    global current_mode
    data = load_file(current_dir.selected_filepath())
    emulator.load_ram(data)
    emulator.enter_ice_mode()
    oled.fill(0)
    oled.text("Emulating", 0, 0)
    oled.text(current_dir.selected_filename(), 0, 10)
    oled.show()
    current_mode = ICE_MODE


def enter_programming_mode():
    global current_mode
    emulator.enter_programmer_mode()
    current_mode = PROGRAM_MODE
    current_dir.update()


#--------------------------------------------------------------------------------
# Main loop
# get initial/prev state and store at beginning

last_button = button.value
rotary_prev_state = [rot_a.value, rot_b.value]

current_dir = DirectoryNode(oled, named = "/sd")
current_dir.update()

while True:
    # reset encoder and wait for the next turn
    encoder_direction = 0

    if current_mode == PROGRAM_MODE:      #Ignore rotation if in ICE mode
    # See https://learn.adafruit.com/media-dial/code
    # take a 'snapshot' of the rotary encoder state at this time
        rotary_curr_state = [rot_a.value, rot_b.value]
 
        if rotary_curr_state != rotary_prev_state:
            if rotary_prev_state == [True, True]:
                # we caught the first falling edge!
                if not rotary_curr_state[A_POSITION]:
                    falling_edge = A_POSITION
                elif not rotary_curr_state[B_POSITION]:
                    falling_edge = B_POSITION
                else:
                    # uhh something went deeply wrong, lets start over
                    continue
 
            if rotary_curr_state == [True, True]:
                # Ok we hit the final rising edge
                if not rotary_prev_state[B_POSITION]:
                    rising_edge = B_POSITION
                elif not rotary_prev_state[A_POSITION]:
                    rising_edge = A_POSITION
                else:
                    # uhh something went deeply wrong, lets start over
                    continue
 
                # check first and last edge
                if (rising_edge == A_POSITION) and (falling_edge == B_POSITION):
                    encoder_counter -= 1
                    encoder_direction = -1
                elif (rising_edge == B_POSITION) and (falling_edge == A_POSITION):
                    encoder_counter += 1
                    encoder_direction = 1
                else:
                    # (shrug) something didn't work out, oh well!
                    encoder_direction = 0
 
                # reset our edge tracking
                rising_edge = falling_edge = UNKNOWN_POSITION
 
        rotary_prev_state = rotary_curr_state
 
    # Handle encoder rotation
    if encoder_direction == -1:
        current_dir.up()
    elif encoder_direction == 1:
        current_dir.down()

    # look for the initial edge of the rotary encoder switch press, with debouncing
    first = button.value
    time.sleep(0.01)
    second = button.value
    if first and not second:
        while not button.value:
            time.sleep(0.01)
        if current_mode == ICE_MODE:
            enter_programming_mode()
        elif is_binary_name(current_dir.selected_filename()):
            enter_run_mode()
        else:
            current_dir = current_dir.click()
        
    last_button = button.value
 
