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

pytesseract.pytesseract.tesseract_cmd = r'.\TesserAct\tesseract.exe'

# Select Flyff Window
print("YOU HAVE 5 SECS TO SELECT FLYFF WINDOW, THAN JUST WAIT")
time.sleep(5)
print("WAITED ENOUGH, DETECTING FLYFF WINDOW")
# get position of window
rect = win32gui.GetWindowRect(GetForegroundWindow())

print(rect)
x = rect[0]
y = rect[1]
w = rect[2] - x
h = rect[3] - y

def click(x,y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

bounding_box = {'top': y - 100 , 'left': x, 'width': w, 'height': h - 200}
print("WINDOW BOUNDING BOX:")
print(bounding_box)

sct = mss()

while True:
    sct_img = sct.grab(bounding_box)
    Img_img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX").convert('L')
    ret,Img_img  = cv2.threshold(np.array(Img_img), 240, 255, cv2.THRESH_BINARY)

    img = np.array(Img_img)
    d = pytesseract.image_to_data(img,   output_type='data.frame', config='--psm 11')

    n_boxes = len(d['level'])

    for i in range(n_boxes):
                # this condition describes a found monster - settings may change over time
                if(d['conf'][i] > 1 and d['text'][i] != " " and d['text'][i] != "" and d['text'][i] != "nan" and d['text'][i] != "NaN" and type(d['text'][i]) == str and len(d['text'][i]) > 4):

                    #print(x)
                    click(x + d['left'][i] + 20, y + d['top'][i] + 100 + 5)
                    #keyboard.press('s')
                    #time.sleep(0.05)
                    #keyboard.release('s')
                    keyboard.press_and_release('c')
                    keyboard.press_and_release('esc')
                    
                    (xa, ya, wa, ha) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                    cv2.rectangle(img, (xa, ya), (xa + wa, ya + ha), (255, 255, 255), 2)

                    cv2.imshow('screen', img)
                    time.sleep(0.5)
                    break
                else :
                    keyboard.press('w')

                    

    

    if (cv2.waitKey(1) & 0xFF) == ord('q'):
        cv2.destroyAllWindows()
        break

    