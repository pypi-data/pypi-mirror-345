import oss2
from multicloud_storage.core.base import StorageClient
from multicloud_storage.core.registry import register_provider
from multicloud_storage.core.providers import OSS

@register_provider(OSS)
class OSS2Client(StorageClient):
    """
    阿里云 OSS 客户端，使用官方 oss2 SDK。
    """

    def __init__(self,
                 endpoint: str,
                 access_key: str,
                 secret_key: str,
                 bucket: str,
                 prefix: str = ""):
        """
        :param endpoint: OSS Endpoint，例如 https://oss-cn-hangzhou.aliyuncs.com
        :param access_key: AccessKeyId
        :param secret_key: AccessKeySecret
        :param bucket: 存储桶名称
        :param prefix: 公共前缀
        """
        super().__init__(prefix)
        auth = oss2.Auth(access_key, secret_key)
        self.bucket = bucket
        self.client = oss2.Bucket(auth, endpoint, bucket)

    def upload_file(self, local_path: str, key: str) -> None:
        """
        本地文件上传到 OSS。
        """
        full_key = self._full_key(key)
        self.client.put_object_from_file(full_key, local_path)

    def download_file(self, key: str, local_path: str) -> None:
        """
        从 OSS 下载对象到本地。
        """
        full_key = self._full_key(key)
        self.client.get_object_to_file(full_key, local_path)

    def delete(self, key: str) -> None:
        """
        删除 OSS 上的对象。
        """
        full_key = self._full_key(key)
        self.client.delete_object(full_key)

    def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """
        生成带签名的 GET URL。
        """
        full_key = self._full_key(key)
        return self.client.sign_url('GET', full_key, expires_in)
