import pygame
from pygame.locals import *
import serial , time

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
        while True:
            for event in pygame.event.get():
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
                   
                #print('L3: ',  left, ', R3: ', right)

                #serial to arduino
                val = left*10 + right
                print(val)
                valByte = val.to_bytes(1,'big')
                ser.flush()
                ser.write(valByte)
#                 time.sleep(2)

                #            left = 0
                #            right = 0

    except( KeyboardInterrupt, SystemExit):
        ser.close()
        print( "end")

main()

