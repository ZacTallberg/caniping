from infi.systray import SysTrayIcon
import aioping
import logging
import time
import pydash
import asyncio
from pydash import py_
import sys
import ctypes
import os
import win32process
import math


import win32process


import win32serviceutil
import win32service
import win32event
import servicemanager
import socket


class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "Ping-Check"
    _svc_display_name_ = "Ping-Check"

    active_ping = '8.8.8.8'
    test_ping = '0.0.0.0'
    min_ms = '0'
    avg_ms = '0'
    max_ms = '0'

    async def checkForIpChange():
        if len(ip_list) > 0:
            test_ping = ip_list[0]
            print('we changed: ' + test_ping)
            ip_list.remove(test_ping)
            active_ping = test_ping
        else:
            # print('returned active: ' + active_ping)
            pass

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
        if ip_list[0] != australia:
            ip_list.clear()
            ip_list.append(australia)
    # async def pingReturnLeagueOfLegends(systray): 
    #     return '139.130.4.5'
    def pingListLeagueOfLegends(systray): 
        if ip_list[0] != leagueoflegends:
            ip_list.clear()
            ip_list.append(leagueoflegends)
    # async def pingReturnGoogle(systray):
    #     return '8.8.8.8'
    def pingListGoogle(systray):
        if ip_list[0] != google:
            ip_list.clear()
            ip_list.append(google)

    def pingListNullIP(systray):
        if ip_list[0] != nullIP:
            ip_list.clear()
            ip_list.append(nullIP)

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
        delay = await aioping.ping(ip, timeout=0.4)
        return delay

    async def ping(systray, asyncState):
        if systray:
            try:
                ping_target = await get_target()
                delay = await test_ping(ping_target)
                delay_string = str(math.floor(delay*1000))
                ping_string = str(ping_target)
                display = "Ping to {} took {}ms".format(ping_string, delay_string)
                print(display)
                systray.update(icon='./green_icon.ico')
                
            except TimeoutError:
                print('Ping RTT is more than 400ms')
                systray.update(icon='./red_icon.ico')
        else:
            print('not pinging')

    async def shell(asyncState):
        
        while True:
            if not asyncState.loop_running and not asyncState.restarting:
                systray = SysTrayIcon("grey_icon.ico", "null_internet", asyncState.menu_options, on_quit=quitApplication)
                systray.start()
                asyncState.loop_running = True

            if asyncState.loop_running and asyncState.restarting:
                test_input = ('test_item', None, newMenu)
                await addMenuOption(asyncState, test_input)
                systray.shutdown()
                systray = SysTrayIcon("grey_icon.ico", "null_internet", asyncState.menu_options, on_quit=quitApplication)
                systray.start()
                asyncState.restarting = False

            if systray:
                await ping(systray, asyncState)

            await asyncio.sleep(1)

    def restartSystray(systray):
        systray.shutdown()
        systray = SysTrayIcon('grey_icon.ico', 'null_internet', menu_options, on_quit=quitApplication)
        systray.start()

    def __init__(self,args):
            win32serviceutil.ServiceFramework.__init__(self,args)
            self.hWaitStop = win32event.CreateEvent(None,0,0,None)
            socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                            servicemanager.PYS_SERVICE_STARTED,
                            (self._svc_name_,''))
        self.main()

    def main(self):
        try:
            with open ('menu_items.txt') as file:
                menu_text = file.read()
            asyncState = type('', (), {})()
            asyncState.loop_running = False
            asyncState.restarting = False
            menu = list(menu_text)
            # asyncState.menu_options = menu
            asyncState.menu_options = (
                ('Australia', None, pingListAustralia),
                ('LoL', None, pingListLeagueOfLegends),
                ('Google', None, pingListGoogle),
                ('Null', None, pingListNullIP),
                ('Test New Menu Item', None, testAdd),
            )
            asyncState.shutdown_now = False
            loop = asyncio.get_event_loop()
            asyncio.ensure_future(shell(asyncState))
            loop.run_forever()
        except KeyboardInterrupt:
            # quitApplication(systray)
            try:
                SvcStop(self)
                sys.exit(0)
            except SystemExit:
                os._exit(0)
        finally:
            loop.close()
            # quitApplication(systray)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)


