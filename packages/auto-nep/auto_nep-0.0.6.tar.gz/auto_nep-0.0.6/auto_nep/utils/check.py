#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：auto_nep
@File ：check.py
@Author ：RongYi
@Date ：2025/5/2 16:22
@E-mail ：2071914258@qq.com
"""
import os
import shutil

from auto_nep.utils import myprint
from auto_nep.select.select_active import select_active

def check(config):
    if os.path.exists("./gpumd-dataset"):
        myprint(f"Warning: 主动学习期间将清空 gpumd-datase 文件夹!(保留文件)", "RED")
        while True:
            user_input = input("=========== 输入 yes 继续 输入 no 退出 ===========\n")
            if user_input == "yes":
                for item in os.listdir("./gpumd-dataset"):
                    if os.path.isdir(f"./gpumd-dataset/{item}"):
                        shutil.rmtree(f"./gpumd-dataset/{item}")
                break
            elif user_input == "no":
                exit()
            else:
                continue

    if not os.path.exists(config["nep"]['init_train_xyz']):
        myprint(f"未找到 {config["nep"]['init_train_xyz']} 请检查配置文件", 'RED')
        exit()

    if not os.path.exists(config["gpumd"]["model_path"]):
        myprint(f"未找到 {config["gpumd"]["model_path"]} 请检查配置文件", "RED")
        exit()

    if not os.path.exists(config["gpumd"]["init_nep_txt"]):
        myprint(f"未找到 {config["gpumd"]["init_nep_txt"]} 请检查配置文件", "RED")
        exit()

    if not os.path.exists(config[f"abacus"]["pbs_path"]):
        myprint(f'未找到 {config["abacus"]["pbs_path"]} 请检查配置文件', 'RED')
        exit()

    if not os.path.exists(config["abacus"]["input_path"]):
        myprint(f'未找到 {config["abacus"]["input_path"]} 请检查配置文件', 'RED')
        exit()

    # gpumd 专属检测
    if config["task_type"] == "gpumd":
        if not os.path.exists(config["gpumd"]["asi_file"]):
            myprint(f'未找到 {config["gpumd"]["asi_file"]} 将自动生成!', 'RED')
            if not os.path.exists(config["gpumd"]["init_train_xyz"]):
                myprint(f'未找到 {config["gpumd"]["init_train_xyz"]} 请检查配置文件', 'RED')
                exit()
            os.makedirs("./gpumd-dataset", exist_ok=True)
            select_active(config["gpumd"]["init_nep_txt"], config["gpumd"]["init_train_xyz"], "./gpumd-dataset/")


