import os
import platform
import hashlib
import psutil
import sys
import inspect
import base64
import secrets
import orjson as json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding


def _ki():
    """
    Get kernel information.
    """
    info = {
        "kernel_version": platform.release(),
        "kernel_full": platform.version(),
        "system": platform.system(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "uname": platform.uname()._asdict(),
    }
    with open("/proc/version", "r") as f:
        info["proc_version"] = f.read().strip()
    with open("/proc/sys/kernel/osrelease", "r") as f:
        info["osrelease"] = f.read().strip()
    with open("/proc/cmdline", "r") as f:
        info["cmdline"] = f.read().strip()
    return info


def _rp():
    """
    Check all running processes.
    """
    processes = []
    for proc in psutil.process_iter(["name", "exe", "cmdline"]):
        try:
            pinfo = proc.info
            pinfo["username"] = proc.username()
            processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return processes


def _op():
    """
    Check information about our own process.
    """
    current_process = psutil.Process()
    return {
        "pid": current_process.pid,
        "exe": current_process.exe(),
        "cmdline": current_process.cmdline(),
        "cwd": current_process.cwd(),
    }


def _rc():
    """
    Inspect the currently running Python code.
    """
    current_frame = inspect.currentframe()
    call_stack = inspect.stack()
    stack_info = []
    for frame_info in call_stack:
        stack_info.append(
            {
                "filename": frame_info.filename,
                "line_number": frame_info.lineno,
                "function": frame_info.function,
                "code_context": frame_info.code_context,
            }
        )
    loaded_modules = {}
    for name, module in sys.modules.items():
        if hasattr(module, "__file__"):
            loaded_modules[name] = module.__file__
    current_file = frame_info.filename
    frame_info = inspect.getframeinfo(current_frame)
    source_code = None
    if os.path.exists(current_file):
        with open(current_file, "r") as f:
            source_code = {"path": current_file, "content": f.read()}
    return {
        "stack_info": stack_info,
        "loaded_modules": loaded_modules,
        "sys_path": sys.path,
        "source_code": source_code,
    }


# __pyarmor_entrance__
def signature(salt):
    """
    Generate a signature of the running app.
    """
    sig_data = [
        _op(),
        _rc(),
    ]
    return hashlib.sha256(json.dumps(sig_data) + salt.encode()).hexdigest()


# __pyarmor_entrance__
def dump(key):
    """
    Dump all info and encrypt with key.
    """
    data = json.dumps(
        [
            _ki(),
            _op(),
            _rc(),
            _rp(),
        ]
    )
    padder = padding.PKCS7(128).padder()
    iv = secrets.token_bytes(16)
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend(),
    )
    padded_data = padder.update(data) + padder.finalize()
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(iv + encrypted_data).decode()
