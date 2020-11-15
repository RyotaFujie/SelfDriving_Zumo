import pygame
from pygame.locals import *
import serial , time
import cv2
import sys
import threading

def capture(cap, cont_capture, label):
    ret, frame = cap.read()
    if ret :
        print("captured")
        frame = cv2.flip(frame, -1)
        frame = cv2.resize(frame, (80, 60))
        #cv2.imshow("test window", frame)
        cv2.imwrite(f'../dataset/Zumo_run01_{cont_capture}_{label}.jpeg', frame)

def setMode(mode_flags, index):
    # clear flag
    for i in range(len(mode_flags)):
        mode_flags[i] = False

    mode_flags[index] = True
    return mode_flags

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

    # camera setup
    camera_id = 0
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        print("can not open camrea")
        sys.exit()
    print("camrea is opend")

    try:
        # vals that using in remoto control
        cont_capture = 0 # count capture num
        start = time.time()

        # vals that using in self driving
        mode_flags = [True, False, False]
        NOMAL = 0
        LEARNING = 1 # capture camera
        INFERENCE = 2


        while True:

            # interval
            now = time.time()
            if (now - start) < 0.1:
                continue
            else:
                start = time.time()

            # get event
            events = pygame.event.get()
            if len(events) == 0:
                continue
            event = events[0]
            print(len(events))

            # switch driving mode
            if event.type == pygame.locals.JOYBUTTONDOWN:
                if event.button == 0: # end
                    exit()

                elif event.button == 1: # nomal
                    setMode(mode_flags, NOMAL)
                    print("on Nomal Driving")

                elif event.button == 2: # learning (capture)
                    setMode(mode_flags, LEARNING)
                    print("on capture")

                elif event.button == 3: # inference
                    setMode(mode_flags, INFERENCE)
                    print("on Self Driving")
                continue # 次のイベントへスキップ

            # remoto control
            if mode_flags[NOMAL] or mode_flags[LEARNING] :
                # get controller joystick input
                if event.type == pygame.locals.JOYAXISMOTION:
                    # throttle control
                    throttle = int(joystick.get_axis(1) * 10) * -1   
                    if throttle > 0:
                        throttle = 100
                    else:
                        throttle = 0   
                    # steer control
                    steer = (int(joystick.get_axis(3) * 10)  / 2) * 2# -10から9   [-1 → -10], [0 → 9] を二つ飛ばしに変換
                    label = steer + 10
                    if 0 > steer:
                        steer = (steer * -1 ) - 1# 0から9に変換
                        ctl = (9 - steer) * 10 + 9
                    else:
                        ctl = 90 + (9 - steer)

                    if ctl == 99 :#直線になった瞬間に急加速してしまうのでスピード調整
                        ctl = 88
                    ctl += throttle
                    ctl = int(ctl)
                    print(ctl)
                continue # 次のイベントへスキップ

            # self driving
            if mode_flags[INFERENCE] :




    except( KeyboardInterrupt, SystemExit):
        ser.close()
        print( "end")

main()

