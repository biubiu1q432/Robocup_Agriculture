#!/usr/bin/python3
import os
import time
import numpy as np
import threading as th
from Modules import const
from Modules.Camera import *
from Modules.Bridge import *
from Modules.SocketClient import *


'''
    注释掉的部分有些可以看看，当然这版是最终上赛场的版本
    色域都是在现场用手动调试脚本手调出来的的，本人曾尝试过写一个自动化脚本进行色域的筛选，大体逻辑应该是没问题，但是我对其效果的稳定性持怀疑态度（能做到大致正确但没能做到完全正确）
    如果想看看或者想尝试优化的话可以再找我要，如果觉得我写得过于答辩不如你自己想到的解决方案则请无视我上面的这句话(
    
    源码就不给解释了，相信视觉处理那块你能看懂的（哪里看不太明白可以再问我

    以及后边可以试着重构一下这套代码，让其能兼容ROS2之类的，当作是ROS2的应用练习了，想试试的可以试试
'''


Option = {
    "Arm_Serial": {"port": "/dev/arm", "baudrate": 115200},
    "Car_Serial": {"port": "/dev/car", "baudrate": 115200},
}
#配置通讯串口

# l_colors = [
#     #([45, 146, 152], [213, 190, 205]),    # 成熟色 —— left用
#     ([45, 135, 152], [255, 190, 205]),    # 成熟色 —— left用_融合室外
#     ([27, 100, 137], [152, 119, 166]),     # 未成熟色 —— left用
# ]	# 需要检测到的颜色
# r_colors = [
#     #([59, 140, 106], [213, 190, 199]),     # 成熟色 —— right用
#     #([36, 140, 106], [213, 255, 199]),     # 成熟色 —— right用_融合室外
#     #([0, 153, 160], [202, 200, 203]),     # 成熟色 —— right用，关闭白平衡且设为5850；室内，尚未室外
#     ([0, 153, 140], [202, 210, 203]),     # 成熟色 —— right用，关闭白平衡且设为5850；结合室外
#     #([27, 100, 105], [114, 125, 159]),     # 未成熟色 —— right用
#     #([0, 94, 104], [114, 124, 159]),     # 未成熟色 —— right用_融合室外
#     #([0, 95, 129], [128, 122, 180]),     # 未成熟色 —— right用，关闭白平衡且设为5850；室内，尚未室外
#     #([0, 94, 104], [255, 122, 183]),     # 未成熟色 —— right用，关闭白平衡且设为5850；结合室外
#     ([0, 94, 130], [174, 126, 172]),     # 未成熟色 —— right用，关闭白平衡且设为5850；结合室外2
# ]

# 红、绿 —— 只用于进行成熟度判断，需要区分颜色

# # lab
# colors = [
#     ([45, 142, 130], [255, 190, 205]),  # 红
# 	#([55, 103, 115], [180, 125, 166]),  # 绿
# 	([0, 0, 0], [187, 120, 163]),  # 绿
# ]
# filtered_colors = [
    
# ]


# hsv
colors = [
    # #([42,14,0],[245,255,185]),  # 绿
	# #([42,14,60],[255,255,110]),  # 绿（天亮一上午高亮）
	# #([42,14,0],[255,255,82]),  # 绿（天亮一中亮）
	# ([42,30,80],[245,255,185]),  # 绿 —— 实验室，靠谱 —— 所以一部分意外色块是因为S轴的l太小了所以才没能滤掉？

    # ([0,92,0],[22,255,255]),    # 红（实验室内也可用）
    # #([0,92,0],[20,255,255]),    # 红（反光地毯？天亮？）

    # #专项赛现场
    # #([37,30,30],[245,255,185]),     # 普通绿色
    # ([28,30,30],[245,156,150]),     # 三种绿色都有
    # ([0,92,0],[22,255,255]),    # 红色

    # 国赛现场
    ([40,61,72],[70,255,255]),     # 绿色
    ([0,141,170],[22,255,255]),     # 橙色场上
    #([0,92,110],[30,255,255]),     # 橙色场下
]
filtered_colors = [
    
]


colorNames = [
    "green", # unripe
    "red",  # ripe
]



# 红、绿、白  —— 只用于进行微调，只要目标，不用区分颜色 —— 所以 是使用detect_color_onedetect
# check_corrected_colors = [
#     ([0, 153, 140], [202, 210, 203]),     # 成熟色 —— right用，关闭白平衡且设为5850；结合室外（还挺稳的，这么多情况都能用。。。）
#     #([0, 94, 130], [174, 126, 172]),     # 未成熟色 —— right用，关闭白平衡且设为5850；结合室外2
#     #([0, 94, 130], [174, 117, 180]),     # 未成熟色 —— right用，关闭白平衡且设为5850 —— 光从前向后，挺近的
#     ([0, 94, 130], [174, 121, 180]),     # 未成熟色 —— right用，关闭白平衡且设为5850 —— 白天，但只是改了一个更大的范围而已，要是这个范围晚上也能用的话那就直接用这个就行了
#     #([138, 113, 104], [255, 130, 151]),     # 白色（框&爪子，但爪子是不要的）
#     ([138, 113, 104], [255, 165, 151]),     # 白色（框&爪子，但爪子是不要的） —— 白天，但只是改了一个更大的范围而已，要是这个范围晚上也能用的话那就直接用这个就行了
# ]


# # lab
# check_corrected_colors = [
#     ([45, 142, 130], [255, 190, 205]),
# 	#([55, 103, 115], [180, 125, 166]),
#     ([0, 0, 0], [187, 120, 163]),
# 	([105, 126, 101], [255, 146, 135]),
# ]
# check_corrected_filtered_colors = [

# ]

# hsv
check_corrected_colors = [
    # #([42,14,0],[245,255,185]),  # 绿
	# #([42,14,60],[255,255,110]),  # 绿（天亮一上午高亮）
	# #([42,14,0],[255,255,82]),  # 绿（天亮一中亮）
	# ([42,30,80],[245,255,185]),  # 绿 —— 实验室，靠谱 —— 所以一部分意外色块是因为S轴的l太小了所以才没能滤掉？

    # ([0,92,0],[22,255,255]),    # 红（实验室内也可用）
    # #([0,92,0],[20,255,255]),    # 红（反光地毯？天亮？）


    

	# #([70,0,136],[255,28,255]),  # 白
	# #([0,0,250],[255,27,255]),  # 白 —— 高亮
    # ([0,0,245],[255,70,255]),  # 白 —— 中亮
    # #([0,0,252],[255,70,255]),  # 白 —— 实验室内亮度

    # # 专项赛现场
    # #([37,30,30],[245,255,185]),     # 普通绿色
    # ([28,30,30],[245,156,150]),     # 三种绿色都有
    # ([0,92,0],[22,255,255]),    # 红色
    # ([50,0,230],[255,16,255]),   # 白色

    # 国赛现场
    ([40,61,72],[70,255,255]),     # 绿色
    ([0,141,170],[22,255,255]),     # 橙色
    # 国赛逻辑没用到白色
]
check_corrected_filtered_colors = [

]


# 画面切割
rois = [
    #(0,0,242,112),  # 左侧的roi（640x480）
    #(372,0,268,107),  # 右侧的roi(640x480)

    # (0,0,783,251),  # 左侧roi(1920x1080)
    # (1079,0,841,245),   # 右侧roi(1920x1080)

    # # 新roi
    # (0,0,783,320),  # 左侧roi(1920x1080)
    # (1079,0,841,325),   # 右侧roi(1920x1080)

    # 现场
    (0,0,870,378),  # 左侧roi(1920x1080)
    (1207,0,713,373),  # 右侧roi(1920x1080)
]
roiNames = [
    "left",
    "right",
]



class Robot():
    def __init__(self): # 这里 对值进行init
        self.arm_bridge = Arm_Bridge() # 机械臂通讯桥
        self.car_bridge = Car_Bridge() # 底盘通讯桥

        self.socket_client = SocketClient()
        

        self.camera = Camera("top")



        self.__big_step = -0.39   # 果间运动竖直距离
        self.__side_step = 0.04     # 左右偏移用距离

        self.monitor_round_cnt = -1  # 第几轮monitor的判断，初始化为-1是因为打开摄像头的时候需要开启一下


        # 不同情况进入不同的分支（一共就九种情况嘛），一个决策分支用一个元组表示
        self.__decisions_no_new_sideway = (
            (
                #   -1 -1
                (
                    {'action': self.car_bridge.go_distance, 'args': (self.__big_step,), 'time': 1.3},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((1, 1),(1, 1), 1), 'time': 1.8},

                    #{'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(0, 0), 1), 'time': 1.8},

                    #{'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(2, 2), 1), 'time': 0.6},
                ),
                #   -1 0 —— 左无右生
                (
                    {'action': self.car_bridge.go_distance, 'args': (self.__big_step,), 'time': 1.3},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((1, 1),(1, 1), 1), 'time': 1.8},

                    # {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(0, 0), 1), 'time': 1.8},

                    # {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(2, 2), 1), 'time': 0.6},
                ),
                #   -1 1 —— 左无右熟
                (
                    {'action': self.car_bridge.go_distance, 'args': (self.__big_step,), 'time': 1.3},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(0, 0), 0), 'time': 1.8},
                     
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 1),(0, 0), 0), 'time': 0.2},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 1),(0, 0), 1), 'time': 1.8},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 1),(2, 1), 1), 'time': 1},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(2, 1), 1), 'time': 0.2},

                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(2, 2), 1), 'time': 0.6},
                ),
            ),
            (
                #   0 -1 —— 左生右无
                (
                    {'action': self.car_bridge.go_distance, 'args': (self.__big_step,), 'time': 1.3},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((1, 1),(1, 1), 1), 'time': 1.8},

                    # {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(0, 0), 1), 'time': 1.8},

                    # {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(2, 2), 1), 'time': 0.6}, 
                ),
                #   0 0 —— 左生右生
                (
                    {'action': self.car_bridge.go_distance, 'args': (self.__big_step,), 'time': 1.3},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((1, 1),(1, 1), 1), 'time': 1.8},

                    # {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(0, 0), 1), 'time': 1.8},

                    # {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(2, 2), 1), 'time': 0.6},
                ),
                #   0 1 —— 左生右熟
                (
                    {'action': self.car_bridge.go_distance, 'args': (self.__big_step,), 'time': 1.3},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(0, 0), 0), 'time': 1.8},
                     
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 1),(0, 0), 0), 'time': 0.2},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 1),(0, 0), 1), 'time': 1.8},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 1),(2, 1), 1), 'time': 1},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(2, 1), 1), 'time': 0.2},

                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(2, 2), 1), 'time': 0.6},
                ),
            ),
            (
                #   1 -1 —— 左熟右无
                (
                    {'action': self.car_bridge.go_distance, 'args': (self.__big_step,), 'time': 1.3},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(0, 0), 0), 'time': 1.8},
                     
                    {'action': self.arm_bridge.arm_cmd, 'args': ((1, 0),(0, 0), 0), 'time': 0.2},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((1, 0),(0, 0), 1), 'time': 1.8},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((1, 0),(1, 2), 1), 'time': 1},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(1, 2), 1), 'time': 0.2},

                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(2, 2), 1), 'time': 0.6},
                ),
                #   1 0 —— 左熟右生
                (
                    {'action': self.car_bridge.go_distance, 'args': (self.__big_step,), 'time': 1.3},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(0, 0), 0), 'time': 1.8},
                     
                    {'action': self.arm_bridge.arm_cmd, 'args': ((1, 0),(0, 0), 0), 'time': 0.2},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((1, 0),(0, 0), 1), 'time': 1.8},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((1, 0),(1, 2), 1), 'time': 1},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(1, 2), 1), 'time': 0.2},

                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(2, 2), 1), 'time': 0.6},
                ),
                #   1 1 —— 左熟右熟
                (
                    {'action': self.car_bridge.go_distance, 'args': (self.__big_step,), 'time': 1.3},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(0, 0), 0), 'time': 1.8},
                     
                    {'action': self.arm_bridge.arm_cmd, 'args': ((1, 1),(0, 0), 0), 'time': 0.2},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((1, 1),(0, 0), 1), 'time': 1.8},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((1, 1),(1, 1), 1), 'time': 1},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(1, 1), 1), 'time': 0.2},

                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(2, 2), 1), 'time': 0.6},
                ),
            ),
        )


        self.__decisions = (
            (
                #   -1 -1
                (
                    {'action': self.__align_vector_fuzzy, 'args': (), 'time': 0},
                    {'action': self.__start_reset_is_move_thread, 'args': (), 'time': 3},
                    #{'action': self.car_bridge.yaw_adjustment, 'args': (self.car_bridge.log_vector_angle,), 'time': 0.2},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((1, 1),(1, 1), 1), 'time': 3.5},   # 原1.8

                    #{'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(0, 0), 1), 'time': 1.8},

                    #{'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(2, 2), 1), 'time': 0.6},
                ),
                #   -1 0 —— 左无右生
                (
                    {'action': self.__align_vector_fuzzy, 'args': (), 'time': 0},
                    {'action': self.__start_reset_is_move_thread, 'args': (), 'time': 3},
                    #{'action': self.car_bridge.yaw_adjustment, 'args': (self.car_bridge.log_vector_angle,), 'time': 0.2},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((1, 1),(1, 1), 1), 'time': 3.5},   # 原1.8

                    # {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(0, 0), 1), 'time': 1.8},

                    # {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(2, 2), 1), 'time': 0.6},
                ),
                #   -1 1 —— 左无右熟
                (
                    {'action': self.__align_vector_fuzzy, 'args': (), 'time': 0},
                    {'action': self.__start_reset_is_move_thread, 'args': (), 'time': 3},
                    #{'action': self.car_bridge.yaw_adjustment, 'args': (self.car_bridge.log_vector_angle,), 'time': 0.2},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(0, 0), 0), 'time': 3.5},   # 原1.8
                     
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 1),(0, 0), 0), 'time': 0.2},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 1),(0, 0), 1), 'time': 1.8},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 1),(2, 1), 1), 'time': 1},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(2, 1), 1), 'time': 0.2},

                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(2, 2), 1), 'time': 0.6},
                ),
            ),
            (
                #   0 -1 —— 左生右无
                (
                    {'action': self.__align_vector_fuzzy, 'args': (), 'time': 0},
                    {'action': self.__start_reset_is_move_thread, 'args': (), 'time': 3},
                    #{'action': self.car_bridge.yaw_adjustment, 'args': (self.car_bridge.log_vector_angle,), 'time': 0.2},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((1, 1),(1, 1), 1), 'time': 3.5},   # 原1.8

                    # {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(0, 0), 1), 'time': 1.8},

                    # {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(2, 2), 1), 'time': 0.6}, 
                ),
                #   0 0 —— 左生右生
                (
                    {'action': self.__align_vector_fuzzy, 'args': (), 'time': 0},
                    {'action': self.__start_reset_is_move_thread, 'args': (), 'time': 3},
                    #{'action': self.car_bridge.yaw_adjustment, 'args': (self.car_bridge.log_vector_angle,), 'time': 0.2},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((1, 1),(1, 1), 1), 'time': 3.5},   # 原1.8

                    # {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(0, 0), 1), 'time': 1.8},

                    # {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(2, 2), 1), 'time': 0.6},
                ),
                #   0 1 —— 左生右熟
                (
                    {'action': self.__align_vector_fuzzy, 'args': (), 'time': 0},
                    {'action': self.__start_reset_is_move_thread, 'args': (), 'time': 3},
                    #{'action': self.car_bridge.yaw_adjustment, 'args': (self.car_bridge.log_vector_angle,), 'time': 0.2},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(0, 0), 0), 'time': 3.5},   # 原1.8
                     
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 1),(0, 0), 0), 'time': 0.2},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 1),(0, 0), 1), 'time': 1.8},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 1),(2, 1), 1), 'time': 1},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(2, 1), 1), 'time': 0.2},

                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(2, 2), 1), 'time': 0.6},
                ),
            ),
            (
                #   1 -1 —— 左熟右无
                (
                    {'action': self.__align_vector_fuzzy, 'args': (), 'time': 0},
                    {'action': self.__start_reset_is_move_thread, 'args': (), 'time': 3},
                    #{'action': self.car_bridge.yaw_adjustment, 'args': (self.car_bridge.log_vector_angle,), 'time': 0.2},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(0, 0), 0), 'time': 3.5},   # 原1.8
                     
                    {'action': self.arm_bridge.arm_cmd, 'args': ((1, 0),(0, 0), 0), 'time': 0.2},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((1, 0),(0, 0), 1), 'time': 1.8},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((1, 0),(1, 2), 1), 'time': 1},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(1, 2), 1), 'time': 0.2},

                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(2, 2), 1), 'time': 0.6},
                ),
                #   1 0 —— 左熟右生
                (
                    {'action': self.__align_vector_fuzzy, 'args': (), 'time': 0},
                    {'action': self.__start_reset_is_move_thread, 'args': (), 'time': 3},
                    #{'action': self.car_bridge.yaw_adjustment, 'args': (self.car_bridge.log_vector_angle,), 'time': 0.2},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(0, 0), 0), 'time': 3.5},   # 原1.8
                     
                    {'action': self.arm_bridge.arm_cmd, 'args': ((1, 0),(0, 0), 0), 'time': 0.2},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((1, 0),(0, 0), 1), 'time': 1.8},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((1, 0),(1, 2), 1), 'time': 1},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(1, 2), 1), 'time': 0.2},

                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(2, 2), 1), 'time': 0.6},
                ),
                #   1 1 —— 左熟右熟
                (
                    {'action': self.__align_vector_fuzzy, 'args': (), 'time': 0},
                    {'action': self.__start_reset_is_move_thread, 'args': (), 'time': 3},
                    #{'action': self.car_bridge.yaw_adjustment, 'args': (self.car_bridge.log_vector_angle,), 'time': 0.2},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(0, 0), 0), 'time': 3.5},   # 原1.8
                     
                    {'action': self.arm_bridge.arm_cmd, 'args': ((1, 1),(0, 0), 0), 'time': 0.2},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((1, 1),(0, 0), 1), 'time': 1.8},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((1, 1),(1, 1), 1), 'time': 1},
                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(1, 1), 1), 'time': 0.2},

                    {'action': self.arm_bridge.arm_cmd, 'args': ((0, 0),(2, 2), 1), 'time': 0.6},
                ),
            ),
        )


    def __reset_is_move_and_yawback(self):
        # while self.car_bridge.is_move == None:
        #     print("在__reset_is_move_and_yawback线程里")
        #     time.sleep(0.01)
        # self.car_bridge.is_move = None
        #print("真改成None了")
        self.car_bridge.yaw_adjustment(self.car_bridge.log_vector_angle, is_print=False)
        self.car_bridge.go_distance_atom(self.car_bridge.log_vector_distance, is_print=False)
        self.car_bridge.yaw_adjustment(-self.car_bridge.log_vector_angle, is_print=False)    # 顺便扭回来
    def __start_reset_is_move_thread(self):
        t = th.Thread(target=self.__reset_is_move_and_yawback)
        t.start()


    # 还是用之前的队列概率法 —— n次拍摄，n次判断
    # 可用
    def __monitor(self, show_wanted=False, save_wanted=True):    # FIXME:
        start = time.time()

        cnt = 0
        max_stable_size = 40
        ripe_cnt = [0, 0]
        unripe_cnt = [0, 0]
        novege_cnt = [0, 0]


        while cnt < max_stable_size:
            self.camera.clean_ROIs()
            self.camera.shoot(save_wanted=False)
            self.camera.screen_cutting(rois, roiNames)
            for i in range(len(self.camera.ROIs)):
                self.camera.ROIs[i].check(colors, filtered_colors, colorNames, no_edge=False, show_wanted=show_wanted)    # 因为是同一个画面，所以用同一套颜色阈值
                ripe_cnt[i] = ripe_cnt[i] + 1 if self.camera.ROIs[i].is_ripe == const.RIPE else ripe_cnt[i]
                unripe_cnt[i] = unripe_cnt[i] + 1 if self.camera.ROIs[i].is_ripe == const.UNRIPE else unripe_cnt[i]
                novege_cnt[i] = novege_cnt[i] + 1 if self.camera.ROIs[i].is_ripe == const.NOVEGE else novege_cnt[i]
            cnt += 1
        
        
        # 保存本次检测中最后一张采集到的图片
        if save_wanted:
            if self.monitor_round_cnt != -1:
                # 保存filtered_images
                if self.camera.ROIs[0].roi_filtered_frame is not None:
                    cv2.imwrite(f"filtered_images_save/left/{self.monitor_round_cnt}_{self.camera.ROIs[0].is_ripe}.jpg", self.camera.ROIs[0].roi_filtered_frame)
                else:
                    print(f"{self.monitor_round_cnt}号检测 left 接收不到roi_filtered_frame")
                if self.camera.ROIs[1].roi_filtered_frame is not None:
                    cv2.imwrite(f"filtered_images_save/right/{self.monitor_round_cnt}_{self.camera.ROIs[1].is_ripe}.jpg", self.camera.ROIs[1].roi_filtered_frame)
                else:
                    print(f"{self.monitor_round_cnt}号检测 right 接收不到roi_filtered_frame")
                
                # 保存raw_images
                if self.camera.ROIs[0].roi_frame is not None:
                    cv2.imwrite(f"raw_images_save/left/{self.monitor_round_cnt}_{self.camera.ROIs[0].is_ripe}.jpg", self.camera.ROIs[0].roi_frame)
                else:
                    print(f"{self.monitor_round_cnt}号检测 left 接收不到roi_frame")
                if self.camera.ROIs[1].roi_frame is not None:
                    cv2.imwrite(f"raw_images_save/right/{self.monitor_round_cnt}_{self.camera.ROIs[1].is_ripe}.jpg", self.camera.ROIs[1].roi_frame)
                else:
                    print(f"{self.monitor_round_cnt}号检测 right 接收不到roi_frame")
            self.monitor_round_cnt += 1
        
            
        for i in range(len(self.camera.ROIs)):
            print(f"看看 {roiNames[i]} 识别具体结果{(ripe_cnt[i], unripe_cnt[i], novege_cnt[i])}")
            if ripe_cnt[i] > unripe_cnt[i] and ripe_cnt[i] >= max_stable_size / 2:
                self.camera.ROIs[i].is_ripe = const.RIPE
            elif ripe_cnt[i] <= unripe_cnt[i] and unripe_cnt[i] >= max_stable_size / 2:
                self.camera.ROIs[i].is_ripe = const.UNRIPE
            else:
                self.camera.ROIs[i].is_ripe = const.NOVEGE

        end = time.time()

        for i in range(0, len(self.camera.ROIs)):
            print(f">>> {roiNames[i]} 蔬菜: {str(self.camera.ROIs[i].is_ripe)}")

        print(f'>>>> monitor视觉部分 耗时: {end - start}')





### 真正有用的基于视觉的微调 —— 与monitor对应
# 以后有时间再提取出Aligner
    # 可用
    def __align_monitor(self):
        # 拍摄+画面分割 —— 采用 n次拍摄，最后才一次判断 的策略
        max_stable_size = 40
        #start = time.time()
        self.camera.clean_ROIs()
        self.camera.shoot(max_stable_size, save_wanted=False)
        self.camera.screen_cutting(rois, roiNames)
        # 我们默认 idx=0表示左边，idx=1表示右边
        for i in range(0, len(self.camera.ROIs)):
            #self.camera.ROIs[i].check(check_corrected_colors, check_corrected_filtered_colors, no_edge=False)    # 因为是同一个画面，所以用同一套颜色阈值
            self.camera.ROIs[i].check(colors, filtered_colors, no_edge=False)    # 现在不需要白框
            #print(f"roi_{i}: 图像={self.camera.ROIs[i].roi_frame}, 成熟度={self.camera.ROIs[i].is_ripe}, 中心坐标={self.camera.ROIs[i].obj_center_coord}, 尺寸={self.camera.ROIs[i].obj_shape}")
        #end = time.time()
        #print(f'>>>> align视觉部分 耗时: {end - start}')




    def __align_vector_fuzzy(self):
        start = time.time()
        deflection_limit_px = 70    # 这个不用变

        if self.camera.ROIs[0].is_ripe != const.NOVEGE and self.camera.ROIs[1].is_ripe != const.NOVEGE:

            #car_mid_x_px = 1043   # 中线（需要调）
            #car_mid_x_px = 1055   # 中线（需要调），但摄像头摆平了之后大概就是这个位置
            #car_mid_x_px = 928   # 中线（需要调），但摄像头摆平了之后大概就是这个位置
            car_mid_x_px = 982   # 国赛现场

            self.__align_monitor()
            l_roi, r_roi = self.camera.ROIs[0], self.camera.ROIs[1]
            if l_roi.obj_center_coord[0] == -1 or r_roi.obj_center_coord[0] == -1:
                print("它左右fuzzy调 寄了")
                return
            print(rois[0][0], rois[1][0])
            l_obj_cx, r_obj_cx = l_roi.obj_center_coord[0] + rois[0][0], r_roi.obj_center_coord[0] + rois[1][0]
            print(f"l_roi的目标中心点={l_obj_cx}, r_roi的目标中心点={r_obj_cx}")
            now_mid_x_px = (l_obj_cx + r_obj_cx)/2
            print(f"我的now_mid_x_px为 {now_mid_x_px}")
            if now_mid_x_px - car_mid_x_px >= deflection_limit_px:
                self.car_bridge.go_vector(self.__big_step, -self.__side_step)
                print(f"有 carmid:{car_mid_x_px} - nowmid:{now_mid_x_px} = {car_mid_x_px - now_mid_x_px}; 因 now_mid_x在 car_mid_x的左边 偏移{now_mid_x_px - car_mid_x_px}个px，故向右边走了4cm", end="，以及 ")
            elif car_mid_x_px - now_mid_x_px >= deflection_limit_px:
                self.car_bridge.go_vector(self.__big_step, self.__side_step)
                print(f"有 carmid:{car_mid_x_px} - nowmid:{now_mid_x_px} = {car_mid_x_px - now_mid_x_px}; 因 now_mid_x在 car_mid_x的右边 偏移{car_mid_x_px - now_mid_x_px}个px，故向左边走了4cm", end="，以及 ")
            else:
                self.car_bridge.go_vector(self.__big_step, 0)
                print("单纯直走 完毕")
            print("左右大概调 完毕")
        else:
            self.car_bridge.go_vector(self.__big_step, 0)
            print("单纯直走 完毕")
        end = time.time()
        print(f"向量模糊调 耗时: {end - start} s")

    def go_start_color(self):   # 拿来测试用的一个函数，不用管这个函数，主逻辑里没有用到它

        self.__align_vector_fuzzy()
        #self.arm_bridge.arm_cmd((0,0),(0,0),0)
        #time.sleep(2)
        # self.arm_bridge.arm_cmd((1,1),(0,0),0)
        # time.sleep(2)

        time.sleep(10000)



        # self.arm_bridge.arm_cmd((1,1),(0,0),0)
        # time.sleep(0.2)
        # self.arm_bridge.arm_cmd((1,1),(0,0),1)
        # time.sleep(2)
        # self.arm_bridge.arm_cmd((1,1),(1,1),1)
        # time.sleep(2)
        # self.arm_bridge.arm_cmd((0,0),(1,1),1)
        # time.sleep(0.2)
        # self.arm_bridge.arm_cmd((0,0),(0,0),1)

        # time.sleep(10000)

        #self.__monitor()

        # while True:
        #     self.arm_bridge.arm_cmd((0,1),(0,0),0)
        #     time.sleep(3)
        #     self.arm_bridge.arm_cmd((0,1),(0,0),1)
        #     time.sleep(3)

        # self.car_bridge.go_distance_atom(0.39)
        # time.sleep(10000)


        # self.change_track()
        # self.car_bridge.go_distance_atom(-0.39)


        #self.car_bridge.go_distance_atom(0.39)

        #self.__align()

        # for _ in range(5):
        #     self.car_bridge.go_distance_atom(-0.39)
        #     time.sleep(1)
        
        # self.car_bridge.go_distance_atom(0.39)
        # self.car_bridge.go_distance_atom(0.39)
        # self.car_bridge.go_distance_atom(0.39)
        # self.car_bridge.go_distance_atom(0.39)
        # self.car_bridge.go_distance_atom(0.39)

        # self.car_bridge.go_distance_atom(0.39)

        # self.arm_bridge.arm_cmd((0,0),(0,0),0)
        # time.sleep(2)

        # self.__monitor()    # 先激活一下摄像头
        self.go_start()
        time.sleep(10000)
        
        self.change_track()
        time.sleep(10000)

        # for _ in range(5):
        #     print('\n' + '=== do ===')
        #     self.__monitor()
        #     dicision = self.__decisions[self.camera.ROIs[0].is_ripe + 1][self.camera.ROIs[1].is_ripe + 1]

        #     for i in range(len(dicision)):
        #         dicision[i]['action'](*dicision[i]['args'])
        #         time.sleep(dicision[i]['time'])



        #time.sleep(10000)


        # self.change_track()

        # time.sleep(10000)

        # for _ in range(5):
        #     self.car_bridge.go_distance_atom(-0.39)
        #     time.sleep(1)


        # self.car_bridge.go_distance_atom(-0.4)
        # self.car_bridge.go_distance_atom(0.39*5 + 0.9)
        # # 确保落在框内
        # self.car_bridge.yaw_adjustment(-90)
        # self.car_bridge.go_distance_atom(0.05)
        

        # time.sleep(10000)


        # while True:
        #     self.arm_bridge.arm_cmd((0,1),(0,0),0)
        #     time.sleep(2.5)
        #     self.arm_bridge.arm_cmd((1,1),(0,0),0)
        #     time.sleep(0.5)
        #     self.arm_bridge.arm_cmd((1,1),(0,0),1)
        #     time.sleep(1.8)
        #     self.arm_bridge.arm_cmd((1,1),(1,1),1)
        #     time.sleep(1.4)
        #     self.arm_bridge.arm_cmd((0,1),(1,1),1)
        #     time.sleep(0.5)
        #     self.arm_bridge.arm_cmd((0,0),(2,2),1)
        #     time.sleep(1)


        # self.__align_monitor()

        # #self.__align_yaw()
        # self.__align_sideway()        

        time.sleep(1000000)

    # 以下这仨是没用到十字标对齐的，还挺准
    def go_start(self):

        # # 测联调的通信用的
        # print("man what can i say")
        # time.sleep(1000)

        # #测试微调相机
        # self.__corrected_monitor()
        # self.l_side.c2w.show()
        # self.r_side.c2w.show()
        # time.sleep(1000)

        # self.arm_bridge.arm_cmd((1,1),(0,0),1)
        # time.sleep(2)
        # self.arm_bridge.arm_cmd((0,0),(0,0),1)
        # time.sleep(0.2)
        # self.arm_bridge.arm_cmd((0,0),(0,0),0)
        # time.sleep(1.4)
        #time.sleep(1000)

        # self.arm_bridge.arm_cmd((1,1),(0,0),1)
        # time.sleep(1.4)
        # self.arm_bridge.arm_cmd((1,1),(1,1),1)
        # time.sleep(2)


        # 到时是从A区起点走到C区起点的，得保证小车投影落在框内，然后从C区起始位置开始进行微调
        #self.car_bridge.go_distance_atom(-2.17)     # 自建图的距离
        self.car_bridge.go_distance_atom(-2.19)     # 自建图的距离(with 充电宝在前)
        #self.car_bridge.go_distance_atom(-2.02)    # 专项赛没问题的距离
        #self.car_bridge.go_distance_atom(-2.04)    # 专项赛没问题的距离 + 充电宝
        self.car_bridge.yaw_adjustment(-90)
        #self.car_bridge.go_sideway(-0.04, mode=0)
        #self.car_bridge.go_distance_atom(-0.9)
  	#self.car_bridge.go_distance_atom(-0.45)     # 自建图的距离
        self.car_bridge.go_distance_atom(-0.49)     # 新测自建图的距离
        #self.car_bridge.go_distance_atom(-0.53)     # 专项赛没问题的距离

        ## 让它走回去
        # self.car_bridge.go_distance_atom(0.87)
        # self.car_bridge.yaw_adjustment(90)
        # self.car_bridge.go_distance_atom(2.17)


#   YES I CHANGED IT
        # self.arm_bridge.arm_cmd((1,1),(0,0),1)
        # time.sleep(2)
        # self.arm_bridge.arm_cmd((0,0),(0,0),1)
        # time.sleep(0.2)
        # self.arm_bridge.arm_cmd((0,0),(0,0),0)
        # time.sleep(1.4)


        #time.sleep(1000)
        print('>从起点走到本道一开始')



        ## ori_start
        # self.car_bridge.go_sideway(-0.04, mode=0)
        # self.car_bridge.go_distance_atom(-0.73)
        # print('>从起点走到本道一开始')
        
        

    def change_track(self):     # 记得改距离
        print('>> 换道')
        self.car_bridge.is_move = None  # 因为go_distance不是go_distance_atom，故需要手动改is_move
        self.car_bridge.go_distance_atom(self.__big_step+(-0.04))
        self.car_bridge.yaw_adjustment(90)
        #self.car_bridge.go_distance_atom(-1.01)     # 地图变化了得调
        self.car_bridge.go_distance_atom(-0.99)     # 地图变化了得调
        self.car_bridge.yaw_adjustment(90)
        #self.car_bridge.go_distance_atom(-0.4)
        #self.car_bridge.go_distance_atom(-0.42)
        

    def go_end(self):
        print('>去往收集区，现在改在D区了')
        self.car_bridge.is_move = None
        self.car_bridge.go_distance_atom(-0.85)  # tested
        self.arm_bridge.arm_cmd((1,1),(0,0),1)
        time.sleep(1.4)
        self.arm_bridge.arm_cmd((1,1),(1,1),1)
        time.sleep(2)
        self.car_bridge.yaw_adjustment(-90)
        self.car_bridge.go_distance_atom(-2.70)  # tested

        time.sleep(5)   # 小车移到终点的延时
        self.socket_client.arrive_end = 1
        time.sleep(2)


        ## 专项赛地图
        # print('>去往另一边的收集区')
        # self.car_bridge.is_move = None
        # self.car_bridge.go_distance_atom(-0.4)
        # self.arm_bridge.arm_cmd((1,1),(0,0),1)
        # time.sleep(1.4)
        # self.arm_bridge.arm_cmd((1,1),(1,1),1)
        # time.sleep(2)
        # self.car_bridge.go_distance_atom(0.39*5 + 0.9)
        # # 确保落在框内
        # self.car_bridge.yaw_adjustment(-90)
        # self.car_bridge.go_distance_atom(0.05)

        # time.sleep(5)   # 小车移到终点的延时
        # self.socket_client.arrive_end = 1
        # time.sleep(2)


        ##ori_end
        # print('>去往另一边的收集区')
        # self.car_bridge.go_distance_atom(-0.45)
        # self.arm_bridge.arm_cmd((0,0),(1,1),1)
        # time.sleep(4)
        # self.car_bridge.yaw_adjustment(90)
        # time.sleep(10)



    def init(self):
        # # 用v4l2-ctl预先设置摄像头的白平衡相关东西
        # #os.system('v4l2-ctl --device /dev/video_left --set-ctrl white_balance_automatic=1')
        # print("已打开left的自动白平衡")
        # #os.system('v4l2-ctl --device /dev/video_left --set-ctrl white_balance_temperature=417')
        # print("已调节left的白平衡为417")
        # os.system('v4l2-ctl --device /dev/video_right --set-ctrl white_balance_automatic=0')
        # print("已关闭right的自动白平衡")
        # os.system('v4l2-ctl --device /dev/video_right --set-ctrl white_balance_temperature=5850')
        # print("已调节right的白平衡为5850")

        #os.system('v4l2-ctl --device /dev/video_top --set-ctrl brightness=255')
        print("已调节top的亮度为 255")



        '''
            摄像头需要的预先处理：
                1、画面分辨率 —— 尽可能大
                2、视频输出格式 MJPG
                3、关闭自动对焦，并将对焦值调成32
        '''




        # 初始化串口通讯桥
        self.arm_bridge.init(Option)
        self.car_bridge.init(Option)
        # 开启 偏转角接收 线程
        self.car_bridge.run_thread()
        # socket客户端功能启动 线程
        self.socket_client.run_thread()

        # 创建存储左右filtered图像的文件夹
        if not os.path.exists("filtered_images_save"):
            if not os.path.exists("filtered_images_save/left"):
                os.makedirs("filtered_images_save/left")
            if not os.path.exists("filtered_images_save/right"):
                os.makedirs("filtered_images_save/right")
        
        # 创建存储左右raw图像的文件夹
        if not os.path.exists("raw_images_save"):
            if not os.path.exists("raw_images_save/left"):
                os.makedirs("raw_images_save/left")
            if not os.path.exists("raw_images_save/right"):
                os.makedirs("raw_images_save/right")

    def run(self):
        self.init()
        print("我真开始了")
        for track_no in range(3):
            if track_no == 2:
                self.go_end()
                break
            elif track_no == 1:
                self.change_track()
                #self.__align_sideway_fuzzy()
                #self.__align()
            elif track_no == 0:
                self.__monitor()    # 先激活一下摄像头
                self.go_start()

            for _ in range(5):
                print('\n' + '=== do ===')
                self.__monitor()
                dicision = self.__decisions[self.camera.ROIs[0].is_ripe + 1][self.camera.ROIs[1].is_ripe + 1]

                for i in range(len(dicision)):
                    dicision[i]['action'](*dicision[i]['args'])
                    time.sleep(dicision[i]['time'])



#  到时看看整个流程的go_distance有没有问题
#   包括 start、change_track、end ！确保画面都在视野内！
    # 每次抓一对蔬菜都进行一次对齐
    def run_1(self):   # 逻辑没问题，可直接用于测试
        self.init()
        for track_no in range(3):
            if track_no == 2:
                self.go_end()
            elif track_no == 1:
                self.change_track()
            elif track_no == 0:
                self.__monitor()    # 先激活一下摄像头
                self.go_start()

            for _ in range(5):
                print('\n' + '=== do ===')
                self.__align()      # 按理来说是会放在这里的
                self.__monitor()
                # 默认rois[0]是左roi，rois[1]是右roi
                dicision = self.__decisions[self.camera.ROIs[0].is_ripe + 1][self.camera.ROIs[1].is_ripe + 1]

                for i in range(len(dicision)):
                    dicision[i]['action'](*dicision[i]['args'])
                    time.sleep(dicision[i]['time'])


    # 仍然是 每次到 道头才进行一次检测，共两次检测
    def run_2(self):   # 逻辑没问题，可直接用于测试
        self.init()
        for track_no in range(3):
            if track_no == 2:
                self.go_end()
            elif track_no == 1:
                self.change_track()
                self.__align()
            elif track_no == 0:
                self.__monitor()    # 先激活一下摄像头
                self.go_start()
                self.__align()

            for _ in range(5):
                print('\n' + '=== do ===')
                self.__monitor()
                # 默认rois[0]是左roi，rois[1]是右roi
                dicision = self.__decisions[self.camera.ROIs[0].is_ripe + 1][self.camera.ROIs[1].is_ripe + 1]

                for i in range(len(dicision)):
                    dicision[i]['action'](*dicision[i]['args'])
                    time.sleep(dicision[i]['time'])


# 树莓派的用户名:gintama
# 密码也是gintama
# 预配置preconfig.sh这部分记得根据实际情况改一下路径
def env_preconfig():
    user_password = 'gintama'
    os.system('echo %s | sudo -S chmod 777 preconfig.sh' % (user_password))
    os.system('echo %s | sudo -S ./preconfig.sh' % (user_password))


if __name__ == '__main__':
    env_preconfig()
    robot = Robot()
    robot.run()
