from Modules.Bridge import *

Option = {
        "Arm_Serial": {"port": "/dev/arm", "baudrate": 115200},
        "Car_Serial": {"port": "/dev/car", "baudrate": 115200},
        #"K210_Serial": {"port": "/dev/k210", "baudrate": 115200},
}

if __name__ == '__main__':
    arm_bridge = Arm_Bridge()
    arm_bridge.init(Option)
    # arm_bridge.arm_cmd((1,1),(0,0),0)
    # time.sleep(0.2)
    # arm_bridge.arm_cmd((1,1),(0,0),1)
    # time.sleep(1.4)
    # arm_bridge.arm_cmd((1,1),(1,1),1)
    # time.sleep(2)

    arm_bridge.arm_cmd((1,1),(1,1),1)
    time.sleep(2)
