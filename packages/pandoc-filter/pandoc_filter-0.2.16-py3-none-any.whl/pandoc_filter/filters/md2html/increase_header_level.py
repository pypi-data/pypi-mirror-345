import logging
import panflute as pf

from ...utils.logging_helper import TracingLogger

r"""A pandoc filter that mainly for converting `markdown` to `html`.
Increase the header level by 1.

In markdown, the header level is from 1 to 6, which is represented by `#` to `######`.
We may use `#` to represent the chapter, `##` to represent the section, and so on.
But in html, the first level header is `<h1>`, and the last level header is `<h6>`.
And, the first level header is usually used for the title of the whole document instead of the chapter.
So, we may want to increase the header level by 1 when converting markdown to html, to maintain a general html style structure.

"""

def _increase_header_level(elem:pf.Element,doc:pf.Doc,tracing_logger:TracingLogger,**kwargs)->None:
    r"""Follow the general procedure of [Panflute](http://scorreia.com/software/panflute/)
    An `action` function to increase the header level by 1.
    [modify elements in place]
    """
    if isinstance(elem, pf.Header):
        tracing_logger.mark(elem)
        if elem.level < 6:
            elem.level += 1
        else:
            elem.level = 6 #  truncate the level to 6
        tracing_logger.check_and_log('header',elem)
        

def run_filter(doc:pf.Doc=None,**kwargs):
    return pf.run_filters(actions= [_increase_header_level],doc=doc,tracing_logger=TracingLogger(),**kwargs)