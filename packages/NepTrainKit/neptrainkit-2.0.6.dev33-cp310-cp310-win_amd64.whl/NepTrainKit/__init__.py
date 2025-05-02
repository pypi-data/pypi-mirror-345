#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/11/28 12:52
# @Author  :
# @email    : 1747193328@qq.com


# start delvewheel patch
def _delvewheel_patch_1_10_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'neptrainkit.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

import os
import sys
from loguru import logger


try:
    # Actual if statement not needed, but keeps code inspectors more happy
    if __nuitka_binary_dir is not None:
        is_nuitka_compiled = True
except NameError:
    is_nuitka_compiled = False



if is_nuitka_compiled:


    logger.add("./Log/{time:%Y-%m}.log",
               level="DEBUG",
                )
    module_path="./"
else:

    module_path = os.path.dirname(__file__)
