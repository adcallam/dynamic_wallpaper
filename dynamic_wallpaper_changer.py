import time
import subprocess
from datetime import datetime
import calendar
from suntime import Sun
import sys

DYNAMIC_BRIGHTNESS = False
MASTER_VOL = 0 #From 0 to 100
PROP_UPDATE_RATE = 900 # Property refresh rate for wallpaper in seconds (such as brightness)
WP_PATH_PREFIX = "C:\\Users\\andre\\OneDrive\\Pictures\\Wallpapers\\"
LIVELY_EXE_PATH = "C:\\Users\\andre\\AppData\\Local\\Programs\\Lively Wallpaper\\Lively.exe"

# latitude and longitude of London, Ontario
LDN_ON_LAT = 42.9849
LDN_ON_LONG = -81.2453

def set_wp(wp_path):
    run_command(['setwp', f'--monitor={1}', f'--file={wp_path}'])
    return

def set_default_wp_properties():
    #set all parameters to default values
    change_property("saturation", 0, 1)
    change_property("brightness", 0, 1) 
    change_property("hue", 0, 1)
    change_property("contrast", 0, 1)
    change_property("gamma", 0, 1)
    change_property("speed", 1, 1)

def set_wp_vol(master_vol, wp_file):
    MAX_VOL = 100
    
    if wp_file == "treehouse_spring.mp4":
        eq_vol = 50
    elif wp_file == "treehouse_summer.mp4":
        eq_vol = 70
    elif wp_file == "treehouse_fall.mp4":
        eq_vol = 100
    elif wp_file == "treehouse_winter.mp4":
        eq_vol = 90
    elif wp_file == "treehouse_christmas.mp4":
        eq_vol = 100
    elif wp_file == "treehouse_halloween.mp4":
        eq_vol = 70

    vol = round(eq_vol*(master_vol/MAX_VOL), 0)

    #volume_level should be 0-100
    run_command(['volume', f'--volume={vol}'])
    return

def change_property(name, value):
    run_command(['setprop', f'--monitor={1}', f'--property={name}={value}'])
    return

def run_command(args):
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    subprocess.run(['Livelycu'] + args, startupinfo=si)
    return

# Function to get the current weather
def get_current_season():
    leapyear=False

    # check if current year is leap year
    if (calendar.isleap(datetime.today().year)):
        leapyear = True

    # get the current day of the year
    doy = datetime.today().timetuple().tm_yday #returns 1 to 366


    # adjust for leapyear
    if doy>=60 and leapyear:
        doy=doy-1

    # "day of year" ranges for the northern hemisphere
    spring = range(60, 152)
    summer = range(152, 244)
    fall = range(244, 335)

    if doy in spring:
        season = 'spring'
    elif doy in summer:
        season = 'summer'
    elif doy in fall:
        season = 'fall'
        if doy == 304:
            season = 'halloween'
    else:
        season = 'winter'
        if doy == 359:
            season = 'christmas'

    return season

def calc_new_brightness():
    MAX_BRIGHTNESS = 10
    MIN_BRIGHTNESS = -20
    BRIGHTNESS_RANGE = MAX_BRIGHTNESS-MIN_BRIGHTNESS

    sun = Sun(LDN_ON_LAT, LDN_ON_LONG)

    current_time = datetime.now()

    sunrise_time = sun.get_local_sunrise_time(current_time)
    sunset_time = sun.get_local_sunset_time(current_time)
    
    current_time = current_time.replace(second=0, microsecond=0)
    sunrise_time = sunrise_time.replace(second=0, microsecond=0, tzinfo=None)
    sunset_time = sunset_time.replace(second=0, microsecond=0, tzinfo=None)

    current_time_minutes = (current_time.hour*60)+current_time.minute
    sunrise_time_minutes = (sunrise_time.hour*60)+sunrise_time.minute
    sunset_time_minutes = (sunset_time.hour*60)+sunset_time.minute

    if current_time_minutes < sunrise_time_minutes or current_time_minutes > sunset_time_minutes:
        brightness = MIN_BRIGHTNESS  # lowest brightness during darkness
    elif current_time_minutes > sunrise_time_minutes and current_time_minutes < sunset_time_minutes:
        brightness = round((-1.0*(BRIGHTNESS_RANGE/((sunrise_time_minutes-((sunrise_time_minutes+sunset_time_minutes)/2))**2)))*((current_time_minutes-((sunset_time_minutes+sunrise_time_minutes)/2))**2)+MAX_BRIGHTNESS, 0)

    return brightness

subprocess.Popen([LIVELY_EXE_PATH])
time.sleep(3) #ensures Lively is fully opened before executing the rest of the program

# set wallpaper and volume based on season
season = get_current_season()
wp_file = "treehouse_" + season + ".mp4"
wp_path = WP_PATH_PREFIX + wp_file
set_wp(wp_path)
set_default_wp_properties()
set_wp_vol(MASTER_VOL, wp_file)

# update brightness of wallpaper based on daylight outside
while DYNAMIC_BRIGHTNESS:
    change_property("brightness", calc_new_brightness()) # change brightness of wallpaper based on time of day relative to sunrise and sunset for current day
    time.sleep(PROP_UPDATE_RATE)  # change wallpaper every 15 minutes to account for brightness changes

sys.exit()