import pyrealsense2 as rs
import numpy as np
import cv2
import time

"""
修改：连接相机时间优化
"""


def img_save(path, image, depth_image):
    timestamp = int(time.time())
    cv2.imwrite(path + r"color\{0}.bmp".format(timestamp), image)
    np.save(path + r"depth\{0}.npy".format(timestamp), depth_image)


class RealSenseProcessor:
    def __init__(self):
        self.running = None
        self.path = r'data/1/'
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
        self.config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
        self.pipeline.start(self.config)
        self.align = rs.align(rs.stream.color)

    # 启动，获取一帧
    def run(self):
        try:
            self.running = True
            while self.running:
                # 等待一帧
                frames = self.pipeline.poll_for_frames()
                if not frames:
                    continue
                # 对其深度与RGB帧
                frames = self.align.process(frames)
                color_frame = frames.get_color_frame()
                depth_frame = frames.get_depth_frame()

                if not color_frame or not depth_frame:
                    continue

                # 转换图像格式
                color_image = np.asanyarray(color_frame.get_data())
                depth_image = np.asanyarray(depth_frame.get_data())
                img_save(self.path, color_image, depth_image)
                self.running = False

        except Exception as e:
            print(f"运行异常: {e}")


def main():
    # 模拟双相机情况
    camera1 = RealSenseProcessor()

    # 初始化保存路径
    camera1.path = r'./data/deep_camera'

    # 模拟启动情况
    start_time = time.time()
    while time.time() - start_time < 2:
        start_time1 = time.time()
        camera1.run()
        print(time.time() - start_time1)
    # stop
    camera1.pipeline.stop()


if __name__ == "__main__":
    main()
