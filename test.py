from mfrc522 import MFRC522
from machine import Pin, SPI
import time
import os
from time import sleep_ms
from machine import I2C, Pin
from i2c_lcd import I2cLcd

AddressOfLcd = 0x27
i2c = I2C(scl=Pin(5), sda=Pin(21))
lcd = I2cLcd(i2c, AddressOfLcd, 2, 16)

spi = SPI(2, baudrate=2500000, polarity=0, phase=0, sck=Pin(22), mosi=Pin(19), miso=Pin(18))
spi.init()

rdr = MFRC522(spi=spi, gpioRst=4, gpioCs=23)

# LED Pins
green_led = Pin(32, Pin.OUT)  
red_led = Pin(33, Pin.OUT)    # GPIO 15

def display_welcome_message():
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("   Welcome to ")
    lcd.move_to(0, 1)
    lcd.putstr("   NEXATTEND ")
    

def display_access_status(status):
    lcd.move_to(0, 1)
    lcd.putstr("Status: " + status)

def check_access(uid):
    authorized_uids = {
        "0x29C51969",  # Example UID
        "0xE9EB1669",
        "0xA9111A69",
        "0xD3E5DA19"
    }
    return uid in authorized_uids

def log_attendance(uid, granted):
    t = time.localtime()
    timestamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(t[0], t[1], t[2], t[3], t[4], t[5])
    access_status = "Granted" if granted else "Denied"
    with open('attendance.csv', 'a') as f:
        f.write('{},{},{}\n'.format(timestamp, uid, access_status))

if 'attendance.csv' not in os.listdir():
    with open('attendance.csv', 'w') as f:
        f.write('Timestamp,UID,Access Status\n')

display_welcome_message()

while True:
    stat, tag_type = rdr.request(rdr.REQIDL)
    if stat == rdr.OK:
        stat, raw_uid = rdr.anticoll()
        if stat == rdr.OK:
            card_id = "0x%02X%02X%02X%02X" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])
            print("Card ID:", card_id)
            lcd.clear()
            lcd.move_to(0, 0)
            lcd.putstr("UID: " + card_id)
            access_granted = check_access(card_id)
            if access_granted:
                print("Access granted for UID:", card_id)
                display_access_status("Success")
                green_led.on()  # Turn on green LED
                time.sleep(2)   # Keep the green LED on for 2 seconds
                green_led.off() # Turn off green LED
            else:
                print("Access denied for UID:", card_id)
                display_access_status("Fail")
                red_led.on()    # Turn on red LED
                time.sleep(2)   # Keep the red LED on for 2 seconds
                red_led.off()  # Turn off red LED
            log_attendance(card_id, access_granted)
            time.sleep(5)
            display_welcome_message()
