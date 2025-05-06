import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)
import sys
import os
import json
import pandas as pd

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)
from bypy import ByPy
from loguru import logger
import subprocess
import re


def upload_to_baidu(file_name, folder_name, data_df):
    upload_path_temp = fr'D:\upload_temp\{file_name}.csv'
    bp = ByPy()

    data_df.to_csv(upload_path_temp, index=False, encoding='gbk')

    # 上传临时文件到百度云
    remote_path = f'/{folder_name}/{file_name}.csv'
    result = bp.upload(upload_path_temp, remote_path)
    if result == 0:
        logger.info("上传成功:{}", file_name)
    else:
        logger.error("上传失败:{}", file_name)
    del_local_file(upload_path_temp)
    return result


def del_local_file(local_file_path):
    try:
        os.remove(local_file_path)
    except Exception as e:
        print(f"删除文件时出错: {e}")


def mkdir_baidu_new_folder(remote_path):
    bp = ByPy()
    try:
        # 调用 mkdir 方法创建文件夹
        result = bp.mkdir(remote_path)

        if result == 0:
            logger.info("成功创建文件夹:{}", remote_path)
        else:
            logger.error("创建文件夹失败:{}", result)

    except Exception as e:
        logger.error("创建文件夹失败:{}", e)


def del_baidu_old_folder(remote_path):
    bp = ByPy()
    try:
        # 调用 mkdir 方法创建文件夹
        result = bp.delete(remote_path)

        if result == 0:
            logger.info("成功删除文件夹:{}", remote_path)
        else:
            logger.error("删除文件夹失败:{}", result)

    except Exception as e:
        logger.error("删除文件夹失败:{}", e)


def get_file_folder(path):
    result = subprocess.run(
        ['bypy', 'list', path],
        capture_output=True,
        text=True,
        check=True,
        encoding='utf-8'
    )

    # 假设 result 是 subprocess.run 的返回结果
    stdout = result.stdout

    # 正则表达式匹配文件行
    pattern = re.compile(
        r'^[FD]\s+(\S+)\s+(\d+)\s+(\d{4}-\d{2}-\d{2},\s\d{2}:\d{2}:\d{2})\s+([a-zA-Z0-9]{32})$',
        re.IGNORECASE
    )

    data = []
    for line in stdout.split('\n'):
        line = line.strip()
        if not line:
            continue
        match = pattern.match(line)
        if match:
            filename, size, mod_time, hash_val = match.groups()
            # 处理时间格式：替换逗号为空格
            mod_time = mod_time.replace(', ', ' ')
            data.append({
                'name': filename,
                'size': int(size),
                'update_time': mod_time,
                'hash_value': hash_val
            })

    # 创建 DataFrame 并转换时间类型
    df = pd.DataFrame(data)
    if not df.empty:
        df['update_time'] = pd.to_datetime(df['update_time'], format='%Y-%m-%d %H:%M:%S')

    return df


if __name__ == '__main__':
    folder_name1 = '/A股/1分钟/2025/4'
    get_file_folder(folder_name1)
