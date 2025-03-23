import RPi.GPIO as GPIO
import time
import os
import threading as th

'''
    这里是一键启动，这个东西可以放到serivce里的，到时写个函数方便你直接放到service里
'''

# 这个得在上场之前就启动；然后当main执行完了之后需要继续跑这个功能（用echo发指令，另外开一个应用进程），形成闭环
#   最好是设置为开机自启动，因为没有图形界面，所以应该是能搞成开机自启动的
'''
    一键发命令按钮
'''
class Button:
    def __init__(self, pin, cmd):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, GPIO.PUD_UP)
        self.cmd = cmd
        self.thread = th.Thread(target=self.run)
        self.thread.start()
        self.thread.join()

    def run(self):
        while True:
            time.sleep(0.02)
            if GPIO.input(self.pin) == 0:
                while GPIO.input(self.pin) == 0:
                    time.sleep(0.01)
                '''  功能   '''     # 按钮回弹之后才执行功能
                os.system(self.cmd)
                return  # 进来之后就直接退出，是一次性的按钮

    def change_cmd(self, new_cmd):
        self.cmd = new_cmd

if __name__ == '__main__':
    button = Button(17, 'python3 /home/gintama/C_area/ruler.py')

    button = Button(17, 'python3 /home/gintama/C_area/reset.py')
    
    # 如果允许上场后说开始再开始，则用这行
    button = Button(17, 'python3 /home/gintama/C_area/main.py')

    ## 否则改用下面这两行
    # time.sleep(4)
    # os.system('python3 /home/gintama/C_area/main.py')


