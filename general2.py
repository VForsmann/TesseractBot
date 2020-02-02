import numpy as np
import cv2
from mss import mss
from PIL import Image
import win32gui, win32con, win32api
from win32gui import GetWindowText, GetForegroundWindow
import time
import logging
import pytesseract
from pytesseract import Output
import re
import keyboard
from random import *

pytesseract.pytesseract.tesseract_cmd = r'.\TesserAct\tesseract.exe'

# Select Flyff Window
print("YOU HAVE 5 SECS TO SELECT FLYFF WINDOW, THAN JUST WAIT")
time.sleep(5)
print("WAITED ENOUGH, DETECTING FLYFF WINDOW")
# get position of window
window = GetForegroundWindow()
rect = win32gui.GetWindowRect(window)

print(rect)
x = rect[0]
y = rect[1]
w = rect[2] - x
h = rect[3] - y

def click(x,y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

def press_and_release(key, prtime):
    keyboard.press(key)
    time.sleep(prtime)
    keyboard.release(key)

def move(runtime):
    keyboard.release("w")
    keyboard.release("space")
    time.sleep(1)
    press_and_release("a", 0.8)
    keyboard.press("space")
    keyboard.press("w")
    



bounding_box = {'top': y + 100 , 'left': x, 'width': w, 'height': h - 160}
print("WINDOW BOUNDING BOX:")
print(bounding_box)

waittime = 0 
sct = mss()
try:
    while True:
        if(keyboard.is_pressed("q")):
            exit()
        k = cv2.waitKey(1) & 0xFF
        # press 'q' to exit
        if k == ord('q'):
            break
        sct_img = sct.grab(bounding_box)
        Img_img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX").convert('L')
        ret,Img_img  = cv2.threshold(np.array(Img_img), 240, 255, cv2.THRESH_BINARY)

        img = np.array(Img_img)
        # FE0000 FF0000
        d = pytesseract.image_to_data(img,   output_type='data.frame', config='--psm 11')

        # filter the results of tesseract for flyff
        # Just strings in Texts
        d = d[d['text'].apply(lambda x: isinstance(x, str))]
        # confident
        #& (d['text'].apply(lambda x: len(x)>3))
        d = d[(d['conf'] != -1) & (d['conf'] > 2) & (d['text'] != "") & (d['text'] != " ") & (d['text'] != "NaN") & (d['text'].apply(lambda x: len(x)>2))]
        if(d.shape[0] > 0):
            keyboard.release("w")
            keyboard.release("space")
            waittime = 0
            row = d.iloc[0]
            #click
            click(x + row['left'] + 20, y + row['top'] + 100 + 5)
            #spellcast
            keyboard.press_and_release("c")

            # general wait time for next analysis of image
            time.sleep(0.1)
        else:
            time.sleep(1)
            waittime = waittime + 1
            if(waittime > 3):
                waittime = 0
                move(5)
        



        
except KeyboardInterrupt:
    pass

# Ideen: 
# Den nächsten Mob von der Position zu erst angreifen
# Hindernisserkennung
# - Wenn Hinderniss, dann einmal 180 Grad drehen und vorwärts springen
# Wenn länger keinen Mob, dann einmal 180Grad drehen und vorwärts springen


    