#!/usr/bin/env python

import sys
import time
import dothat.backlight as backlight
import dothat.lcd as lcd
import dothat.touch as nav
from dot3k.menu import Menu, MenuIcon, MenuOption

sys.path.append('.')
from plugins.clock import Clock
from plugins.graph import IPAddress, GraphTemp, GraphCPU, GraphNetSpeed
from plugins.text import Text
from plugins.utils import Backlight, Contrast
from plugins.wlan import Wlan

class Video(MenuOption):
    def __init__(self):
        self.enabled = True
        self._icons_setup = False
        MenuOption.__init__(self)

    def right(self):
        self.enabled = True
        self.update_enabled()
        return True

    def left(self):
        self.enabled = False
        self.update_enabled()
        return True

    def setup_icons(self, menu):
        menu.lcd.create_char(0, MenuIcon.arrow_left_right)
        self._icons_setup = True

    def cleanup(self):
        self._icons_setup = False

    def setup(self, config):
        self.config = config
        self.enabled = bool(self.get_option('Video', 'enabled', True))

    def update_enabled(self):
        self.set_option('Video', 'enabled', str(self.enabled))

    def redraw(self, menu):
        if not self._icons_setup:
            self.setup_icons(menu)

        menu.write_row(0, 'Video')
        menu.write_row(1, chr(0) + 'Enabled: ' + str(self.enabled))
        menu.clear_row(2)

class Performance(MenuOption):
    def __init__(self):
        #self._icons_setup = False
        MenuOption.__init__(self)

    #def right(self):
    #    self.update_enabled()
    #    return True

    #def left(self):
    #    self.update_enabled()
    #    return True

    #def setup_icons(self, menu):
    #    self._icons_setup = True

    #def cleanup(self):
    #    self._icons_setup = False

    def setup(self, config):
        self.config = config

    #def update_enabled(self):
    #    self.set_option('Video', 'enabled', str(self.enabled))

    def redraw(self, menu):
        #if not self._icons_setup:
        #    self.setup_icons(menu)

        menu.write_row(0, 'Performance')
        menu.write_row(1, 'Recording...')
        menu.clear_row(2)

video = Video()
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
