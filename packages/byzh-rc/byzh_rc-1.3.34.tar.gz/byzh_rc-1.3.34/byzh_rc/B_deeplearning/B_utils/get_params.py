def get_params(model):
    '''
    获取模型参数数量params
    :param model:
    :return:
    '''
    params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return params

if __name__ == '__main__':

    import torchvision.models as models
    # 实例化模型
    model = models.resnet18()
    # 打印参数数量
    print(get_params(model))
