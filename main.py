import multiprocessing
import traceback
from multiprocessing import Process, freeze_support
import os
import subprocess
import sys
import time

import psutil
from loguru import logger

import main_comm
import main_deep_camera
import main_gui
import main_infrared_camera
import main_response_Modbus


def run_comm_program():
    subprocess.run([sys.executable, "./main_comm.py"])


def run_gui_program():
    subprocess.run([sys.executable, "./main_gui.py"])


def run_deep_camera_program():
    subprocess.run([sys.executable, "./main_deep_camera.py"])


def run_infrared_camera_program():
    subprocess.run([sys.executable, "./main_infrared_camera.py"])


"""
确认子进程没有启动其他子进程，如果有，必须递归管理或用系统命令杀死整个进程树。
用 psutil 库递归杀死进程树
multiprocessing.Process.terminate() 只会终止对应的单个进程，如果该进程启动了其他进程，这些“子进程”不会被自动终止，因而可能会在任务管理器中残留。
"""


def kill_process_tree(pid, including_parent=True):
    try:
        parent = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return
    children = parent.children(recursive=True)
    for child in children:
        child.terminate()
    gone, alive = psutil.wait_procs(children, timeout=5)
    for p in alive:
        p.kill()
    if including_parent:
        if psutil.pid_exists(pid):
            parent.terminate()
            parent.wait(5)


def custom_excepthook(exc_type, exc_value, exc_traceback):
    """
    自定义捕获未知的异常
    :param exc_type:
    :param exc_value:
    :param exc_traceback:
    :return:
    """
    logger.error(f"发生未捕获异常:{exc_type, exc_value}|堆栈追踪：{traceback.print_exception(exc_type, exc_value, exc_traceback)}")


if __name__ == "__main__" and os.path.basename(__file__) == "main.py":

    sys.excepthook = custom_excepthook
    freeze_support()
    # 加载日志配置
    logger.add(
        "./log/main/main_{time:YYYY-MM-DD}.log",
        rotation="00:00",  # 日志文件转存
        retention="30 days",  # 多长时间之后清理
        enqueue=True,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} |{process.name} | {thread.name} |  {name} : {module}:{line} | {message}"
    )
    logger.info(f"{'-' * 40}main_start{'-' * 40}")
    logger.info(f"{__name__} | {os.path.basename(__file__)}|{os.getpid()}|{os.getppid()}")

    q = multiprocessing.Queue()  # 创建 Queue 消息传递
    # p_comm = Process(target=run_comm_program, name="p_comm")
    # p_gui = Process(target=run_gui_program, name="p_gui")

    # p_deep_camera = Process(target=run_deep_camera_program, name="p_deep_camera")
    # p_infrared_camera = Process(target=run_infrared_camera_program, name="p_infrared_camera")

    # p_comm = Process(target=main_comm.main, name="p_comm")
    p_response_comm = Process(target=main_response_Modbus.main, name="p_response_comm")
    p_gui = Process(target=main_gui.main, name="p_gui",args=(q,))

    p_deep_camera = Process(target=main_deep_camera.main, name="p_deep_camera",args=(q,))
    p_infrared_camera = Process(target=main_infrared_camera.main, name="p_infrared_camera",args=(q,))
    # try:
    #     logger.info(f"p_comm子进程开始运行")
    #     p_comm.start()
    # except Exception as e:
    #     logger.error(f"p_comm子进程发生异常：{e} |  异常堆栈跟踪：{traceback.print_exc()}，准备终止该子进程")
    #     if p_comm.is_alive():
    #         kill_process_tree(p_comm.pid)
    #         p_comm.join(timeout=5)
    #     pass

    try:
        logger.info(f"p_response_comm子进程开始运行")
        p_response_comm.start()
    except Exception as e:
        logger.error(f"p_response_comm子进程发生异常：{e} |  异常堆栈跟踪：{traceback.print_exc()}，准备终止该子进程")
        if p_response_comm.is_alive():
            kill_process_tree(p_response_comm.pid)
            p_response_comm.join(timeout=5)
    try:
        logger.info(f"p_deep_camera子进程开始运行")
        p_deep_camera.start()
    except Exception as e:
        logger.error(f"p_deep_camera子进程发生异常：{e} |  异常堆栈跟踪：{traceback.print_exc()}，准备终止该子进程")
        if p_deep_camera.is_alive():
            kill_process_tree(p_deep_camera.pid)
            p_deep_camera.join(timeout=5)
    try:
        logger.info(f"p_infrared_camera子进程开始运行")
        p_infrared_camera.start()
    except Exception as e:
        logger.error(f"p_infrared_camera子进程发生异常：{e} |  异常堆栈跟踪：{traceback.print_exc()}，准备终止该子进程")
        if p_infrared_camera.is_alive():
            kill_process_tree(p_infrared_camera.pid)
            p_infrared_camera.join(timeout=5)
    try:
        logger.info(f"p_gui子进程开始运行")
        p_gui.start()
    except Exception as e:
        logger.error(f"p_gui子进程发生异常：{e} |  异常堆栈跟踪：{traceback.print_exc()}，准备终止该子进程")
        if p_gui.is_alive():
            kill_process_tree(p_gui.pid)
            p_gui.join(timeout=5)
    # 如果gui进程死亡 则将其他的进程全部终止
    is_loop = True
    while is_loop:

        # 检测 gui 进程是否存活
        if not p_gui.is_alive():
            logger.error(f"p_gui子进程已停止，同步终止p_comm子进程")
            if p_deep_camera.is_alive():
                kill_process_tree(p_deep_camera.pid)
                logger.error(f"终止p_deep_camera子进程")
                p_deep_camera.join(timeout=5)
                pass
            if p_infrared_camera.is_alive():
                kill_process_tree(p_infrared_camera.pid)
                logger.error(f"终止p_infrared_camera子进程")
                p_infrared_camera.join(timeout=5)
                pass
            if p_response_comm.is_alive():
                kill_process_tree(p_infrared_camera.pid)
                logger.error(f"终止p_response_comm子进程")
                p_response_comm.join(timeout=5)
                pass

            # if p_comm.is_alive():
            #     # 先尝试正常终止
            #     kill_process_tree(p_comm.pid)
            #     logger.error(f"终止p_comm子进程")
            #     # 等待一会儿，确保结束
            #     p_comm.join(timeout=5)
            is_loop = False
            break
        time.sleep(0.5)

    # 等待所有子进程退出
    # p_comm.join()
    p_response_comm.join()
    p_infrared_camera.join()
    p_deep_camera.join()
    p_gui.join()

else:
    pass
