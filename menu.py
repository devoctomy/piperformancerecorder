#!/usr/bin/env python

import sys
import time
import dothat.backlight as backlight
import dothat.lcd as lcd
import dothat.touch as nav
from dot3k.menu import Menu, MenuOption

sys.path.append('.')
from plugins.clock import Clock
from plugins.graph import IPAddress, GraphTemp, GraphCPU, GraphNetSpeed
from plugins.text import Text
from plugins.utils import Backlight, Contrast
from plugins.wlan import Wlan

class Video(MenuOption):
    def __init__(self):
        MenuOption.__init__(self)
    def redraw(self, menu):
        menu.write_row(0, 'Video Options')
        menu.clear_row(1)
        menu.clear_row(2)

video = Video()

class Performance(MenuOption):
    def __init__(self):
        MenuOption.__init__(self)
    def redraw(self, meunu):
        menu.write_row(0, 'Performance')
        menu.clear_row(1)
        menu.clear_row(2)

performance = Performance()

menu = Menu(
    structure={
        'Performance': performance,
        'Status': {
            'Wifi': Wlan(),
            'IP': IPAddress(),
            'CPU': GraphCPU(backlight),
            'Temp': GraphTemp(),
            'Clock': Clock(backlight)
        },
        'Settings': {
            'Display': {
                'Contrast': Contrast(lcd),
                'Backlight': Backlight(backlight)
            },
            'Video': video
        }
    },
    lcd=lcd,
    #idle_handler=my_invader,
    idle_timeout=30,
    input_handler=Text())
nav.bind_defaults(menu)
lcd.set_contrast(50)

while 1:
    menu.redraw()
    time.sleep(0.05)
