import difflib
import pathlib
import logging
import functools
import subprocess
import panflute as pf
import pytest
import pandoc_filter
import pandoc_filter.filters

def _check_file_path(file_path:str)->pathlib.Path:
    file_path:pathlib.Path = pathlib.Path(file_path)
    assert file_path.exists()
    assert file_path.is_file()
    return file_path

def _check_the_same_content(file1_path, file2_path):
    with open(file1_path, 'r', encoding='utf-8') as file1:
        content1 = file1.readlines()
    with open(file2_path, 'r', encoding='utf-8') as file2:
        content2 = file2.readlines()
    differ = difflib.Differ()
    diff = list(differ.compare(content1, content2))
    if not any(line.startswith('- ') or line.startswith('+ ') for line in diff):
        return True
    else:
        for line in diff:
            logging.warning(line)
        return False

@pytest.mark.parametrize('input_format',['markdown'])
@pytest.mark.parametrize('output_format',['markdown','gfm'])
def test_md2md_norm_footnote_filter(input_format:str,output_format:str):
    file_path = _check_file_path("./resources/inputs/test_md2md_footnote.md")
    pathlib.Path("./temp").mkdir(parents=True, exist_ok=True)
    output_path = pathlib.Path(f"./temp/{file_path.name}")
    answer_path = pathlib.Path(f"./resources/outputs/{file_path.name}")
    pandoc_command = [
        'pandoc',
        file_path,
        '-o',
        output_path,
        '-f',
        input_format,
        '-t',
        output_format,
        '-s',
        '--filter',
        'md2md-norm-footnote-filter'
    ]
    assert subprocess.run(pandoc_command, check=True).returncode == 0
    assert _check_the_same_content(output_path,answer_path)

@pytest.mark.parametrize('input_format',['markdown'])
@pytest.mark.parametrize('output_format',['markdown','gfm'])
def test_md2md_norm_footnote_filter_pyio(input_format:str,output_format:str):
    file_path = _check_file_path("./resources/inputs/test_md2md_footnote.md")
    pathlib.Path("./temp").mkdir(parents=True, exist_ok=True)
    output_path = pathlib.Path(f"./temp/{file_path.name}")
    answer_path = pathlib.Path(f"./resources/outputs/{file_path.name}")
    pandoc_filter.run_filters_pyio(file_path,output_path,input_format,output_format,
        [pandoc_filter.filters.md2md.norm_footnote.run_filter])
    assert _check_the_same_content(output_path,answer_path)

@pytest.mark.parametrize('input_format',['markdown'])
@pytest.mark.parametrize('output_format',['gfm'])
def test_md2md_norm_internal_link_filter(input_format:str,output_format:str):
    file_path = _check_file_path("./resources/inputs/test_md2md_internal_link.md")
    pathlib.Path("./temp").mkdir(parents=True, exist_ok=True)
    output_path = pathlib.Path(f"./temp/{file_path.name}")
    answer_path = pathlib.Path(f"./resources/outputs/{file_path.name}")
    pandoc_command = [
        'pandoc',
        file_path,
        '-o',
        output_path,
        '-f',
        input_format,
        '-t',
        output_format,
        '-s',
        '--filter',
        'md2md-norm-internal-link-filter'
    ]
    assert subprocess.run(pandoc_command, check=True).returncode == 0
    assert _check_the_same_content(output_path,answer_path)
    
@pytest.mark.parametrize('input_format',['markdown'])
@pytest.mark.parametrize('output_format',['gfm'])
def test_md2md_norm_internal_link_filter_pyio(input_format:str,output_format:str):
    file_path = _check_file_path("./resources/inputs/test_md2md_internal_link.md")
    pathlib.Path("./temp").mkdir(parents=True, exist_ok=True)
    output_path = pathlib.Path(f"./temp/{file_path.name}")
    answer_path = pathlib.Path(f"./resources/outputs/{file_path.name}")
    pandoc_filter.run_filters_pyio(file_path,output_path,input_format,output_format,
        [pandoc_filter.filters.md2md.norm_internal_link.run_filter])
    assert _check_the_same_content(output_path,answer_path)

@pytest.mark.parametrize('input_format',['markdown','gfm'])
@pytest.mark.parametrize('output_format',['markdown','gfm'])
def test_md2md_enhance_equation_filter(input_format:str,output_format:str):
    file_path = _check_file_path("./resources/inputs/test_md2md_math.md")
    pathlib.Path("./temp").mkdir(parents=True, exist_ok=True)
    output_path = pathlib.Path(f"./temp/{file_path.name}")
    answer_path = pathlib.Path(f"./resources/outputs/{file_path.name}")
    pandoc_command = [
        'pandoc',
        file_path,
        '-o',
        output_path,
        '-f',
        input_format,
        '-t',
        output_format,
        '-s',
        '--filter',
        'md2md-enhance-equation-filter'
    ]
    assert subprocess.run(pandoc_command, check=True).returncode == 0
    assert _check_the_same_content(output_path,answer_path)

@pytest.mark.parametrize('input_format',['markdown','gfm'])
@pytest.mark.parametrize('output_format',['markdown','gfm'])
def test_md2md_enhance_equation_filter_pyio(input_format:str,output_format:str):
    file_path = _check_file_path("./resources/inputs/test_md2md_math_metadata.md")
    pathlib.Path("./temp").mkdir(parents=True, exist_ok=True)
    output_path = pathlib.Path(f"./temp/{file_path.name}")
    answer_path = pathlib.Path(f"./resources/outputs/{file_path.name}")
    def finalize(doc:pf.Doc,**kwargs):
        runtime_dict:dict = doc.runtime_dict
        if runtime_dict.get('math'):
            doc.metadata['math'] = doc.runtime_dict['math']
    pandoc_filter.run_filters_pyio(file_path,output_path,input_format,output_format,
        [pandoc_filter.filters.md2md.enhance_equation.run_filter],finalize=finalize)
    assert _check_the_same_content(output_path,answer_path)

@pytest.mark.parametrize('input_format',['markdown'])
@pytest.mark.parametrize('output_format',['gfm'])
def test_md2md_convert_github_style_alert_to_hexo_style_alert_filter(input_format:str,output_format:str):
    file_path = _check_file_path("./resources/inputs/test_md2md_alert.md")
    pathlib.Path("./temp").mkdir(parents=True, exist_ok=True)
    output_path = pathlib.Path(f"./temp/{file_path.name}")
    answer_path = pathlib.Path(f"./resources/outputs/{file_path.name}")
    pandoc_command = [
        'pandoc',
        file_path,
        '-o',
        output_path,
        '-f',
        input_format,
        '-t',
        output_format,
        '-s',
        '--filter',
        'md2md-convert-github-style-alert-to-hexo-style-alert-filter'
    ]
    assert subprocess.run(pandoc_command, check=True).returncode == 0
    assert _check_the_same_content(output_path,answer_path)

@pytest.mark.parametrize('input_format',['markdown'])
@pytest.mark.parametrize('output_format',['gfm'])
def test_md2md_convert_github_style_alert_to_hexo_style_alert_filter_pyio(input_format:str,output_format:str):
    file_path = _check_file_path("./resources/inputs/test_md2md_alert.md")
    pathlib.Path("./temp").mkdir(parents=True, exist_ok=True)
    output_path = pathlib.Path(f"./temp/{file_path.name}")
    answer_path = pathlib.Path(f"./resources/outputs/{file_path.name}")
    pandoc_filter.run_filters_pyio(file_path,output_path,input_format,output_format,
        [pandoc_filter.filters.md2md.convert_github_style_alert_to_hexo_style_alert.run_filter])
    assert _check_the_same_content(output_path,answer_path)