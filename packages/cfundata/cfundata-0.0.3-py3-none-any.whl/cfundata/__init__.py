import importlib.resources as pkg_resources
from . import data  # 确保 src/cfun/data/__init__.py 存在
from . import dx
from . import font

ALL_FREQUENCY_PARQUENT_PATH = pkg_resources.files(data).joinpath("all_frequency.parquet")  # 词频数据

DX_DET_ONNX_PATH = pkg_resources.files(dx).joinpath("dx_det.onnx")  # 目标检测模型，由pt转onnx
DX_CLS_ONNX_PATH = pkg_resources.files(dx).joinpath("dx_cls.onnx")
DX_DET_PT_PATH = pkg_resources.files(dx).joinpath("dx_det.pt")  # 目标检测模型对应的pt模型
DX_CLS_PT_PATH = pkg_resources.files(dx).joinpath("dx_cls.pt")
FONT_SIMSUN_PATH = pkg_resources.files(font).joinpath("simsun.ttc")  # 字体文件
__all__ = [
    "ALL_FREQUENCY_PARQUENT_PATH",
    "DX_DET_ONNX_PATH",
    "DX_CLS_ONNX_PATH",
    "DX_DET_PT_PATH",
    "DX_CLS_PT_PATH",
    "FONT_SIMSUN_PATH",
]
