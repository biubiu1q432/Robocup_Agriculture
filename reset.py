from Modules.Bridge import *   
#包含了一些用于串口通信和控制机械臂和小车的类和方法的模块

Option = {
        "Arm_Serial": {"port": "/dev/arm", "baudrate": 115200},
        "Car_Serial": {"port": "/dev/car", "baudrate": 115200},
        #"K210_Serial": {"port": "/dev/k210", "baudrate": 115200},
}
#option是字典，包含串口通信的配置信息
#初始化配置，波特率为115200，机械臂串口端口为/dev/arm，车轮串口端口为/dev/car
if __name__ == '__main__':
#当脚本作为主程序时，下面代码模块将被执行
    arm_bridge = Arm_Bridge()
#创建一个Arm_Bridge类的实例，用于控制机械臂
    arm_bridge.init(Option)
#使用Option字典中的配置信息初始化机械臂的串口通信
    # arm_bridge.arm_cmd((1,1),(0,0),0)
    # time.sleep(0.2)
    # arm_bridge.arm_cmd((1,1),(0,0),1)
    # time.sleep(1.4)
    # arm_bridge.arm_cmd((1,1),(1,1),1)
    # time.sleep(2)

    arm_bridge.arm_cmd((1,1),(1,1),1)
#发送一个控制命令给机械臂
#参数一是左爪和右爪的张开情况,(0,1)为左爪张开右爪闭合
#参数二为左右臂的弯曲程度,(1,0)为左弯曲右不弯曲
#参数三为机械臂的高度,0为最低处1为最高处
    time.sleep(2)
#程序暂停2秒