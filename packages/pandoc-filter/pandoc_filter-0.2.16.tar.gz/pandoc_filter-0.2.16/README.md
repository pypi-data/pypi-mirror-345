<div align="center">
<strong>
<samp>

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pandoc-filter?logo=python)](https://badge.fury.io/py/pandoc-filter)
[![PyPI - Version](https://img.shields.io/pypi/v/pandoc-filter?logo=pypi)](https://pypi.org/project/pandoc-filter)
[![DOI](https://zenodo.org/badge/741871139.svg)](https://zenodo.org/doi/10.5281/zenodo.10528322)
[![GitHub License](https://img.shields.io/github/license/Zhaopudark/pandoc-filter)](https://github.com/Zhaopudark/pandoc-filter?tab=GPL-3.0-1-ov-file#readme)

[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/Zhaopudark/pandoc-filter/test.yml?label=Test)](https://github.com/Zhaopudark/pandoc-filter/actions/workflows/test.yml)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/Zhaopudark/pandoc-filter/build_and_deploy.yml?event=release&label=Build%20and%20Deploy)](https://github.com/Zhaopudark/pandoc-filter/actions/workflows/build_and_deploy.yml)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/Zhaopudark/pandoc-filter/post_deploy_test.yml?event=workflow_run&label=End%20Test)](https://github.com/Zhaopudark/pandoc-filter/actions/workflows/post_deploy_test.yml)
[![codecov](https://codecov.io/gh/Zhaopudark/pandoc-filter/graph/badge.svg?token=lb3cLoh3e5)](https://codecov.io/gh/Zhaopudark/pandoc-filter)

</samp>
</strong>
</div>

# pandoc-filter

This project supports some useful and highly customized [pandoc python filters](https://pandoc.org/filters.html) that based on [panflute](http://scorreia.com/software/panflute/). They can meet some special requests when using [pandoc](https://pandoc.org) to

- [x] convert files from `markdown` to `gfm`
- [x] convert files from `markdown` to `html`
- [ ] convert other formats (In the future)

Please see [Main Features](#main-features) for the concrete features.

Please see [Samples](#Samples) for the recommend usage.

# Backgrounds

I'm used to taking notes with markdown and clean markdown syntax. Then, I usually post these notes on [my site](https://little-train.com/) as web pages. So, I need to convert markdown to html. There were many tools to achieve the converting and  I chose [pandoc](https://pandoc.org) at last due to its powerful features.

But sometimes, I need many more features when converting from `markdown` to `html`, where pandoc filters are needed. I have written some pandoc python filters with some advanced features by [panflute](https://github.com/sergiocorreia/panflute) and many other tools. And now, I think it's time to gather these filters into a combined toolset as this project. 

# Installation

```
pip install -i https://pypi.org/simple/ -U pandoc-filter
```

# Main Features

There are 2 supported ways:

-  **command-line-mode**: use non-parametric filters in command-lines with [pandoc](https://pandoc.org).
- **python-mode**: use `run_filters_pyio`  function in python.

For an example, `md2md_enhance_equation_filter` in [enhance_equation.py](./src/pandoc_filter/filters/md2md/enhance_equation.py) is a filter function as [panflute-user-guide ](http://scorreia.com/software/panflute/guide.html). And its registered command-line script is `md2md-enhance-equation-filter`. 

- So, after the installation, one can use it in **command-line-mode**:

  ```powershell
  pandoc ./input.md -o ./output.md -f markdown -t gfm -s --filter md2md-enhance-equation-filter
  ```

- Or, use in **python mode**

  ```python
  import pandoc_filter
  file_path = pathlib.Path("./input.md")
  output_path = pathlib.Path("./output.md")
  pandoc_filter.run_filters_pyio(file_path,output_path,'markdown','gfm',[pandoc_filter.md2md_enhance_equation_filter])
  ```

**Runtime status** can be recorded. In **python mode**, any filter function will return a proposed panflute `Doc`. Some filter functions will add an instance attribute dict `runtime_dict` to the returned `Doc`, as a record for **runtime status**, which may be very useful for advanced users.  For an example,  `md2md_enhance_equation_filter`, will add an instance attribute dict `runtime_dict` to the returned `Doc`, which may contain a mapping `{'math':True}` if there is any math element in the `Doc`.

All filters with corresponding registered command-line scripts, the specific features, and the recorded **runtime status** are recorded as the following:

> [!NOTE]
>
> Since some filters need additional arguments, not all filter functions support **command-line-mode**, even though they all support **python-mode** indeed.
>
> All filters support cascaded invoking.

- `pandoc_filter.filters.md2md.convert_github_style_alert_to_hexo_style_alert.run_filter`
  - [source](./src/pandoc_filter/filters/md2md/convert_github_style_alert_to_hexo_style_alert.py)
  - command-line: `md2md-convert-github-style-alert-to-hexo-style-alert-filter`
  - main features: Convert the [github-style alert](https://github.com/orgs/community/discussions/16925) to hexo-style alert.
- `pandoc_filter.filters.md2md.enhance_equation.run_filter`
  - [source](./src/pandoc_filter/filters/md2md/enhance_equation.py)
  - command-line: `md2md-enhance-equation-filter`
  - main features: Enhance math equations.
  - Runtime status (`doc.runtime_dict`): ` {'math':< bool >,'equations_count':<some_number>}`
- `pandoc_filter.filters.md2md.norm_footnote.run_filter`
  - [source](./src/pandoc_filter/filters/md2md/norm_internal_link.py)
  - command-line: `md2md-norm-footnote-filter`
  - main features: Normalize the footnotes.
- `pandoc_filter.filters.md2md.norm_internal_link.run_filter`
  - [source](./src/pandoc_filter/filters/md2md/norm_internal_link.py)
  - command-line: `  md2md-norm-internal-link-filter`
  - main features:  Normalize internal links' URLs.
- `pandoc_filter.filters.md2md.upload_figure_to_aliyun.run_filter`
  - [source](./src/pandoc_filter/filters/md2md/upload_figure_to_aliyun.py)
  - command-line:  ==Unsupported.==
  - Additional Arguments: `doc_path`
  - main features: Auto upload local pictures to Aliyun OSS.
  - Runtime status (`doc.runtime_dict`): {'doc_path':<doc_path>,'oss_helper':<Oss_Helper>}
- `pandoc_filter.filters.md2html.centralize_figure.run_filter`
  - [source](./src/pandoc_filter/filters/md2html/centralize_figure.py)
  - command-line: `md2html-centralize-figure-filter`
  - main features: ==Deprecated==
- `pandoc_filter.filters.md2html.enhance_footnote.run_filter`
  - [source](./src/pandoc_filter/filters/md2html/enhance_footnote.py)
  - command-line: `md2html-enhance-footnote-filter`
  - main features: Enhance the footnote.
- `pandoc_filter.filters.md2html.enhance_link_like.run_filter`
  - [source](./src/pandoc_filter/filters/md2html/enhance_link_like.py)
  - command-line: `md2html-enhance-link-like-filter`
  - main features: Enhance the link-like string to a `link` element.
- `pandoc_filter.filters.md2html.hash_anchor_and_internal_link.run_filter`
  - [source](./src/pandoc_filter/filters/md2html/hash_anchor_and_internal_link.py)
  - command-line: `md2html-hash-anchor-and-internal-link-filter`
  - main features: Hash both the anchor's `id` and the internal-link's `url ` simultaneously.
  - Runtime status (`doc.runtime_dict`): `{'anchor_count':<anchor_count_dict>,'internal_link_record':<internal_link_record_list>}`
- `pandoc_filter.filters.md2html.increase_header_level.run_filter`
  - [source](./src/pandoc_filter/filters/md2html/increase_header_level.py)
  - command-line: `md2html-increase-header-level-filter`
  - main features: Increase the header level by `1`.

# Samples

Here are 2 basic types of examples

## Convert markdown to markdown (Normalization)

- [Adapt AMS rule for math formula](./examples/md2md_adapt_ams_rule_for_math_formula.md)
- [Convert Github style alert to Hexo style alert](./examples/md2md_convert_github_style_alert_to_hexo_style_alert_filter.md)
- [Normalize footnotes](./examples/md2md_normalize_footnotes.md)
- [Normalize internal link](./examples/md2md_normalize_internal_link.md)
- [Sync local images to `Aliyun OSS`](./examples/md2md_sync_local_images_to_`Aliyun_OSS`.md)

## Convert markdown to html

- [Normalize headers, anchors, internal links and link-like strings](./examples/md2html_normalize_headers_anchors_internal_links_and_link-like_strings.md)


# Contribution

Contributions are welcome. But recently, the introduction and documentation are not complete. So, please wait for a while.

A simple way to contribute is to open an issue to report bugs or request new features.



