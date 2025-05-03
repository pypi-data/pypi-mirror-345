# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
# pyright: reportUnusedImport=false

TORCH_ENABLED = False

try:
    import torch  # @IgnoreException
    from .torchfunction import TorchFunction
    from .torchmodule import TorchModule
    from .torchstruct import TorchStruct

    __all__ = [
        "TorchFunction",
        "TorchModule",
        "TorchStruct",
    ]

    TORCH_ENABLED = True

except ImportError:
    pass
