import pyautogui as pgui
import time
pgui.PAUSE = 1
print(pgui.size())
refpics_path = '../narda_navigator_referencepics'
print("location: ")
print(pgui.locateOnScreen(refpics_path + '/search_bar.PNG'))
print()
# pgui.click(pgui.center(pgui.locateOnScreen(refpics_path + '/stop_button.PNG')))  # Dumb line that stops script
while True:
    try:
        x, y, w, h = pgui.locateOnScreen(refpics_path + '/search_bar.PNG')
    except TypeError:
        print('Reference image not found on screen...')
        time.sleep(2)
    try:
        ctrx, ctry = pgui.center((x, y, w, h))
        print(ctrx, ctry)
        pgui.click((ctrx, ctry))
        pgui.typewrite('Hello World!')
        pgui.press('enter')
        time.sleep(2)
    except:
        print('Reference img. not found on screen')
        time.sleep(1)
