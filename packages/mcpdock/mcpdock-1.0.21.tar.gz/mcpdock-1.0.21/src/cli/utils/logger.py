import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from ..config.app_config import APP_ENV

# Get log directory based on environment


def get_log_directory():
    """
    根据环境变量和操作系统确定日志文件的保存位置

    根据不同环境选择不同的日志目录:
    - dev: 使用项目目录下的logs/cli
    - test/prod: 
      - Windows: 使用%APPDATA%\mcpdock\logs
      - macOS/Linux: 使用~/.mcpdock/logs
    - 如果无法创建上述目录，则使用系统临时目录

    Returns:
        日志目录路径
    """
    # 检测操作系统
    import sys
    is_windows = sys.platform == "win32"

    # 1. 根据环境变量选择合适的目录
    if APP_ENV == 'dev':
        # 开发环境：尝试使用项目目录
        try:
            current_path = Path(__file__).resolve()
            for parent in current_path.parents:
                if parent.name == 'cli':
                    log_dir = os.path.join(parent, 'logs', 'cli')
                    os.makedirs(log_dir, exist_ok=True)
                    return log_dir
            # 如果找不到cli目录，回退到上级目录
            project_dir = current_path.parents[2]  # 回退到上级目录
            log_dir = os.path.join(project_dir, 'logs', 'cli')
            os.makedirs(log_dir, exist_ok=True)
            return log_dir
        except Exception as e:
            print(f"Warning: Could not create log directory in project folder: {e}")

    # 2. 生产/测试环境：根据操作系统选择合适的目录
    try:
        if is_windows:
            # Windows环境：使用 APPDATA 目录
            app_data = os.environ.get('APPDATA', '')
            if app_data:
                log_dir = os.path.join(app_data, 'mcpdock', 'logs', 'cli')
            else:
                # 如果APPDATA不可用，回退到用户主目录
                home_dir = os.path.expanduser("~")
                log_dir = os.path.join(home_dir, 'mcpdock', 'logs', 'cli')
        else:
            # macOS/Linux环境：使用用户主目录下的.mcpdock文件夹
            home_dir = os.path.expanduser("~")
            log_dir = os.path.join(home_dir, '.mcpdock', 'logs', 'cli')

        os.makedirs(log_dir, exist_ok=True)
        return log_dir
    except Exception as e:
        print(f"Warning: Could not create log directory in user folder: {e}")

    # 3. 最终回退：使用系统临时目录
    try:
        temp_dir = tempfile.gettempdir()
        log_dir = os.path.join(temp_dir, 'mcpdock-logs', 'cli')
        os.makedirs(log_dir, exist_ok=True)
        return log_dir
    except Exception as e:
        print(f"Critical: Could not create log directory in temp folder: {e}")
        # 最后的回退方案：返回当前目录
        return '.'


# Set date format
date = datetime.now()
date_str = f"{date.year}-{date.month}-{date.day}"


def create_dir_if_not_exist(dir_name: str):
    """Create directory if it doesn't exist"""
    dir_path = os.path.join(get_log_directory(), dir_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)


# Define log formatter
class CustomFormatter(logging.Formatter):
    def __init__(self, worker_id: str = 'main'):
        super().__init__(fmt='[%(levelname)s] - [%(asctime)s] [%(worker_id)s] %(message)s',
                         datefmt='%Y-%m-%d %H:%M:%S.%f')
        self.worker_id = worker_id

    def format(self, record):
        record.worker_id = self.worker_id
        return super().format(record)


# Create CLI Logger
cli_logger = logging.getLogger('cli_logger')
cli_logger.setLevel(logging.DEBUG)

# Log file location
log_directory = get_log_directory()
cli_log_file = os.path.join(log_directory, f'{date_str}.log')

# Prevent duplicate logs if logger is imported multiple times
if not cli_logger.handlers:
    # File handler
    fh_cli = logging.FileHandler(cli_log_file, encoding='utf-8')
    fh_cli.setLevel(logging.DEBUG)
    fh_cli.setFormatter(CustomFormatter())
    cli_logger.addHandler(fh_cli)

    # Console handler: 仅在开发环境或DEBUG_STDIO_RUNNER=1时输出到终端
    # if APP_ENV == "dev":
    # ch_cli = logging.StreamHandler()
    # ch_cli.setLevel(logging.DEBUG)
    # ch_cli.setFormatter(CustomFormatter())
    # cli_logger.addHandler(ch_cli)


def verbose(message: str, err: Optional[Any] = False) -> None:
    """Logs a verbose message to both file and console (if INFO level)"""
    if err:
        cli_logger.error(message)
    else:
        cli_logger.debug(message)

# def verbose(message: str) -> None:
#     """Logs a verbose message to both file and console (if INFO level)"""
#     cli_logger.debug(message)


# For compatibility with existing code
debug = cli_logger.debug
info = cli_logger.info
warning = cli_logger.warning
error = cli_logger.error
critical = cli_logger.critical
