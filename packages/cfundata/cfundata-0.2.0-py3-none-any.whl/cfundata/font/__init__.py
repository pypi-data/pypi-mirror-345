"""该包主要用于存放字体文件
该包主要用于存放字体文件，主要是simsun.ttc字体文件，有些时候在不同的操作系统上，
字体文件的路径可能会有所不同，因此将其放在包内，方便统一管理和使用。

Attributes:
    FONT_SIMSUN_PATH (Path): simsun.ttc字体文件的路径

Example:
    ```python
    from cfundata import FONT_SIMSUN_PATH
    print(FONT_SIMSUN_PATH)
    ```
"""

import importlib.resources as pkg_resources

FONT_SIMSUN_PATH = pkg_resources.files("cfundata.font").joinpath(
    "simsun.ttc"
)  # 字体文件


__all__ = [
    "FONT_SIMSUN_PATH",
]
