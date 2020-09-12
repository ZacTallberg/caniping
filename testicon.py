from pystray import Icon as icon, Menu as menu, MenuItem as item

from PIL import Image, ImageDraw
from pythonping import ping
import time
import pydash
from pydash import py_
import sys
import ctypes
import os
import win32process

def quitApplication():
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)

def pingAustralia():
    test_ping = '139.130.4.5'

def pingLeagueOfLegends(): 
    test_ping = '104.160.131.3'

def pingGoogle():
    test_ping = '8.8.8.8'

active_ping = '8.8.8.8'
test_ping = None
min_ms = None
avg_ms = None
max_ms = None

image = Image.open('./green_icon.png')
menu_obj = item('quit', quitApplication)
icon_obj = icon('internet', icon=image, menu=menu(
    item(
        'Quit',
        quitApplication
    ),
    item(
        'Australia',
        pingAustralia
    ),
    item(
        'LoL',
        pingLeagueOfLegends
    ),
    item(
        'Google',
        pingGoogle
    )
))

def doIt():
    icon_obj.run(setup2)


trip_times = [
    min_ms,
    avg_ms,
    max_ms
]

def responseCalc():
    response_obj = ping(active_ping, count=10, timeout=1)
    return response_obj

def setup(icon_obj):
    icon_obj.visible = True
    try:
        response = responseCalc()
        if (response):
            time_values = str(response).partition('is ')[2].partition(' ms')[0].split('/')
            for count, value in enumerate(time_values):                
                if count == 0:
                    min_ms = value 
                    trip_times[0] = min_ms
                if count == 1:
                    avg_ms = value 
                    trip_times[1] = avg_ms
                if count == 2:
                    max_ms = value
                    trip_times[2] = max_ms
        else:
            for value in trip_times:
                value = 0
            

        if 'timed out' in str(response):
            image_red = Image.open('./red_icon.png')
            icon_obj.icon = image_red
            print('no internet')
        else:
            image_green = Image.open('./green_icon.png')
            icon_obj.icon = image_green
            print('average ms: ' + avg_ms)

        time.sleep(1)
        setup(icon_obj)
    
    except KeyboardInterrupt:
        quitApplication()

icon_obj.run(setup)


# def main():
#     try:
#         response = ping('8.8.8.8', count=1, timeout=1)

#         if 'timed out' in str(response):
#             image_red = Image.open('./red_icon.png')
#             icon_obj.icon = image_red
#             print('no internet')
#         else:
#             image_green = Image.open('./green_icon.png')
#             icon_obj.icon = image_green
#             print('yay internet')
#         time.sleep(1)
#         main()

#     except KeyboardInterrupt:
#         sys.exit(0)

# if __name__ == '__main__':
#     main()


