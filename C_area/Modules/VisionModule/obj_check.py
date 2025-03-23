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
#obj_check 函数用于在图像中检测特定颜色的目标，并返回目标的位置、大小和颜色信息。
#image: 输入的图像。colors: 需要检测的颜色范围。filtered_colors: 需要过滤掉的颜色范围。
#colorNames: 颜色名称列表，用于标识检测到的颜色。no_edge: 是否去除图像边缘的轮廓。
#show_wanted: 是否显示处理后的图像。windowName: 显示图像的窗口名称。
def color_check(image, colors, filtered_colors, colorNames=None, show_wanted=False, windowName="filtered"):
    # 1. 图像预处理
    blurred = cv2.medianBlur(image, 3)  # 中值滤波去噪
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)  # 转换为HSV颜色空间

    # 2. 过滤掉不需要的颜色
    filtered_mask = np.zeros(hsv.shape[:2], dtype="uint8")  # 创建空白掩码
    for (lower, upper) in filtered_colors:
        lower = np.array(lower, dtype='uint8')
        upper = np.array(upper, dtype='uint8')
        mask = cv2.inRange(hsv, lower, upper)  # 生成颜色掩码
        filtered_mask = cv2.bitwise_or(filtered_mask, mask)  # 合并掩码
    filtered_mask = cv2.bitwise_not(filtered_mask)  # 反转掩码，保留需要的颜色
    filtered_unwanted = cv2.bitwise_and(hsv, hsv, mask=filtered_mask)  # 应用掩码

    # 3. 对每个目标颜色进行二值化处理
    max_area = 0
    target_color = "undefined"
    c = None
    for i, (lower, upper) in enumerate(colors):
        # 生成目标颜色的掩码
        lower = np.array(lower, dtype='uint8')
        upper = np.array(upper, dtype='uint8')
        mask = cv2.inRange(filtered_unwanted, lower, upper)  # 在HSV空间中过滤目标颜色

        # 对掩码进行二值化处理
        _, binary = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY)

        # 查找轮廓
        cnts, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if cnts:
            c = max(cnts, key=cv2.contourArea)  # 找到最大轮廓
            area = cv2.contourArea(c)  # 计算轮廓面积
            if area > 3000 and area > max_area:  # 过滤掉太小的区域
                max_area = area
                target_color = colorNames[i]  # 更新目标颜色

    # 4. 显示处理后的图像（可选）
    if show_wanted:
        if isinstance(c, np.ndarray):
            # 在原图上绘制轮廓
            output_image = cv2.bitwise_and(image, image, mask=binary)  # 只保留目标颜色区域
            cv2.drawContours(output_image, [c], -1, (0, 255, 0), 2)  # 绘制轮廓
            cv2.imshow(windowName, output_image)
            cv2.waitKey(1)

    return target_color, binary  # 返回目标颜色和二值化图像



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






        