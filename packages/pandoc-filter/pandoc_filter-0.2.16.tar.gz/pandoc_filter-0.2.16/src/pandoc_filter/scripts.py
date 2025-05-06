import pathlib
from typing import Callable

import panflute as pf
import typeguard

@typeguard.typechecked
def run_filters_pyio(input_path:pathlib.Path,
                     output_path:pathlib.Path,
                     input_format:str,
                     output_format:str,
                     actions:list[Callable],
                     prepare:Callable|None=None,
                     finalize:Callable|None=None,
                     doc:pf.Doc|None=None,
                     **kwargs):
    with open(input_path, "r", encoding='utf-8') as f:
        markdown_content = f.read()
    doc = pf.convert_text(markdown_content,input_format=input_format,output_format='panflute',standalone=True)
    if prepare:
        prepare(doc=doc,**kwargs)
    for action in actions:
        doc = action(doc=doc,**kwargs)
    if finalize:
        finalize(doc=doc,**kwargs)
    with open(output_path, "w", encoding="utf-8") as f:
        text = pf.convert_text(doc,input_format='panflute',output_format=output_format,standalone=True)
        if not text.endswith('\n'):
            text += '\n'
        f.write(text)
