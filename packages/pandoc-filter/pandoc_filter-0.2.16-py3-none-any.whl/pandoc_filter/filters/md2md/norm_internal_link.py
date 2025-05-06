import panflute as pf

from ...utils.logging_helper import TracingLogger

from ...utils.html_helper import get_html_href,sub_html_href

from ...utils.panflute_helper import decode_internal_link_url

r"""A pandoc filter that mainly for converting `markdown` to `markdown`.
Normalize internal links' URLs. Decode the URL if it is URL-encoded.

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
"""

def _norm_internal_link(elem:pf.Element,doc:pf.Doc,tracing_logger:TracingLogger,**kwargs)->None:
    r"""Follow the general procedure of [Panflute](http://scorreia.com/software/panflute/)
    An action to normalize any internal link's url. Decode if it is URL-encoded.
    [modify elements in place]
    """
    if isinstance(elem, pf.Link) and elem.url.startswith('#'):
        tracing_logger.mark(elem)       
        elem.url = decode_internal_link_url(elem.url)
        tracing_logger.check_and_log('anchor_links',elem)
    elif isinstance(elem, pf.RawInline) and elem.format == 'html' and (old_href:=get_html_href(elem.text)) and old_href.startswith('#'):
        tracing_logger.mark(elem)
        elem.text = sub_html_href(elem.text,decode_internal_link_url(old_href))
        tracing_logger.check_and_log('raw_anchor_links',elem)

def run_filter(doc:pf.Doc=None,**kwargs):
    return pf.run_filters(actions=[_norm_internal_link],doc=doc,tracing_logger=TracingLogger(),**kwargs)