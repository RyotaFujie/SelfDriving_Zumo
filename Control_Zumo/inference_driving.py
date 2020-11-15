import pygame
from pygame.locals import *
import serial , time
import cv2
import sys
import threading


############################################################################################################
# # モデルの定義および学習に使用する
# import torch
# import torch.nn as nn
# import torch.optim as optim
# import torch.nn.functional as F
# from tqdm import tqdm   # 進捗状況をプログレスバーで表示する
# import time

# # 学習データの読み込みに使用する
# from torch.utils.data import DataLoader
# from torchvision import datasets, transforms
# import torchvision
# import os
# from pathlib import Path
# from PIL import Image

# # 学習後の可視化に使用する
# import numpy as np
# import matplotlib.pyplot as plt
# # スプライン補完を使用して滑らかに点を結ぶ
# from scipy.interpolate import InterpolatedUnivariateSpline


# class MyLeNet(nn.Module):
#     def __init__(self):
#         super(MyLeNet, self).__init__()
#         #チャンネル数input_image_channelsの特徴マップを受け取って，チャンネル数6の特徴マップを出力
#         self.conv1 = nn.Conv2d(3, 3, kernel_size=(5, 5), stride=(1, 1))
#         self.conv2 = nn.Conv2d(3, 8, kernel_size=(5, 5), stride=(1, 1))
#         self.conv3 = nn.Conv2d(8, 16, kernel_size=(5, 5), stride=(1, 1))
#         self.max_pool = nn.MaxPool2d(kernel_size=(2, 2), stride=(2, 2)) #　最大値プーリング
#         self.bn1 = nn.BatchNorm2d(3)#　バッチ正規化
#         self.bn2 = nn.BatchNorm2d(8)# バッチ正規化
#         self.bn3 = nn.BatchNorm2d(16)#　バッチ正規化
#         self.fc1 = nn.Linear(4*6*16, 256)  # 線形変換
#         self.fc2 = nn.Linear(256, 64)
#         self.fc3 = nn.Linear(64, 10) # 出力数10で，交差エントロピーする

#     def forward(self, x):
#         #https://qiita.com/poorko/items/c151ff4a827f114fe954
#         #結合の解説記事
#         x = F.relu(self.bn1(self.conv1(x)))
#         x = self.max_pool(x)
#         x = F.relu(self.bn2(self.conv2(x)))
#         x = self.max_pool(x)
#         x = F.relu(self.bn3(self.conv3(x)))
#         x = self.max_pool(x)
#         x = x.view(-1, self.num_flat_features(x))
#         x = F.relu(self.fc1(x))
#         x = F.relu(self.fc2(x))
#         y = self.fc3(x) #回帰
#         return y
  
#     def num_flat_features(self, x):
#         size = x.size()[1:]
#         num_features = 1
#         for s in size:
#             num_features *= s
#         return num_features


# class MyInfernceDataset(torch.utils.data.Dataset):
#     IMG_EXTENSIONS = [".jpg", ".jpeg", ".png", ".bmp"]

#     def __init__(self, inference_img, transform=None):
#         self.img = inference_img
#         self.transform = transform


#     # obj[i]とインデックス指定の時に呼ばれるコール
#     def __getitem__(self, idx):

#         if self.transform:
#             out_data = self.transform(self.img)

#         return out_data

# model = MyLeNet()
# model.load_state_dict(torch.load("model.pth"))
# model.eval() #推論モード

############################################################################################################

def capture(cap):
    ret, frame = cap.read()
    if ret :
        print("captured")
        frame = cv2.flip(frame, -1)
        frame = cv2.resize(frame, (80, 60))
        return frame

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

            # self driving
            # elif mode_flags[INFERENCE] :
            #     batch_size = 1  # バッチサイズを定義
            #     transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
            #     inference_set = MyDataset(capture(cap), transform)
            #     inference_loader = torch.utils.data.DataLoader(inference_set, batch_size, shuffle=False)


            # serial to arduino
            val = ctl
            print(val)
            valByte = val.to_bytes(1,'big')
            ser.flush()
            ser.write(valByte)




    except( KeyboardInterrupt, SystemExit):
        ser.close()
        print( "end")

main()

