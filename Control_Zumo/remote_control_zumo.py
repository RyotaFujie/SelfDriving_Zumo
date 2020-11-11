import pygame
from pygame.locals import *
import serial , time
import cv2
import sys

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

    try:
        while True:
            for event in pygame.event.get():

                # get controller input
                if event.type == pygame.locals.JOYAXISMOTION:
                    #get joystick axes and calcurate level            
                    left = int(joystick.get_axis(1) * 10) * -1
                    if left < 0:
                        left = 0
                    if left == 10:
                        left = 9
                       
                    right = int(joystick.get_axis(4) * 10) * -1
                    if right < 0:
                        right = 0
                    if right == 10:
                        right = 9

                # camera caputre and save labels
                ret, frame = cap.read()
                if ret :
                    frame = cv2.flip(frame, -1)
                    cv2.imshow("test window", frame)

                # serial to arduino
                val = left*10 + right
                print(val)
                valByte = val.to_bytes(1,'big')
                ser.flush()
                ser.write(valByte)

    except( KeyboardInterrupt, SystemExit):
        ser.close()
        print( "end")

main()

