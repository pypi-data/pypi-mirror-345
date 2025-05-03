import os

from ..B_basic.Btext_style import BColor
from pathlib import Path
import subprocess
import time

def args_process(args: tuple) -> list:
    lst = []
    for x in args:
        if type(x) is str:
            lst.append(x)
        elif type(x) is list:
            lst.extend(x)
    return lst

def b_run_cmd(
        *args: str,
        show: bool = True,
):
    '''
    可传入多个字符串, 在cmd中运行
    :param args:
    :param show: 若show=True, 则会单开一个cmd, 在cmd中运行
    :return:
    '''
    command = ''
    for i in range(len(args)):
        if i == len(args) - 1:
            command += str(args[i])
            break
        command += str(args[i]) + ' && '
    if show:
        command = f'start cmd /K "{command}"'
    # print(command)
    subprocess.run(command, shell=True)

def b_run_python(
    *args: str|list[str],
    limit_time: int|float|None = None,
    log_path: Path|None = None
):
    '''
    可传入多个字符串, 在当前python环境下运行
    :param args: 以python开头, 用于运行.py文件
    :param show:
    :return:
    '''
    def run_log(content=''):
        if log_path is not None:
            parent = Path(log_path).parent
            os.makedirs(parent, exist_ok=True)
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write("=====================\n")
                for string in str_lst:
                    f.write("\t" + string + '\n')
                f.write("=====================\n")
                f.write(content)

    str_lst = args_process(args)

    print(f"{BColor.GREEN}=====================")
    print("BRunPython 将在3秒后开始:")
    for string in str_lst:
        print("\t" + string)
    print(f"====================={BColor.RESET}")
    time.sleep(3)

    for string in str_lst:
        try:
            command_lst = string.split(' ')
            run_log("正在执行: " + string)
            result = subprocess.run(command_lst, timeout=limit_time)
            if result.returncode != 0:
                index = str_lst.index(string)
                str_lst[index] = string + "\t[Error!!!]"
        except subprocess.TimeoutExpired:
            print(f"程序运行超过 {limit_time} 秒，已被强制终止")
            index = str_lst.index(string)
            str_lst[index] = string + "\t[Time limit!!!]"

    print(f"{BColor.GREEN}=====================")
    print("BRunPython 结束:")
    for string in str_lst:
        print("\t"+string)
    print(f"====================={BColor.RESET}")

    run_log('结束')



if __name__ == '__main__':
    b_run_cmd("echo hello", "echo world", "echo awa", show=True)
    # b_run_python(
    #     r"python E:\byzh_workingplace\byzh-rc-to-pypi\test1.py",
    #     r"python E:\byzh_workingplace\byzh-rc-to-pypi\test2.py",
    #     limit_time=3,
    # )