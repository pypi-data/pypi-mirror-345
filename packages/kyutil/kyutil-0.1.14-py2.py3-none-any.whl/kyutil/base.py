# -*- coding: UTF-8 -*-
"""基础类"""
import base64
import decimal
import fcntl
import hashlib
import json
import os
import re
from datetime import date, datetime
from hashlib import md5 as hash_md5
from hashlib import sha256 as hash_s256

from kyutil.reg_exp import URL_REG

HTTP = "http://"
TMP_PATH = "/ctdy/"
HTTPS = "https://"


def is_url(url):
    if not url:
        return None
    return re.findall(URL_REG, url)


def request_data(request):
    """
    请求参数转换为字典
    @param request:
    @return:
    """
    try:
        return dict(**dict(request.json), **dict(request.args), **dict(request.form), **dict(request.values))
    except Exception:
        return dict(request.args or request.form)


def get_err_msg(code) -> str:
    """
    获取自定义错误码信息
    @param code:
    @return:
    """
    fp = os.path.dirname(__file__) + os.sep + "code.json"
    if os.path.exists(fp):
        with open(fp, encoding="utf-8") as f:
            try:
                d2 = json.loads(f.read())
                return d2[str(code)[0]]["codes"][str(code)]
            except ValueError:
                return ''
    return ""


def sha256(s: str) -> str:
    """
    生成md5
    @param s:
    @return:

    Returns:
        object:
    """
    m = hash_s256()
    m.update(str(s).encode())
    return m.hexdigest()


def md5_file(file_path) -> str:
    """
    获取文件md5
    @param file_path:
    @return:
    """
    return hash_file(file_path, hash_md5())


def sha256_file(file_path):
    m = hashlib.sha256()  # 创建md5对象
    return hash_file(file_path, m)


def hash_file(file_path, m) -> str:
    """
    获取文件的加密值
    @param file_path:
    @param m:
    @return:
    """
    if os.path.isfile(file_path):
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(4096)
                if not data:
                    break
                m.update(data)  # 更新md5对象

        return m.hexdigest()  # 返回md5对象


def send_chunk(path2file):
    """ 流式读取"""
    with open(path2file, 'rb') as target_file:
        while True:
            chunk = target_file.read(20 * 1024 * 1024)  # 每次读取20M
            if not chunk:
                break
            yield chunk


def encode_base64(input_string):
    # 将字符串转换为字节串
    input_bytes = input_string.encode('utf-8')
    # 使用 base64 对字节串进行编码
    encoded_bytes = base64.b64encode(input_bytes)
    # 将编码后的字节串转换回字符串
    encoded_string = encoded_bytes.decode('utf-8')
    return encoded_string


def decode_base64(encoded_string):
    # 将字符串转换为字节串
    encoded_bytes = encoded_string.encode('utf-8')
    # 使用 base64 对字节串进行解码
    decoded_bytes = base64.b64decode(encoded_bytes)
    # 将解码后的字节串转换回字符串
    decoded_string = decoded_bytes.decode('utf-8')
    return decoded_string


def format_slashes(path):
    return re.sub(r'/{2,}', '/', path)


def get_parent_path(path, levels_up=1):
    for _ in range(levels_up):
        path = os.path.dirname(path)
    return path


def get_base_arch(iso_name):
    if iso_name.find("arm64") >= 0:
        return "aarch64"
    elif iso_name.find("aarch64") >= 0:
        return 'aarch64'
    elif iso_name.find("x86_64") >= 0:
        return 'x86_64'
    elif iso_name.find("loongarch64") >= 0:
        return 'loongarch64'
    else:
        return ''


def acquire_lock(lock_file):
    """ 获取文件锁 """
    dir_path = os.path.dirname(lock_file)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    lock_fd = os.open(lock_file, os.O_RDWR | os.O_CREAT)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return lock_fd
    except IOError:
        return None


def release_lock(lock_fd):
    """ 释放文件锁 """
    fcntl.flock(lock_fd, fcntl.LOCK_UN)
    os.close(lock_fd)


def ensure_list(s):
    if isinstance(s, str):
        return [s]
    return s


def strip_dict(_params_dict: dict):
    for k, v in _params_dict.items():
        if isinstance(v, list):
            _params_dict[k] = strip_list(v)
        elif isinstance(v, dict):
            _params_dict[k] = strip_dict(v)
        elif isinstance(v, str):
            _params_dict[k] = v.strip() if v else None
        else:
            _params_dict[k] = v
    return _params_dict


def strip_list(l: list):
    r = []
    for i in l:
        if isinstance(i, list):
            r.append(strip_list(i))
        elif isinstance(i, dict):
            r.append(strip_dict(i))
        else:
            r.append(i.strip() if i else None)
    return l


def dict_to_argv(dict_info):
    """dict convert"""
    fake_argv = []
    for key, value in dict_info.items():
        arg_str = f"--{key}={value}"
        fake_argv.append(arg_str)
    return fake_argv


class DateEncoder(json.JSONEncoder):
    """日期转换"""

    def default(self, obj):
        """
        默认的日期格式
        @param obj:
        @return:
        """
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        else:
            return json.JSONEncoder.default(self, obj)
