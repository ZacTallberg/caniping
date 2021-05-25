
##------------------> 1) To run this program, double click the .bat file after cloning, right click to change options of locations to ping!

##------------------> 2) You can add more ping locations by adding a new ip on line 48 of test.systray
##---------/ australia = '203.24.100.125'
##---------/ def pingListAustralia(systray):
##---------/    if asyncState.pingTarget != australia:
##---------/        asyncState.pingTarget = australia
##---------/    if ip_list[0] != australia:
##---------/        ip_list.clear()
##---------/  

##------------------> 3) Add your new menu item by editing the "menu_items.txt"
##---------/ (
##---------/ ('Australia', None, pingListAustralia),
##---------/ ('LoL', None, pingListLeagueOfLegends),
##---------/ ('Google', None, pingListGoogle),
##---------/ ('Null', None, pingListNullIP),
##---------/ ('Test New Menu Item', None, testAdd),
##---------/ )

