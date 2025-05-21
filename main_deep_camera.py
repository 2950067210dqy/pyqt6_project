import os
import threading
from threading import Thread

import pyrealsense2 as rs
import numpy as np
import cv2
import time

from loguru import logger

from communication.ini_pareser.ini_parser import ini_parser
from config.global_setting import global_setting
from util.time_util import time_util

"""
修改：连接相机时间优化
"""
event = threading.Event()
frame_nums = 0
lock = threading.Lock()


class Delete_file(Thread):
    """
    清除文件线程
    """

    def __init__(self, path, start_time):
        super().__init__()
        self.path = path
        self.start_time = start_time

    # 获得删除文件的大小
    def get_and_delete_files(self):

        total_size = 0
        total_nums = 0
        for root, dirs, files in os.walk(self.path):
            # logger.warning(f"{root} | {dirs} | {files}")
            # 将深度信息npy文件排除 不删除
            if "depth" not in root:
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)  # 获取文件大小（字节）
                        size = float(size / 1204 / 1024 / 1024)  # 将字节B转成GB
                        total_size += size
                        total_nums += 1
                        os.remove(file_path)  # 删除文件
                    except Exception as e:
                        logger.error(f"deep_camera Failed to delete {file_path}: reason:{e}")

        logger.info(f"deep_camera Total size of deleted files: {total_size} G-bytes")
        logger.info(f"deep_camera Total nums of deleted files: {total_nums} ")
        global frame_nums
        with lock:
            logger.info(f"deep_camera Total nums of frame : {frame_nums}")
            frame_nums = 0
        return total_size

    def stop(self):
        self.running = False

    def run(self) -> None:
        try:
            logger.info(f"深度相机删除文件线程开始运行")
            self.running = True
            while self.running:
                # 获取现在时间与上次删除时间之差
                current_time = time.time()
                elapsed = current_time - self.start_time
                if elapsed >= float(global_setting.get_setting("camera_config")['DELETE']['interval_seconds']):
                    # 尝试删除文件
                    # 获取删除文件内的所有文件大小
                    self.get_and_delete_files()
                    event.set()

                    logger.info(f"deep_camera 删除文件成功")
                    self.start_time = time.time()

                    pass
                # logger.info(f"时间差{time_util.get_format_minute_from_time(elapsed)}")
                time.sleep(float(global_setting.get_setting("camera_config")['DEEP_CAMERA']['delay']))
        except Exception as e:
            logger.error(f"深度相机删除文件线程运行异常，异常原因：{e}")
        pass


class RealSenseProcessor(Thread):
    def __init__(self, path='', id=1):
        super().__init__()
        self.running = None
        self.id = id
        self.path = path
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
        self.config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
        self.pipeline.start(self.config)
        self.align = rs.align(rs.stream.color)

    def img_save(self, image, depth_image):
        timestrf = time_util.get_format_file_from_time(time.time())
        directory_color = self.path + f"color"
        if not os.path.exists(directory_color):
            os.makedirs(directory_color)  # 递归创建目录
        cv2.imwrite(directory_color + f"/{timestrf}.bmp", image)
        directory_depth = self.path + f"depth"
        if not os.path.exists(directory_depth):
            os.makedirs(directory_depth)  # 递归创建目录
        np.save(directory_depth + f"/{timestrf}.npy", depth_image)

    # 运行结束
    def join(self):
        self.pipeline.stop()
        self.running = False
        event.set()  # 解除阻塞
        pass

    def stop(self):
        self.pipeline.stop()
        self.running = False
        event.set()  # 解除阻塞

    # 启动，获取一帧
    def run(self):
        try:
            logger.info(f"相机{self.id}开始运行")
            global frame_nums
            self.running = True
            while self.running:
                # 等待一帧 连续拍
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
                with lock:
                    frame_nums += 1
                self.img_save(color_image, depth_image)
                # self.running = False
                time.sleep(float(global_setting.get_setting("camera_config")['DEEP_CAMERA']['delay']))
        except Exception as e:
            logger.error(f"相机{self.id}运行异常，异常原因：{e}")


def load_global_setting():
    # 加载相机配置
    config_file_path = os.getcwd() + "/camera_config.ini"

    # 串口配置数据{"section":{"key1":value1,"key2":value2,....}，...}
    config = ini_parser(config_file_path).read()
    if (len(config) != 0):
        logger.info("相机配置文件读取成功。")
    else:
        logger.error("相机配置文件读取失败。")
    global_setting.set_setting("camera_config", config)
    # 记录运行时间的开始时间
    start_time = time.time()
    global_setting.set_setting("start_time", start_time)
    logger.info(f"相机连接开始时间：{time_util.get_format_from_time(start_time)}")
    # 记录运行时上一次删除文件时间
    last_delete_time = time.time()
    global_setting.set_setting("last_delete_time", last_delete_time)
    return config


# 加载日志配置
logger.add(
    "./log/deep_camera/d_camera_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="30 days",
    enqueue=True,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} |{process.name} | {thread.name} |  {name} : {module}:{line} | {message}"
)
logger.info(f"{'-' * 30}deep_camera_start{'-' * 30}")
# 设置全局变量
load_global_setting()
# 初始化保存路径
path = global_setting.get_setting("camera_config")['STORAGE']['fold_path'] + \
       global_setting.get_setting("camera_config")['DEEP_CAMERA']['path']
# 删除文件线程
delete_file_thread = Delete_file(path=path, start_time=global_setting.get_setting("start_time"))
delete_file_thread.start()
# 模拟8相机情况
camera_nums = int(global_setting.get_setting("camera_config")['DEEP_CAMERA']['nums'])
camera_list = []
for num in range(camera_nums):
    camera_struct = {}

    try:
        camera = RealSenseProcessor(path=path + f"camera_{num + 1}/", id=num + 1)
    except Exception as e:
        logger.error(f"相机{num + 1}初始化失败，失败原因：{e}")
    camera.start()
    camera_struct['id'] = num + 1
    camera_struct['camera'] = camera
    camera_list.append(camera_struct)
    pass

# stop
# camera1.pipeline.stop()
