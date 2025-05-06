"""
进程管理工具模块

该模块提供了与进程管理相关的工具函数，包括：
- 查找进程ID
- 保存PID文件
- 读取PID文件
"""
import json
import os
import time
import socket
import psutil
import sys
import tempfile
from filelock import FileLock
from typing import List, Dict, Any, Optional, Tuple
from logging import error
from ..utils.logger import verbose


def find_server_process_by_command(command: str, args: List[str]) -> Optional[int]:
    """
    根据命令和参数查找匹配的进程并返回其PID
    针对Python CLI启动的MCP服务器进程进行了特殊处理

    Args:
        command: 命令名称 (如 'python' 或 'npx')
        args: 命令参数 (如 ['-m', 'server_name'] 或 ['-y', '@package/name'])

    Returns:
        匹配进程的PID，如果没找到则返回None
    """
    try:
        command_str = ' '.join([command] + args)
        verbose(f"[Runner] 查找进程，命令: {command_str}")

        import sys

        # 检测是否为Windows系统
        is_windows = sys.platform == "win32"

        # 提取关键标识符 - 对于MCP服务器尤其重要
        # 通常是最后一个参数或包含@的参数
        key_identifiers = []
        server_name = None

        # 查找包含 @ 的参数，通常是包名或服务器标识
        for arg in args:
            if '@' in arg:
                key_identifiers.append(arg)
                # 保存可能的服务器名称
                if '/' in arg:
                    # 对于 @scope/package 格式，提取 package 部分
                    server_name = arg.split('/', 1)[1] if arg.startswith('@') else arg

        # 如果没有找到包含 @ 的参数，使用最后一个参数
        if not key_identifiers and args:
            key_identifiers.append(args[-1])
            server_name = args[-1]

        # 加入命令本身作为标识符
        if command not in ['python', 'python3', 'node', 'npx', 'uvx', 'npm']:
            key_identifiers.append(command)

        verbose(f"[Runner] 使用关键标识符: {key_identifiers}")

        # 1. 首先尝试直接匹配完整命令行
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline']:
                    proc_cmd = ' '.join(proc.info['cmdline'])
                    # 检查命令是否完全匹配
                    if command_str in proc_cmd:
                        verbose(f"[Runner] 找到完全匹配进程 PID: {proc.info['pid']}, 命令行: {proc_cmd}")
                        return proc.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        # 2. 处理NPX和Node特殊情况
        if command.lower() == 'npx':
            # 通常npx会启动node进程
            node_patterns = ["node", "node.exe"]
            if len(args) >= 2 and args[0] == '-y':
                # 如果是npx -y package的格式，实际执行的可能是node命令
                package_name = args[1]
                verbose(f"[Runner] NPX命令检测：寻找包含 '{package_name}' 的Node进程")

                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['cmdline']:
                            cmdline = proc.info['cmdline']
                            cmd_str = ' '.join(cmdline)

                            # 检查是否是node进程并且命令行包含包名
                            proc_name = os.path.basename(cmdline[0].lower())
                            if (any(pattern in proc_name for pattern in node_patterns) and
                                    package_name in cmd_str):
                                verbose(f"[Runner] 找到匹配的NPX启动的进程 PID: {proc.info['pid']}, 命令行: {cmd_str}")
                                return proc.info['pid']
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass

        # 3. 查找Python CLI启动的子进程
        parent_processes = []
        child_processes = []

        # 特别检查可能是Python/Node启动的进程
        potential_parent_commands = ['python', 'python3', 'node', 'node.exe']

        # 查找所有潜在的父进程和子进程
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline']:
                    cmdline = proc.info['cmdline']
                    proc_cmd = ' '.join(cmdline)

                    # 检查是否是可能的父进程
                    proc_name = os.path.basename(cmdline[0].lower())
                    if any(parent_cmd in proc_name for parent_cmd in potential_parent_commands):
                        # 如果命令行包含任何关键标识符，这可能是我们要找的进程
                        if any(identifier in proc_cmd for identifier in key_identifiers):
                            parent_processes.append((proc.info['pid'], proc_cmd))

                    # 记录所有可能的子进程
                    if server_name and server_name.lower() in proc_cmd.lower():
                        child_processes.append((proc.info['pid'], proc_cmd))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        # 4. 如果找到了可能的父进程，返回最匹配的一个
        if parent_processes:
            # 按照命令行长度排序，更长的命令行通常包含更多信息，匹配度更高
            parent_processes.sort(key=lambda x: len(x[1]), reverse=True)
            verbose(f"[Runner] 找到最匹配的父进程 PID: {parent_processes[0][0]}, 命令行: {parent_processes[0][1]}")
            return parent_processes[0][0]

        # 5. 如果没有找到父进程，但找到了可能的子进程，返回第一个
        if child_processes:
            verbose(f"[Runner] 找到可能的服务器进程 PID: {child_processes[0][0]}, 命令行: {child_processes[0][1]}")
            return child_processes[0][0]

        verbose("[Runner] 未找到匹配的服务器进程")
        return None
    except Exception as e:
        error(f"[Runner] 查找进程异常: {str(e)}")
        return None


def save_pid_to_file(server_pid: int, server_name: str, client_name: str, command: str, args: List[str]) -> Optional[str]:
    """
    将进程ID保存到PID文件，记录MCP服务器的使用情况，包括客户端名称。
    同时查找并保存与该MCP服务器相关的进程ID（包括父进程和子进程）。

    Args:
        server_pid: 服务器进程ID
        server_name: MCP服务器名称
        client_name: 客户端名称
        command: 启动命令
        args: 命令参数

    Returns:
        成功时返回PID文件路径，失败时返回None
    """
    # 获取PID文件路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(current_dir))
    pid_file = os.path.join(base_dir, "pids", "run-mcp-srv.pid")
    lock_file = f"{pid_file}.lock"

    try:
        # 获取当前CLI进程的PID
        cli_pid = os.getpid()
        verbose(f"[Runner] 当前CLI进程PID: {cli_pid}")

        # 获取客户端进程ID（可能是第三级父进程）
        client_pid = None
        try:
            # 尝试找到三级父进程（如果存在）
            try:
                process = psutil.Process(server_pid)
                parent = process.parent()
                if parent:
                    grandparent = parent.parent()
                    if grandparent:
                        # 找到三级父进程
                        client_pid = grandparent.pid
                        if client_pid:
                            verbose(f"[Runner] 找到MCP服务器的三级父进程 PID: {client_pid}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                verbose(f"[Runner] 无法获取进程 {server_pid} 的父进程")

            verbose(f"[Runner] 为MCP服务器 {server_name} 找到客户端进程ID: {client_pid}")
        except Exception as e:
            verbose(f"[Runner] 查找客户端进程时出错: {str(e)}")

        with FileLock(lock_file, timeout=5):
            pid_data = {}

            # 如果文件存在，读取现有数据
            if os.path.exists(pid_file):
                with open(pid_file, 'r') as f:
                    content = f.read().strip()
                    if not content:
                        verbose(f"[Runner] PID文件为空: {pid_file}")
                        content = '{}'
                    pid_data = json.loads(content)

            # 如果当前服务器名称不存在，初始化为数组
            if server_name not in pid_data:
                pid_data[server_name] = []

            # 客户端信息
            client_info = {
                "client_name": client_name,
                "server_id": server_pid,  # mcp server 服务器进程ID
                "client_pid": client_pid,  # 客户端进程ID（第三级父进程）
                "cli_pid": cli_pid,       # 当前CLI进程的PID
                "command": command,
                "args": args,
                "timestamp": int(time.time()),
                "hostname": os.uname().nodename if hasattr(os, 'uname') else socket.gethostname()
            }

            # 检查是否已存在相同客户端，如果存在则更新
            found = False
            for i, entry in enumerate(pid_data[server_name]):
                if entry.get("client_name") == client_name:
                    pid_data[server_name][i] = client_info
                    found = True
                    break

            # 如果不存在，则添加到列表
            if not found:
                pid_data[server_name].append(client_info)

            # 写回文件
            with open(pid_file, 'w') as f:

                json.dump(pid_data, f, indent=2)

            verbose(f"[Runner] PID信息已保存到文件: {pid_file}")
            return pid_file

    except Exception as e:
        error(f"[Runner] 保存PID文件失败: {str(e)}")
        return None


def read_pid_file() -> Optional[Dict[str, Any]]:
    """
    读取PID文件，按优先级尝试查找并读取PID文件
    使用文件锁防止与并发写入操作的冲突

    Returns:
        成功时返回PID信息字典，失败时返回None
    """
    # 按照写入文件时的优先级顺序尝试查找
    # 1. 项目内部日志目录
    try:
        # 获取PID文件路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(os.path.dirname(current_dir))
        pid_file = os.path.join(base_dir, "pids", "run-mcp-srv.pid")
        lock_file = f"{pid_file}.lock"

        if os.path.exists(pid_file):
            # 使用文件锁防止与并发写入操作冲突
            with FileLock(lock_file, timeout=2):
                with open(pid_file, 'r') as f:
                    pid_info = json.load(f)
                    verbose(f"[Runner] 从项目日志目录读取到PID信息: {pid_info}")
                    return pid_info
    except Exception as e:
        verbose(f"[Runner] 读取项目日志目录PID文件失败: {str(e)}")

    # 2. 用户主目录
    try:
        home_dir = os.path.expanduser("~")
        pid_file = os.path.join(home_dir, ".mcpdock", "run-mcp-srv.pid")
        lock_file = f"{pid_file}.lock"

        if os.path.exists(pid_file):
            # 使用文件锁防止与并发写入操作冲突
            with FileLock(lock_file, timeout=2):
                with open(pid_file, 'r') as f:
                    pid_info = json.load(f)
                    verbose(f"[Runner] 从用户主目录读取到PID信息: {pid_info}")
                    return pid_info
    except Exception as e:
        verbose(f"[Runner] 读取用户主目录PID文件失败: {str(e)}")

    # 3. 系统临时目录
    try:
        temp_dir = tempfile.gettempdir()
        pid_file = os.path.join(temp_dir, "mcpdock-srv.pid")
        lock_file = f"{pid_file}.lock"

        if os.path.exists(pid_file):
            # 使用文件锁防止与并发写入操作冲突
            with FileLock(lock_file, timeout=2):
                with open(pid_file, 'r') as f:
                    pid_info = json.load(f)
                    verbose(f"[Runner] 从临时目录读取到PID信息: {pid_info}")
                    return pid_info
    except Exception as e:
        verbose(f"[Runner] 读取临时目录PID文件失败: {str(e)}")

    verbose("[Runner] 在所有位置均未找到有效的PID文件")
    return None


def is_process_running(pid: int) -> bool:
    """
    检查指定PID的进程是否正在运行

    Args:
        pid: 进程ID

    Returns:
        进程是否存在且正在运行
    """
    try:
        # 检查进程是否存在
        process = psutil.Process(pid)
        # 进一步检查进程状态
        return process.is_running() and process.status() != psutil.STATUS_ZOMBIE
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return False
    except Exception as e:
        error(f"[Runner] 检查进程状态异常: {str(e)}")
        return False


def check_server_process() -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    检查MCP服务器进程是否正在运行

    Returns:
        (是否正在运行, PID信息)
    """
    # 尝试读取PID文件
    pid_info = read_pid_file()
    if not pid_info:
        return False, None

    # 获取PID - 兼容新旧格式：先尝试读取server_id，如果不存在则使用pid字段
    server_id = pid_info.get("server_id")
    if not server_id:
        server_id = pid_info.get("pid")  # 兼容旧格式

    if not server_id:
        return False, pid_info

    # 检查进程是否在运行
    is_running = is_process_running(server_id)
    return is_running, pid_info


def check_server_by_package_name(package_name: str) -> Tuple[bool, Optional[int]]:
    """
    通过包名检查MCP服务器是否正在运行

    这个方法不依赖PID文件，而是直接搜索运行中的进程，查找包含指定包名的进程

    Args:
        package_name: 服务器包名，如 '@suekou/mcp-notion-server'

    Returns:
        (是否正在运行, 进程ID如果找到)
    """
    try:
        verbose(f"[Runner] 通过包名搜索服务器进程: {package_name}")

        # 处理包名格式
        server_id = package_name
        server_name = None

        # 处理 @scope/package 格式
        if '/' in package_name and package_name.startswith('@'):
            # 提取包名的主要部分（不含scope）
            server_name = package_name.split('/', 1)[1]
        else:
            server_name = package_name

        # 去除特殊字符，便于匹配
        clean_name = server_name.replace('-', '').lower() if server_name else ''

        # 潜在进程类型
        potential_cmd_patterns = ['node', 'python', 'python3']
        matching_processes = []

        # 搜索所有匹配的进程
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline']:
                    cmdline = proc.info['cmdline']
                    cmd_str = ' '.join(cmdline).lower()

                    # 检查命令行是否包含包名
                    if package_name.lower() in cmd_str:
                        matching_processes.append((proc.info['pid'], cmd_str, 3))  # 完全匹配权重最高
                    elif server_name and server_name.lower() in cmd_str:
                        matching_processes.append((proc.info['pid'], cmd_str, 2))  # 不含scope的包名匹配
                    elif clean_name and clean_name in cmd_str.replace('-', ''):
                        matching_processes.append((proc.info['pid'], cmd_str, 1))  # 去除横线后的匹配

                    # 特殊检测: 看命令行是否有可能是MCP服务器
                    proc_base = os.path.basename(cmdline[0]).lower()
                    if any(pattern in proc_base for pattern in potential_cmd_patterns):
                        if 'mcp' in cmd_str and (server_name in cmd_str or clean_name in cmd_str.replace('-', '')):
                            matching_processes.append((proc.info['pid'], cmd_str, 2))  # MCP相关进程

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        # 按照匹配权重和命令行长度排序
        if matching_processes:
            # 先按权重排序，权重相同时按命令行长度排序
            matching_processes.sort(key=lambda x: (x[2], len(x[1])), reverse=True)
            best_match = matching_processes[0]
            verbose(f"[Runner] 找到匹配的服务器进程 PID: {best_match[0]}, 命令行: {best_match[1]}")
            return True, best_match[0]

        verbose(f"[Runner] 未找到包含 '{package_name}' 的服务器进程")
        return False, None
    except Exception as e:
        error(f"[Runner] 通过包名查找进程异常: {str(e)}")
        return False, None


def find_child_processes(parent_pid: int, server_id: Optional[str] = None) -> List[Tuple[int, str]]:
    """
    查找指定父进程的所有子进程

    Args:
        parent_pid: 父进程ID
        server_id: 可选的服务器标识符，用于过滤子进程

    Returns:
        匹配的子进程列表，每项包含(pid, 命令行)
    """
    try:
        matching_children = []

        # 尝试获取父进程
        try:
            parent = psutil.Process(parent_pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            verbose(f"[Runner] 无法访问父进程 PID: {parent_pid}")
            return matching_children

        # 获取所有子进程
        children = parent.children(recursive=True)

        # 如果没有指定服务器ID，返回所有子进程
        if not server_id:
            return [(child.pid, ' '.join(child.cmdline())) for child in children if child.is_running()]

        # 处理服务器标识符以便匹配
        server_name = None
        clean_name = None

        # 处理 @scope/package 格式
        if server_id and '/' in server_id and server_id.startswith('@'):
            server_name = server_id.split('/', 1)[1]
        else:
            server_name = server_id

        # 去除特殊字符以便更灵活匹配
        if server_name:
            clean_name = server_name.replace('-', '').lower()

        # 过滤匹配的子进程
        for child in children:
            try:
                if not child.is_running():
                    continue

                cmd_str = ' '.join(child.cmdline()).lower()

                # 使用多种匹配策略
                if server_id and server_id.lower() in cmd_str:
                    matching_children.append((child.pid, cmd_str))
                elif server_name and server_name.lower() in cmd_str:
                    matching_children.append((child.pid, cmd_str))
                elif clean_name and clean_name in cmd_str.replace('-', ''):
                    matching_children.append((child.pid, cmd_str))
                elif 'mcp' in cmd_str and (server_name in cmd_str or
                                           (clean_name and clean_name in cmd_str.replace('-', ''))):
                    matching_children.append((child.pid, cmd_str))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # 子进程可能已经结束
                continue

        # 按命令行长度排序，通常更长的命令行包含更多信息
        matching_children.sort(key=lambda x: len(x[1]), reverse=True)

        if matching_children:
            verbose(f"[Runner] 找到 {len(matching_children)} 个匹配的子进程，第一个: "
                    f"PID: {matching_children[0][0]}, 命令行: {matching_children[0][1]}")
        else:
            verbose(f"[Runner] 未找到父进程 {parent_pid} 下匹配的子进程")

        return matching_children
    except Exception as e:
        error(f"[Runner] 查找子进程异常: {str(e)}")
        return []


def find_server_process_from_current() -> Tuple[bool, Optional[int], Optional[str]]:
    """
    从当前进程开始，查找MCP服务器进程

    利用进程的父子关系，查找当前CLI工具启动的MCP服务器进程

    Returns:
        (是否找到, 进程ID, 命令行)
    """
    try:
        # 获取当前进程ID
        current_pid = os.getpid()
        verbose(f"[Runner] 当前进程ID: {current_pid}")

        # 查找当前进程启动的所有子进程
        child_processes = find_child_processes(current_pid)

        if not child_processes:
            verbose("[Runner] 当前进程没有子进程")
            return False, None, None

        # 过滤可能是MCP服务器的子进程
        mcp_candidates = []

        for pid, cmd_str in child_processes:
            cmd_lower = cmd_str.lower()
            # 查找命令行中包含MCP相关关键词的进程
            if any(kw in cmd_lower for kw in ['mcp', 'notion-server', 'node', 'python']):
                mcp_candidates.append((pid, cmd_str))

        if mcp_candidates:
            # 按命令行长度排序
            mcp_candidates.sort(key=lambda x: len(x[1]), reverse=True)
            best_match = mcp_candidates[0]
            verbose(f"[Runner] 找到最可能的MCP服务器进程: PID: {best_match[0]}, 命令行: {best_match[1]}")
            return True, best_match[0], best_match[1]

        verbose("[Runner] 未找到可能的MCP服务器子进程")
        return False, None, None
    except Exception as e:
        error(f"[Runner] 从当前进程查找服务器异常: {str(e)}")
        return False, None, None


def remove_pid_by_server_name(server_name: str, client_name: Optional[str] = None, target_pid: Optional[int] = None) -> None:
    """
    根据服务器名称或目标进程ID从PID文件中移除对应的PID信息。
    支持通过当前CLI进程ID匹配删除记录。

    Args:
        server_name: 服务器名称
        client_name: 客户端名称（如果提供，只移除该客户端的记录；否则移除服务器的所有记录）
        target_pid: 目标进程ID（如果提供，会匹配server_id、client_pid和cli_pid）

    Returns:
        None
    """
    try:
        # 获取当前CLI进程ID
        current_cli_pid = os.getpid()
        verbose(f"[Runner] 当前CLI进程PID: {current_cli_pid}")

        # 获取PID文件路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(os.path.dirname(current_dir))
        pid_file = os.path.join(base_dir, "pids", "run-mcp-srv.pid")
        lock_file = f"{pid_file}.lock"

        # 使用文件锁防止并发写入
        with FileLock(lock_file, timeout=5):
            if not os.path.exists(pid_file):
                verbose(f"[Runner] PID文件不存在: {pid_file}")
                return

            with open(pid_file, 'r') as f:
                content = f.read().strip()
                if not content:
                    verbose(f"[Runner] PID文件为空: {pid_file}")
                    return
                pid_data = json.loads(content)

            # 检查服务器名称是否存在
            if server_name not in pid_data:
                verbose(f"[Runner] 服务器名称 {server_name} 不存在于PID文件中")
                return

            entries_to_remove = []

            # 优先使用当前CLI进程ID匹配记录
            for i, entry in enumerate(pid_data[server_name]):
                cli_pid = entry.get("cli_pid")

                # 如果当前CLI进程ID与记录中的CLI PID匹配，标记为删除
                if cli_pid == current_cli_pid:
                    entries_to_remove.append(i)
                    verbose(f"[Runner] 通过当前CLI进程ID {current_cli_pid} 找到匹配记录，客户端: {entry.get('client_name')}")

            # 如果没有通过CLI PID找到记录且提供了目标进程ID，查找所有包含该PID的记录
            if not entries_to_remove and target_pid:
                for i, entry in enumerate(pid_data[server_name]):
                    server_id = entry.get("server_id")
                    client_pid = entry.get("client_pid")
                    cli_pid = entry.get("cli_pid")

                    # 检查目标PID是否匹配服务器ID、客户端进程ID或CLI进程ID
                    if server_id == target_pid or client_pid == target_pid or cli_pid == target_pid:
                        entries_to_remove.append(i)
                        verbose(f"[Runner] 已找到匹配目标PID {target_pid} 的记录，客户端: {entry.get('client_name')}")

            # 如果通过PID未找到记录且提供了客户端名称，只移除该客户端的记录
            elif not entries_to_remove and client_name:
                for i, entry in enumerate(pid_data[server_name]):
                    if entry.get("client_name") == client_name:
                        entries_to_remove.append(i)
                        verbose(f"[Runner] 已找到客户端 {client_name} 的记录")
                        break

            # 如果既没有通过PID找到记录也没有指定客户端名称，移除服务器的所有记录
            elif not entries_to_remove and not target_pid and not client_name:
                verbose(f"[Runner] 移除服务器 {server_name} 的所有记录")
                del pid_data[server_name]

            # 按索引从高到低删除，避免索引变化导致的问题
            if entries_to_remove:
                entries_to_remove.sort(reverse=True)
                for i in entries_to_remove:
                    removed_entry = pid_data[server_name].pop(i)
                    verbose(f"[Runner] 已从文件中移除记录，客户端: {removed_entry.get('client_name')}, "
                            f"服务器ID: {removed_entry.get('server_id')}, 客户端进程ID: {removed_entry.get('client_pid')}, "
                            f"CLI进程ID: {removed_entry.get('cli_pid')}")

                # 如果该服务器没有客户端了，移除服务器记录
                if not pid_data[server_name]:
                    del pid_data[server_name]
                    verbose(f"[Runner] 服务器 {server_name} 没有客户端记录，已移除")

            # 如果文件中没有服务器了，删除文件
            if not pid_data:
                os.remove(pid_file)
                verbose(f"[Runner] PID文件已被删除: {pid_file}")
            else:
                # 否则更新文件内容
                with open(pid_file, 'w') as f:
                    json.dump(pid_data, f, indent=2)
                verbose(f"[Runner] PID文件已更新")
    except Exception as e:
        error(f"[Runner] 移除PID记录失败: {str(e)}")
