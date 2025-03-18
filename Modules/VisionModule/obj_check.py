#!/usr/bin/python3
import imutils
import cv2
import numpy as np
from Modules.utils.ColorHandler import ColorHandler

'''
    小车视觉功能的核心逻辑大部分都在这
'''


'''
    找寻目标 —— 基于颜色过滤实现
    
    用到了minAreaRect用来对齐用

'''
def obj_check(image, colors, filtered_colors, colorNames=None, no_edge=False, show_wanted=False, windowName="filtered"):
    color_handler = ColorHandler(colors, colorNames, filtered_colors)
    blurred = cv2.medianBlur(image, 3)		# 中值滤波的效果个人感觉用起来比高斯滤波好一点
    filtered = color_handler.filter_color(blurred)
    gray = cv2.cvtColor(filtered, cv2.COLOR_BGR2GRAY)   # 为了可读性，这个就不改了
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)[1]	# 因为用颜色过滤过了，所以二值图阈值只要不会太高就行
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

	# 去边框（可选）
    cnts_in_range = cnts
    limitArea = 1000
    if no_edge:
        maskedge_x = 0
        maskedge_y = 0
        maskedge_w = image.shape[0]
        maskedge_h = image.shape[1]
        cnts_in_range = []
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)    # 这个的w和h是用来算是否在画面边框内的，不是给下边用的
            #print(x, y, w, h)
            if not (abs(x - maskedge_x) <= 1 or abs(y - maskedge_y) <= 1 or abs(x + w - maskedge_x - maskedge_w) <= 1 or abs(y + h - maskedge_y - maskedge_h) <= 1):
                cnts_in_range.append(c)
        limitArea = 3000    # 这个需要调


    color = None
    cX, cY, w, h = -1, -1, -1, -1
    c = None
    if len(cnts_in_range) > 0:

        c = max(cnts_in_range, key=cv2.contourArea)
        
        M = cv2.moments(c)
        if not M["m00"] == 0 and cv2.contourArea(c) > limitArea:     # 保证得有轮廓，且面积太小的轮廓不要
            (cX, cY), (w, h), _ = cv2.minAreaRect(c)    # 基于这个来进行对齐
            cX, cY = int(cX), int(cY)

            if colorNames != None:  # 输入的颜色名字如果被指定为None，则说明我们不需要知道是什么颜色
                #print(f"中心 {(cX, cY)}")
                color = color_handler.detect_color(filtered, cX, cY)
                print("zhe " + color)
    
    if show_wanted:
        if isinstance(c, np.ndarray):
            cv2.drawContours(filtered, [c], -1, (255, 0, 0), 2)
        cv2.imshow(windowName, filtered)
        cv2.waitKey(1)


    # 返回的是：
    #   color - 检测到的目标的颜色，(cX,cY) - 用minAreaRect得到的目标的中心，(w,h) - 用minAreaRect得到的目标的尺寸    
    return color, (cX, cY), (w, h), filtered





# 专门给颜色识别用的
#   untested
def color_check(image, colors, filtered_colors, colorNames=None, show_wanted=False, windowName="filtered"):

    blurred = cv2.medianBlur(image, 3)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # 去掉不要的颜色
    filtered_mask = np.zeros(hsv.shape[:2], dtype="uint8")
    for (lower, upper) in filtered_colors:
        lower = np.array(lower, dtype='uint8')
        upper = np.array(upper, dtype='uint8')
        mask = cv2.inRange(hsv, lower, upper)
        filtered_mask = cv2.bitwise_or(filtered_mask, mask)
    filtered_mask = cv2.bitwise_not(filtered_mask)
    filtered_unwanted = cv2.bitwise_and(hsv, hsv, mask=filtered_mask)



    max_area = 0
    target_color = "undefined"
    c = None
    for i, (lower, upper) in enumerate(colors):
        # 使用每个色域 去 对 原图 进行 颜色过滤
        lower = np.array(lower)
        upper = np.array(upper)
        mask = cv2.inRange(filtered_unwanted, lower, upper)
        cnts, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #cnts = imutils.grab_contours(cnts)
        color_filtered_image = cv2.bitwise_and(blurred, blurred, mask=mask)
        if cnts:
            c = max(cnts, key=cv2.contourArea)
            area = cv2.contourArea(c)
            if area > 3000 and area > max_area:
                max_area = area
                target_color = colorNames[i]

    if show_wanted:
        if isinstance(c, np.ndarray):
            cv2.drawContours(color_filtered_image, [c], -1, (255, 0, 0), 2)
        cv2.imshow(windowName, color_filtered_image)
        cv2.waitKey(1)

    return target_color, color_filtered_image






        