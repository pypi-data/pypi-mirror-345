import panflute as pf

from ...utils.logging_helper import TracingLogger

r"""A pandoc filter that mainly for converting `markdown` to `html`.
Enhance the link-like string to a `link` element.
"""


def _enhance_link_like(elem:pf.Element,doc:pf.Doc,tracing_logger:TracingLogger,**kwargs)->pf.Link|None:
    r"""Follow the general procedure of [Panflute](http://scorreia.com/software/panflute/)
    An action to process a string that may be like a link.
    Replace the string with a `Link` element.
    [replace elements]
    """
    if isinstance(elem, pf.Str) and elem.text.lower().startswith('http'):
        tracing_logger.mark(elem)
        link = pf.Link(elem,url=elem.text)
        tracing_logger.check_and_log('link_like',elem)
        return link

def run_filter(doc:pf.Doc=None,**kwargs)->pf.Doc:
    return pf.run_filters(actions=[_enhance_link_like],doc=doc,tracing_logger=TracingLogger(),**kwargs)

