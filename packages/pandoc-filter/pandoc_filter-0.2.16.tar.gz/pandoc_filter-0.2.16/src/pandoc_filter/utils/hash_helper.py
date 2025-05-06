import hashlib
import urllib.parse
import pathlib

def get_text_hash(text:str)->str:
    """
    Normalize the input text to a hash string. This is the global hash function for this project.
    
    There are several steps to normalize the input text:
        1. Decode the url-encoded text.
        2. Strip the leading and trailing spaces.
        3. Lower the text.
        4. Hash the text.
    """
    text = urllib.parse.unquote(text).strip(' ').lower() # 需要统一小写以获取更大的兼容性
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def get_text_file_hash(file_path:pathlib.Path)->str:
    with open(file_path, "r", encoding="utf-8") as file:
        file_data  = file.read()
    return hashlib.sha256(file_data.encode('utf-8')).hexdigest()

def get_raw_file_hash(file_path:pathlib.Path)->str:
    with open(file_path, "rb") as file:
        file_data  = file.read()
    return hashlib.sha256(file_data).hexdigest()