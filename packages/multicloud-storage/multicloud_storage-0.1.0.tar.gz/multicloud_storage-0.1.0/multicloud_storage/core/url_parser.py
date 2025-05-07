from urllib.parse import urlparse, unquote
from typing import Dict

def parse_storage_url(storage_url: str) -> Dict[str, str]:
    """
    将 Oxylabs 风格的 storage_url:
      https://ACCESS:SECRET@host[:port]/bucket[/prefix...]
    解析为 create_storage_client 所需的参数：
      endpoint, access_key, secret_key, bucket, prefix

    :param storage_url: 带凭证和路径的完整 URL
    :return: 参数字典
    :raises ValueError: 若缺少用户名或密码
    """
    parsed = urlparse(storage_url)
    if not parsed.username or not parsed.password:
        raise ValueError("storage_url 必须包含用户名(ACCESS)和密码(SECRET)")
    access_key = unquote(parsed.username)
    secret_key = unquote(parsed.password)
    endpoint = f"{parsed.scheme}://{parsed.hostname}"
    if parsed.port:
        endpoint += f":{parsed.port}"

    # 去掉开头斜杠，分割 bucket 和可选 prefix
    parts = parsed.path.lstrip("/").split("/", 1)
    bucket = parts[0]
    prefix = parts[1].rstrip("/") if len(parts) > 1 else ""

    return {
        "endpoint": endpoint,
        "access_key": access_key,
        "secret_key": secret_key,
        "bucket": bucket,
        "prefix": prefix,
    }
