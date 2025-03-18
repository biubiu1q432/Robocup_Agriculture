class ArmBridge:
    def arm_cmd(self, param1, param2, param3):
        print(f"param1: {param1}")
        print(f"param2: {param2}")
        print(f"param3: {param3}")

def main():
    arm_bridge = ArmBridge()
    action = {'action': arm_bridge.arm_cmd, 'args': ((0, 0), (0, 0), 0), 'time': 3.5}
    action['action'](*action['args'])

    '''
    action['action'] = arm_bridge.arm_cmd
    action['args'] = ((0, 0), (0, 0), 0)
    action['action'](*action['args']) = arm_bridge.arm_cmd((0, 0), (0, 0), 0)
    '''

if __name__ == "__main__":
    main()