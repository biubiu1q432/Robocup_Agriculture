#!/usr/bin/python3
import cv2
import os
import numpy as np
from Modules import const
from Modules.VisionModule.obj_check import *



'''
    ROI类 —— 感兴趣区域

    内部有：
        roi在原先画面中的位置
        缓存图像


    图像处理的单位是 ROI

'''

'''
    到时需要：
    前左/右ROI —— 先（红、绿、白）对齐（前后、偏角、左右） —— 再（红、绿）识别成熟与否

    
    检测（只看前段） -> 微调 -> 直行到能抓的位置 -> 抓放 -> 边外折边直行一小段

    检测（只看前段）包括：
        切割成左右roi -> 识别左右roi（先对齐、再识别成熟与否）

    对齐包括：
        get 两个minAreaRect的左右底坐标（主要是这个足够平），用来计算偏角（l左底~r左底，l右底~r右底）
        我们不会用到minAreaRect的yaw，yaw是我们用点 自己再算的

'''
class ROI:
    def __init__(self, roi, roi_frame, roi_name=None):
        self.roi = roi    # 这是 当前这块roi_frame在原frame中的区域标识
        # roi为 (左上角点x坐标,左上角点y坐标,区域w,区域h)
        self.roi_frame = roi_frame
        self.roi_filtered_frame = None  # 用来保存并看结果的，不是用来处理的
        self.roi_name = roi_name    # 默认没有名字

        self.obj_center_coord = (-1, -1)
        self.obj_shape = (-1, -1)
        self.is_ripe = const.NOVEGE

    # 检测 目标，还能获得 用于对齐的量
    def check_ori(self, colors, filtered_colors, colorNames=None, no_edge=True):
        color = None
        if isinstance(self.roi_frame, np.ndarray):
            color, self.obj_center_coord, self.obj_shape = obj_check(self.roi_frame, colors, filtered_colors, colorNames, no_edge, show_wanted=True, windowName=self.roi_name)

        # 判断成熟度
        self.is_ripe = const.NOVEGE
        if color == "red":
            self.is_ripe = const.RIPE
        elif color == "green":
            self.is_ripe = const.UNRIPE


    """
        能分成 识别颜色 和 微调对齐 两种模式
    """
    def check(self, colors, filtered_colors, colorNames=None, no_edge=True, show_wanted=False):
        if isinstance(self.roi_frame, np.ndarray):
            if colorNames == None:  # 微调对齐用的，不需要知道是什么颜色
                _, self.obj_center_coord, self.obj_shape, self.roi_filtered_frame = obj_check(self.roi_frame, colors, filtered_colors, colorNames, no_edge, show_wanted=show_wanted, windowName=self.roi_name)
            else:   # 识别颜色用的，成熟度
                color, self.roi_filtered_frame = color_check(self.roi_frame, colors, filtered_colors, colorNames, show_wanted=show_wanted, windowName=self.roi_name)
                # 判断成熟度
                self.is_ripe = const.NOVEGE
                if color == "red":
                    self.is_ripe = const.RIPE
                elif color == "green":
                    self.is_ripe = const.UNRIPE


'''
    摄像头类
    功能：
        判断生熟、获取摄像头到水果中心的距离、判断对齐与否、带有监视现场的测试用代码
'''
class Camera:
    def __init__(self, camera_name):
        self.camera_name = '/dev/video_' + camera_name
        self.open()

        self.ROIs = []
        self.frame = None

        self.i = 0


    def __del__(self):
        print(f"关闭摄像头，已拍摄 {self.i+1} 张照片")
        self.close()

    def open(self):
        self.cap = cv2.VideoCapture(self.camera_name)
        print(f'已打开摄像头: {self.camera_name}')
        print(f'摄像头打开与否：{self.cap.isOpened()}')
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))   # 视频流压缩，防止两个摄像头出事儿
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        print(f"已关闭 {self.camera_name} 的自动对焦")
        self.cap.set(cv2.CAP_PROP_FOCUS, 38)
        print(f"已调节 {self.camera_name} 的对焦值为 38")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        print(f"摄像头分辨率设置为 1920x1080")

    def close(self):
        self.cap.release()
        print(f'已关闭摄像头: {self.camera_name}')

    def reboot(self):
        self.close()
        self.open()

    def shoot(self, max_size=1, save_wanted=False):    # 拍摄图像（可指定数量/次数 以求画面稳定, 是否需要保存）
        for _ in range(max_size):
            #print(self.cap.isOpened())
            if self.cap.isOpened():     # 现在是一次check一张单帧
                haveCap, frame = self.cap.read()
                if haveCap == False or frame is None:
                    print(f"error device: 摄像头{self.camera_name} 连接有误or摄像头没开")
                    return
                self.frame = frame
        if save_wanted:
            if not os.path.exists("./CameraShoot"):
                os.mkdir("./CameraShoot", 0o777)
            cv2.imwrite(f"./CameraShoot/{self.i}.jpg", frame)
            self.i += 1

    def screen_cutting(self, rois, roiNames=None):  # 画面切割 并保存
        for (i, roi) in enumerate(rois):
            #print(f"roi_{i}:   {int(roi[0])}:{int(roi[0]+roi[2])}, {int(roi[1])}:{int(roi[1]+roi[3])}")
            #roi_frame = self.frame[int(roi[0]):int(roi[0]+roi[2]), int(roi[1]):int(roi[1]+roi[3])] # 这个把w和h搞反了
            roi_frame = self.frame[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]  # 这个才正确。。
            roi_name = "roi_"+str(i) if roiNames == None else roiNames[i]
            self.ROIs.append(ROI(roi, roi_frame, roi_name))

    def clean_ROIs(self):
        self.ROIs = []

    def show_rois(self):
        if isinstance(self.ROIs[0].roi_frame, np.ndarray):
            cv2.imshow("left", self.ROIs[0].roi_frame)
        if isinstance(self.ROIs[1].roi_frame, np.ndarray):
            cv2.imshow("right", self.ROIs[1].roi_frame)
        print("请按任意键")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # 对齐是得让Robot来做的


    # def check(self, colors, colorNames, filtered_colors):
    #     # 从处理过的图像中获得color、dist、(cX,cY)
    #     color = None
    #     if self.cap.isOpened():     # 现在是一次check一张单帧
    #         haveCap, frame = self.cap.read()
    #         if haveCap == False:
    #             print(f"error device: 摄像头{self.camera_name} 连接有误or摄像头没开")
    #             return
    #         self.frame = frame
    #         color, _, _, _, _ = obj_check(frame, colors, filtered_colors, colorNames)

    #         #image, color, _, self.obj_coord, self.obj_width_px = obj_check(frame, colors, colorNames, filtered_colors)
    #         #cv2.imshow(f'isekai {self.camera_name}', image)
    #         #cv2.waitKey(1)

    #         # 判断成熟度
    #         self.is_ripe = const.NOVEGE
    #         if color == 'red':
    #             self.is_ripe = const.RIPE
    #         elif color == 'green':
    #             self.is_ripe = const.UNRIPE

    #         #print('inCamera ' + self.camera_name + '.check: ' + str(self.is_ripe))


