
##------------------> 1) To run this program, pipenv install after cloning, 
 Edit the .bat file with your python path, then the path to this .py file--
 example file contents: 

          "{{YOUR PYTHON PATH}}" "{{YOUR PATH TO HERE}}\test_systray.py"
          exit
          

##------------------> 2) You can add more ping locations by adding a new ip and function on line 48 of test_systray.py
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

