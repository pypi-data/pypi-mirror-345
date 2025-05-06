from typing import TypedDict
import urllib.parse
import pathlib
import panflute as pf

from .logging_helper import TracingLogger
from .html_helper import sub_html_href
from .oss_helper import OssHelper
        
class InternalLink():
    def __init__(self,elem:pf.Link|pf.RawInline,url:str,guessed_url:str|None) -> None:
        self.elem = elem
        self.url = url
        self.guessed_url = guessed_url
    def sub(self,text:str,tracing_logger:TracingLogger)->None:
        tracing_logger.mark(self.elem)
        if isinstance(self.elem, pf.Link):
            self.elem.url = f"#{text}"
        else: # RawInline
            self.elem.text = sub_html_href(self.elem.text,f"#{text}")
        tracing_logger.check_and_log('internal_link',self.elem)

class DocRuntimeDict(TypedDict):
    anchor_count:dict[str,int]|None
    internal_link_record:list[InternalLink]|None
    equations_count:int|None
    math:bool|None
    doc_path:pathlib.Path|None
    oss_helper:OssHelper|None

def decode_internal_link_url(url:str)->str:
    r"""When converting markdown to any type via pandoc, internal links' URLs may be automatically URL-encoded before any filter works.
    The encoding is done by default and may not be avoided.
    This function is used to decode the URL.
    """
    decoded_url = urllib.parse.unquote(url.lstrip('#'))
    header_mimic = pf.convert_text(f"# {decoded_url}",input_format='markdown',output_format='gfm',standalone=True)
    return f"#{header_mimic.lstrip('# ')}"

def decode_src_url(url:str)->str:
    r"""When converting markdown to any type via pandoc, some elements' `src` URLs may be automatically URL-encoded before any filter works.
    The encoding is done by default and may not be avoided.
    This function is used to decode the URL.
    """
    return urllib.parse.unquote(url)
