import datetime
import time
import uuid

import RPi.GPIO as GPIO
from fastapi import FastAPI, HTTPException
from libcamera import controls
from picamera2 import Picamera2

import yahtzee

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
relay_pin = 14
GPIO.setup(relay_pin, GPIO.OUT)
app = FastAPI()

picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": (1920, 1080)})
picam2.set_controls(
    {"AfMode": controls.AfModeEnum.Auto, "AfSpeed": controls.AfSpeedEnum.Fast, 'LensPosition': (0.0, 32.0, 1.0)}
)

dice_roll_images = []


@app.on_event('startup')
async def app_startup():
    picam2.start()
    print('Camera started up and focused')


@app.on_event('shutdown')
async def app_startup():
    picam2.stop()
    print('Camera was shut down')


@app.get("/throw_fast")
def throw_fast():
    if len(dice_roll_images) == 0:
        raise HTTPException(status_code=418, detail="Dice roll queue empty")

    start_time = datetime.datetime.now()
    dices = dice_roll_images[0]
    dice_roll_images.pop(0)
    end_time = datetime.datetime.now()
    return {"throw": dices, "elapsed_time": end_time - start_time}


@app.get("/throw")
def throw():
    try:
        start_time = datetime.datetime.now()
        roll_dice(2)
        dice_roll_image = take_dice_roll_picture()
        dices = interpret_dice_roll_image(dice_roll_image)
        end_time = datetime.datetime.now()
        return {"throw": dices, "elapsed_time": end_time - start_time}
    except ValueError as e:
        raise HTTPException(status_code=402, detail=str(e))


def take_dice_roll_picture():
    picam2.autofocus_cycle()
    dice_roll_image = str(uuid.uuid4()) + ".jpg"
    picam2.switch_mode_and_capture_file(config, dice_roll_image)
    return dice_roll_image


def roll_dice(roll_time):
    GPIO.output(relay_pin, GPIO.HIGH)
    time.sleep(roll_time)
    GPIO.output(relay_pin, GPIO.LOW)
    time.sleep(2)


def interpret_dice_roll_image(dice_roll_image):
    return yahtzee.process(dice_roll_image)


def thread_dice_roll_task():
    global dice_roll_images
    while True:
        if len(dice_roll_images) < 5:
            roll_dice(2)
            image_name = take_dice_roll_picture()
            dice_roll = interpret_dice_roll_image(image_name)
            dice_roll_images.append(dice_roll)
