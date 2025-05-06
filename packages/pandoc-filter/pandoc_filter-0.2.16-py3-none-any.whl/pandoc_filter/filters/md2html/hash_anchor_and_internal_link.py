import re
import functools

import panflute as pf

from ...utils.logging_helper import TracingLogger

from ...utils.panflute_helper import DocRuntimeDict,InternalLink
from ...utils.panflute_helper import decode_internal_link_url
from ...utils.hash_helper import get_text_hash
from ...utils.html_helper import get_html_id,sub_html_id,get_html_href


r"""A pandoc filter that mainly for converting `markdown` to `html`.
Hash both the anchor's `id` and the internal-link's `url` simultaneously.

Anchor:
    An anchor represents a section of a document.
    If in markdown, it is a header or a raw-HTML element with id attribute. Such as:
        headings: `## aaa`
        raw-HTML: `<a id="aaa"></a>`
    If in html, it is a raw-HTML element with id attribute. Such as:
        `<a id="aaa"></a>`
   
Internal Link:
    A internal link is a link that points to an anchor in the same document.
    If in markdown, it is a link with a URL that starts with `#`. Such as:
       md internal links: `[bbb](#aaa)`
       raw-HTML internal links: `<a href="#aaa">bbb</a>`
    If in html, it is a raw-HTML element with href attribute that starts with `#`. Such as:
        `<a href="#aaa">bbb</a>`

Generally, an anchor's id attribute should be equal to the internal-link's url attribute. But in many converting scenarios, due to some unknown restrictions or normalization mechanisms,
if there are some special characters in the anchor's id attribute or the internal-link's url attribute, their texts may be modified automatically. Then, the above equality may not be satisfied,
thus making the link invalid.

So, to maintain the validity of the link, this filter is designed to normalize both the anchor's id and the internal-link's url simultaneously to their hash,
avoiding auto modification by unknown restrictions. (Hash values are all regular legal characters and will generally be retained.)

Sepcifically, this filter will:
    1. calculate any anchor's id hash value with a unified/global hash function
    2. record and numbering each anchor's id hash value
    3. substitute any anchor's id with its hash value and numbering
        the first anchor will be numbered as `<hash value>-1`, the second anchor (if exists) will be numbered as `<hash value>-2`,...
    4. record and guess any internal-link's url with 2 options:
        For example, if the url is '#aaa-2', then the 2 options are:
           `not number`  - link to the first anchor with original id 'aaa-1' and current id '<hash(aaa-2)>-1'
           `number`      - link to the second anchor with original id 'aaa' and current id '<hash(aaa)>-2'
        record both the two options
    6. after recording and dealing with all anchors, deal with the recorded internal-link:
        if
            the `not number` one matches any recorded anchor, substitute the internal-link's url with the `not number` one
        else if 
            the `number` one matches any recorded anchor, substitute the internal-link's url with the `number` one
        else
            log a warning message and do nothing       
"""

def _prepare_hash_anchor_and_internal_link(doc:pf.Doc):
    doc.runtime_dict = DocRuntimeDict(
        {'anchor_count':{},
         'internal_link_record':[]
         })

def __text_hash_count(doc:pf.Doc,text:str)->str:
    text_hash = get_text_hash(text)
    if text_hash in doc.runtime_dict['anchor_count']: # 按照text_hash值计数, 重复则加1
        doc.runtime_dict['anchor_count'][text_hash] += 1
    else:
        doc.runtime_dict['anchor_count'][text_hash] = 1
    return text_hash
    
def _hash_anchor_id(elem:pf.Element,doc:pf.Doc,tracing_logger:TracingLogger,**kwargs)->None:
    r"""Follow the general procedure of [Panflute](http://scorreia.com/software/panflute/)
    An `action` function to normalize any anchor's `id` to its hash.
    [modify elements in place]
    """
    if isinstance(elem, pf.Header):
        tracing_logger.mark(elem)
        # 获取header文本内容并剔除#号
        header_text = pf.convert_text(elem,input_format='panflute',output_format='gfm',standalone=True).lstrip('#')
        text_hash = __text_hash_count(doc,header_text)
        elem.identifier = f"{text_hash}-{doc.runtime_dict['anchor_count'][text_hash]}"
        # According to https://github.com/Zhaopudark/pandoc-filter/issues/3, add an invisible link in the header.
        link_in_hearder = pf.Link(url=f"#{elem.identifier}",title=header_text,classes=['headerlink'])
        elem.content.insert(0,link_in_hearder)
        
        tracing_logger.check_and_log('headings anchor',elem)
    elif isinstance(elem, pf.RawInline) and elem.format == 'html' and (raw_id_text:=get_html_id(elem.text)): # 获取id文本内容但不做任何剔除
        tracing_logger.mark(elem)
        text_hash = __text_hash_count(doc,raw_id_text)
        elem.text = sub_html_id(elem.text,f"{text_hash}-{doc.runtime_dict['anchor_count'][text_hash]}")
        tracing_logger.check_and_log('raw-HTML anchor',elem)

def __url_hash_guess(text:str)->str:
    old_url = text.lstrip('#')
    url = get_text_hash(old_url)
    if match:= re.search(r'-(?P<guessed_index>\d+)$', old_url):
        guessed_index = int(match.groupdict()['guessed_index'])  # 从匹配结果中提取数字部分
        if guessed_index == 0:
            guessed_index = 1
        url_striped = old_url[:match.start()]  # 从匹配结果中提取数字前面的部分
        guessed_url_with_num = get_text_hash(url_striped) + f"-{guessed_index}"
    else:
        guessed_url_with_num = None
    return url,guessed_url_with_num

def _internal_link_recorder(elem:pf.Element,doc:pf.Doc,**kwargs)->None:
    r"""Follow the general procedure of [Panflute](http://scorreia.com/software/panflute/)
    A action to pre-normalize and record internal links's `url`.
    [modify nothing]
    """
    if isinstance(elem, pf.Link) and elem.url.startswith('#'):
        # Olny md internal links need to be decoded since it will be encoded by pandoc before filter.:
        if 'headerlink' not in elem.classes: # pass the headerlink
            decoded_url = decode_internal_link_url(elem.url) 
            url,guessed_url_with_num = __url_hash_guess(decoded_url)
            doc.runtime_dict['internal_link_record'].append(InternalLink(elem,url=url,guessed_url=guessed_url_with_num))

    elif isinstance(elem, pf.RawInline) and elem.format == 'html' and (old_href:=get_html_href(elem.text)) and old_href.startswith('#'):
        # raw-HTML internal links will not be encoded by pandoc before filter. So there is no need to decode it.
        url,guessed_url_with_num = __url_hash_guess(old_href)
        doc.runtime_dict['internal_link_record'].append(InternalLink(elem,url=url,guessed_url=guessed_url_with_num))

def _finalize_hash_anchor_and_internal_link(doc:pf.Doc,tracing_logger:TracingLogger,**kwargs):    
    id_set = set()
    for k,v in doc.runtime_dict['anchor_count'].items():
        for i in range(1,v+1):
            id_set.add(f"{k}-{i}")
    for internal_link in doc.runtime_dict['internal_link_record']:
        internal_link:InternalLink
        if f"{internal_link.url}-1" in id_set:
            internal_link.sub(f"{internal_link.url}-1",tracing_logger)
        elif internal_link.guessed_url in id_set: # None is not in id_set
            internal_link.sub(f"{internal_link.guessed_url}",tracing_logger)
        else:
            # According to https://github.com/Zhaopudark/pandoc-filter/issues/1, 
            # Even though the internal link's target is not found, we still modify it compulsorily, instead of do nothing.
            # The warning message is just for reminding the user.
            tracing_logger.warning("hash_anchor_and_internal_link",f"{internal_link.elem}")
            tracing_logger.warning("hash_anchor_and_internal_link",f"The internal link `{internal_link.url}` may be invalid because no target header is found. But it will still be modified to `{internal_link.url}-1`.")
            internal_link.sub(f"{internal_link.url}-1",tracing_logger)

def run_filter(doc:pf.Doc=None,**kwargs)->pf.Doc:
    __finalize_hash_anchor_and_internal_link = functools.partial(_finalize_hash_anchor_and_internal_link,tracing_logger=TracingLogger(),**kwargs)
    return pf.run_filters(
        actions= [_hash_anchor_id,_internal_link_recorder],
        prepare=_prepare_hash_anchor_and_internal_link,
        finalize=__finalize_hash_anchor_and_internal_link,
        doc=doc,tracing_logger=TracingLogger(),**kwargs)