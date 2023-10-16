import time
import subprocess
from datetime import datetime
import calendar
from suntime import Sun

change_based_on_time = False

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

def brightness_level():
    MAX_BRIGHTNESS = 10
    MIN_BRIGHTNESS = -20
    BRIGHTNESS_RANGE = MAX_BRIGHTNESS-MIN_BRIGHTNESS

    # latitude and longitude of London, Ontario
    latitude = 42.9849
    longitude = -81.2453

    sun = Sun(latitude, longitude)

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

# Select wallpaper based on season
def select_wallpaper(season):
    
    if season == "spring":
        wallpaper_file = "treehouse_spring.mp4"
        wallpaper_volume = 50
    elif season == "summer":
        wallpaper_file = "treehouse_summer.mp4"
        wallpaper_volume = 70
    elif season == "fall":
        wallpaper_file = "treehouse_fall.mp4"
        wallpaper_volume = 100
    elif season == "winter":
        wallpaper_file = "treehouse_winter.mp4"
        wallpaper_volume = 90
    elif season == "christmas":
        wallpaper_file = "treehouse_christmas.mp4"
        wallpaper_volume = 100
    elif season == "halloween":
        wallpaper_file = "treehouse_halloween.mp4"
        wallpaper_volume = 70
    else:
        wallpaper_file = "car-camping-in-the-rain-moewalls.com.mp4"
        wallpaper_volume = 40
    
    return wallpaper_file, wallpaper_volume

# Function to run the wallpaper changer continuously
def run_wallpaper_changer():

    global change_based_on_time
    lively_wallpaper_path_prefix = "C:\\Users\\andre\\OneDrive\\Pictures\\Wallpapers\\"

    # set wallpaper and volume based on season
    season = get_current_season()
    wallpaper_file_name, wallpaper_volume = select_wallpaper(season)
    wallpaper_path = lively_wallpaper_path_prefix + wallpaper_file_name
    set_wallpaper(wallpaper_path, 1)
    set_volume(wallpaper_volume)

    # update brightness of wallpaper based on daylight outside
    while change_based_on_time:
        try:          
            changeProperty("brightness", brightness_level(), 1) # change brightness of wallpaper based on time of day relative to sunrise and sunset for current day
            time.sleep(900)  # change wallpaper every 15 minutes to account for brightness changes
        except Exception as e:
            # handle any exceptions that may occur during the process
            print(f"Error: {e}")
            change_based_on_time = False
            time.sleep(30) #should wait for key to be pressed instead or something
    
    if not change_based_on_time:
        #set all parameters to default values
        try:          
            changeProperty("saturation", 0, 1)
            changeProperty("brightness", 0, 1) 
            changeProperty("hue", 0, 1)
            changeProperty("contrast", 0, 1)
            changeProperty("gamma", 0, 1)
            changeProperty("speed", 1, 1)
            exit()
        except Exception as e:
            # handle any exceptions that may occur during the process
            print(f"Error: {e}")
            change_based_on_time = False
            time.sleep(30) #should wait for key to be pressed instead or something

subprocess.Popen(["C:\\Users\\andre\\AppData\\Local\\Programs\\Lively Wallpaper\\Lively.exe"])
time.sleep(3) #ensures Lively is fully opened before executing the rest of the program

run_wallpaper_changer()