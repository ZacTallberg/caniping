
##------------------> 1) To run this program, pipenv install after cloning, then run the .bat file, right click to change options of locations to ping!

##------------------> 2) You can add more ping locations by adding a new ip on line 48 of test_systray.py
##---------/ australia = '203.24.100.125'
##---------/ def pingListAustralia(systray):
##---------/    if asyncState.pingTarget != australia:
##---------/        asyncState.pingTarget = australia
##---------/    if ip_list[0] != australia:
##---------/        ip_list.clear()
##---------/  

##------------------> 3) Add your new menu item to line 205 of test_systray.py
##---------/ asyncState.menu_options = (
##---------/        ('Australia', None, pingListAustralia),
##---------/        ('LoL', None, pingListLeagueOfLegends),
##---------/        ('Google', None, pingListGoogle),
##---------/        ('Null', None, pingListNullIP),
##---------/        # ('Test New Menu Item', None, testAdd),
##---------/    )

