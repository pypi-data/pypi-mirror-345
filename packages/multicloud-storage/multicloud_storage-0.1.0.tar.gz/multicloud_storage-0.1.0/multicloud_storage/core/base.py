from abc import ABC, abstractmethod

class StorageClient(ABC):
    """
    抽象基类，定义统一接口并实现 prefix 逻辑。
    prefix：对象键的统一前缀，可为空。
    """

    def __init__(self, prefix: str = ""):
        # 存储前缀（去除尾部斜杠），后续所有 key 方法都自动拼上这个前缀
        self.prefix = prefix.rstrip("/")

    def _full_key(self, key: str) -> str:
        """
        将用户传入的 key（可以包含斜杠）拼接 prefix：
        - 若 prefix 为空，直接返回 key
        - 否则返回 "{prefix}/{key.lstrip('/')}"
        """
        key = key.lstrip("/")
        return f"{self.prefix}/{key}" if self.prefix else key

    @abstractmethod
    def upload_file(self, local_path: str, key: str) -> None:
        """
        上传本地文件到对象存储。
        :param local_path: 本地文件绝对或相对路径
        :param key: 对象键（相对于 bucket 和 prefix）
        """

    @abstractmethod
    def download_file(self, key: str, local_path: str) -> None:
        """
        下载对象到本地文件。
        :param key: 对象键
        :param local_path: 本地保存路径
        """

    @abstractmethod
    def delete(self, key: str) -> None:
        """
        删除存储中的对象。
        :param key: 对象键
        """

    @abstractmethod
    def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """
        生成对象的预签名 URL（默认 3600 秒后过期）。
        :param key: 对象键
        :param expires_in: 过期时间（秒）
        :return: 带签名的 URL 字符串
        """
