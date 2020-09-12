


time_values = []
response = None
ip_list = ['8.8.8.8',]
ping_target = '8.8.8.8'
australia = '203.24.100.125'
leagueoflegends = '104.160.131.3'
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

def addMenuOption(systray):
    print('menu')
    test_list = list(menu)
    test_tuple = ('Testing', None, newMenuOption)
    test_list.append(test_tuple)
    menu = tuple(test_list)
    print('menu')

def newMenuOption(systray):
    print('yay')

def restartSystray():
    systray = SysTrayIcon('grey_icon.ico', 'null_internet', menu_options, on_quit=quitApplication)

menu = (
    ('Australia', None, pingListAustralia),
    ('LoL', None, pingListLeagueOfLegends),
    ('Google', None, pingListGoogle),
    ('test', None, addMenuOption)
)

