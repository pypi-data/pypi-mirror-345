import logging
import panflute as pf

from ...utils.logging_helper import TracingLogger

r"""A pandoc filter that mainly for converting `markdown` to `html`.
Centralize the `figure` element by setting inline styles.

Specifically:
    set `figure` attribute to `text-align:center;`
    set `figure`'s `caption` attribute to `color:#858585;`
 
Deprecated.
    The best way is to use CSS files to define global styles and use them by `--css <css_files>`,
    instead of make an action here.
    So, this method is deprecated.        
    
    When converting markdown to html, Pandoc will generate a `Figure` element for each image,
    and copy the `alt_text` in `![image_url](alt_text)` to the `Caption` part of the `Figure`.
    
    And if in many Blog systems, the `alt_text` in `Image` will be copied again into the `Figure`,
    parallel with the original `Caption` part. Leading to dual captions in html.
    
    A not-so-good solution is to delete/elimiate the `Caption` part of the `Figure` element,
    which relys on the post-processing of the html file.
    
    A better way is to set inline styles on the `Figure` element, which does not rely on
    the post-processing components.
    
    Since in `Panflute`, the `Caption` element has no attributes, it is hard to modify it.
    So, we have to insert a `Div` element into the `Caption` element, and modify the `Div`
    element to show our target `alt_text`.
    
    And, it is better if set a global style `text-align:center` for the whole `Figure` element,
    which will not only influence the `Caption` part, but also the `Image` part.
    
    Even though in some Blog systems, the `Figure` element will be centered automatically,
    it is still a good practice to set the style in the `Figure` element, which will not
    be limited by post-processing components.
    
    For specific, the `Figure` element will be modified as:
        - add `text-align:center;` to the `style` attribute of the `Figure` element
        - new a `Caption` element, which includes a new `Div` element that contains the original `alt_text`
        - add `color:#858585;` to the `style` attribute of the `Div` element
        - replace the original `Caption` element with the new one.
"""

def _centralize_figure(elem:pf.Element,doc:pf.Doc,tracing_logger:TracingLogger,**kwargs)->None:
    r"""Follow the general procedure of [Panflute](http://scorreia.com/software/panflute/)
    An `action` function to centralize the `Figure` element.
    [modify elements in place]
    """
    if isinstance(elem, pf.Figure):
        logging.warning("""
        The `centralize_figure` filter is deprecated. Please use CSS files to define global styles and use them by `--css <css_files>`.
        See https://github.com/Zhaopudark/pandoc-filter/blob/main/src/pandoc_filter/filters/md2html/centralize_figure.py#L13 for more details.
        """)
        tracing_logger.mark(elem)
        for img in elem.content:
            if isinstance(img, pf.Image):
                break
        if 'style' in elem.attributes:
            elem.attributes['style'] += "text-align:center;"
        else:
            elem.attributes = {'style':"text-align:center;"}
        centered_div = pf.Div(*elem.caption.content,attributes={'style':"color:#858585;"})
        elem.caption = pf.Caption(centered_div)
        tracing_logger.check_and_log('figure',elem)

def run_filter(doc:pf.Doc=None,**kwargs):
    return pf.run_filters(actions= [_centralize_figure],doc=doc,tracing_logger=TracingLogger(),**kwargs)