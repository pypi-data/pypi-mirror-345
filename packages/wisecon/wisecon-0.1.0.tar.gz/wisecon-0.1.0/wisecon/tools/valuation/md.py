import os
from typing import Union, List, Any


__all__ = [
    "make_industry_valuation_markdown"
]


template_blog_title = """---
draft: false
pin: true
date: {date}
authors:
  - chensy
categories:
  - 行业估值
---

# {title}

{summary}

<!-- more -->

"""

def make_industry_valuation_markdown(
        path: str,
        html_dir: Union[str, List[str]],
        iframe_dir: str,
        **kwargs: Any,
):
    """"""
    iframe_template = '''<div style="text-align: center;"><iframe src="{}" width="720" height="380" frameborder="0"></iframe></div>'''.format

    if isinstance(html_dir, list):
        html_files = []
        for item_html_path in html_dir:
            html_files.extend(os.listdir(item_html_path))
    else:
        html_files = os.listdir(html_dir)

    content_list = [template_blog_title.format(**kwargs)]

    for html_file in html_files:
        html_path, html_name = os.path.split(html_file)
        title = html_name.split(".")[0]
        content_list.append(f"## {title}")
        content_list.append(iframe_template(os.path.join(iframe_dir, html_name)))
        content_list.append("\n")

    content = "\n".join(content_list)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
