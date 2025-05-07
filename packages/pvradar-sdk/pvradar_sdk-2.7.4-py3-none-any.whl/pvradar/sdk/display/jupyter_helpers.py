from typing import Optional
from h3 import Literal
import httpx
import importlib.util

from ..common.settings import SdkSettings


FlowchartRenderer = Literal['markdown', 'kroki_svg', 'kroki_png']


def display_flowchart(flowchart_script, *, renderer: Optional[FlowchartRenderer] = None):
    if renderer is None:
        renderer = SdkSettings.instance().default_flowchart_renderer  # pyright: ignore [reportAssignmentType]
    if importlib.util.find_spec('IPython') is None:
        raise ImportError('IPython package is not installed. Please install Jupyter kernel')
    if renderer == 'markdown':
        from IPython.display import display, Markdown, clear_output  # pyright: ignore [reportMissingImports]

        clear_output(wait=True)
        display(Markdown('```mermaid\n' + flowchart_script + '\n```'))
    elif renderer == 'kroki_svg' or renderer == 'kroki_png':
        from IPython.display import display, SVG, Image, clear_output  # pyright: ignore [reportMissingImports]

        # see https://docs.kroki.io/kroki/setup/http-clients/
        format = 'svg' if renderer == 'kroki_svg' else 'png'
        url = f'https://kroki.io/mermaid/{format}'
        headers = {'Content-Type': 'text/plain'}

        verify = SdkSettings.instance().httpx_verify
        response = httpx.post(url, content=flowchart_script, headers=headers, verify=verify)

        if response.status_code == 200:
            if renderer == 'kroki_svg':
                display(SVG(response.content))
            elif renderer == 'kroki_png':
                display(Image(response.content))
        else:
            print(f'Error: {response.status_code} - {response.text}')
    else:
        raise ValueError(f'Unsupported flowchart renderer: {renderer}')
