from typing import Type, Dict

import pkg_resources

# 内部注册表：provider_name -> client 类
_registry: Dict[str, Type] = {}

def register_provider(name: str):
    """
    装饰器：将具体 StorageClient 子类注册到 _registry 中。
    用法示例：
        @register_provider('minio')
        class MinioClient(StorageClient): ...
    """
    def decorator(cls: Type):
        _registry[name] = cls
        return cls
    return decorator

# 自动加载通过 entry_points 注册的插件
for ep in pkg_resources.iter_entry_points('multicloud_storage.providers'):
    cls = ep.load()
    _registry[ep.name] = cls

def get_client(provider: str, **kwargs):
    """
    工厂接口：根据 provider 名称返回对应的客户端实例。
    :param provider: 注册时指定的名称
    :param kwargs: 该客户端 __init__ 接受的参数
    :return: StorageClient 子类实例
    :raises ValueError: provider 未注册
    """
    cls = _registry.get(provider)
    if not cls:
        raise ValueError(
            f"Unsupported provider '{provider}'. "
            f"已注册的 providers: {', '.join(_registry.keys())}"
        )
    return cls(**kwargs)
