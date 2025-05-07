from typing import Any, Dict
from multicloud_storage.core.registry import get_client
from multicloud_storage.core.url_parser import parse_storage_url

def create_storage_client(*,
                          provider: str = None,
                          storage_url: str = None,
                          **kwargs: Any) -> Any:
    """
    创建统一的 StorageClient 实例，支持两种方式：

    1) 通过 storage_url 初始化（Oxylabs 风格）：
       create_storage_client(
           provider='oss',
           storage_url='https://AK:SK@host/bkt/pfx'
       )

    2) 通过拆解后的参数初始化：
       create_storage_client(
           provider='minio',
           endpoint='https://minio...',
           access_key='AK',
           secret_key='SK',
           bucket='my-bucket',
           prefix='pfx',
           region='us-east-1',
           use_ssl=False
       )

    :param provider: 必填，注册时使用的名称（如 "minio","oss","s3_compatible" 或自定义扩展名）
    :param storage_url: 带凭证和路径的完整 URL
    :param kwargs: 拆解后的参数覆写（endpoint, access_key, secret_key, bucket, prefix, region, use_ssl）
    :return: StorageClient 子类实例
    """
    if not provider:
        raise ValueError("必须指定 provider")

    params: Dict[str, Any] = {}

    # 如果提供了 storage_url，则先解析
    if storage_url:
        parsed = parse_storage_url(storage_url)
        params.update(parsed)

    # 再用显式传入的 kwargs 覆盖解析结果
    params.update(kwargs)

    # 返回对应的客户端实例
    return get_client(provider, **params)
