import os
import urllib.parse
import pathlib

import panflute as pf

from ...utils.logging_helper import TracingLogger

from ...utils.oss_helper import OssHelper

from ...utils.html_helper import get_html_src,sub_html_src

from ...utils.panflute_helper import decode_src_url



r"""A pandoc filter that mainly for converting `markdown` to `markdown`.
Auto upload local pictures to Aliyun OSS. Replace the original `src` with the new one.

NOTE:
    The following environment variables should be given in advance:
        $Env:OSS_ENDPOINT_NAME
        $Env:OSS_BUCKET_NAME
        $Env:OSS_ACCESS_KEY_ID
        $Env:OSS_ACCESS_KEY_SECRET
    The doc_path should be given in advance.
"""

def _upload_figure_to_aliyun(elem:pf.Element,doc:pf.Doc,tracing_logger:TracingLogger,oss_helper:OssHelper,doc_path:pathlib.Path,**kwargs)->None:
    r"""Follow the general procedure of [Panflute](http://scorreia.com/software/panflute/)
    An `action` function to upload local pictures to Aliyun OSS. Replace the original src with the new one.
    [modify elements in place]
    """
    if isinstance(elem, pf.Image) and (old_src:=str(elem.url)).startswith('.'): # reletive path
        old_src = decode_src_url(old_src)
        new_src = oss_helper.maybe_upload_file_and_get_src(doc_path.parent/old_src)
        tracing_logger.mark(elem)
        elem.url = new_src
        tracing_logger.check_and_log('image',elem)
    elif isinstance(elem, pf.RawInline) and elem.format == 'html' and (old_src:=get_html_src(elem.text)) and old_src.startswith('.'): # reletive path
        old_src = decode_src_url(old_src)
        new_src = oss_helper.maybe_upload_file_and_get_src(doc_path.parent/old_src)
        tracing_logger.mark(elem)
        elem.text = sub_html_src(elem.text,new_src)
        tracing_logger.check_and_log('raw_html_img',elem)

def run_filter(doc:pf.Doc=None,doc_path:pathlib.Path=None,**kwargs):
    assert doc_path.exists(),f"doc_path: {doc_path} does not exist."
    assert os.environ['OSS_ENDPOINT_NAME'], "OSS_ENDPOINT_NAME is not given in environment variables."
    assert os.environ['OSS_BUCKET_NAME'], "OSS_BUCKET_NAME is not given in environment variables."
    assert os.environ['OSS_ACCESS_KEY_ID'], "OSS_ACCESS_KEY_ID is not given in environment variables."
    assert os.environ['OSS_ACCESS_KEY_SECRET'], "OSS_ACCESS_KEY_SECRET is not given in environment variables."
    return pf.run_filters(
        actions=[_upload_figure_to_aliyun],
        doc=doc,
        tracing_logger=TracingLogger(),
        doc_path=doc_path,
        oss_helper=OssHelper(os.environ['OSS_ENDPOINT_NAME'],os.environ['OSS_BUCKET_NAME']),**kwargs)