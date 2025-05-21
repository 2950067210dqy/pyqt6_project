import pyrealsense2 as rs
import cv2
import csv
from datetime import datetime
from ultralytics import YOLO
import json
import os
import time
import numpy as np
"""
修改： 1.解决xyz是0的问题 
      2.只需要修改最新的图片文件 
"""
# 根目录设置
location = "location.csv"
data_dir = "data/"
color_dir = "color/"
depth_dir = "depth/"
result_dir = "result/"
processed_log = data_dir+"processed_log.json"
img = result_dir + "img/"
intrinsics = data_dir + "intrinsics.json"


class coordinate_writing:
    def __init__(self):
        self.csv_file = None
        self.csv_writer = None
        self.filename = data_dir + result_dir + location

    def csv_create(self):
        self.csv_file = open(self.filename, "w", newline="")
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(["Timestamp", "X (m)", "Y (m)", "Z (m)"])

    def csv_write(self, timestamp, x, y, z):
        if self.csv_writer is not None:
            self.csv_writer.writerow([timestamp, x, y, z])

    def csv_close(self):
        if self.csv_file is not None:
            self.csv_file.close()
            self.csv_file = None
            self.csv_writer = None


class Detection:
    def __init__(self):
        self.model = YOLO('yolo11n.pt')
        self.data_save = coordinate_writing()
        self.data_save.csv_create()
        self.intrinsics, self.unit = get_intrinsics(intrinsics)


    def detect(self, color_image, depth_frame, timestamp):
        imge = cv2.imread(color_image)
        results = self.model(imge, classes=[62],verbose=False)
        # 处理检测结果
        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            if len(boxes) == 0:
                x, y, z = 'NaN'
                print("x, y, z = 'NaN'")
                self.data_save.csv_write(timestamp, x, y, z)
                img_save(imge,timestamp)
                print('保存')

                continue
            # 获取检测框坐标
            x1, y1, x2, y2 = map(int, boxes[0])
            print(f"{[x1, y1, x2, y2]}")
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            # 获取深度坐标
            depth = np.load(depth_frame)
            #  读取到的深度信息/1000 为真实的深度信息，单位为m
            depth = depth[center_y, center_x] * self.unit
            # depth = float(depth)   # 转换为米
            point_3d = rs.rs2_deproject_pixel_to_point(self.intrinsics, [center_x, center_y], depth)
            print(f"point_3d{point_3d}")
            x, y, z = map(lambda v: round(v, 3), point_3d)

            # 写入
            self.data_save.csv_write(timestamp, x, y, z)

            # 可视化
            imge = self.draw_overlay(imge, x1, y1, x2, y2, center_x, center_y, x, y, z)
            img_save(imge, timestamp)
            print('保存')

    # 绘制可视化信息
    def draw_overlay(self, image, x1, y1, x2, y2, center_x, center_y, x, y, z):
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.circle(image, (center_x, center_y), 5, (0, 0, 255), -1)
        text = f"X: {x:.2f}m, Y: {y:.2f}m, Z: {z:.2f}m"
        cv2.putText(image, text, (x1, max(y1 - 10, 0)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        return image


def img_save(image, timestamp):
    cv2.imwrite(data_dir + img + "{0}.bmp".format(timestamp), image)

def initialize_log():
    """初始化日志文件，如果不存在则创建一个空日志文件"""
    if not os.path.exists(processed_log):
        with open(processed_log, 'w') as f:
            json.dump([], f)


def mark_as_processed(filename):
    log = []

    # 尝试读取已存在的日志文件
    if os.path.exists(processed_log):
        try:
            with open(processed_log, 'r') as f:
                log = json.load(f)
        except (json.JSONDecodeError, IOError):
            log = []

    # 避免重复添加
    if filename not in log:
        log.append(filename)

    # 保存更新后的日志
    with open(processed_log, 'w') as f:
        json.dump(log, f)


def has_been_processed(filename):
    if not os.path.exists(processed_log):
        return False
    with open(processed_log, 'r') as f:
        log = json.load(f)
    return filename in log


def get_intrinsics(intrinsics):
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


def process_files():
    pro = Detection()
    """处理文件夹中的文件"""
    files = sorted(f for f in os.listdir(data_dir + color_dir) if f.endswith(".bmp"))

    # 从日志文件中获取最后处理的文件名
    last_processed_file = None
    if os.path.exists(processed_log):
        with open(processed_log, 'r') as f:
            log = json.load(f)
        if log:
            last_processed_file = log[-1]  # 获取最后处理的文件

    # 如果是增量处理，从上次未处理的文件开始
    start_processing = False
    for file in files:
        if last_processed_file:
            if not start_processing and file == last_processed_file:
                start_processing = True
            if not start_processing:
                continue  # 如果未到达上次处理的文件，跳过
        base_name = os.path.splitext(file)[0]
        # 在这里进行文件处理（可以替换为实际的处理函数）
        bmp_path = os.path.join(data_dir + color_dir, file)
        npy_path = os.path.join(data_dir + depth_dir, base_name + ".npy")

        if not os.path.exists(npy_path):
            print(f"缺少对应的npy文件: {npy_path}")
            continue
        pro.detect(bmp_path, npy_path, base_name)

        # 处理完毕后，标记文件为已处理
        mark_as_processed(file)
    pro.data_save.csv_close()


if __name__ == "__main__":
    process_files()
