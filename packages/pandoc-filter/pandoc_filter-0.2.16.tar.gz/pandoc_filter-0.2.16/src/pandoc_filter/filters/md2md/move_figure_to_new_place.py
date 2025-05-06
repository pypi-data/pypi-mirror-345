import os
import shutil
import urllib.parse
import pathlib

import panflute as pf

from ...utils.logging_helper import TracingLogger

from ...utils.oss_helper import OssHelper

from ...utils.html_helper import get_html_src,sub_html_src

from ...utils.panflute_helper import decode_src_url

from ...utils.hash_helper import get_text_file_hash,get_raw_file_hash



r"""A pandoc filter that mainly for converting `markdown` to `markdown`.
Move local pictures to a new place. Replace the original `src` with the new one.
The new src will only remain the last directory name and the file name.
A root flag '/' will be added to the new src's header.

NOTE:
    The following environment variables should be given in advance:
        $Env:NEW_ASSETS_DIR
    The doc_path should be given in advance.
"""
def _get_hashed_file_name(file_path:str):
    file_path:pathlib.Path = pathlib.Path(file_path)
    try:
        with open(file_path,'r', encoding='utf-8') as file:
            file.read()
        file_hash = get_text_file_hash(file_path)
    except UnicodeDecodeError:
        file_hash = get_raw_file_hash(file_path)
    return file_hash+file_path.suffix

def _copy_figure(file_path):
    new_path = pathlib.Path(os.environ['NEW_ASSETS_DIR'])/_get_hashed_file_name(file_path)
    shutil.copy(file_path,new_path)
    return f"/{new_path.parent.name}/{new_path.name}" # add a root flag '/' to the new src's header

    
def _move_figure_to_new_place(elem:pf.Element,doc:pf.Doc,tracing_logger:TracingLogger,doc_path:pathlib.Path,**kwargs)->None:
    r"""Follow the general procedure of [Panflute](http://scorreia.com/software/panflute/)
    An `action` function to move local pictures to a new place (usually in a unified directory). Replace the original src with the new one.
    [modify elements in place]
    """
    if isinstance(elem, pf.Image) and (old_src:=str(elem.url)).startswith('.'): # reletive path
        old_src = decode_src_url(old_src)
        new_src = _copy_figure(doc_path.parent/old_src)
        tracing_logger.mark(elem)
        elem.url = new_src
        tracing_logger.check_and_log('image',elem)
    elif isinstance(elem, pf.RawInline) and elem.format == 'html' and (old_src:=get_html_src(elem.text)) and old_src.startswith('.'): # reletive path
        old_src = decode_src_url(old_src)
        new_src = _copy_figure(doc_path.parent/old_src)
        tracing_logger.mark(elem)
        elem.text = sub_html_src(elem.text,new_src)
        tracing_logger.check_and_log('raw_html_img',elem)

def run_filter(doc:pf.Doc=None,doc_path:pathlib.Path=None,**kwargs):
    assert doc_path.exists(),f"doc_path: {doc_path} does not exist."
    assert os.environ['NEW_ASSETS_DIR'], "NEW_ASSETS_DIR is not given in environment variables."
    return pf.run_filters(
        actions=[_move_figure_to_new_place],
        doc=doc,
        tracing_logger=TracingLogger(),
        doc_path=doc_path,**kwargs)