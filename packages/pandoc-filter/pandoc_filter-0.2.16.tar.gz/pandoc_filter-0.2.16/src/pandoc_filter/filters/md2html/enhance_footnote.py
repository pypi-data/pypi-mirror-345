import panflute as pf
from urllib.parse import urlparse

from ...utils.logging_helper import TracingLogger

r"""A pandoc filter that mainly for converting `markdown` to `html`.
Enhance the footnote.
"""
        
def _enhance_footnote(elem:pf.Element,doc:pf.Doc,tracing_logger:TracingLogger,**kwargs)->pf.Note|None:
    r"""Follow the general procedure of [Panflute](http://scorreia.com/software/panflute/)
    An action to process footnotes. Deal with the footnote content as follows:
        - upgrade the link-like string to a `link` element.
        - Remove unnecessary `\n`.
        - Remove the markdown link.
        - Normalize many markdown formats like emphasis(italic) and strong(bold).
    [replace elements]
    """
    if isinstance(elem, pf.Note):
        # elem = pf.Note(pf.Para(pf.Str(pf.stringify(elem).strip(' \n'))))
        # buf = 
        
        tracing_logger.mark(elem)
        buf = []
        for item in pf.stringify(elem).strip(' \n').split():
            
            url = urlparse(item)
            if (url.scheme and url.netloc):
                # tracing_logger.info('url:',url)
                # link = 
                buf.append(pf.Link(pf.Str(item),url=url.geturl()))
            elif url.path.lower().startswith('www'):
                # link = 
                buf.append(pf.Link(pf.Str(item),url='https://'+url.geturl()))
            else:
                buf.append(pf.Str(item))
            buf.append(pf.Space())
                
            # if isinstance(item,pf.Str):
            #     url = urlparse(item.text)
            #     if (url.scheme and url.netloc):
            #         # tracing_logger.info('url:',url)
            #         link = pf.Link(item,url=url.geturl())
            #         buf.append(link)
            #     elif url.path.lower().startswith('www'):
            #         link = pf.Link(item,url='https://'+url.geturl())
            #         buf.append(link)
            #     else:
            #         buf.append(item)
            # else:
            #     buf.append(item)
            #     # link = pf.Link(item,url=item.text)
            #     # item = link
        elem = pf.Note(pf.Para(*buf))
        
        tracing_logger.check_and_log('footnote',elem)
        return elem

    # if isinstance(elem, pf.Str):
    #     url  = urlparse(elem.text)
    #     if url.scheme and url.netloc:
    #         tracing_logger.info('url:',url)
            
        # tracing_logger.mark(elem)
        # link = pf.Link(elem,url=elem.text)
        
        # tracing_logger.check_and_log('link_like',elem)
        # return link

def run_filter(doc:pf.Doc=None,**kwargs):
    return pf.run_filters(actions=[_enhance_footnote],doc=doc,tracing_logger=TracingLogger(),**kwargs)