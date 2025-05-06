import panflute as pf
import re
from ...utils.logging_helper import TracingLogger

r"""A pandoc filter that mainly for converting `markdown` to `markdown`.
Convert the [github-style alert](https://github.com/orgs/community/discussions/16925) to hexo-style alert.
The github-style alert is based on pandoc's `BlockQuote` element, while the hexo-style alert is based on [hexo tag plugins](https://hexo.io/docs/tag-plugins#Note).
We use a general mode to confirm the hexo-style alert type, which are widely used in the hexo community by many themes, such as
    - [hexo-theme-butterfly](https://butterfly.js.org/posts/4aa8abbe/?highlight=%25+endnote#%E6%A8%99%E7%B1%A4%E5%A4%96%E6%8E%9B%EF%BC%88Tag-Plugins%EF%BC%89),
    - [hexo-theme-fluid](https://hexo.fluid-dev.com/docs/guide/#tag-%E6%8F%92%E4%BB%B6),
    - [hexo-them-next](https://theme-next.js.org/docs/tag-plugins/note).
The mapping between the github-style alert and hexo-style alert is:
    - [!NOTE] -> {% note info %} ... {% endnote %}
    - [!TIP] -> {% note success %} ... {% endnote %}
    - [!IMPORTANT] -> {% note primary %} ... {% endnote %}
    - [!WARNING] -> {% note warning %} ... {% endnote %}
    - [!CAUTION] -> {% note danger %} ... {% endnote %}
"""

def __get_and_map_alerts(input_string:str)->tuple[str,str]|None:
    if matched:=re.match(r'\[\!(?P<alert_string>NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]',input_string.strip().upper()):
        match matched.group('alert_string'):
            case 'NOTE':
                return "{% note info %}","{% endnote %}"
            case 'TIP':
                return "{% note success %}","{% endnote %}"
            case 'IMPORTANT':
                return "{% note primary %}","{% endnote %}"
            case 'WARNING':
                return "{% note warning %}","{% endnote %}"
            case 'CAUTION':
                return "{% note danger %}","{% endnote %}"
            case _:
                return "{% note default %}","{% endnote %}"
    else:
        return None
def _convert_github_style_alert_to_hexo_style_alert(elem:pf.Element,doc:pf.Doc,tracing_logger:TracingLogger,**kwargs)->pf.Note|None:
    r"""Follow the general procedure of [Panflute](http://scorreia.com/software/panflute/)
    An action to process alerts (`BlockQuote` element). Convert github-style alerts, such as:
        > [!NOTE]
        > This is a note
    to [hexo-style alerts], such as:
        {% note info %}
        This is a note
        {% endnote %}
    [replace elements]
    """
    if isinstance(elem, pf.BlockQuote):
        tracing_logger.mark(elem)
        content = []
        match elem.content:
            case [pf_para,*rest] if isinstance(pf_para,pf.Para) and len(rest)>0 and len(pf_para.content)==1 and isinstance(pf_para.content[0],pf.Str):
                pf_str:pf.Str = pf_para.content[0]
                if (maybe_alert_type:=__get_and_map_alerts(pf_str.text)) is not None:
                    content = [pf.Para(pf.Str(maybe_alert_type[0])),
                               *rest,
                               pf.Para(pf.Str(maybe_alert_type[1]))]
                    tracing_logger.check_and_log('alert',content)
                    return content
            case [pf_para] if isinstance(pf_para,pf.Para) and isinstance(pf_para.content[0],pf.Str):
                pf_str:pf.Str = pf_para.content[0]
                if (maybe_alert_type:=__get_and_map_alerts(pf_str.text)) is not None:
                    for index,item in enumerate(pf_para.content[1::]):
                        if isinstance(item,pf.LineBreak) or isinstance(item,pf.SoftBreak) or isinstance(item,pf.Space):
                            continue
                        else:
                            break
                    else:
                        index = 0
                    content = [pf.Para(pf.Str(maybe_alert_type[0])),
                               pf.Para(*pf_para.content[index+1::]),
                               pf.Para(pf.Str(maybe_alert_type[1]))]
                    tracing_logger.check_and_log('alert',content)
                    return content
            case _:
                pass

def run_filter(doc:pf.Doc=None,**kwargs):
    return pf.run_filters(actions=[_convert_github_style_alert_to_hexo_style_alert],doc=doc,tracing_logger=TracingLogger(),**kwargs)