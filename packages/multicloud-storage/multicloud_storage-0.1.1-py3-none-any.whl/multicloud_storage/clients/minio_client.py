from minio import Minio
from multicloud_storage.core.base import StorageClient
from multicloud_storage.core.registry import register_provider
from multicloud_storage.core.providers import MINIO

@register_provider(MINIO)
class MinioClient(StorageClient):
    """
    MinIO 客户端，S3 协议兼容存储。
    依赖：minio SDK
    """

    def __init__(self,
                 endpoint: str,
                 access_key: str,
                 secret_key: str,
                 bucket: str,
                 prefix: str = "",
                 use_ssl: bool = True):
        """
        :param endpoint: MinIO 服务地址，例如 https://minio.example.com
        :param access_key: ACCESS_KEY
        :param secret_key: SECRET_KEY
        :param bucket: 存储桶名称
        :param prefix: 公共前缀（路径）
        :param use_ssl: 是否使用 HTTPS
        """
        super().__init__(prefix)
        self.bucket = bucket
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=use_ssl
        )

    def upload_file(self, local_path: str, key: str) -> None:
        """
        上传本地文件到 MinIO。
        """
        full_key = self._full_key(key)
        self.client.fput_object(self.bucket, full_key, local_path)

    def download_file(self, key: str, local_path: str) -> None:
        """
        下载对象到本地文件。
        """
        full_key = self._full_key(key)
        self.client.fget_object(self.bucket, full_key, local_path)

    def delete(self, key: str) -> None:
        """
        删除指定对象。
        """
        full_key = self._full_key(key)
        self.client.remove_object(self.bucket, full_key)

    def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """
        生成对象的预签名 GET URL。
        """
        full_key = self._full_key(key)
        return self.client.presigned_get_object(
            bucket_name=self.bucket,
            object_name=full_key,
            expires=expires_in
        )
