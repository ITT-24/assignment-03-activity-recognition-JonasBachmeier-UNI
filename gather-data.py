# this program gathers sensor data

import pyglet as pg
from pyglet import shapes, window, clock
import os
from DIPPID import SensorUDP
import random
import time
from math import sqrt
import pandas as pd
import glob

HEIGHT = 600
WIDTH = 800
BUTTONS = [
    'button_1',
    'button_2',
    'button_3',
    'button_4'
]

FONT_SIZE = 15
COLLECTION_TIME = 5

INSTRUCTIONS = [pg.text.Label(f'Press a button on phone to start gathering data for {COLLECTION_TIME} seconds', font_size=FONT_SIZE, x=WIDTH//2, y=HEIGHT//2, anchor_x='center', anchor_y='center'),
            pg.text.Label('gathered data will be saved as a .csv file with ~1000 entries', font_size=FONT_SIZE, x=WIDTH//2, y=HEIGHT//2-(FONT_SIZE + 5), anchor_x='center', anchor_y='center'),
            pg.text.Label('Button 1 for rowing', font_size=FONT_SIZE, x=WIDTH//2, y=HEIGHT//2-(FONT_SIZE + 5)*2, anchor_x='center', anchor_y='center'),
            pg.text.Label('Button 2 for lifting', font_size=FONT_SIZE, x=WIDTH//2, y=HEIGHT//2-(FONT_SIZE + 5)*3, anchor_x='center', anchor_y='center'),
            pg.text.Label('Button 3 for running', font_size=FONT_SIZE, x=WIDTH//2, y=HEIGHT//2-(FONT_SIZE + 5)*4, anchor_x='center', anchor_y='center'),
            pg.text.Label('Button 4 for jumpingjacks', font_size=FONT_SIZE, x=WIDTH//2, y=HEIGHT//2-(FONT_SIZE + 5)*5, anchor_x='center', anchor_y='center')]
PORT = 5700
sensor = SensorUDP(PORT)

def map_button(name, button):
    files = glob.glob('*.csv')
    # remove /r from name
    name = name.replace('\r', '')
    if button == 'button_1':
        rowingcount = sum((str(name) + '-rowing-')  in file for file in files)
        return str(name) + '-rowing-' + str(rowingcount+1) + '.csv'
    elif button == 'button_2':
        liftingcount = sum((str(name) + '-lifting-') in file for file in files)
        return str(name) + '-lifting-' + str(liftingcount+1) + '.csv'
    elif button == 'button_3':
        runningcount = sum((str(name) + '-running-') in file for file in files)
        return str(name) + '-running-' + str(runningcount+1) + '.csv'
    elif button == 'button_4':
        jumpingjackscount = sum((str(name) + '-jumpingjacks-') in file for file in files)
        return str(name) + '-jumpingjacks-' + str(jumpingjackscount+1) + '.csv'

def start_gathering(time_start):
    # create empty DF
    sensordata = pd.DataFrame(columns=['timestamp', 'acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z'])
    # gather data for 10 seconds
    while time.time() - time_start < COLLECTION_TIME:
        if sensor.has_capability('accelerometer') and sensor.has_capability('gyroscope'):
            acc_x = sensor.get_value('accelerometer')['x']
            acc_y = sensor.get_value('accelerometer')['y']
            acc_z = sensor.get_value('accelerometer')['z']
            gyro_x = sensor.get_value('gyroscope')['x']
            gyro_y = sensor.get_value('gyroscope')['y']
            gyro_z = sensor.get_value('gyroscope')['z']
            # Add data to dataframe
            sensordata.loc[len(sensordata)] = {'timestamp': time.time() - time_start, 'acc_x': acc_x, 'acc_y': acc_y, 'acc_z': acc_z, 'gyro_x': gyro_x, 'gyro_y': gyro_y, 'gyro_z': gyro_z}
            # sleep for 10 ms to avoid duplicates in data
            time.sleep(0.01)
    return sensordata

# show window for instructions

# Code for Class created by Github Copilot
class TextInputWindow(pg.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = pg.text.Label('', font_size=FONT_SIZE, x=WIDTH//2, y=HEIGHT//2-(FONT_SIZE + 10), anchor_x='center', anchor_y='center')

    def on_text(self, text):
        self.label.text += text

    def on_text_motion(self, motion):
        if motion == pg.window.key.MOTION_BACKSPACE:
            self.label.text = self.label.text[:-1]

instructionswindow = TextInputWindow()
#instructionswindow = window.Window()
instructionswindow.set_size(WIDTH, HEIGHT)

gathering_started = False
user_name_input = False

@instructionswindow.event
def on_key_press(symbol, modifiers):
    global user_name_input
    global gathering_started
    if symbol == pg.window.key.ENTER and instructionswindow.label.text != '':
        user_name_input = True

@instructionswindow.event
def on_draw():
    global gathering_started
    global user_name_input
    time_start = time.time()
    instructionswindow.clear()
    # first get users name by input
    if not user_name_input:
        print('user_name_input', user_name_input)
        pg.text.Label('Please enter your name like this: max_mustermann', font_size=FONT_SIZE, x=WIDTH//2, y=HEIGHT//2, anchor_x='center', anchor_y='center').draw()
        pg.text.Label('Press enter to continue', font_size=FONT_SIZE, x=WIDTH//2, y=HEIGHT//2-(FONT_SIZE + 5)*6, anchor_x='center', anchor_y='center').draw()
        instructionswindow.label.draw()
    # only after user has entered name, show instructions and enable gathering
    elif sensor.has_capability('button_1'):
        if not gathering_started:
            
            for button in BUTTONS:
                if sensor.get_value(button) == 1: 
                    pg.text.Label('Gathering data...', font_size=FONT_SIZE, x=WIDTH//2, y=HEIGHT//2, anchor_x='center', anchor_y='center').draw()              
                    gathering_started = True
                    data = start_gathering(time_start)
                    csv_file = map_button(instructionswindow.label.text, button)
                    data.to_csv(csv_file)
                    gathering_started = False
                else:
                    # for instruction in INSTRUCTIONS:
                    #     instruction.draw()
                    pg.text.Label(f'Press a button on phone to start gathering data for {COLLECTION_TIME} seconds', font_size=FONT_SIZE, x=WIDTH//2, y=HEIGHT//2, anchor_x='center', anchor_y='center').draw()
                    pg.text.Label('gathered data will be saved as a .csv file with ~1000 entries', font_size=FONT_SIZE, x=WIDTH//2, y=HEIGHT//2-(FONT_SIZE + 5), anchor_x='center', anchor_y='center').draw()
                    pg.text.Label('Button 1 for rowing', font_size=FONT_SIZE, x=WIDTH//2, y=HEIGHT//2-(FONT_SIZE + 5)*2, anchor_x='center', anchor_y='center').draw()
                    pg.text.Label('Button 2 for lifting', font_size=FONT_SIZE, x=WIDTH//2, y=HEIGHT//2-(FONT_SIZE + 5)*3, anchor_x='center', anchor_y='center').draw()
                    pg.text.Label('Button 3 for running', font_size=FONT_SIZE, x=WIDTH//2, y=HEIGHT//2-(FONT_SIZE + 5)*4, anchor_x='center', anchor_y='center').draw()
                    pg.text.Label('Button 4 for jumpingjacks', font_size=FONT_SIZE, x=WIDTH//2, y=HEIGHT//2-(FONT_SIZE + 5)*5, anchor_x='center', anchor_y='center').draw()

pg.app.run()
