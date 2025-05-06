import re

def __get_attribute(text:str,attribute:str)->str|None:
    match = re.search(rf"{attribute}=['\"]([^'\"]+)['\"]",text)
    if match:
        return str(match.group(1))
    else:
        return None
def __sub_attribute(text:str,attribute:str,sub_string:str)->str:
    return re.sub(rf"({attribute}=['\"])([^'\"]+)(['\"])", f"\\g<1>{sub_string}\\g<3>", text)

# href
def get_html_href(text:str)->str|None:
    return __get_attribute(text,"href")
    
def sub_html_href(text:str,sub_string:str)->str:
    return __sub_attribute(text,"href",sub_string)

# id
def get_html_id(text:str)->str|None:
    return __get_attribute(text,"id")

def sub_html_id(text:str,sub_string:str)->str:
    return __sub_attribute(text,"id",sub_string)

# src
def get_html_src(text:str)->str|None:
    return __get_attribute(text,"src")

def sub_html_src(text:str,sub_string:str)->str:
    return __sub_attribute(text,"src",sub_string)