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
        # using vals in loop
        cont_capture = 0 # count capture num
        on_capture = False # start capture camera

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
                    if throttle > 0:
                        throttle = 100
                    else:
                        throttle = 0

                    #steer control
                    steer = int(joystick.get_axis(3) * 10) # -10から9   [-1 → -10], [0 → 9] の左右縦断階
                    if 0 > steer:
                        steer = (steer * -1 ) - 1# 0から9に変換
                        ctl = (9 - steer) * 10 + 9
                    else:
                        ctl = 90 + (9 - steer)

                    if ctl == 99 :#直線になった瞬間に急加速してしまうのでスピード調整
                        ctl = 88
                    ctl += throttle
                    print(ctl)


                    # serial to arduino
                    val = ctl
                    print(val)
                    valByte = val.to_bytes(1,'big')
                    ser.flush()
                    ser.write(valByte)

                    # camera caputre and save labels
                    if on_capture :
                        # 別のスレットでcaptureを実行
                        t = threading.Thread(target=capture, args=([cap, cont_capture, steer]))
                        t.start()
                        cont_capture += 1

                # get controller button input
                elif event.type == pygame.locals.JOYBUTTONDOWN:
                    if event.button == 3: # if press A button(bottom side)
                        on_capture = True
                        print("on capture")

                    if event.button == 0:
                        exit()

    except( KeyboardInterrupt, SystemExit):
        ser.close()
        print( "end")

main()

