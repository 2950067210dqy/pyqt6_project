import json
import os
import threading
from threading import Thread

from loguru import logger

from communication.ini_pareser.ini_parser import ini_parser
from config.global_setting import global_setting

from util.time_util import time_util
import pyrealsense2 as rs
import cv2
import csv

from ultralytics import YOLO
import os
import time
import numpy as np

"""
修改：连接相机时间优化
"""

# 总图像帧数量
frame_nums = 0
lock = threading.Lock()

processed_log_lock = threading.Lock()
# 相机参数
intrinsics = "./equipment/deep_camera/intrinsics.json"


class coordinate_writing:
    """
    将处理的坐标写入csv文件
    """

    def __init__(self, path, camera_id):
        self.path = path
        self.camera_id = camera_id
        self.csv_file = None
        self.csv_writer = None
        self.folder_path = self.path + global_setting.get_setting("camera_config")['DEEP_CAMERA']['result_dir']
        self.filename = self.folder_path + global_setting.get_setting("camera_config")['DEEP_CAMERA'][
            'location_filename']

    def csv_create(self):
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
        with open(self.filename, mode='w', newline='', encoding='utf-8') as file:
            self.csv_file = file
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow(["base_file_name", "X (m)", "Y (m)", "Z (m)"])

    def csv_write(self, file_base_name, x, y, z):
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
        with open(self.filename, mode='a', newline='', encoding='utf-8') as file:
            self.csv_file = file
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow([file_base_name, x, y, z])

    def csv_close(self):
        if self.csv_file is not None:
            self.csv_file.close()
            self.csv_file = None
            self.csv_writer = None


class Detection:
    """
    使用yolo模型探查坐标
    """

    def __init__(self, path, camera_id):
        self.path = path
        self.camera_id = camera_id
        self.model = YOLO('./model/yolo11n.pt')
        self.data_save = coordinate_writing(path=path, camera_id=camera_id)
        self.data_save.csv_create()
        self.intrinsics, self.unit = self.get_intrinsics(intrinsics)

    def get_intrinsics(self, intrinsics):
        with open(intrinsics, "r") as f:
            intrinsics_data = json.load(f)

        depth_intrin = rs.intrinsics()
        depth_intrin.width = intrinsics_data["width"]
        depth_intrin.height = intrinsics_data["height"]
        depth_intrin.ppx = intrinsics_data["ppx"]
        depth_intrin.ppy = intrinsics_data["ppy"]
        depth_intrin.fx = intrinsics_data["fx"]
        depth_intrin.fy = intrinsics_data["fy"]
        depth_intrin.model = rs.distortion(intrinsics_data["model"])
        depth_intrin.coeffs = intrinsics_data["coeffs"]
        unit = intrinsics_data["units"]
        return depth_intrin, unit

    def img_save(self, image, timestamp):
        img = global_setting.get_setting("camera_config")['DEEP_CAMERA']['result_dir'] + \
              global_setting.get_setting("camera_config")['DEEP_CAMERA']['result_img_dir']
        if not os.path.exists(self.path + img):
            os.makedirs(self.path + img)
        cv2.imwrite(self.path + img + "{0}.bmp".format(timestamp), image)

    def detect(self, color_image, depth_frame, file_base_name):
        if os.path.exists(color_image) and os.path.isfile(color_image) and os.path.exists(
                depth_frame) and os.path.isfile(depth_frame):
            try:
                imge = cv2.imread(color_image)
            except Exception as e:
                logger.error(f"camera_{self.camera_id}图像处理程序读取{file_base_name}.bmp文件出错，原因：{e}")
                return
            results = self.model(imge, classes=[62], verbose=False)
            # 处理检测结果
            for result in results:
                boxes = result.boxes.xyxy.cpu().numpy()
                if len(boxes) == 0:
                    x, y, z = 'NaN'
                    self.data_save.csv_write(file_base_name, x, y, z)
                    self.img_save(imge, file_base_name)
                    # with lock:
                    #     logger.info(
                    #         f'深度相机camera_{self.camera_id}的图像{file_base_name}处理结果保存成功 | x, y, z = NaN')
                    continue
                # 获取检测框坐标
                x1, y1, x2, y2 = map(int, boxes[0])
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                # 获取深度坐标
                try:
                    depth = np.load(depth_frame)
                except Exception as e:
                    logger.error(f"camera_{self.camera_id}图像处理程序读取{file_base_name}.npy文件出错，原因：{e}")
                    return
                    #  读取到的深度信息/1000 为真实的深度信息，单位为m
                depth = depth[center_y, center_x] * self.unit
                # depth = float(depth)   # 转换为米
                point_3d = rs.rs2_deproject_pixel_to_point(self.intrinsics, [center_x, center_y], depth)
                # print(f"point_3d{point_3d}")
                x, y, z = map(lambda v: round(v, 3), point_3d)

                # 写入
                self.data_save.csv_write(file_base_name, x, y, z)

                # 可视化
                imge = self.draw_overlay(imge, x1, y1, x2, y2, center_x, center_y, x, y, z)
                self.img_save(imge, file_base_name)
                # with lock:
                #     logger.info(
                #         f'深度相机camera_{self.camera_id}的图像{file_base_name}处理结果保存成功. | x, y, z ={x},{y},{z}')
        else:
            logger.error(f"{file_base_name}的bmp文件或npy文件不存在")

    # 绘制可视化信息
    def draw_overlay(self, image, x1, y1, x2, y2, center_x, center_y, x, y, z):
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.circle(image, (center_x, center_y), 5, (0, 0, 255), -1)
        text = f"X: {x:.2f}m, Y: {y:.2f}m, Z: {z:.2f}m"
        cv2.putText(image, text, (x1, max(y1 - 10, 0)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        return image


class Img_process(Thread):
    """
    将bmp文件和npm文件进行处理 线程处理
    """

    def __init__(self, path, camera_id):
        super().__init__()
        self.path = path
        self.camera_id = camera_id
        self.running = None
        self.dection = Detection(path=self.path, camera_id=self.camera_id)
        pass

    def clear_processed(self):
        """
        清空日志文件
        :return:
        """
        log = []
        # 保存更新后的日志
        with open(self.path + global_setting.get_setting("camera_config")['DEEP_CAMERA']['processed_log_filename'],
                  'w') as f:
            json.dump(log, f)
        pass

    def mark_as_processed(self, filename):
        """
        标记文件为已处理并存入json日志文件中
        :param filename:
        :return:
        """
        log = []

        # 尝试读取已存在的日志文件
        if os.path.exists(
                self.path + global_setting.get_setting("camera_config")['DEEP_CAMERA']['processed_log_filename']):
            try:
                with open(self.path + global_setting.get_setting("camera_config")['DEEP_CAMERA'][
                    'processed_log_filename'], 'r') as f:
                    log = json.load(f)
            except (json.JSONDecodeError, IOError):
                log = []

        # 避免重复添加
        if filename not in log:
            log.append(filename)

        # 保存更新后的日志
        with open(self.path + global_setting.get_setting("camera_config")['DEEP_CAMERA']['processed_log_filename'],
                  'w') as f:
            json.dump(log, f)

    def has_been_processed(self, filename):
        """
        判断文件是否已经处理
        :param filename:
        :return:
        """
        if not os.path.exists(
                self.path + global_setting.get_setting("camera_config")['DEEP_CAMERA']['processed_log_filename']):
            return False
        with open(self.path + global_setting.get_setting("camera_config")['DEEP_CAMERA']['processed_log_filename'],
                  'r') as f:
            log = json.load(f)
        return filename in log

    def stop(self):
        self.running = False

    def run(self) -> None:
        self.running = True
        logger.info(f"相机{self.camera_id}图像处理线程开始运行")
        while self.running:
            start_time = time.time()
            """处理文件夹中的文件"""
            # color文件夹下的 对bmp文件名牌序
            files = sorted(f for f in os.listdir(
                self.path + global_setting.get_setting("camera_config")['DEEP_CAMERA']['color_dir']) if
                           f.endswith(".bmp"))

            # 从日志文件中获取最后处理的文件名
            last_processed_file = None
            processed_log_path = self.path + global_setting.get_setting("camera_config")['DEEP_CAMERA'][
                'processed_log_filename']
            if os.path.exists(processed_log_path):
                with processed_log_lock:
                    with open(processed_log_path, 'r') as f:
                        log = json.load(f)
                if log:
                    last_processed_file = log[-1]  # 获取最后处理的文件

            # 如果是增量处理，从上次未处理的文件开始
            start_processing = False
            # 一次处理文件的数量
            handle_files_nums = 0
            for file in files:
                if last_processed_file:
                    if not start_processing and file == last_processed_file:
                        start_processing = True
                    if not start_processing:
                        continue  # 如果未到达上次处理的文件，跳过
                base_name = os.path.splitext(file)[0]
                # 在这里进行文件处理（可以替换为实际的处理函数）
                bmp_path = os.path.join(
                    self.path + global_setting.get_setting("camera_config")['DEEP_CAMERA']['color_dir'], file)
                npy_path = os.path.join(
                    self.path + global_setting.get_setting("camera_config")['DEEP_CAMERA']['depth_dir'],
                    base_name + ".npy")

                if not os.path.exists(npy_path):
                    logger.error(f"深度相机{self.camera_id}的图像处理缺少对应的npy文件: {npy_path}")
                    continue
                self.dection.detect(bmp_path, npy_path, base_name)

                # 处理完毕后，标记文件为已处理
                with processed_log_lock:
                    self.mark_as_processed(file)
                handle_files_nums += 1
            # 如果遍历完所有文件start_processing还是False 则processed_log日志文件出现问题，直接清空processed_log日志文件
            if not start_processing:
                self.clear_processed()
            self.dection.data_save.csv_close()
            end_time = time.time()
            logger.debug(
                f"camera_{self.camera_id} | 图像处理程序一次处理时间：{end_time - start_time}秒 | 共处理{handle_files_nums}个图像文件 | 此时总图像帧数量:{frame_nums}")
            time.sleep(float(global_setting.get_setting("camera_config")['DEEP_CAMERA']['process_delay']))
        pass


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
            # if "depth" not in root:
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
        global frame_nums
        with lock:
            logger.warning(f"深度相机 | 删除文件总大小: {total_size} G-bytes | 删除文件总数量： {total_nums} | 此时相机拍摄的图像数量：{frame_nums}")
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

                    logger.info(f"deep_camera 删除文件成功")
                    self.start_time = time.time()

                    pass
                # logger.info(f"时间差{time_util.get_format_minute_from_time(elapsed)}")
                time.sleep(float(global_setting.get_setting("camera_config")['DELETE']['delay']))
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
        directory_color = self.path + global_setting.get_setting("camera_config")['DEEP_CAMERA']['color_dir']
        if not os.path.exists(directory_color):
            os.makedirs(directory_color)  # 递归创建目录
        cv2.imwrite(directory_color + f"/{timestrf}.bmp", image)
        directory_depth = self.path + global_setting.get_setting("camera_config")['DEEP_CAMERA']['depth_dir']
        if not os.path.exists(directory_depth):
            os.makedirs(directory_depth)  # 递归创建目录
        np.save(directory_depth + f"/{timestrf}.npy", depth_image)

    # 运行结束
    def join(self):
        self.pipeline.stop()
        self.running = False

        pass

    def stop(self):
        self.pipeline.stop()
        self.running = False

    # 启动，获取一帧
    def run(self):
        try:
            logger.info(f"相机{self.id}开始运行")
            global frame_nums
            # 读取之前存储了多少图像
            with os.scandir(self.path + global_setting.get_setting("camera_config")['DEEP_CAMERA']['color_dir']) as it:
                for entry in it:
                    if entry.is_file():
                        with lock:
                            frame_nums += 1
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
                self.img_save(color_image, depth_image)
                with lock:
                    frame_nums += 1
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
# 根据设置的相机数量来连接
camera_nums = int(global_setting.get_setting("camera_config")['DEEP_CAMERA']['nums'])
camera_list = []
for num in range(camera_nums):
    camera_struct = {}
    camera = None
    try:
        # 相机初始化
        camera = RealSenseProcessor(path=path + f"camera_{num + 1}/", id=num + 1)
    except Exception as e:
        logger.error(f"deep相机{num + 1}初始化失败，失败原因：{e}")
        # 所有线程停止
        delete_file_thread.stop()
        for camera_struct_l in camera_list:
            if len(camera_struct_l) != 0 and 'camera' in camera_struct_l:
                camera_struct_l['camera'].stop()
            if len(camera_struct_l) != 0 and 'img_process' in camera_struct_l:
                camera_struct_l['img_process'].stop()
        continue
    img_process = None

    try:
        # 图像处理初始化
        img_process = Img_process(path=path + f"camera_{num + 1}/", camera_id=num + 1)
    except Exception as e:
        logger.error(f"deep 图像处理相机{num + 1}初始化失败，失败原因：{e}")
        # 所有线程停止
        delete_file_thread.stop()
        for camera_struct_l in camera_list:
            if len(camera_struct_l) != 0 and 'camera' in camera_struct_l:
                camera_struct_l['camera'].stop()
            if len(camera_struct_l) != 0 and 'img_process' in camera_struct_l:
                camera_struct_l['img_process'].stop()
        continue
    camera.start()
    img_process.start()
    camera_struct['id'] = num + 1
    camera_struct['camera'] = camera
    camera_struct['img_process'] = img_process
    camera_list.append(camera_struct)
    pass

# stop
# camera1.pipeline.stop()
