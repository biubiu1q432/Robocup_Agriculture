#!/usr/bin/python3
import cv2
import numpy as np

'''
    颜色处理器，功能如下：
        图像颜色过滤
        颜色识别
'''

# # lab
# class ColorHandler:    
#     # 基于lab —— 测试后lab效果最好
    
#     def __init__(self, colors, colorNames, filtered_colors):
#         self.colors = colors
#         self.colorNames = colorNames
#         self.filtered_colors = filtered_colors
        

#     def filter_color(self, blurred):
#         blurred = cv2.cvtColor(blurred, cv2.COLOR_BGR2LAB)
#         truemask = np.zeros(blurred.shape[:2], dtype="uint8")
#         filtered_mask = np.zeros(blurred.shape[:2], dtype="uint8")
#         for (lower, upper) in self.colors:
#             lower = np.array(lower, dtype='uint8')
#             upper = np.array(upper, dtype='uint8')
#             mask = cv2.inRange(blurred, lower, upper)
#             truemask = cv2.bitwise_or(truemask, mask)

#         for (lower, upper) in self.filtered_colors:
#             lower = np.array(lower, dtype='uint8')
#             upper = np.array(upper, dtype='uint8')
#             mask = cv2.inRange(blurred, lower, upper)
#             filtered_mask = cv2.bitwise_or(filtered_mask, mask)

        
#         truemask = cv2.bitwise_or(truemask, filtered_mask)
#         truemask = cv2.bitwise_xor(truemask, filtered_mask)
#         color_filtered_image = cv2.bitwise_and(blurred, blurred, mask=truemask)
#         return color_filtered_image
    
#     def detect_color(self, image, cX, cY):	# cX和cY是轮廓检测到的对象的中心坐标
#         mask = np.zeros(image.shape[:2], dtype="uint8")
#         cv2.circle(mask, (cX, cY), 40, 255, -1)     # 水波纹会影响。。。
        
#         mask = cv2.erode(mask, None, iterations=2)  # 对上文得到的边缘进行erode，能成功模糊掉规定区域之外的部分，使得mask能成功保留下contour内区域
#         #cv2.imshow("mask", mask)
#         #cv2.waitKey(0)

#         mean = cv2.mean(image, mask=mask)[:3]   # 求image由mask罩起来的区域内的颜色平均值
#         i = 0
#         for (l, r) in self.colors:
#             if mean[0] >= l[0] and mean[1] >= l[1] and mean[2] >= l[2] and mean[0] <= r[0] and mean[1] <= r[1] and mean[2] <= r[2]:
#                 break
#             i += 1
#         if i >= len(self.colorNames):
#             return "undefined"
#         return self.colorNames[i]



# HSV
class ColorHandler:    
    
    def __init__(self, colors, colorNames, filtered_colors):
        self.colors = colors
        self.colorNames = colorNames
        self.filtered_colors = filtered_colors

    def filter_color(self, blurred):
        blurred = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        truemask = np.zeros(blurred.shape[:2], dtype="uint8")
        filtered_mask = np.zeros(blurred.shape[:2], dtype="uint8")
        for (lower, upper) in self.colors:
            lower = np.array(lower, dtype='uint8')
            upper = np.array(upper, dtype='uint8')
            mask = cv2.inRange(blurred, lower, upper)
            truemask = cv2.bitwise_or(truemask, mask)

        for (lower, upper) in self.filtered_colors:
            lower = np.array(lower, dtype='uint8')
            upper = np.array(upper, dtype='uint8')
            mask = cv2.inRange(blurred, lower, upper)
            filtered_mask = cv2.bitwise_or(filtered_mask, mask)

        truemask = cv2.bitwise_or(truemask, filtered_mask)
        truemask = cv2.bitwise_xor(truemask, filtered_mask)
        color_filtered_image = cv2.bitwise_and(blurred, blurred, mask=truemask)
        return color_filtered_image
    
    
    # 原先用的 逻辑有点问题的版本
    def detect_color_ori(self, image, cX, cY):	# cX和cY是轮廓检测到的对象的中心坐标
        mask = np.zeros(image.shape[:2], dtype="uint8")
        cv2.circle(mask, (cX, cY), 20, 255, -1)     # 水波纹会影响。。。
        
        mask = cv2.erode(mask, None, iterations=2)  # 对上文得到的边缘进行erode，能成功模糊掉规定区域之外的部分，使得mask能成功保留下contour内区域
        # cv2.imshow("mask", mask)
        # cv2.waitKey(0)

        mean = cv2.mean(image, mask=mask)[:3]   # 求image由mask罩起来的区域内的颜色平均值

        # 但是我们不要黑色色块。。

        #print(f"mean={mean}")
        i = 0
        for (l, r) in self.colors:
            #print(f"l={l}, r={r}")
            if mean[0] >= l[0] and mean[1] >= l[1] and mean[2] >= l[2] and mean[0] <= r[0] and mean[1] <= r[1] and mean[2] <= r[2]:
                break
            i += 1
        if i >= len(self.colorNames):
            #print("hehe")
            return "undefined"
        return self.colorNames[i]
    
    # 逻辑已经修正了
    def detect_color(self, image, cX, cY):
        # 得有 目标中心点 才能知道是否有识别出的足够大的对象
        # 然后基于我们有识别出 足够大的对象，我们就能求出它的颜色
        #   即 这个版本没有让黑色色块参与平均值的计算
        if cX == -1 or cY == -1:
            return "undefined"

        circle_mask = np.zeros(image.shape[:2], dtype="uint8")
        cv2.circle(circle_mask, (cX, cY), 30, 255, -1)     # 此时取的圆的大小 只会影响 运算速度，至少只要你能识别到对象并把中心传进来，那它就能成功识别出颜色
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # 灰度图作为mask
        nonzeros_mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)[1]   # 此时不暗的就是我们要的

        mask = cv2.bitwise_and(circle_mask, nonzeros_mask)
        # 甚至erode都不需要了

        # cv2.imshow("nonzeros_mask", nonzeros_mask)
        # cv2.imshow("circle_mask", circle_mask)
        # cv2.imshow("mask", mask)
        # cv2.waitKey(0)
        mean = cv2.mean(image, mask=mask)[:3]   # 求image由mask罩起来的区域内的颜色平均值
        #print(f"mean={mean}")
        
        i = 0
        for (l, r) in self.colors:
            #print(f"l={l}, r={r}")
            if mean[0] >= l[0] and mean[1] >= l[1] and mean[2] >= l[2] and mean[0] <= r[0] and mean[1] <= r[1] and mean[2] <= r[2]:
                break
            i += 1
        if i >= len(self.colorNames):
            #print("hehe")
            return "undefined"
        return self.colorNames[i]
