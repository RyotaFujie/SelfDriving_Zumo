import pygame
from pygame.locals import *
import serial , time
import cv2
import sys
import threading

def capture(cap, cont_capture, labels):
    ret, frame = cap.read()
    if ret :
        print("captured")
        frame = cv2.flip(frame, -1)
        frame = cv2.resize(frame, (80, 60))
        #cv2.imshow("test window", frame)
        cv2.imwrite(f'../dataset/Zumo_run01_{cont_capture}_{labels}.jpeg', frame)

def main():

    # ジョイスティックの初期化
    pygame.joystick.init()
    try:
       # ジョイスティックインスタンスの生成
       pygame.init()
       joystick = pygame.joystick.Joystick(0)
       joystick.init()
       print('ジョイスティックの名前:', joystick.get_name())
       print('ボタン数 :', joystick.get_numbuttons())
    except pygame.error:
       print('ジョイスティックが接続されていません')
       exit()

    # pygameの初期化
    pygame.init()

    # serial to
    ser = serial.Serial('/dev/ttyACM0',9600)
    time.sleep(2)

    try:

        start = time.time()

        while True:
            for event in pygame.event.get():

                now = time.time()
                if (now - start) < 0.1:
                    continue
                else:
                    start = time.time()

                # get controller joystick input
                if event.type == pygame.locals.JOYAXISMOTION:
                    #get joystick axes and calcurate level
                    # throttle　control
                    throttle = int(joystick.get_axis(1) * 10) * -1      
                    if throttle > 2:
                        run = 100
                    elif throttle < -2:
                        run = 200
                    else:
                        run = 0
                    #steer control
                    steer = int(joystick.get_axis(3) * 10) # -10から9   [-1 → -10], [0 → 9] の左右縦断階
                    if 0 >= steer:
                        speed = 90 + (9-curve)
                    else:
                        (steer * -1) - 1 # 0から9に変換
                        speed = (9-steer) * 10 + 9

                    speed += throttle

                    print(speed)

                # get controller button input
                elif event.type == pygame.locals.JOYBTTONDOWN:
                    if event.button == 3: # if press A button(bottom side)
                        on_capture = True
                        print("on capture")

                    if event.button == 0:
                        exit()

    except( KeyboardInterrupt, SystemExit):
        ser.close()
        print( "end")

main()

