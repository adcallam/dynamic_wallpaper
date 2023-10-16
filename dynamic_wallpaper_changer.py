'''
A Python program that sets a wallpaper using the Lively Wallpaper application.

The program is executed on PC startup using a script in the windows startup folder.

The program applies unique animated wallpapers (with audio) based on the current season or holiday.

The program can continually update the brightness of the wallpaper throughout
the day to match the estimated amount of daylight outside.
'''

import time
import subprocess
from datetime import datetime
import calendar
from suntime import Sun

DYNAMIC_BRIGHTNESS = False # Control to set whether the brightness should change with time of day
MASTER_VOL = 50  # The desired wallpaper volume level (from 0 to 100)
MAX_VOL = 100 # The maximum value that can be set for a wallpaper's volume using Lively
PROP_UPDATE_RATE = 900 # Property refresh rate for wallpaper in seconds (such as brightness)
WP_PATH_PREFIX = "C:\\Users\\andre\\OneDrive\\Pictures\\Wallpapers\\"
LIVELY_EXE_PATH = "C:\\Users\\andre\\AppData\\Local\\Programs\\Lively Wallpaper\\Lively.exe"

# Latitude and longitude of London, Ontario
LDN_ON_LAT = 42.9849
LDN_ON_LONG = -81.2453

MAX_BRIGHTNESS = 10
MIN_BRIGHTNESS = -20
BRIGHTNESS_RANGE = MAX_BRIGHTNESS-MIN_BRIGHTNESS

def set_wp(wp_path):
    '''Applies the wallpaper at "wp_path" using Lively.'''
    run_command(['setwp', f'--monitor={1}', f'--file={wp_path}'])

def reset_wp_properties():
    '''Applies default property values to whatever wallpaper is currently in use.'''

    change_property("saturation", value=0)
    change_property("brightness", value=0)
    change_property("hue", value=0)
    change_property("contrast", value=0)
    change_property("gamma", value=0)
    change_property("speed", value=1)

def set_wp_vol(master_vol, wp_file):
    '''Sets the volume level for the wallpaper that is in use.

    This is calculated using a combination of the desired master volume, 
    as well as each wallpaper's specific equalization volume, which is meant 
    to account for the differences between the volume levels of the different wallpapers. 
    '''

    # Equalize the volume based on the file, since they have different volume levels
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
        eq_vol = 100

    # Volume_level should be 0-100
    vol = round(eq_vol*(master_vol/MAX_VOL), 0)

    run_command(['volume', f'--volume={vol}'])

def change_property(name, value):
    '''Change the value of a property for the wallpaper that is currently in use.'''

    run_command(['setprop', f'--monitor={1}', f'--property={name}={value}'])

def run_command(args):
    '''Not sure what this does yet.'''

    startup_info = subprocess.STARTUPINFO()
    startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    subprocess.run(['Livelycu'] + args, startupinfo=startup_info, check = False)

def get_current_season():
    '''Determines the current season based on their meteorological definitions.

    The function will return the current season as a String based on what day of the year it is. 
    It will return "Christmas" on December 25th and "Halloween" on October 31st as there are special
    wallpapers prepared for those two specific days of the year.
    '''

    leapyear = False

    # Check if current year is leap year
    if calendar.isleap(datetime.today().year):
        leapyear = True

    # Get the current day of the year
    doy = datetime.today().timetuple().tm_yday  # Returns 1 to 366

    # Adjust for leapyear
    if doy >= 60 and leapyear:
        doy = doy-1

    # "Day of Year" ranges for the northern hemisphere
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

    season = 'winter'

    return season

def update_wp_brightness():
    '''Sets a wallpaper brightness value based on the amount of daylight outside.'''

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
        brightness = round((-1.0*(BRIGHTNESS_RANGE/((sunrise_time_minutes-((sunrise_time_minutes+sunset_time_minutes)/2))**2)))
                           * ((current_time_minutes-((sunset_time_minutes+sunrise_time_minutes)/2))**2)+MAX_BRIGHTNESS, 0)

    change_property("brightness", brightness)

def main():
    '''Executes the main program.'''

    subprocess.Popen([LIVELY_EXE_PATH])  # Opens the Lively Wallpaper program
    time.sleep(3) # Ensures Lively is fully opened before executing the rest of the program

    # Set wallpaper and volume based on season
    season = get_current_season()
    wp_file = "treehouse_" + season + ".mp4"
    wp_path = WP_PATH_PREFIX + wp_file
    set_wp(wp_path)
    reset_wp_properties()
    set_wp_vol(MASTER_VOL, wp_file)

    # Periodically update brightness of wallpaper based on daylight outside
    while DYNAMIC_BRIGHTNESS:
        update_wp_brightness()
        time.sleep(PROP_UPDATE_RATE)

if __name__ == '__main__':
    main()
