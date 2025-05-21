import multiprocessing
import subprocess
import sys
import time

import psutil
from loguru import logger

from config.global_setting import global_setting

venv_python = sys.executable


def run_comm_program():
    subprocess.run([venv_python, "D:\WorkSpace\pythonProjectAnimal\main_comm.py"])


def run_gui_program():
    subprocess.run([venv_python, "D:\WorkSpace\pythonProjectAnimal\main_gui.py"])


def run_deep_camera_program():
    subprocess.run([venv_python, "D:\WorkSpace\pythonProjectAnimal\main_deep_camera.py"])


def run_infrared_camera_program():
    subprocess.run([venv_python, "D:\WorkSpace\pythonProjectAnimal\main_infrared_camera.py"])


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
        parent.terminate()
        parent.wait(5)


if __name__ == "__main__":
    # 加载日志配置
    logger.add(
        "./log/main/main_{time:YYYY-MM-DD}.log",
        rotation="00:00",  # 日志文件转存
        retention="30 days",  # 多长时间之后清理
        enqueue=True,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} |{process.name} | {thread.name} |  {name} : {module}:{line} | {message}"
    )
    logger.info(f"{'-' * 40}main_start{'-' * 40}")

    p_comm = multiprocessing.Process(target=run_comm_program)

    p_gui = multiprocessing.Process(target=run_gui_program)
    p_deep_camera = multiprocessing.Process(target=run_deep_camera_program)
    p_infrared_camera = multiprocessing.Process(target=run_infrared_camera_program)
    try:
        logger.info(f"p_comm子进程开始运行")
        p_comm.start()
    except Exception as e:
        logger.error(f"p_comm子进程发生异常：{e}，准备终止该子进程")
        if p_comm.is_alive():
            kill_process_tree(p_comm.pid)
        pass
    try:
        logger.info(f"p_deep_camera子进程开始运行")
        p_deep_camera.start()
    except Exception as e:
        logger.error(f"p_deep_camera子进程发生异常：{e}，准备终止该子进程")
        if p_deep_camera.is_alive():
            kill_process_tree(p_deep_camera.pid)
    try:
        logger.info(f"p_infrared_camera子进程开始运行")
        p_infrared_camera.start()
    except Exception as e:
        logger.error(f"p_infrared_camera子进程发生异常：{e}，准备终止该子进程")
        if p_infrared_camera.is_alive():
            kill_process_tree(p_infrared_camera.pid)
    try:
        logger.info(f"p_gui子进程开始运行")
        p_gui.start()
    except Exception as e:
        logger.error(f"p_gui子进程发生异常：{e}，准备终止该子进程")
        if p_gui.is_alive():
            kill_process_tree(p_gui.pid)
    # 如果gui进程死亡 则将其他的进程全部终止
    is_loop = True
    while is_loop:
        # 检测 gui 进程是否存活
        if not p_gui.is_alive():
            logger.error(f"p_gui子进程已停止，同步终止p_comm子进程")
            if p_comm.is_alive():
                # 先尝试正常终止
                kill_process_tree(p_comm.pid)
                logger.error(f"终止p_comm子进程")
                kill_process_tree(p_deep_camera.pid)
                logger.error(f"终止p_deep_camera子进程")
                kill_process_tree(p_infrared_camera.pid)
                logger.error(f"终止p_infrared_camera子进程")
                # 等待一会儿，确保结束
                p_comm.join(timeout=5)
                p_deep_camera.join(timeout=5)
                p_infrared_camera.join(timeout=5)
                is_loop = False
            break
        time.sleep(0.5)

    # 等待所有子进程退出
    p_comm.join()

    p_gui.join()
