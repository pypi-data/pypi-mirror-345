# multicloud-storage

一个统一操作 MinIO、阿里云 OSS 与任意 S3 协议兼容存储（如 AWS S3、DigitalOcean Spaces、腾讯 COS 等）的 Python 工具包。



## 项目目录

```bash
multicloud-storage/               # 仓库根（含中划线）
├── README.md                     # 项目说明
├── requirements.txt              # 列出所有第三方依赖
├── setup.py                      # 安装脚本，从 requirements.txt 动态读取依赖
└── multicloud_storage/           # Python 包名（下划线）
    ├── core/                     # 核心模块：抽象、工厂、解析器、注册表
    │   ├── __init__.py
    │   ├── base.py               # StorageClient 抽象基类
    │   ├── registry.py           # 注册表：@register_provider + get_client
    │   ├── url_parser.py         # Oxylabs 风格 storage_url 解析器
    │   └── factory.py            # create_storage_client 工厂方法
    └── clients/                  # 各厂商 SDK 实现
        ├── __init__.py		
        ├── minio_client.py       # minio（minio SDK）
        ├── oss2_client.py        # oss (oss2 SDK)
        └── s3_compat_client.py	  # s3（boto3 SDK）
```

------



## 安装

### 本地可编辑安装（开发模式）

```bash
git clone https://github.com/your_username/multicloud-storage.git
cd multicloud-storage
pip install -e .
```

### 直接从 GitHub 安装

```
pip install -e git+https://github.com/your_username/multicloud-storage.git#egg=multicloud-storage
```

或在项目的 `requirements.txt` 加入：

```
-e git+https://github.com/your_username/multicloud-storage.git#egg=multicloud-storage
```

然后：

```
pip install -r requirements.txt
```



## 扩展新厂商

1. 在 multicloud_storage/clients/ 下创建新模块 new_client.py

2. 编写继承 StorageClient 的类，并加 @register_provider('new_name')

3. 安装／更新后即可通过 provider='new_name' 使用，无需修改核心代码。

   

无需修改核心代码，按下面步骤即可“即插即用”：

1. 在独立包或本地 `multicloud_storage/clients/` 下新建文件 `new_provider_client.py`

2. 实现并注册：

   ```python
   from multicloud_storage.core.base import StorageClient
   from multicloud_storage.core.registry import register_provider
   import newprovider_sdk
   
   @register_provider('newprovider')
   class NewProviderClient(StorageClient):
       def __init__(self, endpoint, access_key, secret_key, bucket, prefix='', **kw):
           super().__init__(prefix)
           self.client = newprovider_sdk.Client(endpoint, access_key, secret_key, bucket)
   
       def upload_file(self, local_path, key):
           self.client.upload(self._full_key(key), local_path)
       def download_file(self, key, local_path):
           self.client.download(self._full_key(key), local_path)
       def delete(self, key):
           self.client.delete(self._full_key(key))
       def generate_presigned_url(self, key, expires_in=3600):
           return self.client.sign_url(self._full_key(key), expires_in)
   ```
   
   

## 在其他项目，如 yt-downloader 项目中本地使用示例

假设你的项目结构如下：

```bash
yt-downloader/
├── app/
│   └── utils/
│       └── multicloud-storage/    ← 已通过 git clone 下载的 multicloud-storage
├── requirements.txt
└── ...
```

**方法一：可编辑安装**

在 `yt-downloader` 根目录执行：

```bash
pip install -e app/utils/multicloud-storage
```

这样，`multicloud_storage` 即可在项目任意处 import，且本地源码修改即时生效。

**方法二：在 requirements.txt 添加**

在 `yt-downloader/requirements.txt` 增加一行：

```txt
-e app/utils/multicloud-storage
```

然后执行：

```bash
pip install -r requirements.txt
```

两种方式安装后，即可在 `yt-downloader` 代码中：

```python
from multicloud_storage.core.factory import create_storage_client

client = create_storage_client(
    provider='minio',
    storage_url='https://AK:SK@minio.example.com/my-bucket/dir'
)
client.upload_file('video.mp4', 'uploads/video.mp4')
```



**注意，这里 使用相对路径，执行 -e 安装后，为了让 pycharm 可以识别到，需要将 multicloud_storage 这个子目录配置为 sources root 才行，配置方法为：右键目录 → Mark Directory as → Sources Root ，然后 重建一下缓存，才能检测出新加的源码目录：File → Invalidate Caches / Restart… → Invalidate and Restart**



------



## 项目架构梳理

对 **核心模块**、**客户端模块** 以及对外的 **统一接口** 的详细说明，用来帮助你快速理解项目架构与调用流程。

------

### 核心模块（Core）

核心模块位于 `multicloud_storage/core/` 下，负责：

1. 定义统一的抽象基类
2. 管理各厂商实现的注册与发现
3. 解析用户传入的 `storage_url`
4. 提供工厂方法生成客户端实例

```bash
multicloud_storage/
└── core/
    ├── base.py         # 抽象基类
    ├── registry.py     # 注册表与自动发现插件
    ├── url_parser.py   # storage_url 解析器
    └── factory.py      # create_storage_client 工厂
```

------

#### 1. `base.py` —— 抽象基类 StorageClient

- **职责**：定义所有具体客户端必须实现的接口，并统一处理 `prefix` 前缀逻辑。

- **主要内容**：

  - `__init__(self, prefix: str = "")`

    - 接收可选的 `prefix`，后续所有对象键都会自动拼接上这段前缀

  - `self._full_key(key: str) → str`

    - 将用户传入的 `key`（如 `"dir/file.txt"`）与 `prefix` 合并

  - 抽象方法（必须由子类实现）：

    ```python
    upload_file(local_path: str, key: str)  
    download_file(key: str, local_path: str)  
    delete(key: str)  
    generate_presigned_url(key: str, expires_in: int) → str
    ```

------

#### 2. `registry.py` —— 注册表与插件发现

- **职责**：维护“provider 名称 → 客户端类” 的映射，并在包加载时自动扫描插件。

- **主要内容**：

  - 内部字典 `_registry: Dict[str, Type]`

  - 装饰器 `@register_provider(name: str)`

    ```python
    @register_provider('minio')
    class MinioClient(StorageClient): ...
    ```
    
    向 `_registry['minio']` 注册 `MinioClient`
    
  - 包导入时扫描 setuptools `entry_points('multicloud_storage.providers')`，自动加载第三方插件

  - 工厂辅助函数 `get_client(provider: str, **kwargs)`

    - 从 `_registry` 取出对应类并实例化

------

#### 3. `url_parser.py` —— Oxylabs 风格 URL 解析器

- **职责**：把类似

  ```bash
  https://ACCESS:SECRET@host[:port]/bucket[/prefix/...]
  ```
  
  的 URL 拆解成工厂方法需要的参数：
  
  ```python
  {
    "endpoint": "https://host[:port]",
    "access_key": ACCESS,
    "secret_key": SECRET,
    "bucket": bucket,
    "prefix": "optional/prefix"
  }
  ```
  
- **主要函数**：

  ```python
  def parse_storage_url(storage_url: str) -> Dict[str,str]:
      ...
  ```

------

#### 4. `factory.py` —— 统一工厂方法

- **职责**：对外暴露单一入口 `create_storage_client()`，支持两种初始化方式：

  1. **通过 `storage_url`**（Oxylabs 风格）
  2. **通过显式参数**：`endpoint`、`access_key`、`secret_key`、`bucket`、`prefix?`、`region?`、`use_ssl?`

- **主要函数**：

  ```python
  def create_storage_client(*,
                            provider: str = None,
                            storage_url: str = None,
                            **kwargs) -> StorageClient:
      # 1. 若传 storage_url，则先 parse
      # 2. 将 parse 得到的参数与 kwargs 合并
      # 3. 调用 get_client(provider, **params)
      # 4. 返回 StorageClient 子类实例
  ```
  
- **外部调用**：

  ```python
  from multicloud_storage.core.factory import create_storage_client
  
  client = create_storage_client(
      provider='minio',
      storage_url='https://AK:SK@minio.example.com/bucket/prefix'
  )
  # 或
  client = create_storage_client(
      provider='oss',
      endpoint='https://oss-cn-region.aliyuncs.com',
      access_key='AK',
      secret_key='SK',
      bucket='bucket',
      prefix='prefix',
  )
  ```

------

### 客户端模块（Clients）

每个客户端模块都放在 `multicloud_storage/clients/`，各自独立，只依赖其对应的 SDK，并通过装饰器注册到核心注册表。

```bash
multicloud_storage/
└── clients/
    ├── minio_client.py       # MinIO（minio SDK）
    ├── oss2_client.py        # 阿里云 OSS（oss2 SDK）
    └── s3_compat_client.py   # S3 兼容（boto3 SDK）
```

------

#### 1. `minio_client.py` —— MinioClient

- **注册名称**：`"minio"`

- **依赖**：`minio` 官方 SDK

- **构造参数**：`endpoint, access_key, secret_key, bucket, prefix="", use_ssl=True`

- **实现方法**：

  ```python
  upload_file → client.fput_object(bucket, full_key, local_path)
  download_file → client.fget_object(bucket, full_key, local_path)
  delete → client.remove_object(bucket, full_key)
  generate_presigned_url → client.presigned_get_object(bucket, full_key, expires)
  ```

------

#### 2. `oss2_client.py` —— OSS2Client

- **注册名称**：`"oss"`

- **依赖**：`oss2` 官方 SDK

- **构造参数**：`endpoint, access_key, secret_key, bucket, prefix=""`

- **实现方法**：

  ```python
  upload_file → client.put_object_from_file(full_key, local_path)
  download_file → client.get_object_to_file(full_key, local_path)
  delete → client.delete_object(full_key)
  generate_presigned_url → client.sign_url('GET', full_key, expires)
  ```

------

#### 3. `s3_compat_client.py` —— S3CompatClient

- **注册名称**：`"s3_compatible"`

- **依赖**：`boto3` + `botocore.config.Config(signature_version='s3v4', s3={'addressing_style':'path'})`

- **构造参数**：`endpoint, access_key, secret_key, bucket, prefix="", region=None, use_ssl=True`

- **实现方法**：

  ```python
  upload_file → client.upload_file(Filename=..., Bucket=bucket, Key=full_key)
  download_file → client.download_file(Bucket=bucket, Key=full_key, Filename=...)
  delete → client.delete_object(Bucket=bucket, Key=full_key)
  generate_presigned_url → client.generate_presigned_url(ClientMethod='get_object',
                                                          Params={...}, ExpiresIn=...)
  ```

------

### 统一接口（对外调用）

所有具体客户端都遵循同一套接口，业务方只需记住这四个方法，与底层 SDK、厂商实现完全无关：

| 方法                                      | 功能                               | 参数说明                                                     |
| ----------------------------------------- | ---------------------------------- | ------------------------------------------------------------ |
| `upload_file(local_path, key)`            | 上传本地文件到对象存储             | `local_path`：本地文件路径 `key`：对象键（不含 bucket/prefix） |
| `download_file(key, local_path)`          | 下载远程对象到本地                 | `key`：对象键 `local_path`：本地保存路径                     |
| `delete(key)`                             | 删除远程对象                       | `key`：对象键                                                |
| `generate_presigned_url(key, expires_in)` | 生成一个临时可公开访问的预签名 URL | `key`：对象键 `expires_in`：过期时长（秒）                   |

------

### 示例代码

```python
from multicloud_storage.core.providers import MINIO, OSS, S3_COMPATIBLE, DEFAULT_PROVIDERS
from multicloud_storage.core.factory import create_storage_client

print("内置支持的后端：", DEFAULT_PROVIDERS)

# 方法一：使用 storage_url
# 使用内置 provider
client = create_storage_client(
    provider=MINIO,
    storage_url='https://AK:SK@minio.example.com/my-bucket/pfx'
)
client.upload_file('local.txt', 'docs/report.txt')
url = client.generate_presigned_url('docs/report.txt', expires_in=600)
print(url)

# 方法二：显式参数
# 使用自定义扩展 provider
# （假设 elsewhere 已 register_provider('custom') 并实现了客户端）
client = create_storage_client(
    provider='custom',
    endpoint="https://custom.example.com",
    access_key="AK",
    secret_key="SK",
    bucket="custom-bucket"
)

# S3_COMPATIBLE
client = create_storage_client(
    provider='S3_COMPATIBLE',
    endpoint='https://s3.amazonaws.com',
    access_key='AWS_KEY',
    secret_key='AWS_SECRET',
    bucket='aws-bucket',
    prefix='backups',
    region='us-west-2',
    use_ssl=True
)
client.download_file('backups/db.sql', '/tmp/db.sql')
```





## 推送到 PyPI

> **前提**：已经在 `setup.py` 中正确配置了 `name="multicloud-storage"`、`version="0.1.0"` 等信息。

1. **安装打包工具**

   ```bash
   pip install --upgrade build twine
   ```
   
2. **生成分发包**
    在项目根目录（含 `setup.py`）下运行：

   ```bash
   python -m build
   ```
   
   该命令会生成：
   
   ```bash
   dist/
     multicloud-storage-0.1.0-py3-none-any.whl
     multicloud-storage-0.1.0.tar.gz
   ```
   
3. **上传到测试仓库（可选）**
    先向 TestPyPI 验证包是否正常：

   ```bash
   twine upload --repository testpypi dist/*
   ```
   
   然后可以使用：
   
   ```
   pip install --index-url https://test.pypi.org/simple/multicloud-storage
   ```

   验证安装无误后，再推到正式 PyPI。
   
4. **上传到正式 PyPI**

   ```bash
   twine upload dist/*
   ```
   
   执行后输入你的 PyPI 用户名和密码，即可将包发布到 `https://pypi.org/project/multicloud-storage/`。
   
5. **确认安装**
    在任意新环境中运行：

   ```bash
   pip install multicloud-storage
   ```
   
   然后在 Python 中试：
   
   ```python
    import multicloud_storage
   print(multicloud_storage.__version__)  # 应显示 0.1.0
    ```

------

**小贴士**

- **版本管理**：每次发布新版本，都要在 `setup.py` 中更新 `version=`，并打对应的 Git tag（如 `v0.1.1`），再重复“生成分发包 → 上传”步骤。

- **README 渲染**：如果你在 `setup.py` 中指定 `long_description=Path('README.md').read_text(encoding='utf-8')`，并在 `setup()` 里加上

  ```python
  long_description_content_type='text/markdown',
  ```
  
  那么 PyPI 页面会自动渲染你的 README.md。
  
- **CI/CD 集成**：可以在 GitHub Actions、Travis CI 等里把上述打包和上传流程自动化，减少手工步骤。

按照以上流程，就能顺利地把 `multicloud-storage` 同步托管到 GitHub 并发布到 PyPI，供所有人通过 `pip install multicloud-storage` 使用。







