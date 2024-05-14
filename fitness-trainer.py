# this program visualizes activities with pyglet

import activity_recognizer as activity

import pyglet as pg
from pyglet import shapes, window, clock
import os
import random
import time
from math import sqrt
import pandas as pd

# Trainer setup
WINDOW_HEIGHT = 800
WINDOW_WIDTH = 800

startup_time = time.time()

trainer_window = window.Window(WINDOW_HEIGHT, WINDOW_WIDTH)

background = pg.shapes.Rectangle(x=0,y=0,width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
# jumpjack1 = pg.sprite.Sprite(pg.resource.image('img/jumpingjack_1.png'))
# jumpjack2 = pg.sprite.Sprite(pg.resource.image('img/jumpingjack_2.png'))
# lifting1 = pg.sprite.Sprite(pg.resource.image('img/lifting_1.png'))
# lifting2 = pg.sprite.Sprite(pg.resource.image('img/lifting_2.png'))
# rowing1 = pg.sprite.Sprite(pg.resource.image('img/rowing_1.png'))
# rowing2 = pg.sprite.Sprite(pg.resource.image('img/rowing_2.png'))
# running1 = pg.sprite.Sprite(pg.resource.image('img/running_1.png'))
# running2 = pg.sprite.Sprite(pg.resource.image('img/running_2.png'))
# ACTIVITES =["jumpingjacks", "lifting", "rowing", "running"]
ACTIVITIES = {
    "jumpingjacks": [pg.sprite.Sprite(pg.resource.image('img/jumpingjack_1.png')), pg.sprite.Sprite(pg.resource.image('img/jumpingjack_2.png'))],
    "lifting": [pg.sprite.Sprite(pg.resource.image('img/lifting_1.png')), pg.sprite.Sprite(pg.resource.image('img/lifting_2.png'))],
    "rowing": [pg.sprite.Sprite(pg.resource.image('img/rowing_1.png')), pg.sprite.Sprite(pg.resource.image('img/rowing_2.png'))],
    "running": [pg.sprite.Sprite(pg.resource.image('img/running_1.png')), pg.sprite.Sprite(pg.resource.image('img/running_2.png'))]
}

class Activity:
    activities = []
    activity_started = False
    cooldown = time.time()

    def __init__(self, type, image, length):
        self.type = type
        self.image = image
        self.length = length
    
    def start_activity(self):
        print("Trying to start activity")
        start_time = time.time()
        # gets random activity
        new_activity = random.choice(Activity.activities)
        print(new_activity.type)
        print(new_activity.length)
        if not Activity.activity_started and time.time() - Activity.cooldown > 10 :
            # TODO: change prediction call method. At the moment this code stops the process until the proediction is complete, and therefore stops the game/trainer UI etc.
            print("Activity started")
            Activity.activity_started = True
            Activity.cooldown = time.time()
            curr_act = activity.predict_activity(new_activity.length)
            print("Activity predicted")
            print(curr_act)
            Activity.activity_started = False
        else:
            print("starting failed")
            print("cooldown left:" + str(time.time() - Activity.cooldown))


        
for type, sprites in ACTIVITIES.items():
            Activity.activities.append(Activity(type = type, image = sprites[0] , length=4))

@trainer_window.event
def on_draw():
    trainer_window.clear()
    background.draw()


# Change time to correct training length later
clock.schedule_interval(Activity.start_activity, 10)
pg.app.run()