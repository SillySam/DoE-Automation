from doe import DOE
import config

import datetime
import calendar
import schedule
from time import sleep
import os

def job(routine):
    day = calendar.day_name[datetime.date.today().weekday()].lower()
    try:
        if routine[day]:
            doe = DOE()
            if doe.login(config.EMAIL, config.PASSWORD):
                r = doe.add_activity(2076106, routine[day])
                log('Added Activity! Responce: ' + r)
    except KeyError:
        log('Skipping... No Activitys to fill in')

def log(message, just_print=False):
    now = datetime.datetime.now()
    now = now.strftime('%B %e, %I:%M %p')
    message = '[{}] {}'.format(now, message)

    print(message)

    if not just_print:
        log_path = os.path.join(os.path.dirname(__file__), 'log.txt')
        with open(log_path, 'a') as file:
            file.write(message + '\n')

if __name__ == "__main__":
    routine = {
        'monday': "Leg Day / Abs: Squat 60kg (8x4), Leg Press - 6 plates (12x4), Lunges with 30kg bag (4 sets), Calf Raisers (21x4), Machine Leg Curls (3x10-15) and Sit Ups/ Abs Coaster (12x3)", 
        'tuesday': "Chest/Biecep Day: Bench Press 60kg (8x4), Cable Flyes (12x4), Preacher Curls 30kg (12x4), Cable Bicep Curls (12x3) and DB Hammer Curls (3x12/12)", 
        'wednesday': "Back: Deadlifts - 100kg (8x4), 3x Landmine Row (12x) - super setted with - Straight Arm Pulldowns (12x), Bent Over Rows (DB 12x3), Lat Pulldowns (DS 12x3), Machine Tricep Pulldowns (12x3)", 
        'thursday': "Arm Day: Triceps Pulldown (12x3), Barbell Curl (6x3), Wrist Curl (24x4), DB Chest Press (10-12x4), Bicep Curls (12x4), Machine Preacher Curls (20x3), Incline DB Curl (12/12x4), Hammer Curls (as many until failer).", 
        'friday': "Shoulder/Trap Day: Sholder Press (8x4), 4 sets of Upright Rows (12x) super setted with Rear Delt Flies (15x), Seated DB Lateral Raises (15x3), Machine Overhead Press (DS) (12x3) and Cable Facepulls (15x3)"
    }

    schedule.every().day.at("01:00").do(job, routine)

    while True:
        try:
            log('Starting')
            schedule.run_pending()
            sleep(60)
            log("Still waiting >.< ")
        except Exception as error:
            log("Error: " + error)