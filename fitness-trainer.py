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

# Call "start_activity" method every 5 seconds -> changes the boolean value of "activity_started" to True and the current activity enum
# Every frame check if "activity_started" is True -> if True, draw the activity image and send the current sensor data to the activity recognizer.
# The recognizer returns the predicted activity. If the predicted activity is the same as the current activity, the activity is successfully executed by the user and UI represents this.
# only after the full activity is done, "activity_started" is set to False again and the next activity can be started.
# This can be measured by anactivity lenght set for each activity. If the time since starting the activity is greater than the activity length, the activity is done and the "activity_started" is set to False again.
# Here a final prediction summary can be shown to the user to tell him how well he did.


# Trainer setup
WINDOW_HEIGHT = 800
WINDOW_WIDTH = 800

startup_time = time.time()

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

# ACTIVITES =["jumpingjacks", "lifting", "rowing", "running"]
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
COOLDOWN = 11

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
    
    def select_activity():
        Activity.current_activity = random.choice(list(ACTIVITIES.keys()))
        Activity.activity_selected = True


    def start_activity():
        # gets random activity
        if not Activity.activity_started:
            Activity.predictions = []
            Activity.start_time = time.time()
            Activity.activity_started = True

    def capture_activity():
        # If activity is started, get sensor data
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
                print(most_common)
                if len(Activity.predictions) > 20:
                    if most_common == 0:
                        return "Rowing"
                    elif most_common == 1:
                        return "Lifting"
                    elif most_common == 2:
                        return "Running"
                    elif most_common == 3:
                        return "Jumping Jacks"
                    else:
                        return "prediction failed"
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
        #print(captured_activity)
        # depending on captured activity, show a text telling the user if he did the activity correctly
        if captured_activity == Activity.current_activity:
            pg.text.Label("Activity done correctly!", color=(0,0,0,255), x=WINDOW_WIDTH//2, y=50, anchor_x='center', anchor_y='center').draw()
        else:
            pg.text.Label("Activity done wrong!", color=(0,0,0,255), x=WINDOW_WIDTH//2, y=50, anchor_x='center', anchor_y='center').draw()

        # Use the modulus operator to alternate between the two sprites every 2 seconds
        sprite_index = int(time.time() % 2)
        time_left = int(ACTIVITIES[Activity.current_activity]['length'] - (time.time() - Activity.start_time))

        pg.text.Label(f"Current Activity: {Activity.current_activity}", color=(0,0,0,255), x=WINDOW_WIDTH//2, y=WINDOW_HEIGHT-50, anchor_x='center', anchor_y='center').draw()
        pg.text.Label(f"Time left: {time_left}", color=(0,0,0,255), x=WINDOW_WIDTH//2, y=WINDOW_HEIGHT-100, anchor_x='center', anchor_y='center').draw()
        ACTIVITIES[Activity.current_activity]["sprites"][sprite_index].draw()
        
    else:
        Activity.predictions = []
        if not Activity.activity_selected:
            Activity.select_activity()
        time_left = int(COOLDOWN - (time.time() - Activity.cooldown))
        pg.text.Label(f"{Activity.current_activity} coming in: {time_left} seconds", color=(0,0,0,255), x=WINDOW_WIDTH//2, y=WINDOW_HEIGHT//2, anchor_x='center', anchor_y='center').draw()
    
    if time.time() - Activity.cooldown > COOLDOWN:
        Activity.start_activity()

# Train model
activity.train_model()
pg.app.run()