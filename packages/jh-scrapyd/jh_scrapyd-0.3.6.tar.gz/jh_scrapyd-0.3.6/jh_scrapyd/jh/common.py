import json
import platform
import psutil


def platform_os() -> str:
    """Get platform"""
    system = platform.system()
    if system == 'Linux':
        return 'linux'
    elif system == 'Darwin':
        return 'mac os'
    elif system == 'Windows':
        return 'windows'


def is_windows() -> bool:
    """Is it a Windows environment"""
    return platform_os() == 'windows'


def str_decode(b: str):
    """String decoding"""
    if isinstance(b, bytes):
        return b.decode('utf-8', errors='ignore')
    else:
        return str(b)


def data_encode(input_dict: dict):
    """Encode data into JSON format"""
    if not input_dict:
        return None
    return json.dumps(input_dict)


def data_decode(input_dict: str):
    """Decoding JSON formatted data"""
    if not input_dict:
        return None
    return json.loads(input_dict)


def process_dict_recursively(data, process_fn, parent_key=None, **kwargs):
    """
    Recursively process each element in a dictionary.

    :param data: The dictionary to process.
    :param process_fn: A function that takes a key and value as arguments and performs some operation.
    :param parent_key: The key of the parent element in case of nested dictionaries.
    :param kwargs: Any parameter.
    :return: A new dictionary with the processed elements.
    """
    if isinstance(data, dict):
        return {k: process_dict_recursively(v, process_fn, k, **kwargs) for k, v in data.items()}
    elif isinstance(data, list):
        return [process_dict_recursively(element, process_fn, parent_key, **kwargs) for element in data]
    else:
        return process_fn(parent_key, data, **kwargs)


def kill_process(pid: int) -> bool:
    """
    终止指定进程及其所有子进程，确保资源清理。

    :param pid: 主进程ID
    :return: 成功终止返回 True，否则返回 False
    """
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)

        # 先终止子进程（SIGTERM）
        for child in children:
            try:
                child.terminate()
            except psutil.NoSuchProcess:
                pass

        # 等待子进程退出，超时后强制终止（SIGKILL）
        _, alive = psutil.wait_procs(children, timeout=5)
        for proc in alive:
            try:
                proc.kill()
            except psutil.NoSuchProcess:
                pass

        # 终止父进程（SIGTERM -> SIGKILL）
        try:
            parent.terminate()
            parent.wait(timeout=5)
        except psutil.TimeoutExpired:
            parent.kill()
            parent.wait(timeout=2)
        except psutil.NoSuchProcess:
            pass

        # 最终检查进程是否已终止
        return not psutil.pid_exists(pid)

    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        print(f"Error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False