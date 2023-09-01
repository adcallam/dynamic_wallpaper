import time
import subprocess
from datetime import datetime
import calendar
from suntime import Sun

specific_wallpaper_volume = 100

first_iter=True
current_time=None
sunrise_time=None
sunset_time=None
current_time_minutes=None
sunrise_time_minutes=None
sunset_time_minutes=None
hours=0

ONE_HOUR_IN_SEC = 1 #number of seconds that equals one hour of elapsed real time
season = "summer"


def set_wallpaper(path, monitor):
    runCommand(['setwp', f'--monitor={monitor}', f'--file={path}'])
    return

def set_volume(volume_level):
    #volume_level should be 0-100
    runCommand(['volume', f'--volume={volume_level}'])
    return

def changeProperty(name, value, monitor):
    runCommand(['setprop', f'--monitor={monitor}', f'--property={name}={value}'])
    return

def runCommand(args):
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    subprocess.run(['Livelycu'] + args, startupinfo=si)
    return

def wallpaper_characteristics():
    global first_iter
    global current_time
    global sunrise_time
    global sunset_time
    global current_time_minutes
    global sunrise_time_minutes
    global sunset_time_minutes
    global hours

    MAX_BRIGHTNESS = 10
    MIN_BRIGHTNESS = -20
    BRIGHTNESS_RANGE = MAX_BRIGHTNESS-MIN_BRIGHTNESS

    MAX_HUE = 15
    MIN_HUE = -45
    HUE_RANGE = MAX_HUE-MIN_HUE

    # latitude and longitude of London, Ontario
    latitude = 42.9849
    longitude = -81.2453

    sun = Sun(latitude, longitude)

    if(first_iter):
        current_time = datetime.now()

        sunrise_time = sun.get_local_sunrise_time(current_time)
        sunset_time = sun.get_local_sunset_time(current_time)
        
        current_time = current_time.replace(second=0, microsecond=0)
        sunrise_time = sunrise_time.replace(second=0, microsecond=0, tzinfo=None)
        sunset_time = sunset_time.replace(second=0, microsecond=0, tzinfo=None)

        current_time_minutes = (current_time.hour*60)+current_time.minute
        sunrise_time_minutes = (sunrise_time.hour*60)+sunrise_time.minute
        sunset_time_minutes = (sunset_time.hour*60)+sunset_time.minute

        first_iter=False
    else:
        current_time_minutes = current_time_minutes + 15
        if current_time_minutes>(24*60):
            current_time_minutes=current_time_minutes-(24*60)

    hours=hours+0.25
    #reset once 24 hours has elapsed
    if(hours==96):
        first_iter=True

    if current_time_minutes < sunrise_time_minutes or current_time_minutes > sunset_time_minutes:
        brightness = MIN_BRIGHTNESS  # lowest brightness during darkness
        hue = MIN_HUE #lowest hue during darkness
    elif current_time_minutes > sunrise_time_minutes and current_time_minutes < sunset_time_minutes:
        brightness = round((-1.0*(BRIGHTNESS_RANGE/((sunrise_time_minutes-((sunrise_time_minutes+sunset_time_minutes)/2))**2)))*((current_time_minutes-((sunset_time_minutes+sunrise_time_minutes)/2))**2)+MAX_BRIGHTNESS, 0)
        hue = round((((MIN_HUE-MAX_HUE)/((sunset_time_minutes+60)-sunrise_time_minutes))*current_time_minutes)+(MAX_HUE+(((-MIN_HUE+MAX_HUE)/((sunset_time_minutes+60)-sunrise_time_minutes))*sunrise_time_minutes)), 0)

    return brightness, hue

# Select wallpaper based on season
def select_wallpaper(season):
    
    global specific_wallpaper_volume

    if season == "spring":
        specific_wallpaper_volume = 50
        return "treehouse-spring-morning-desktop-wallpaperwaifu.com.mp4"
    elif season == "summer":
        specific_wallpaper_volume = 70
        return "treehouse-summer-rain-desktop-wallpaperwaifu.com.mp4"
    elif season == "fall":
        specific_wallpaper_volume = 100
        return "treehouse_autumn.mp4"
    elif season == "winter":
        specific_wallpaper_volume = 90
        return "treehouse_winter_sound.mp4"
    elif season == "christmas":
        specific_wallpaper_volume = 100
        return "treehouse-winter-holidays-desktop-wallpaperwaifu.com.mp4"
    elif season == "halloween":
        specific_wallpaper_volume = 70
        return "treehouse_halloween.mp4"
    else:
        specific_wallpaper_volume = 40
        return "car-camping-in-the-rain-moewalls.com.mp4"

# Function to run the wallpaper changer continuously
def run_wallpaper_changer():

    lively_wallpaper_path = "C:\\Users\\andre\\OneDrive\\Pictures\\Wallpapers\\"

    # set wallpaper and volume based on season
    wallpaper_path = lively_wallpaper_path + select_wallpaper(season)
    set_wallpaper(wallpaper_path, 1)
    set_volume(specific_wallpaper_volume)

    # update wallpaper characteristics based on daylight outside
    loop = True
    while loop:
        try:          
            brightness, hue = wallpaper_characteristics()
            time.sleep(ONE_HOUR_IN_SEC/4)  # change wallpaper every 15 minutes to account for brightness changes
            changeProperty("brightness", brightness, monitor=1) # change brightness of wallpaper based on time of day relative to sunrise and sunset for current day
            changeProperty("hue", hue, monitor=1) # change brightness of wallpaper based on time of day relative to sunrise and sunset for current day
            print("hour {} (time: {}:{}), brightness: {}, hue: {}".format(hours, (current_time_minutes//60), (current_time_minutes%60), brightness, hue))
        except Exception as e:
            # handle any exceptions that may occur during the process
            print(f"Error: {e}")
            loop = False
            time.sleep(30) #should wait for key to be pressed instead or something

#subprocess.Popen(["C:\\Users\\andre\\AppData\\Local\\Programs\\Lively Wallpaper\\Lively.exe"])
#time.sleep(3) #ensures Lively is fully opened before executing the rest of the program

run_wallpaper_changer()