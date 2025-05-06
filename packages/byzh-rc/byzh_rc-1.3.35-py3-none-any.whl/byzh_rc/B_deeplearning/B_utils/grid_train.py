from ...B_tools.B_writer import BWriter
from ...B_basic.Btext_style import BColor
from ...B_tools.B_table import BRowTable, BXYTable
from typing import Union
import time

Iter = Union[list, set, tuple]

def grid_trains_1d(func, x_name:str, iters:Iter, log_path):
    """
    x从iters中取
    :param func: 只有一个输入参数x, 返回值将转化为str并记录
    :param iters:
    :param log_path:
    :return:
    """
    print(f"{BColor.CYAN}=====================")
    print("grid_trains_1d 将在3秒后开始:")
    print(f"====================={BColor.RESET}")
    time.sleep(3)

    my_writer = BWriter(log_path, ifTime=False)
    my_table = BRowTable([x_name, "result"])

    for x in iters:
        result = func(x)
        my_table.append([x, result])

        string = my_table.get_table_by_str()
        my_writer.clearFile()
        my_writer.toFile("[grid_trains] 运行中", ifTime=True)
        my_writer.toFile(string)

    string = my_table.get_table_by_str()
    my_writer.clearFile()
    my_writer.toFile("[grid_trains] 运行结束", ifTime=True)
    my_writer.toFile(string)

def grid_trains_2d(func, x_name:str, x_iters:Iter, y_name:str, y_iters:Iter, log_path):
    print(f"{BColor.CYAN}=====================")
    print("grid_trains_2d 将在3秒后开始:")
    print(f"====================={BColor.RESET}")
    time.sleep(3)

    my_writer = BWriter(log_path, ifTime=False)
    my_table = BXYTable(x_name, y_name, x_iters, y_iters)
    for x in x_iters:
        for y in y_iters:
            result = func(x, y)
            my_table[x][y] = result

            string = my_table.get_table_by_str()
            my_writer.clearFile()
            my_writer.toFile("[grid_trains] 运行结束", ifTime=True)
            my_writer.toFile(string)

    string = my_table.get_table_by_str()
    my_writer.clearFile()
    my_writer.toFile("[grid_trains] 运行结束", ifTime=True)
    my_writer.toFile(string)

if __name__ == '__main__':
    def function(x):
        return x

    grid_trains_1d(function, [1,2,3], './awa.txt')
