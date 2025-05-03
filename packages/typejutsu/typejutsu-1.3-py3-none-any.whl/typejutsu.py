import sys
import os
from time import sleep

def main():
    try:
        import pyautogui as pg
    except:
        os.system("pip install pyautogui")
        import pyautogui as pg
    
    try:
        import pyperclip as pc
    except:
        os.system("pip install pyperclip")
        import pyperclip as pc
    
    if len(sys.argv) <= 1:
        sleep(5)
    else:
        tm = int(sys.argv[1])
        sleep(tm)

    data = pc.paste()

    pg.typewrite(data, 0.1)


if __name__ == "__main__":
    main()
