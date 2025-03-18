#!/usr/bin/python3
import math
import serial
import time
import threading
import numpy as np


'''
    已经改过的Arm_Bridge，可以直接用的Arm
'''


# 一开始先 全部等到接收到指令执行完毕的串口消息 后再退出该动作函数（即暂时全标记为 原子动作，之后再看看需不需要去掉某些原子动作的标记）
# 之后实际调试的时候再看 哪些可以无需等到 接收到指令执行完毕的串口消息，再具体修改这些动作函数


class Arm_Bridge:
    def __init__(self):
        self.arm_ser: serial.Serial
        self.is_close = False
        self.count = 0
        self.__arm_state = [
            [
                0,      # 左腕抓否
                0,      # 右腕抓否
            ],
            [
                0,      # 左肘外内（外0内1）
                0,      # 右肘外内（外0内1）
            ],
            0       # 云台升降（降0升1）
        ]
        
    def __del__(self):
        try:
            self.arm_ser.close()
            print('成功关闭机械臂串口')
        except Exception as e:
            print('机械臂串口关闭失败:', e)


    def init(self, Option) -> bool:
        self.Option = Option

        try:
            self.arm_ser = serial.Serial(
                Option['Arm_Serial']['port'], Option['Arm_Serial']['baudrate']
            )
            if self.arm_ser.is_open == False:
                self.arm_ser.open()  # 打开串口
                self.is_close = False
            print("成功打开机械臂串口")
            self.arm_ser.flushInput()  # type: ignore
            return True
        except Exception as e:
            print("机械臂串口打开失败:", e)
            return False

    def arm_cmd(self, two_wrist, two_elbow, lift):
        # 生成指令用常数
        l_in_pwm = 730
        r_in_pwm = 2550
        l_ex_pwm = 1900
        r_ex_pwm = 1450
        l_mid_pwm = 1600   # 半内折
        r_mid_pwm = 1700   # 半内折
        up_lift_level = 10
        mid_lift_level = 7    # finish
        down_lift_level = 2
        # 生成指令
        #   左肘 三档位
        if two_elbow[0] == 0:
            l_elbow_cmd = l_ex_pwm
        elif two_elbow[0] == 1:
            l_elbow_cmd = l_in_pwm
        else:
            l_elbow_cmd = l_mid_pwm
        l_elbow_cmd = str(l_elbow_cmd).zfill(4)
        #   右肘 三档位
        if two_elbow[1] == 0:
            r_elbow_cmd = r_ex_pwm
        elif two_elbow[1] == 1:
            r_elbow_cmd = r_in_pwm
        else:
            r_elbow_cmd = r_mid_pwm
        r_elbow_cmd = str(r_elbow_cmd).zfill(4)
        #   升降 三档位
        if lift == 0:
            lift_cmd = down_lift_level
        elif lift == 1:
            lift_cmd = up_lift_level
        else:
            lift_cmd = mid_lift_level
        #lift_cmd = up_lift_level if lift == 1 else down_lift_level     # 只有两种情况的方式
        lift_cmd = str(lift_cmd).zfill(2)
        cmd = '@' + str(two_wrist[0])+l_elbow_cmd + str(two_wrist[1])+r_elbow_cmd + lift_cmd + '!'
        


        # 打印用的(到时实际上场可以注释掉，以防卡速度)
        l_wrist_text = '左抓_∠' if two_wrist[0] else '左松_{'
        r_wrist_text = ', 右抓_∠' if two_wrist[1] else ', 右松_{'
        l_elbow_text = '    左内折_in' if two_elbow[0] else '    左外折_ex'
        r_elbow_text = ', 右内折_in' if two_elbow[1] else ', 右外折_ex'
        if lift == 0:
            lift_text = '    降_↓'
        elif lift == 1:
            lift_text = '    升_↑'
        else:
            lift_text = '    高度在一半_↓↑'
        action =  l_wrist_text + r_wrist_text + l_elbow_text + r_elbow_text + lift_text
        print(action)
        print(cmd)
        self.arm_ser.write(cmd.encode())
        print('应该是写入了的')
        print(action + '    完毕')
        self.__arm_state = [list(two_wrist), list(two_elbow), lift]





class Car_Bridge:
    def __init__(self):
        self.car_ser: serial.Serial
        self.Yaw = 0
        self.is_close = False
        self.count = 0
        self.is_move = None

        self.log_vector_angle = 0       # 这里打了个不完美的补丁    FIXME: 应该能用，但是不够低耦合
        self.log_vector_distance = 0    # 效果同上  #FIXME:
        
    def __del__(self):
        try:
            self.car_ser.close()
            self.is_close = True
            print('成功关闭底盘串口')
        except Exception as e:
            print('底盘串口关闭失败:', e)


    def init(self, Option) -> bool:
        self.Option = Option

        try:
            self.car_ser = serial.Serial(
                Option['Car_Serial']['port'], Option['Car_Serial']['baudrate']
            )
            if self.car_ser.is_open == False:
                self.car_ser.open()  # 打开串口
                self.is_close = False
            print("成功打开底盘串口")
            self.car_ser.flushInput()  # type: ignore
            return True
        except Exception as e:
            print("底盘串口打开失败:", e)
            return False

    def send_Command(self, arr, is_print=False):
        try:
            self.car_ser.write(arr.encode("ascii"))
            if is_print:
                print(f"向底盘发送指令：{arr}")
        except Exception as e:
            print("向底盘发送指令失败:", e)

    def Receiver(self):
        try:
            if self.car_ser.in_waiting > 0:
                message = self.car_ser.readline()
                if message:
                    message = message.decode(encoding="UTF-8")
                    message = message.strip()
                    #print(f"这是message: {message}")
                    datas = message.split("|")
                    if datas[0] == "$":
                        if datas[1] == "1":
                            self.is_move = True
                        elif datas[1] == "0":
                            self.is_move = False
                    if datas[0] == "#":
                        self.Yaw = -float(datas[1])

        except Exception as e:
            if self.count < 10:
                self.count += 1
                print("Car_error %s" % e)

    def Car_Receiver(self):
        while True:
            if self.count < 15:
                self.Receiver()
                if self.is_close:
                    break
            else:
                self.count = 0
                self.is_close = True
                break

    def run_thread(self):
        car_receive_thread = threading.Thread(target=self.Car_Receiver)
        car_receive_thread.start()

    def get_cur_Yaw(self, is_print=False):
        arr = "@|5|0|0|0|#"
        self.send_Command(arr=arr, is_print=is_print)
        time.sleep(0.2)
        return self.Yaw

    def go_distance(self, dis, speed=0.15, is_print=False):     # 抓水果联动用到，固定速度为0.15
        print('-- 直行 ' + str(dis))
        #if abs(dis) < 0.5:
        #    speed = 0.1
        #elif abs(dis) > 1:
        #    speed = 0.3
        self.move(dis, 0, speed=speed, is_print=is_print)
        print('-- 直行完毕')
        
    def go_distance_atom(self, dis, speed=0.2, is_print=False): # 原先的那种，精准度优先
        print('-- ori直行 ' + str(dis))
        if abs(dis) < 0.5:
           speed = 0.1
        elif abs(dis) > 1:
           speed = 0.3
        self.move_atom(dis, 0, speed=speed, is_print=is_print)
        print('-- ori直行完毕')

    def yaw_adjustment(self, yaw, is_print=False):
        print(f'() 转角 {yaw} 度')
        cur_yaw = self.get_cur_Yaw()
        time.sleep(0.2)
        # print(cur_yaw)
        arrive_angle = round(cur_yaw + yaw, 2)
        arr = f"@|2|0|{arrive_angle}|0|#"
        self.send_Command(arr=arr, is_print=is_print)

        print(f"现在小车什么情况 yaw_adjustment 前 {self.is_move}")
        while True:
            if self.is_move:
                self.is_move = None
                break
            if self.is_move is False:
                self.send_Command(arr=arr, is_print=is_print)
            time.sleep(0.01)
        print(f"现在小车什么情况 yaw_adjustment 后 {self.is_move}")
        print(f'() 转角完毕')

    def move_atom(self, x_dis, y_dis, speed=0.1, error=0.01, is_print=False):
        x_dis = -int(x_dis * 1000) / 1000
        y_dis = -int(y_dis * 1000) / 1000

        if 0.005 < abs(x_dis) < error and x_dis != 0:
            x_dis = x_dis / abs(x_dis) * error
        if 0.005 < abs(y_dis) < error and y_dis != 0:
            y_dis = y_dis / abs(y_dis) * error
        arr = f"@|6|{speed}|{x_dis}|{y_dis}|#"
        self.send_Command(arr=arr, is_print=is_print)
        print(f"现在小车什么情况 move_atom 前 {self.is_move}")
        while True:
            if self.is_move:
                self.is_move = None
                break
            elif self.is_move is False:
                self.send_Command(arr=arr, is_print=is_print)
            time.sleep(0.1)
        print(f"现在小车什么情况 move_atom 后 {self.is_move}")
          
    def move(self, x_dis, y_dis, speed=0.1, error=0.01, is_print=False):
        x_dis = -int(x_dis * 1000) / 1000
        y_dis = -int(y_dis * 1000) / 1000

        if 0.005 < abs(x_dis) < error and x_dis != 0:
            x_dis = x_dis / abs(x_dis) * error
        if 0.005 < abs(y_dis) < error and y_dis != 0:
            y_dis = y_dis / abs(y_dis) * error
        arr = f"@|6|{speed}|{x_dis}|{y_dis}|#"
        self.send_Command(arr=arr, is_print=is_print)
        #while True:
        #    if self.is_move:
        #        self.is_move = None
        #        break
        #    elif self.is_move is False:
        #        self.send_Command(arr=arr, is_print=is_print)
        #    time.sleep(0.1)  

            

    # 暂时先顶着用， 到时误差过大再考虑
    def go_sideway(self, dis, base_angle=18, is_print=False, mode=1):
        print(f'←→ 假平移 {dis}m')
        if dis < 0:
            base_angle *= -1
        radians = math.radians(base_angle)

        # 计算另一条直角边的长度
        straight_dist = dis / math.tan(radians)
        # 计算斜边的长度
        hypotenuse = dis / math.sin(radians)

        # 四舍五入到小数点后四位
        straight_dist_rounded = round(straight_dist, 3)
        hypotenuse_rounded = round(hypotenuse, 3)

        print(f'平移距离: {dis}')
        print(f'基准角对应弧度: {radians}')
        print(f'斜边长度: {hypotenuse_rounded}')

        if mode == 1:   # 先后退 再挪角度
            self.yaw_adjustment(base_angle)
            self.go_distance_atom(abs(hypotenuse_rounded))
            self.yaw_adjustment(-base_angle)
            self.go_distance_atom(-(abs(straight_dist_rounded) + dis/10))
        else:       # 先前进 再挪角度
            self.yaw_adjustment(base_angle)
            self.go_distance_atom(-abs(hypotenuse_rounded))
            self.yaw_adjustment(-base_angle)
            self.go_distance_atom(abs(straight_dist_rounded) + dis/10)
            

        print('←→ 假平移完毕')


    def go_vector_wrong(self, distance, side):
        #cur_yaw = int(self.get_cur_Yaw())
        distance = int(distance * 1000) / 1000
        side = int(side * 1000) / 1000
        rotate_angle = math.atan2(side, distance) * 180 / math.pi
        hypotenuse = math.sqrt(distance ** 2 + side ** 2)

        if distance < 0 and side > 0:
            rotate_angle -= 180

        self.yaw_adjustment(rotate_angle)
        time.sleep(0.2)
        self.go_distance(hypotenuse)
        time.sleep(0.2)
        self.yaw_adjustment(-rotate_angle)
        print("←→&^v 向量平移完毕")



    def go_vector(self, dis, side, is_print=False):
        print(f'←→&^v 向量平移 纵向{dis}m, 横向{side}m')

        theta_rad = np.arctan(np.abs(dis)/np.abs(side))
        theta = np.rad2deg(theta_rad)
        print(theta)
        rotate_angle = theta - 90
        if side < 0:
            rotate_angle *= -1

        # 现在只能支持 dis<0 的两种情况

        hypotenuse = round(dis/np.sin(theta_rad), 3)    # 要走的斜边距离

        print(f"旋转 {rotate_angle} 度, 斜边移动 {hypotenuse} m")
        #self.yaw_adjustment(rotate_angle, is_print=is_print)
        #self.go_distance_atom(hypotenuse, is_print=is_print)
        self.log_vector_distance = hypotenuse
        self.log_vector_angle = rotate_angle
        #self.yaw_adjustment(-rotate_angle)

        print(f'←→&^v 向量平移完成 值记录')