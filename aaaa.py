import cv2 as cv
import numpy as np
import keyboard
import msvcrt

# cap = cv.VideoCapture(0)


# while True:
#     ret, frame = cap.read()
    
#     cv.imshow("dupa", frame)
#     aa = frame.mean(axis=0).mean(axis=0)

#     print(aa)
    

#     if cv.waitKey(1) == ord("q"):
#         break

# cap.release()

# cv.destroyAllWindows()
# print(type(aa))

# array = np.zeros((3, 3))

# for row in array:
#     for column in row:
#         print(column)

# for item in np.nditer(array):
#     print(item)

# print(np.size(array))

# count = 0
# for array_item in np.nditer(array):
#     array_item = count
#     count += 1

# print(array)

# count = 0
# for index, value in np.ndenumerate(array):
#     array[index] = count
#     count += 1

# print(array)
# count = 0
# while True:
#       if (keyboard.on_release("q")):
#             count += 1
#             print(f"{count} aa")
# class Obiekt():
#       def __init__(self) -> None:
#             self.a = 5

#       def sraj(self):
#           print("kupa")


# class Kupa:
#     def __init__(self, obiekt) -> None:
#         self.obiekt = obiekt

# obiekt = Obiekt()
# kupa = Kupa(obiekt)

# hmm = getattr(kupa, "obiekt")
# funkcja = getattr(hmm, "sraj")
# funkcja()
# # print(type(hmm))

# while True:
#     if msvcrt.kbhit():
#         key_stroke = msvcrt.getwch()
#         print(key_stroke)   # will print which key is pr

# import keyboard

# buttons = ["a", "b", "c"]

# while True:
#     try:
#         if keyboard.is_pressed(buttons):
#             print('Przycisk "a" został wciśnięty')
#     except:
#         break

# from pynput import keyboard

# def on_press(key):
#     try:
#         print(f'Przycisk {key.char} został wciśnięty')
#     except AttributeError:
#         print(f'Przycisk {key} został wciśnięty')

# with keyboard.Listener(on_press=on_press) as listener:
#     listener.join()

# keys_to_detect = ['a', 's', 'd']
# pressed_keys = set()

# while True:
#     for key in keys_to_detect:
#         if keyboard.is_pressed(key):
#             pressed_keys.add(key)
#         else:
#             pressed_keys.discard(key)
#     if set(keys_to_detect) == pressed_keys:
#         print('Wciśnięto a, s i d')
#         break


# w = {
#     "object": "calibration_manager",
#     "function": "update_color",
#     "args": {
#         "color": "white"
#     }
# }

# args = w["args"]
# values =  args.values()
# values = tuple(values)
# print(len(values))

# a ={'up': ['R', 'R', 'R', 'O', 'O', 'R', 'O', 'O', 'O'], 'right': ['R', 'R', 'R', 'O', 'O', 'R', 'O', 'O', 'O'], 'front': ['R', 'R', 'R', 'O', 'O', 'R', 'O', 'O', 
# 'O'], 'down': ['R', 'R', 'R', 'O', 'O', 'R', 'O', 'O', 'O'], 'left': ['R', 'R', 'R', 'O', 'W', 'R', 'O', 'O', 'O'], 'back': ['R', 'R', 'R', 'O', 'W', 'R', 'O', 
# 'O', 'O']}

# print(type(bytes("A", 'utf-8'))

# import twophase.computer_vision as kociembacv

import twophase.server as srv

srv.start(8080, 20, 2)


