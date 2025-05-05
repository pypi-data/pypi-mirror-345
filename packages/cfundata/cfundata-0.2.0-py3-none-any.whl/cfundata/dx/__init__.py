"""该包定义了两个yolo模型的路径，分别是目标检测和分类模型

模型采用的是yolov11训练而来的，目标检查和分类模型都含有两种格式的模型，分别是pt和onnx格式， 主要是针对dx的点选和语序yzm训练而来
大约采用了1.4w张图片训练的. 有些时候装ultralytics太慢，使用onnx模型就快很多。

Attributes:
    DX_DET_PT_PATH (Path): 目标检测模型的pt文件路径
    DX_DET_ONNX_PATH (Path): 目标检测模型的onnx文件路径
    DX_CLS_PT_PATH (Path): 分类模型的pt文件路径
    DX_CLS_ONNX_PATH (Path): 分类模型的onnx文件路径


Example:
    ```python
    from cfundata import DX_DET_ONNX_PATH, DX_DET_PT_PATH, DX_CLS_ONNX_PATH, DX_CLS_PT_PATH
    print(DX_DET_ONNX_PATH)
    print(DX_DET_PT_PATH)
    print(DX_CLS_ONNX_PATH)
    print(DX_CLS_PT_PATH)
    ```
"""

import importlib.resources as pkg_resources

# 目标检测模型对应的pt模型和onnx模型
DX_DET_PT_PATH = pkg_resources.files("cfundata.dx").joinpath("dx_det.pt")
DX_DET_ONNX_PATH = pkg_resources.files("cfundata.dx").joinpath("dx_det.onnx")

# 分类模型对应的pt模型和onnx模型
DX_CLS_ONNX_PATH = pkg_resources.files("cfundata.dx").joinpath("dx_cls.onnx")
DX_CLS_PT_PATH = pkg_resources.files("cfundata.dx").joinpath("dx_cls.pt")


__all__ = [
    "DX_DET_ONNX_PATH",
    "DX_DET_PT_PATH",
    "DX_CLS_ONNX_PATH",
    "DX_CLS_PT_PATH",
]
