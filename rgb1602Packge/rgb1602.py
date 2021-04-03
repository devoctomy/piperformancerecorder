#!/usr/bin/env python
# -*- coding:utf-8 -*-
# -------------------------------
# SDA: Pin3
# SCL: Pin5

import smbus
import time

LCD_ADDRESS             = 0x3e
RGB_ADDRESS             = 0x60

'''
 *  @brief color define
''' 
WHITE                   = 0
RED                     = 1
GREEN                   = 2
BLUE                    = 3

REG_RED                 = 0x04        # pwm2
REG_GREEN               = 0x03        # pwm1
REG_BLUE                = 0x02        # pwm0

REG_MODE1               = 0x00
REG_MODE2               = 0x01
REG_OUTPUT              = 0x08

'''
 *  @brief commands
'''
LCD_CLEARDISPLAY        = 0x01
LCD_RETURNHOME          = 0x02
LCD_ENTRYMODESET        = 0x04
LCD_DISPLAYCONTROL      = 0x08
LCD_CURSORSHIFT         = 0x10
LCD_FUNCTIONSET         = 0x20
LCD_SETCGRAMADDR        = 0x40
LCD_SETDDRAMADDR        = 0x80

'''
 *  @brief flags for display entry mode
'''
LCD_ENTRYRIGHT          = 0x00
LCD_ENTRYLEFT           = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

'''
 *  @brief flags for display on/off control
'''
LCD_DISPLAYON           = 0x04
LCD_DISPLAYOFF          = 0x00
LCD_CURSORON            = 0x02
LCD_CURSOROFF           = 0x00
LCD_BLINKON             = 0x01
LCD_BLINKOFF            = 0x00

'''
 *  @brief flags for display/cursor shift
'''
LCD_DISPLAYMOVE         = 0x08
LCD_CURSORMOVE          = 0x00
LCD_MOVERIGHT           = 0x04
LCD_MOVELEFT            = 0x00

'''
 *  @brief flags for function set
'''
LCD_8BITMODE            = 0x10
LCD_4BITMODE            = 0x00
LCD_2LINE               = 0x08
LCD_1LINE               = 0x00
LCD_5x10DOTS            = 0x04
LCD_5x8DOTS             = 0x00
'''
BUS = smbus.SMBus(1)

class LCD:
    def __init__(self, row, col):
        self._row = row
        self._col = col
        print("LCD _row=%d _col=%d"%(self._row,self._col))

    def print(self,arg):
        if(isinstance(arg,int)):
            arg=str(arg)

        for x in bytearray(arg):
           self.write(x)
'''
class LCD1602():
    def __init__(self, col=16, row=2, i2c=None):
        self._showcontrol = LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF
        self._showmode = LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT
        if i2c == None:
            self._i2c = smbus.SMBus(1)
        else:
            self._i2c = i2c
        self._row = row
        self._col = col
        print("LCD: _row=%d, _col=%d"%(self._row,self._col))
        
        #super(LCD1602, self).__init__(row, col)
        for cmd in(
        LCD_FUNCTIONSET | LCD_2LINE,
        LCD_DISPLAYCONTROL | LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF,
        LCD_CLEARDISPLAY,
        LCD_ENTRYMODESET | LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT
        ):
            self.command(cmd)
            time.sleep(0.1)
        self.setReg(REG_MODE1, 0)
        self.setReg(REG_OUTPUT, 0xff)
        self.setReg(REG_MODE2, 0x20)
        self.setRGB(255, 255, 255)
        
    def printLCD(self,arg):
        if(isinstance(arg,int)):
            arg=str(arg)

        for x in bytearray(arg):
           self.write(x)
        
    def command(self,cmd):
        b = bytearray(2)
        b[0] = 0x80
        b[1] = cmd
        self._i2c.write_byte_data(LCD_ADDRESS, b[0], b[1])

    def write(self,data):
        b = bytearray(2)
        b[0] = 0x40
        b[1] = data
        self._i2c.write_byte_data(LCD_ADDRESS, b[0], b[1])
    
    def setReg(self,reg,data):
        b = bytearray(1)
        b[0] = data
        self._i2c.write_byte_data(RGB_ADDRESS,reg,b[0])

    def setRGB(self,r,g,b):
        self.setReg(REG_RED,  r)
        self.setReg(REG_GREEN,  g)
        self.setReg(REG_BLUE,  b)
        
    def setCursor(self,col,row):
        if(row == 0):
            col |= 0x80
        else:
            col |= 0xc0
        self.command(col)
        
    def clear(self):
        self.command(LCD_CLEARDISPLAY)
        time.sleep(0.002)
        
    def setPWM(self, colorAddr, pwm):
        self.setReg(colorAddr, pwm) 
        
    def autoscroll(self):
        self._showmode |= LCD_ENTRYSHIFTINCREMENT
        self.command(LCD_ENTRYMODESET | self._showmode)
        
    def noAutoscroll(self):
        self._showmode &= ~LCD_ENTRYSHIFTINCREMENT
        self.command(LCD_ENTRYMODESET | self._showmode)

    def display(self):
        self._showcontrol |= LCD_DISPLAYON
        self.command(LCD_DISPLAYCONTROL | self._showcontrol)

    def noDisplay(self):
        self._showcontrol &= ~LCD_DISPLAYON
        self.command(LCD_DISPLAYCONTROL | self._showcontrol)
        
    def blink(self):
        self._showcontrol |= LCD_BLINKON
        self.command(LCD_DISPLAYCONTROL | self._showcontrol)
        
    def stopBlink(self):
        self._showcontrol &= ~LCD_BLINKON
        self.command(LCD_DISPLAYCONTROL | self._showcontrol)
        
    def cursor(self):
        self._showcontrol |= LCD_CURSORON
        self.command(LCD_DISPLAYCONTROL | self._showcontrol)
        
    def noCursor(self):
        self._showcontrol &= ~LCD_CURSORON
        self.command(LCD_DISPLAYCONTROL | self._showcontrol)
        
    def leftToRight(self):
        self._showmode |= LCD_ENTRYLEFT
        self.command(LCD_ENTRYMODESET | self._showmode)

    def rightToLeft(self):
        self._showmode &= ~LCD_ENTRYLEFT
        self.command(LCD_ENTRYMODESET | self._showmode)
        
    def scrollDisplayLeft(self):
        self.command(LCD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVELEFT)
        
    def scrollDisplayRight(self):
        self.command(LCD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVERIGHT)
        
    def home(self):
        self.command(LCD_RETURNHOME)    # set cursor position to zero
        time.sleep(2)                   # this command takes a long time!
        
    def customSymbol(self, location, charmap):
        location &= 0x7 # we only have 8 locations 0-7
        self.command(LCD_SETCGRAMADDR | (location << 3))
    
        for x in charmap:
            self.write(x)

if __name__ == '__main__':
    print("========Raspberry Pi 3 I2C LCD1602 TEST===========")
    num = 0
    lcd=LCD1602()
    lcd.setRGB(0,0,255)
    #lcd.setCursor(0,0)
    lcd.printLCD("Hello world!")

    #lcd.setCursor(5,1)
    #lcd.printLCD("RGBBacklight TEST")
    #lcd.home()
    #lcd.printLCD(3322)
    while True:
        lcd.setCursor(0, 1)
        lcd.printLCD(num)
        num += 1
        time.sleep(1)
        
