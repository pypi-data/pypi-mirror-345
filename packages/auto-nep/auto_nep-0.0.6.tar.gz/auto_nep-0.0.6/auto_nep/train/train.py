#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：automation_nep
@File ：train.py
@Author ：RongYi
@Date ：2025/4/29 14:19
@E-mail ：2071914258@qq.com
"""
import os

from auto_nep.utils import myprint, plot_nep, select_trajectory, check
from auto_nep.dataset import xyz_abacus, abacus_nep
from auto_nep.utils.task import sub_abacus, check_abacus, sub_nep, active_gpumd


def train(config):
    """
    训练逻辑实现 分为 abacus gpumd nep 三个板块
    :param env_dict:
    :param config:
    :return:
    """
    check(config)

    if config["task_type"] == "abacus":
        myprint("abacus 单点能计算开始", "YELLOW")
        dataset_roots = xyz_abacus(config)  # 生成数据集 返回数据集大小
        sub_abacus(config, dataset_roots)  # 提交任务
        check_abacus(config, dataset_roots)  # abacus 任务监测
        abacus_nep(dataset_roots, "v0")  # 单点能提取
        sub_nep(config, "v0")  # nep-v0 训练
        plot_nep()  # 训练效果绘制


    if config["task_type"] == "nep":
        myprint("nep 训练开始", "YELLOW")
        sub_nep(config, "v0")  # nep-v0 训练

    if config["task_type"] == "gpumd":
        myprint("gpumd 主动学习开始", "YELLOW")
        # 主动学习迭代
        active_gpumd(config)  # 主动学习跑 gpumd
