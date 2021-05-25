from infi.systray import SysTrayIcon
import aioping
import logging
import time
import pydash
import asyncio
import datetime
from pydash import py_
import sys
import ctypes
import os
import win32process
import math


active_ping = '8.8.8.8'
test_ping = '0.0.0.0'
min_ms = '0'
avg_ms = '0'
max_ms = '0'

def quitApplication(systray):
    if asyncState.shutdown_now == True:
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    else:
        print('not shutting down')

def quitNow(systray):
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)

time_values = []
response = None
ip_list = ['8.8.8.8',]
ping_target = '8.8.8.8'
australia = '203.24.100.125'
leagueoflegends = '104.160.131.3'
google = '8.8.8.8'
nullIP = '192.168.3.1'

# async def pingReturnAustralia(systray):
#     return '139.130.4.5'
def pingListAustralia(systray):
    if asyncState.pingTarget != australia:
        asyncState.pingTarget = australia

    # if ip_list[0] != australia:
    #     ip_list.clear()
    #     ip_list.append(australia)
# async def pingReturnLeagueOfLegends(systray): 
#     return '139.130.4.5'
def pingListLeagueOfLegends(systray):
    if asyncState.pingTarget != leagueoflegends:
        asyncState.pingTarget = leagueoflegends 
    # if ip_list[0] != leagueoflegends:
    #     ip_list.clear()
    #     ip_list.append(leagueoflegends)
# async def pingReturnGoogle(systray):
#     return '8.8.8.8'
def pingListGoogle(systray):
    if asyncState.pingTarget != google:
        asyncState.pingTarget = google
    # if ip_list[0] != google:
    #     ip_list.clear()
    #     ip_list.append(google)

def pingListNullIP(systray):
    if asyncState.pingTarget != nullIP:
        asyncState.pingTarget = nullIP
    # if ip_list[0] != nullIP:
    #     ip_list.clear()
    #     ip_list.append(nullIP)

async def addMenuOption(asyncState, menu_item):
    menu = asyncState.menu_options 
    menu_list = list(menu)
    menu_list.append(menu_item)
    menu = tuple(menu_list)
    asyncState.menu_options = menu

def stopMenu(systray):
    systray.shutdown()

def testAdd(systray):
    asyncState.restarting = True

def newMenu(systray):
    print(asyncState.loop_running)
    pass

async def get_target():
    return ip_list[0]

async def test_ping(ip):
    delay = await aioping.ping(ip, timeout=1)
    return delay

async def restart_systray(systray):
    systray.shutdown()
    systray = SysTrayIcon("grey_icon.ico", "caniping", asyncState.menu_options, on_quit=quitApplication)
    systray.start()
    return True

async def GetGrammar():
    if asyncState.numberOfDisconnects == 1:
        return 'time'
    else:
        return 'times'



async def ping(systray, asyncState):
    asyncState.total += 1
    connectivity_string = str(round((1 - (asyncState.disconnected/asyncState.total))*100, 1))
    if systray:
        try:
            # ping_target = await get_target()
            ping_target = asyncState.pingTarget
            delay = await test_ping(ping_target)
            delay_string = str(math.floor(delay*1000))
            ping_string = str(ping_target)
            grammar = await GetGrammar()
            display = "Ping to {} took {}ms   Uptime: {}%   I have disconnected {} {} since {}".format(ping_string, delay_string, connectivity_string, asyncState.numberOfDisconnects, grammar, asyncState.startTime)
            print(display)
            systray.update(icon='./green_icon.ico')
            asyncState.counter = 0
            asyncState.connectBool = False
            await asyncio.sleep(1)
            
        except TimeoutError:
            if asyncState.connectBool == False:
                asyncState.numberOfDisconnects += 1
                asyncState.connectBool = True
            asyncState.disconnected += 1
            asyncState.counter += 1
            grammar = await GetGrammar()
            display = 'No Internet for {} seconds   Uptime: {}%   I have disconnected {} {} since {}'.format(asyncState.counter, connectivity_string, asyncState.numberOfDisconnects, grammar, asyncState.startTime)
            print(display)
            systray.update(icon='./red_icon.ico')
    else:
        print('not pinging')

async def shell(asyncState):
    
    while True:
        if not asyncState.loop_running and not asyncState.restarting:
            systray = SysTrayIcon("grey_icon.ico", "null_internet", asyncState.menu_options, on_quit=quitApplication)
            asyncState.systray = systray
            systray.start()
            asyncState.loop_running = True

        if asyncState.loop_running and asyncState.restarting:
            test_input = ('test_item', None, newMenu)
            await addMenuOption(asyncState, test_input)
            await restart_systray(systray)
            asyncState.restarting = False

        if systray:
            await ping(systray, asyncState)

        

def restartSystray(systray):
    systray.shutdown()
    systray = SysTrayIcon('grey_icon.ico', 'null_internet', menu_options, on_quit=quitApplication)
    systray.start()

try:
    with open ('menu_items.txt') as file:
        menu_text = file.read()
    
    asyncState = type('', (), {})()
    asyncState.startTime = datetime.datetime.now().strftime("%H:%M %m-%d-%Y")
    asyncState.pingTarget = '8.8.8.8'
    asyncState.loop_running = False
    asyncState.restarting = False
    asyncState.systray = None
    asyncState.connectBool = False
    asyncState.total = 0
    asyncState.disconnected = 0
    asyncState.numberOfDisconnects = 0
    asyncState.counter = 0
    menu = list(menu_text)
    # asyncState.menu_options = menu
    asyncState.menu_options = (
        ('Australia', None, pingListAustralia),
        ('LoL', None, pingListLeagueOfLegends),
        ('Google', None, pingListGoogle),
        ('Null', None, pingListNullIP),
        # ('Test New Menu Item', None, testAdd),
    )
    asyncState.shutdown_now = False
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(shell(asyncState))
    loop.run_forever()
except KeyboardInterrupt:
    # quitApplication(systray)
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
finally:
    loop.close()
        # quitApplication(systray)


