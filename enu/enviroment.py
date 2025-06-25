import os
import platform
import winreg
from enum import Enum
from pathlib import Path

from loguru import logger


class pc_environment(Enum):
    """
    PC环境枚举
    """
    Windows ='Windows'
    Linux = 'Linux'
    MacOS = 'Darwin'
    Others = 'Others'
class enviroment():
    # 环境变量名称
    enviroment_name = 'HOST_COMPUTER_DATA_STORAGE_LOC'
    def __init__(self):
        # 获取当前项目工作路径
        self.project_dir = None
        self.get_working_directory()
        pass
    def read_envir(self):
        """
        获取环境变量
        :return:
        """
        value = os.getenv(self.enviroment_name, 'Default')
        return value
    def get_working_directory(self):
        """
        获取当前工作目录
        :return:
        """
        # 当前脚本文件所在目录
        project_dir = Path(__file__).resolve().parent.parent
        logger.info(f"串口通讯当前项目的工作路径为：{project_dir}")
        self.project_dir=project_dir
        pass
    def is_envir_exist(self):
        """
        读取环境变量是否存在
        :return: True False
        """
        value = os.getenv(self.enviroment_name, 'Default')
        if value =='Default':
            return False
        else:
            logger.info(f"串口通讯-已存在环境变量{self.enviroment_name}")
            return True
    def set_envir(self):
        """
        设置环境变量
        :return:
        """
        # 不存在该环境变量就存储
        if not self.is_envir_exist():
            pc_environment_return = self.get_pc_environment()
            match pc_environment_return:
                case pc_environment.Windows:
                    # windows环境
                    self.set_envir_windows()
                    pass
                case pc_environment.Linux:
                    # linux环境
                    self.set_envir_linux()
                    pass
                case pc_environment.MacOS:
                    # macOs环境
                    self.set_envir_macOs()
                    pass
                case _:
                    # 其他环境
                    self.set_envir_others()
                    pass
            logger.info(f"串口通讯项目环境变量设置成功，{self.enviroment_name}={self.read_envir()}")
    def set_envir_windows(self):
        """
        设置windows系统下的环境变量
        :return:
        """
        # 永久设置环境变量
        # 用户环境变量
        # subprocess.run(['setx',self.enviroment_name, self.project_dir])
        # 打开系统环境变量注册表位置（需要管理员权限）
        reg_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
        try:
            # 打开注册表键，KEY_SET_VALUE 权限用来写
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_SET_VALUE)
            # 设置环境变量
            expanded_value = str(self.project_dir).replace("/", "\\")  # 转换正斜杠为反斜杠（可选）
            winreg.SetValueEx(reg_key, self.enviroment_name, 0, winreg.REG_EXPAND_SZ, expanded_value )
            winreg.CloseKey(reg_key)

            # 通知系统环境变量已更改，刷新环境变量缓存
            import ctypes
            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x1A
            SMTO_ABORTIFHUNG = 0x0002
            result = ctypes.c_long()
            ctypes.windll.user32.SendMessageTimeoutW(HWND_BROADCAST, WM_SETTINGCHANGE, 0,
                                                     "Environment", SMTO_ABORTIFHUNG, 5000,
                                                     ctypes.byref(result))


        except PermissionError:
            logger.error("获取系统环境变量权限不足，请以管理员身份运行该串口通讯程序。")
        pass
    def set_envir_macOs(self):
        """
        设置macOS系统下的环境变量
        :return:
        """
        # # 用户环境变量
        # home_dir = os.path.expanduser("~")
        # bashrc_path = os.path.join(home_dir, '.bashrc')
        #
        # # 添加环境变量到.bashrc
        # with open(bashrc_path, 'a') as f:
        #     f.write(f'export {self.enviroment_name}="{self.project_dir}"\n')
        #
        # # 刷新环境变量
        # subprocess.run(['source', bashrc_path], shell=True)
        env_file = "/etc/environment"
        try:
            with open(env_file, "r") as f:
                lines = f.readlines()
            with open(env_file, "w") as f:
                found = False
                for line in lines:
                    if line.startswith(self.enviroment_name + "="):
                        f.write(f'{self.enviroment_name}="{self.project_dir}"\n')
                        found = True
                    else:
                        f.write(line)
                if not found:
                    f.write(f'{self.enviroment_name}="{self.project_dir}"\n')
        except PermissionError:
            logger.error("获取系统环境变量权限不足，请用 root 用户或 sudo 运行该串口通讯程序。")
        pass
    def set_envir_linux(self):
        """
        设置linux环境下的环境变量
        :return:
        """
        #  用户环境变量
        # home_dir = os.path.expanduser("~")
        # bashrc_path = os.path.join(home_dir, '.bashrc')
        # # 添加环境变量到.bashrc
        # with open(bashrc_path, 'a') as f:
        #     f.write('export MY_ENV_VAR="some_value"\n')
        # # 刷新环境变量
        # subprocess.run(['source', bashrc_path], shell=True)
        env_file = "/etc/environment"
        try:
            with open(env_file, "r") as f:
                lines = f.readlines()
            with open(env_file, "w") as f:
                found = False
                for line in lines:
                    if line.startswith(self.enviroment_name + "="):
                        f.write(f'{self.enviroment_name}="{self.project_dir}"\n')
                        found = True
                    else:
                        f.write(line)
                if not found:
                    f.write(f'{self.enviroment_name}="{self.project_dir}"\n')
        except PermissionError:
            logger.error("获取系统环境变量权限不足，请用 root 用户或 sudo 运行该串口通讯程序。")
        pass
    def set_envir_others(self):
        """
        设置其他环境下的环境变量
        :return:
        """

        logger.error(f"设置环境变量不支持其他环境下设置环境变量，只支持以下环境：{[system.value for system in pc_environment]}")
        pass
    def get_pc_environment(self):
        """
        当前的操作系统环境
        :return:返回 当前操作系统环境
        """
        system = platform.system()

        match system:
            case pc_environment.Windows.value:
                pc_environment_return = pc_environment.Windows
                pass
            case pc_environment.Linux.value:
                pc_environment_return = pc_environment.Linux
                pass
            case pc_environment.MacOS.value:
                pc_environment_return = pc_environment.MacOS
                pass
            case _:
                pc_environment_return = pc_environment.Others
                pass
        return pc_environment_return