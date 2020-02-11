import numpy as np
import cv2
from mss import mss
from PIL import Image
from PIL import ImageGrab
import win32gui, win32con, win32api
from win32gui import GetWindowText, GetForegroundWindow
import time
import logging
import pytesseract
from pytesseract import Output
import re
import keyboard
from random import *
import threading
from pyrobot import Robot


pytesseract.pytesseract.tesseract_cmd = r'.\TesserAct\tesseract.exe'

# WINDOW SELECTION

# HWND Variable of selected Windows: Array
windows = []
# Window Rects (x,y,w,h) for windows
windowRects = []
#mss to get images
sct = mss()


try:
    while True:
        print("WINDOW SELECTION, CLICK YOUR WINDOW IN NEXT 5 SECS, THEN JUST WAIT")
        time.sleep(5)
        print("WAITED ENOUGH, DETECTING FLYFF WINDOW")
        window = GetForegroundWindow()
        rect = win32gui.GetWindowRect(window)
        print("FOUND WINDOW: " + str(window) + " WITH RECT: " + str(rect))
        # Push
        windows.append(window)
        windowRects.append(rect)
        try:
            morewindows = input("More Flyff Windows? (y / n):")
            if(morewindows == "n"):
                break
        except SyntaxError:
            pass

    # BOT FUNCTIONS

    # Die meisten games umschiffen mittels Gameguards das automatisierte Clicken mittels SendMessage oder PostMessage, daher gehts nur so :O
    def click(x,y):
        win32api.SetCursorPos((x,y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

    def click2(hwnd, x, y):
        lParam = win32api.MAKELONG(x, y)
        win32gui.PostMessage(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, lParam);
        win32gui.PostMessage(hwnd, WM_LBUTTONUP, MK_LBUTTON, lParam);

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

    input('Press ENTER to start BOT after 5 SECS')
    time.sleep(5)
    #multiple window support
    print(range(len(windows)))
    threads = []

    for index in range(len(windows)):
        def bot():
            # get window and rect
            window = windows[index]
            rect = windowRects[index]
            #sepperate x,y,w,h of rect
            x = rect[0]
            y = rect[1]
            w = rect[2]
            h = rect[3]
            #create bounding box: top and height are cut
            bounding_box = (x, y+100 , w, h-160)

            waittime = 0

            try:
                while True:
                    if(keyboard.is_pressed("q")):
                        break
                    robot = Robot()
                    windowimg = robot.take_screenshot(bounding_box)
                    #conert to type L, means just black and white
                    windowimg = windowimg.convert('L')
                    #convert image to numpy array to work with pixels
                    img = np.array(windowimg)
                    
                    # add Threshhold, just black and white
                    ret, img  = cv2.threshold(img, 240, 255, cv2.THRESH_BINARY)

                    d = pytesseract.image_to_data(img, output_type='data.frame')

                    cv2.imshow('screen', img)
                    if (cv2.waitKey(1) & 0xFF) == ord('q'):
                        cv2.destroyAllWindows()
                        break
                    # filter the results of tesseract for flyff
                    # these filter arent perfect yet
                    d = d[d['text'].apply(lambda x: isinstance(x, str))]
                    d = d[(d['conf'] != -1) & (d['conf'] > 2) & (d['text'] != "") & (d['text'] != " ") & (d['text'] != "NaN") & (d['text'].apply(lambda x: len(x)>2))]

                    # text in image is found
                    if(d.shape[0] > 0):
                        # get row of found text
                        row = d.iloc[0]
                        # + 20 because x + row[left] is the x-top left corner of text
                        monsterx = x + row['left'] + 20
                        # + 5 because y + row[top] is the y-top left corner of text
                        # + 100 because we did + 100 at bounding box earlier
                        monstery = y + row['top'] + 100 + 5
                        print("Found Monster in Window: " + str(window) + " at x: " + str(monsterx) + " at y: " + str(monstery))
                        #click
                        click(monsterx,  monstery)
                        #spellcast
                        keyboard.press_and_release("c")
                        keyboard.press_and_release("s")

                        # general wait time for next analysis of image
                        time.sleep(2)
                    
            except KeyboardInterrupt:
                exit()
        thread = threading.Thread(target=bot)
        threads.append(thread)
        thread.start()


    for thread in threads:
        thread.join()
        print("THREAD STOPPED")

    input('Press ENTER to EXIT')
except Exception as e:
    print(e)
    input("ERROR, press ENTER for EXIT")
    exit()
# Ideen: 
# Den nächsten Mob von der Position zu erst angreifen
# Hindernisserkennung
# - Wenn Hinderniss, dann einmal 180 Grad drehen und vorwärts springen
# Wenn länger keinen Mob, dann einmal 180Grad drehen und vorwärts springen
# FARBEN von HINDERNIS TEXT: FE0000 FF0000
