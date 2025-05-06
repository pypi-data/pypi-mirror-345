import difflib
import pathlib
import subprocess
import functools
import pandoc_filter
import pytest

# import pandoc_filter.filters
# import pandoc_filter.filters.md2md
# import pandoc_filter.filters.md2md.norm_internal_link

def _check_file_path(file_path:str)->pathlib.Path:
    file_path:pathlib.Path = pathlib.Path(file_path)
    assert file_path.exists()
    assert file_path.is_file()
    return file_path

def _compare_files(file1_path, file2_path):
    with open(file1_path, 'r', encoding='utf-8') as file1:
        content1 = file1.readlines()

    with open(file2_path, 'r', encoding='utf-8') as file2:
        content2 = file2.readlines()

    differ = difflib.Differ()
    diff = list(differ.compare(content1, content2))
    if not any(line.startswith('- ') or line.startswith('+ ') for line in diff):
        return True
    else:
        return False
    
@pytest.mark.parametrize('input_format',['markdown'])
@pytest.mark.parametrize('output_format',['html'])
def test_md2html_header_anchor_link_filter(input_format:str,output_format:str):
    file_path = _check_file_path("./resources/inputs/test_md2html_header_anchor_and_link.md")
    pathlib.Path("./temp").mkdir(parents=True, exist_ok=True)
    output_path = pathlib.Path(f"./temp/{file_path.stem}.html")
    answer_path = pathlib.Path(f"./resources/outputs/{file_path.stem}.html")
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
        'md2md-norm-internal-link-filter',
        '--filter',
        'md2html-hash-anchor-and-internal-link-filter',
        '--filter',
        'md2html-enhance-link-like-filter',
        '--filter',
        'md2html-increase-header-level-filter',
    ]
    assert subprocess.run(pandoc_command, check=True).returncode == 0
    assert _compare_files(output_path,answer_path)


@pytest.mark.parametrize('input_format',['markdown'])
@pytest.mark.parametrize('output_format',['html'])
def test_md2html_header_anchor_link_filter_pyio(input_format:str,output_format:str):
    file_path = _check_file_path("./resources/inputs/test_md2html_header_anchor_and_link.md")
    pathlib.Path("./temp").mkdir(parents=True, exist_ok=True)
    output_path = pathlib.Path(f"./temp/{file_path.stem}.html")
    answer_path = pathlib.Path(f"./resources/outputs/{file_path.stem}.html")
    pandoc_filter.run_filters_pyio(
        file_path,
        output_path,
        input_format,output_format,
        [pandoc_filter.filters.md2md.norm_internal_link.run_filter,
         pandoc_filter.filters.md2html.hash_anchor_and_internal_link.run_filter,
         pandoc_filter.filters.md2html.enhance_link_like.run_filter,
         pandoc_filter.filters.md2html.increase_header_level.run_filter])
    assert _compare_files(output_path,answer_path)

@pytest.mark.parametrize('input_format',['markdown'])
@pytest.mark.parametrize('output_format',['html'])
def test_md2html_enhance_footnote_filter_pyio(input_format:str,output_format:str):
    file_path = _check_file_path("./resources/inputs/test_md2html_footnote.md")
    pathlib.Path("./temp").mkdir(parents=True, exist_ok=True)
    output_path = pathlib.Path(f"./temp/{file_path.stem}.html")
    answer_path = pathlib.Path(f"./resources/outputs/{file_path.stem}.html")
    pandoc_filter.run_filters_pyio(
        file_path,
        output_path,
        input_format,output_format,
        [pandoc_filter.filters.md2html.enhance_footnote.run_filter,])
    assert _compare_files(output_path,answer_path)
   

@pytest.mark.parametrize('input_format',['markdown'])
@pytest.mark.parametrize('output_format',['html'])
def test_md2html_enhance_footnote_filter(input_format:str,output_format:str):
    file_path = _check_file_path("./resources/inputs/test_md2html_footnote.md")
    pathlib.Path("./temp").mkdir(parents=True, exist_ok=True)
    output_path = pathlib.Path(f"./temp/{file_path.stem}.html")
    answer_path = pathlib.Path(f"./resources/outputs/{file_path.stem}.html")
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
        'md2html-enhance-footnote-filter',
    ]
    assert subprocess.run(pandoc_command, check=True).returncode == 0
    assert _compare_files(output_path,answer_path)

