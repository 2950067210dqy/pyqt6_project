import sys
import logging
import argparse
from pathlib import Path

import numpy as np
import cv2 as cv
import time
import os
import csv

from senxor.utils import connect_senxor, data_to_frame, remap, \
    cv_filter, cv_render, \
    RollingAverageFilter, Display
from senxor.utils import CVSegment
from imutils.video import VideoStream

np.set_printoptions(precision=1)

# global constants

TIP_SEGM_PARAM = {
    # threshold-based segmentation
    # ----------------------------
    # supported: simple, otsu, adaptive
    'threshold_type': 'simple',
    # threshold value for simple thresholding
    'threshold': 190,
    'contour_minArea': -5,

    # contour analysis
    # ----------------
    # absolute value of the area of the smallest contour
    'min_contourarea': 5,
    # extention of the bounding box of the target contour
    # for estimating background temperature
    'bbox_extension': 10,
}

# Make the a global variable and use it as an instance of the mi48.
# This allows it to be used directly in a signal_handler.
global mi48


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-tis', '--thermal-image-source', default=None, dest='tis_id',
                        help='Comport name (str) or thermal video source  ID (int)')
    parser.add_argument('-cis', '--color-image-source', type=int, default=None,
                        dest='cis_id',
                        help='Video source ID: 0=laptop cam, 1=USB webcam')
    parser.add_argument('-fps', '--framerate', default=5, type=int, dest='fps',
                        help='Frame rate per second')
    parser.add_argument('-c', '--colormap', default='rainbow2', type=str,
                        help='Colormap for the thermogram')
    parser.add_argument('--data_file', default=None, type=str,
                        help='file instead of camera stream')
    parser.add_argument('-v', '--video-record', default=False, dest='record_video',
                        action='store_true', help='Record a video of what is shown')
    parser.add_argument('-e', '--emissivity', type=float, default=0.95,
                        dest='emissivity', help='target emissivity')
    parser.add_argument('-histo', '--show-histogram', default=False, action='store_true',
                        dest='show_histogram', help='Show thermal image histogram')
    parser.add_argument('-plots', '--show-plots', default=False, action='store_true',
                        dest='show_plots',
                        help='Show plots of measured temperatures')
    parser.add_argument('-scale', '--thermal-image-scale-factor', default=4, type=int,
                        dest='img_scale', help='Scale factor for thermogram')

    args = parser.parse_args()
    return args


class TIP:
    """Thermal Image Pipeline"""

    def __init__(self, param):
        # 图像尺寸设置
        self.image_scale = param.get('image_scale', 1)
        self.ncol_nrow = param.get('fpa_ncol_nrow', (80, 62))
        self.image_size = (self.image_scale * self.ncol_nrow[0],
                           self.image_scale * self.ncol_nrow[1])
        # 伪彩色
        self.colormap = param.get('colormap', 'rainbow2')

        # 图像分割器初始化
        self.segment = CVSegment(param)

    def execute(self, frame):
        """Thermal data processing pipeline; produces image and stats/metrics"""
        # 把热图数据转成 8-bit 显示图像（通常是灰度或伪彩色图像）
        frame_uint8 = remap(frame)
        self.img_raw = cv_render(frame_uint8, resize=self.image_size,
                                 colormap=self.colormap,
                                 interpolation=cv.INTER_NEAREST, display=False)

        # 图像滤波并进行热点分割 对图像做滤波（如中值/双边滤波），然后用分割器提取热图中最热的区域（hotspot）。
        filtered_ui8 = cv_filter(frame_uint8, parameters={'blur_ks': 5},
                                 use_median=True, use_bilat=True)
        # 生成滤波图像
        # self.img_filtered = cv_render(filtered_ui8, resize=self.image_size,
        #                               colormap=self.colormap,
        #                               interpolation=cv.INTER_NEAREST, display=False)
        self.segment(frame=frame, frui8=filtered_ui8)

        # 渲染热点掩膜图像
        try:
            hs = self.segment.hotspots[0]
            hs_mask = hs.out_frames['hs_mask']
            hs_osd = hs.osd
        except IndexError:
            hs = None
            hs_mask = np.zeros(self.image_size, dtype='uint8')
            hs_osd = {}
        # self.img_hs_mask = cv_render(hs_mask, resize=self.image_size,
        #                              colormap='parula',
        #                              interpolation=cv.INTER_NEAREST, display=False)

        # 返回处理后图像和温度统计数据。
        images = {
            'raw': self.img_raw,
            # 'filtered': self.img_filtered,
            # 'hotspot_mask': self.img_hs_mask,
        }

        output_struct = {
            'hs_max': hs_osd.get('max', None),
            'hs_mean': hs_osd.get('mean', None),
        }

        return images, output_struct

    def __call__(self, thermal_data):
        return self.execute(thermal_data)


def img_save(path, image):
    timestamp = int(time.time())
    cv.imwrite(path + r"data\pic\{0}.bmp".format(timestamp), image)


class coordinate_writing:
    def __init__(self):
        self.csv_file = None
        self.csv_writer = None
        self.filename = r'data/tmp.csv'

    def csv_create(self):
        self.csv_file = open(self.filename, "w", newline="")
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(["Timestamp", "tmp(℃)"])

    def csv_write(self, timestamp, t):
        if self.csv_writer is not None:
            self.csv_writer.writerow([timestamp, t])

    def csv_close(self):
        if self.csv_file is not None:
            self.csv_file.close()
            self.csv_file = None
            self.csv_writer = None


def compose_display(img_list):
    """
    Compose a single image out of a list of opencv-rendered images of the same size
    """
    if len(img_list) == 4:
        top_img = np.hstack(img_list[:2])
        bot_img = np.hstack(img_list[2:])
        img = np.vstack((top_img, bot_img))
        return img
    if len(img_list) == 6:
        top_img = np.hstack(img_list[:3])
        bot_img = np.hstack(img_list[3:])
        img = np.vstack((top_img, bot_img))
        return img
    if len(img_list) == 8:
        top_img = np.hstack(img_list[:4])
        bot_img = np.hstack(img_list[4:])
        img = np.vstack((top_img, bot_img))
        return img
    img = np.hstack(img_list)
    return img


def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))

    args = parse_args()
    save_dir = args.save_dir if hasattr(args, 'save_dir') else './data'
    os.makedirs(save_dir, exist_ok=True)

    mi48, connected_port, port_names = connect_senxor(src=args.tis_id)
    if mi48 is None:
        logging.critical('Cannot connect to SenXor')
        logging.info(f'The following ports have SenXor attached {port_names}')
        sys.exit(1)
    else:
        logging.info(f'{mi48.sn} connected to {connected_port}')
    logger.info(mi48.camera_info)

    mi48.set_fps(args.fps)
    mi48.regwrite(0xD0, 0x00)
    mi48.disable_filter(f1=True, f2=True, f3=True)
    mi48.enable_filter(f1=True, f2=True, f3=True)
    mi48.regwrite(0xC2, 0x64)
    mi48.set_emissivity(args.emissivity)
    mi48.set_offset_corr(3)
    mi48.start(stream=True, with_header=True)

    RA_Tmin = RollingAverageFilter(N=10)
    RA_Tmax = RollingAverageFilter(N=10)

    tip_param = {
        'colormap': args.colormap,
        'fpa_ncol_nrow': (mi48.cols, mi48.rows),
        'image_scale': args.img_scale,
    }
    tip_param.update(TIP_SEGM_PARAM)
    tip = TIP(tip_param)

    if args.cis_id is not None:
        vs = VideoStream(src=args.cis_id).start()
        test_frame = vs.read()
    else:
        vs = None
        test_frame = None

    if test_frame is None:
        vs = None

    display_options = {
        'window_coord': (0, 0),
        'window_title': f'{mi48.camera_id} ({mi48.name}), {args.cis_id}',
        'directory': r'data'
    }
    display = Display(display_options)

    images = {'thermal': {}}
    struct = {'thermal': {}}

    datasave = coordinate_writing()
    datasave.csv_create()

    start_time = time.time()
    while time.time() - start_time < 1:
    # while True:
        raw_data, header = mi48.read()
        frame = data_to_frame(raw_data, (mi48.cols, mi48.rows), hflip=False)  # hflip与USB正反有关，朝上要翻转为true

        #
        Tmin, Tmax = RA_Tmin(frame.min()), RA_Tmax(frame.max())
        frame = np.clip(frame, Tmin, Tmax)
        _imgs, _struct = tip(frame)
        images['thermal'].update(_imgs)
        struct['thermal'].update(_struct)
        display.img = [images['thermal']['raw']]

        display(display.img)  # 显示，可删除

        display.dir = Path('data/pic')
        display.save('{0}.bmp'.format(time.time()))

        datasave.csv_write(time.time(), struct['thermal']['hs_mean'])  # 数据保存

        key = cv.waitKey(1) & 0xFF
        if key != -1:
            if key == ord("q") or key == 27:
                mi48.stop()
                cv.destroyAllWindows()
                datasave.csv_close()
                if vs is not None:
                    vs.stop()
                break

    datasave.csv_close()


if __name__ == '__main__':
    main()
