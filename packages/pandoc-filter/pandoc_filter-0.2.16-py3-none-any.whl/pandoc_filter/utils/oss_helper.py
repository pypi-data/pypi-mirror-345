import pathlib
import logging
from .logging_helper import _logger_factory
from .hash_helper import get_text_file_hash,get_raw_file_hash
import oss2
from oss2.credentials import EnvironmentVariableCredentialsProvider
from oss2.models import BucketReferer

class OssHelper:
    def __init__(self,endpoint_name:str,bucket_name:str) -> None:
        self.logger = _logger_factory('logs/oss_log',logging.INFO)
        # self.local_cache_dir = pathlib.Path(local_cache_dir)
        # self.local_relative_root = pathlib.Path(local_relative_root)
        # 从环境变量中获取访问凭证。运行本代码示例之前，请确保已设置环境变量OSS_ACCESS_KEY_ID和OSS_ACCESS_KEY_SECRET。
        self.auth = oss2.ProviderAuth(EnvironmentVariableCredentialsProvider())
        self.endpoint_name = endpoint_name
        self.bucket_name = bucket_name
        self.bucket = oss2.Bucket(self.auth,endpoint=self.endpoint_name,bucket_name=self.bucket_name)
        self.domain = self.bucket.list_bucket_cname().cname[0].domain
        
    def get_hashed_file_name(self,file_path:str):
        file_path:pathlib.Path = pathlib.Path(file_path)
        try:
            with open(file_path,'r', encoding='utf-8') as file:
                file.read()
            file_hash = get_text_file_hash(file_path)
        except UnicodeDecodeError:
            file_hash = get_raw_file_hash(file_path)
        return file_hash+file_path.suffix
    def maybe_upload_file_and_get_src(self,file_path:str)->str:
        r"""Try to upload file to oss. Use hash to indentify all files.
            1. Read and calculate the hash of the input file.
            2. Then get a file name based on the hash.
            3. If the file name has not existed in the bucket, upload the file.
            4. Return the url of the file.
        """
        obj_name = self.get_hashed_file_name(file_path)
        if self.bucket.object_exists(obj_name):
            self.logger.info(f"The object {obj_name} has already existed.")
        else:
            self.bucket.put_object_from_file(obj_name, file_path)
            self.logger.info(f"The object {obj_name} has been uploaded.")
        return f"https://{self.domain}/{obj_name}"