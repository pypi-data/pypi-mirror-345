import boto3
from botocore.config import Config
from multicloud_storage.core.base import StorageClient
from multicloud_storage.core.registry import register_provider
from multicloud_storage.core.providers import S3_COMPATIBLE


@register_provider(S3_COMPATIBLE)
class S3CompatClient(StorageClient):
    """
    通用 S3 客户端，兼容 AWS S3、DigitalOcean Spaces、腾讯 COS、Ceph、MinIO 等。
    使用 boto3 SDK。
    """

    def __init__(self,
                 endpoint: str,
                 access_key: str,
                 secret_key: str,
                 bucket: str,
                 prefix: str = "",
                 region: str = None,
                 use_ssl: bool = True):
        """
        :param endpoint: S3 兼容服务地址，例如 https://s3.amazonaws.com
        :param access_key: ACCESS_KEY
        :param secret_key: SECRET_KEY
        :param bucket: 存储桶名称
        :param prefix: 公共前缀
        :param region: 区域（可选）
        :param use_ssl: 是否启用 HTTPS
        """
        super().__init__(prefix)
        cfg = Config(signature_version='s3v4', s3={'addressing_style': 'path'})
        self.bucket = bucket
        self.client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=endpoint,
            region_name=region,
            config=cfg,
            verify=use_ssl
        )

    def upload_file(self, local_path: str, key: str) -> None:
        """
        上传本地文件到 S3 兼容存储。
        """
        full_key = self._full_key(key)
        self.client.upload_file(
            Filename=local_path,
            Bucket=self.bucket,
            Key=full_key
        )

    def download_file(self, key: str, local_path: str) -> None:
        """
        下载对象到本地文件。
        """
        full_key = self._full_key(key)
        self.client.download_file(
            Bucket=self.bucket,
            Key=full_key,
            Filename=local_path
        )

    def delete(self, key: str) -> None:
        """
        删除对象。
        """
        full_key = self._full_key(key)
        self.client.delete_object(Bucket=self.bucket, Key=full_key)

    def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """
        生成预签名 GET URL。
        """
        full_key = self._full_key(key)
        return self.client.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': self.bucket, 'Key': full_key},
            ExpiresIn=expires_in
        )
