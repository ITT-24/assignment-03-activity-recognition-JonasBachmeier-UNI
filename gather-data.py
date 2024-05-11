# this program gathers sensor data

import pyglet as pg
from pyglet import shapes, window, clock
import os
from DIPPID import SensorUDP
import random
import time
from math import sqrt
import pandas as pd

HEIGHT = 600
WIDTH = 800
BUTTON_MAP = {
    'button_1': 'rowing.csv',
    'button_2': 'lifting.csv',
    'button_3': 'running.csv',
    'button_4': 'jumpingjacks.csv'
}

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
instructionswindow = window.Window()
instructionswindow.set_size(WIDTH, HEIGHT)

gathering_started = False

@instructionswindow.event
def on_draw():
    global gathering_started
    time_start = time.time()
    if sensor.has_capability('button_1'):
        if not gathering_started:
            
            for button, csv_file in BUTTON_MAP.items():
                if sensor.get_value(button) == 1: 
                    pg.text.Label('Gathering data...', font_size=FONT_SIZE, x=WIDTH//2, y=HEIGHT//2, anchor_x='center', anchor_y='center').draw()              
                    gathering_started = True
                    data = start_gathering(time_start)
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
