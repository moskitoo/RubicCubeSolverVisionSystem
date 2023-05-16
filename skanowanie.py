from http.client import FORBIDDEN
from tkinter import DISABLED
from turtle import back
import cv2
import keyboard
from uncertainties import ufloat
import numpy as np
import kociemba
import serial
import time

#from nauka_klasa import Kolor, zrob_kolor_z_pola



                        # PROGRAM DO UKŁADANIA KOSTKI RUBIKA\

                        # WYKONAŁ:   TOMASZ NIEDZIAŁKOWSKI


THRESHOLD = 0.1


def odleglosc(odczytany, kalibrowany):
    suma = 0
    for kolor_odczytany, kolor_kalibrowany in zip(odczytany,kalibrowany):
        roznica = kolor_kalibrowany - kolor_odczytany
        suma += roznica ** 2
    
    return suma ** 0.5 #liczyc za pomoca math.sqrt jest duzo szybsze


def test_odleglosc():
    wynik = odleglosc((0, 1, 2), (2, 3, 1))
    assert wynik == 3
    print('test zaliczony')


test_odleglosc()

def kolor (b_avg, g_avg, r_avg):
    odleglosc_white = odleglosc((b_avg, g_avg, r_avg), 
                                kolor_avg[0])
    odleglosc_orange = odleglosc((b_avg, g_avg, r_avg), 
                                 kolor_avg[1])
    odleglosc_blue = odleglosc((b_avg, g_avg, r_avg), 
                               kolor_avg[2])
    odleglosc_yellow = odleglosc((b_avg, g_avg, r_avg), 
                                 kolor_avg[3])
    odleglosc_red = odleglosc((b_avg, g_avg, r_avg), 
                              kolor_avg[4])
    odleglosc_green = odleglosc((b_avg, g_avg, r_avg), 
                                kolor_avg[5])

    min_odleglosc = min(odleglosc_white, 
                        odleglosc_orange, 
                        odleglosc_blue, 
                        odleglosc_yellow, 
                        odleglosc_red, 
                        odleglosc_green)

    #to przerobic nie moze byc takie dlugie
    if min_odleglosc == odleglosc_white:
        k = 'U'
        print("WHITE", end=' ')
    elif min_odleglosc == odleglosc_orange:
        k = 'R'
        print("ORANGE", end=' ')
    elif min_odleglosc == odleglosc_blue:
        k = 'F'
        print("BLUE", end=' ')
    elif min_odleglosc == odleglosc_yellow:
        k = 'D'
        print("YELLOW", end=' ')
    elif min_odleglosc == odleglosc_red:
        k = 'L'
        print("RED", end=' ') 
    elif min_odleglosc == odleglosc_green:
        k = 'B'
        print("GREEN", end=' ')
    else:
        print("?", end=' ')
        k = '?'
        
    return k


def color_avg(pole):
    b, g, r = cv2.split(pole)
    r_avg = cv2.mean(r)[0]
    g_avg = cv2.mean(g)[0]
    b_avg = cv2.mean(b)[0]
    suma = (b_avg + g_avg + r_avg)**0.34
    return b_avg/suma, g_avg/suma, r_avg/suma


def write_read(x):
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
    data = arduino.readline()
    return data


#PROGRAM

capture = cv2.VideoCapture(0)

arduino = serial.Serial(port='COM4', baudrate=115200, timeout=.1)

kolor_avg = np.zeros((6,3))
#kolor_avg = np.loadtxt('kalibracja.txt').reshape(6,3)
kolor_avg = np.loadtxt(r"C:\Users\moskit\Desktop\kalibracja.txt").reshape(6,3) 
#zmienic lokalizacje zapisu pliku. nie zapisywac w tej wyzej tylko w tej samej lokalizacji co jest main

kostka_macierz = np.chararray((18,3))
#right, front, down, left, back
kostka = ''

while(True):
    ret, frame = capture.read()

    #rysowanie linii
    gap = 120 #odstep miedzy liniami
    startx = 150 #lewy gówny róg ramki x
    starty = 90 #lewy górny róg ramki y

    # parametry dla kołowej kamerki
    
    # gap = 70 #odstep miedzy liniami
    # startx = 150 #lewy gówny róg ramki x
    # starty = 90 #lewy górny róg ramki y

    #rysowanie lini pionowej
    for i in range(4):
        img = cv2.line(frame, (startx + gap * i, starty), (startx + gap * i, starty + gap * 3), (0, 0, 0), 3)

    #rysowanie lini poziomej
    for i in range(4):
        img = cv2.line(frame, (startx, starty + gap * i), (startx + gap * 3, starty + gap * i), (0, 0, 0), 3)

    main = img[starty:starty+gap*3, startx: startx+gap*3 ]

    #KALIBRACJA
    
    #kolory
    # UP    - WHITE  0
    # RIGHT - ORANGE 1
    # FRONT - BLUE   2
    # DOWN  - YELLOW 3
    # LEFT  - RED    4
    # BACK  - GREEN  5

    DANE_O_KLAWISZACH = [
        (0, 'white'),
        (1, 'orange'),
        (2, 'blue'),
        (3, 'yellow'),
        (4, 'red'),
        (5, 'green')
    ]

    #  KALIBRACJA 
    for indeks, nazwa_koloru in DANE_O_KLAWISZACH:
        klawisz = nazwa_koloru[0]
        if (keyboard.is_pressed(klawisz)):
            b_i, g_i, r_i = color_avg(main)
            kolor_avg[indeks, 0] = b_i
            kolor_avg[indeks, 1] = g_i
            kolor_avg[indeks, 2] = r_i
            print(nazwa_koloru, ':', b_i, g_i, r_i)
    
    #zapisywanie kalibracji do txt
    if(keyboard.is_pressed('w') or keyboard.is_pressed('g') or keyboard.is_pressed('y') or keyboard.is_pressed('b') or keyboard.is_pressed('r') or keyboard.is_pressed('o')):
        kalibracja = open('kalibracja.txt','w+')
        for row in kolor_avg:
            np.savetxt(kalibracja,row)
        kalibracja.close()

    #SKANOWANIE SCIANEK
    KLAWISZE_WYBOR_SCIANEK =[
        (0, '0', 'UP'),
        (1, '1', 'RIGHT'),
        (2, '2', 'FRONT'),
        (3, '3', 'DOWN'),
        (4, '4', 'LEFT'),
        (5, '5', 'BACK')
    ]

    for indeks, klawisz, nazwa_scianki in KLAWISZE_WYBOR_SCIANEK:
        if (keyboard.is_pressed(klawisz)):
            for i in range(3):
                for j in range(3):
                    okno = img[starty+gap*i:starty+gap*(i+1), startx+gap*j: startx+gap*(j+1)]
                    b_avg, g_avg, r_avg = color_avg(okno)
                    k = kolor(b_avg, g_avg, r_avg)
                    kostka_macierz[i + 3 * indeks, j] = k 
                print()
            print()
            print(kostka_macierz)
            print()
            print('end')
            print()

    #predefiniowanie kolorów pól, do których zamontowane są silniki
    kostka_macierz[1,1] = 'U'
    kostka_macierz[4,1] = 'R'
    kostka_macierz[7,1] = 'F'
    kostka_macierz[10,1] = 'D'
    kostka_macierz[13,1] = 'L'
    kostka_macierz[16,1] = 'B'

    #tworzenie ciągu znaków opisującego kostkę do algorytmu kociemby
    if(keyboard.is_pressed('z')):
        kostka = ''
        for p in range (6):
            for i in range(3):
                    for j in range(3):
                        print('adasdad: ', kostka_macierz[i,j].decode('utf-8'))
                        kostka += kostka_macierz[i + p * 3, j].decode('utf-8')
        time.sleep(0.5)#po co jest ten sleep
        #print(kostka)
        
    #sprawdzanie stworzonego ciągu
    if (keyboard.is_pressed('p')):
        print(kostka)
        time.sleep(0.5)

    #WYNIK I UKŁADANIE
    if (keyboard.is_pressed('f')):
        wynik = kociemba.solve(kostka)
        ruchy = wynik.split()         
        print('WYNIK: ', wynik)
        print('UWAGA UKŁADANIE')
        time.sleep(5)


        for ruch in ruchy:
            print('wyslany ruch: ', ruch)
            time.sleep(4)
            value = write_read(ruch)
            if value != '':
                print(value.decode('utf-8'))
        print('wykonano wszystkie ruchy')

        time.sleep(0.5)

    cv2.imshow('pelne',img)
    cv2.imshow('okno',main)
        
    if cv2.waitKey(1) == 27:
        break


 