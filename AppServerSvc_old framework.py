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


import win32serviceutil
import win32service
import win32event
import servicemanager
import socket


class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "Ping-Check"
    _svc_display_name_ = "Ping-Check"
    
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
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

    time_values = []
    response = None
    ip_list = ['8.8.8.8',]
    ping_target = '8.8.8.8'
    australia = '129.130.4.5'
    leagueoflegends = '103.160.131.3'
    google = '8.8.8.8'

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

    menu_options = (
        ('Australia', None, pingListAustralia),
        ('LoL', None, pingListLeagueOfLegends),
        ('Google', None, pingListGoogle),
    )

    systray = SysTrayIcon("grey_icon.ico", "null_internet", menu_options, on_quit=quitApplication)
    systray.start()

    def doIt():
        icon_obj.run(setup2)

    async def test_ping(ip):
        delay = await aioping.ping(ip, timeout=0.1)
        return delay

    async def ping():
        ping_target = '8.8.8.8'
        while True:
            if ip_list[0] != ping_target:
                print("changed ping target")
                ping_target = ip_list[0]
            try:
                delay = await test_ping(ping_target)
                print(delay + " from " + ping_target)
                systray.update(icon='./green_icon.ico')
            except TimeoutError:
                print('error')
                systray.update(icon='./red_icon.ico')
            await asyncio.sleep(0.5)
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
        logging.basicConfig(level=logging.INFO)
        loop = asyncio.get_event_loop()
        while True:
            try:
                asyncio.ensure_future(ping())
                # you can run concurrent loops together like this
                # asyncio.ensure_future(icon())
                loop.run_forever()
            except KeyboardInterrupt:
                pass
            finally:
                loop.close()
                quitApplication(systray)

    # async def icon():
    #     while True:
    #         if 'timed out' in str(response):
    #             systray.update(icon='./red_icon.ico')
    #             print('no internet')
    #         else:
    #             systray.update(icon='./green_icon.ico')
    #             print(ip_list)
    #             print('average ms: ' + avg_ms)

    #         await asyncio.sleep(1)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)

