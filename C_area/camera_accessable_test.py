import cv2
import os
# untested on pi

class Camera:
    def __init__(self, camera_name):
        self.camera_name = camera_name
        self.open()
        self.frame = None
    
    def __del__(self):
        print(f"关闭摄像头")
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


os.system('ls /dev/video*')
print()

camera = Camera('/dev/video_top')
#camera = Camera(0)

while camera.cap.isOpened():     # 现在是一次check一张单帧
    haveCap, frame = camera.cap.read()
    if haveCap == False or frame is None:
        print(f"error device: 摄像头{camera.camera_name} 连接有误or摄像头没开")
        break
    cv2.imshow("image", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cv2.destroyAllWindows()