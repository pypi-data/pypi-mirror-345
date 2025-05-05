#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：auto_nep
@File ：gpumd.py
@Author ：RongYi
@Date ：2025/5/2 16:29
@E-mail ：2071914258@qq.com
"""
import os
import shutil
from auto_nep.select.select_active import select_active


def gpumd_dataset(config, iteration):
    """
    创建主动学习数据集
    :param config:
    :param iteration:
    :return:
    """

    model_path = config["gpumd"]["model_path"]
    nep_path = config["gpumd"]["init_nep_txt"]
    temperature = config["gpumd"]["temperature"]

    now_path = os.path.abspath(f"./gpumd-dataset/v{iteration}")

    os.makedirs(now_path, exist_ok=True)
    shutil.copy(model_path, now_path)
    shutil.copy(nep_path, now_path)
    with open(f"{now_path}/run.in", 'w', encoding='utf-8') as f:
        f.write(f"potential nep.txt\n"
                f"velocity {temperature[0]}\n"
                f"time_step 1\n\n"
                f"compute_extrapolation asi_file ../active_set.asi check_interval 10 gamma_low 5 gamma_high 10\n"
                f"dump_thermo 200\n"
                f"ensemble npt_mttk temp {temperature[0]} {temperature[1]} iso 0 0\n"
                f"run {config["gpumd"]["md_time"] * 1000}\n\n"
                f"compute_extrapolation asi_file ../active_set.asi check_interval 10 gamma_low 5 gamma_high 10\n"
                f"dump_thermo 200\n"
                f"ensemble npt_mttk temp {temperature[1]} {temperature[0]} iso 0 0\n"
                f"run {config["gpumd"]["md_time"] * 1000}\n"
                )

    return os.path.abspath(f"./gpumd-dataset/v{iteration}")
