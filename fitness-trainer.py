# this program visualizes activities with pyglet

import activity_recognizer as activity

import pyglet as pg
from pyglet import shapes, window, clock
import os
import random
import time
from math import sqrt
import pandas as pd
import glob

from DIPPID import SensorUDP

PORT = 5700
sensor = SensorUDP(PORT)

WINDOW_HEIGHT = 800
WINDOW_WIDTH = 800

trainer_window = window.Window(WINDOW_HEIGHT, WINDOW_WIDTH)

background = pg.shapes.Rectangle(x=0,y=0,width=WINDOW_WIDTH, height=WINDOW_HEIGHT)

def create_sprite(image_path, scale):
    image = pg.resource.image(image_path)
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2
    sprite = pg.sprite.Sprite(image, x=WINDOW_WIDTH//2, y=WINDOW_HEIGHT//2)
    sprite.scale = scale
    return sprite

jumpjack1 = create_sprite('img/jumpingjack_1.png', 0.5)
jumpjack2 = create_sprite('img/jumpingjack_2.png', 0.5)
lifting1 = create_sprite('img/lifting_1.png', 0.5)
lifting2 = create_sprite('img/lifting_2.png', 0.5)
rowing1 = create_sprite('img/rowing_1.png', 0.4)
rowing2 = create_sprite('img/rowing_2.png', 0.4)
running1 = create_sprite('img/running_1.png', 0.5)
running2 = create_sprite('img/running_2.png', 0.5)


# Dictionary for activities for simple addition of new activities
ACTIVITIES = {
    "Jumping Jacks": {
        "sprites": [
            jumpjack1,jumpjack2
        ],
        "length": 10
    },
    "Lifting": {
        "sprites": [
            lifting1,lifting2
        ],
        "length": 10
    },
    "Rowing": {
        "sprites": [
            rowing1,rowing2
        ],
        "length": 10
    },
    "Running": {
        "sprites": [
            running1,running2
        ],
        "length": 10
    }
}

# Cooldown time between activities (1 second extra so last second shown isnt 0)
COOLDOWN = 11

# Map prediction number to activity name
def activity_mapping(num):
    if num != None:
        num = int(num)
    if num == 0:
        return "Rowing"
    elif num == 1:
        return "Lifting"
    elif num == 2:
        return "Running"
    elif num == 3:
        return "Jumping Jacks"
    else:
        return "Unknown"

class Activity:
    activity_started = False
    cooldown = time.time()
    current_activity = None
    predictions = []
    activity_selected = False

    def __init__(self, type, image, length):
        self.type = type
        self.image = image
        self.length = length
        self.start_time = time.time()
    
    # Selects a random activity
    def select_activity():
        Activity.current_activity = random.choice(list(ACTIVITIES.keys()))
        Activity.activity_selected = True


    def start_activity():
        if not Activity.activity_started:
            Activity.predictions = []
            Activity.start_time = time.time()
            Activity.activity_started = True


    def capture_activity():
        # If activity is started and not over, get sensor data
        if Activity.activity_started and time.time() - Activity.start_time < ACTIVITIES[Activity.current_activity]['length']:
            # get sensor data
            if sensor.has_capability('accelerometer') and sensor.has_capability('gyroscope'):
                acc_x = sensor.get_value('accelerometer')['x']
                acc_y = sensor.get_value('accelerometer')['y']
                acc_z = sensor.get_value('accelerometer')['z']
                gyro_x = sensor.get_value('gyroscope')['x']
                gyro_y = sensor.get_value('gyroscope')['y']
                gyro_z = sensor.get_value('gyroscope')['z']

                predicted_activity = activity.predict_activity(acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z)
                Activity.predictions.append(predicted_activity)
                most_common = max(set(Activity.predictions), key = Activity.predictions.count)
                if len(Activity.predictions) > 20:
                    return most_common
        
        # if activity is over, stop activity and set cooldown
        elif Activity.activity_started:
            Activity.activity_selected = False
            Activity.activity_started = False
            Activity.cooldown = time.time()
        else:
            return "no activity started"

@trainer_window.event
def on_draw():
    trainer_window.clear()
    background.draw()
    if Activity.activity_started:
        captured_activity = Activity.capture_activity()
        captured_activity = activity_mapping(captured_activity)

        # depending on captured activity, show a text telling the user if he did the activity correctly
        if captured_activity == Activity.current_activity:
            pg.text.Label(f"Great! You're doing it right!", color=(0,0,0,255), x=WINDOW_WIDTH//2, y=50, anchor_x='center', anchor_y='center').draw()
        else:
            pg.text.Label(f"You're doing the activity wrong!", color=(0,0,0,255), x=WINDOW_WIDTH//2, y=50, anchor_x='center', anchor_y='center').draw()
        pg.text.Label(f"Current Activity being recognized: {captured_activity}", color=(0,0,0,255), x=WINDOW_WIDTH//2, y=100, anchor_x='center', anchor_y='center').draw()

        # Use the mod to alternate between the two sprites every second
        sprite_index = int(time.time() % 2)
        time_left = int(ACTIVITIES[Activity.current_activity]['length'] - (time.time() - Activity.start_time))

        pg.text.Label(f"Current Activity: {Activity.current_activity}", color=(0,0,0,255), x=WINDOW_WIDTH//2, y=WINDOW_HEIGHT-50, anchor_x='center', anchor_y='center').draw()
        pg.text.Label(f"Time left: {time_left}", color=(0,0,0,255), x=WINDOW_WIDTH//2, y=WINDOW_HEIGHT-100, anchor_x='center', anchor_y='center').draw()
        ACTIVITIES[Activity.current_activity]["sprites"][sprite_index].draw()
        
    # If activity is not started, show a text telling the user to wait for the next activity
    else:
        Activity.predictions = []
        if not Activity.activity_selected:
            Activity.select_activity()
        time_left = int(COOLDOWN - (time.time() - Activity.cooldown))
        pg.text.Label(f"{Activity.current_activity} coming in: {time_left} seconds", color=(0,0,0,255), x=WINDOW_WIDTH//2, y=WINDOW_HEIGHT//2, anchor_x='center', anchor_y='center').draw()
    
    # If cooldown is over, start the next activity
    if time.time() - Activity.cooldown > COOLDOWN:
        Activity.start_activity()

# Train model
activity.train_model()
pg.app.run()