import torch

def get_device(sout=False):
    lst = []
    # 优先使用NPU
    try:
        import torch_npu
        lst.append(torch.device("npu"))
    except ImportError:
        pass

    # 其次使用GPU
    if torch.cuda.is_available():
        lst.append(torch.device("cuda"))

    # 最后使用CPU
    lst.append(torch.device("cpu"))

    lst_str = [str(i) for i in lst]
    if sout:
        print(f"可用设备:{lst_str}, 使用{lst_str[0]}")
    return lst[0]


if __name__ == '__main__':
    result = get_device()
    print(result)
