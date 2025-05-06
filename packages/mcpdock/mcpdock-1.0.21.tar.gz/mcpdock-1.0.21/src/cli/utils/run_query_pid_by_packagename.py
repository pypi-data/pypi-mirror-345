"""
Utility to query if a process with a specific package name is running by checking its PID.
"""
import os

from cli.utils.logger import verbose
from ..utils.process_utils import read_pid_file


def query_pid_by_packagename(package_names: list) -> dict:
    """
    检查指定包名的进程是否存在于PID文件中。

    参数：
        package_names (list): 要查询的包名列表。

    返回：
        dict: 包含每个包名的PID文件数据（有值为数据，无则为None）。
    """
    if isinstance(package_names, str):
        package_names = [package_names]

    results = {}
    pid_data = read_pid_file()

    if not pid_data:
        verbose(f"未找到任何 PID 文件记录")
        for package_name in package_names:
            results[package_name] = None
        return results

    for package_name in package_names:
        value = None
        # 直接查找包名
        if package_name in pid_data and pid_data[package_name]:
            verbose(f"包名 '{package_name}' 的进程存在于PID文件中")
            value = pid_data[package_name]
        else:
            # 尝试部分匹配
            for server_name, entries in pid_data.items():
                if package_name in server_name and entries:
                    verbose(f"包名 '{package_name}' 匹配服务器 '{server_name}' 存在于PID文件中")
                    value = entries
                    break
            if value is None:
                verbose(f"未找到包名 '{package_name}' 的进程")
        results[package_name] = value
    return results
