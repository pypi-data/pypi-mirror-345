#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：automation_nep
@File ：sub_task.py
@Author ：RongYi
@Date ：2025/4/29 20:48
@E-mail ：2071914258@qq.com
"""
import os
import time
import shutil
from auto_nep.utils import myprint, spend_time, shift_energy
from auto_nep.dataset import gpumd_dataset


def sub_abacus(config, dataset_roots):
    """
    提交任务脚本
    :param config: 配置文件
    :return:
    """

    # 检查数据集路径
    if config["abacus"]["dataset_path"]:
        dataset_path = config["abacus"]["dataset_path"]
    else:
        dataset_path = "./abacus_dataset"

    # 提交任务: 收敛标准 time.json文件
    task_num = 0
    home_path = os.getcwd()
    for root in dataset_roots:
        if not os.path.exists(root + "/time.json"):
            shutil.copy(config["abacus"]["input_path"], root)
            shutil.copy(config["abacus"]["pbs_path"], root)
            os.chdir(root)
            os.system('qsub abacus.pbs')
            task_num += 1
    # 提交完成后退回主目录
    os.chdir(home_path)
    myprint(f"任务提交完成 提交计算任务: {task_num}")


def check_abacus(config, dataset_roots):
    """
    检测任务是否完成
    1.有 out.log 无 time.json 计算中
    2.有 time.json 计算完成
    3. 无 out.log 无 time.json 等待中
    :return:
    """
    start_time = time.perf_counter()
    total_time = 0  # 计算总耗时 min

    # 检查数据集路径
    if config["abacus"]["dataset_path"]:
        dataset_path = config["abacus"]["dataset_path"]
    else:
        dataset_path = "./abacus_dataset"
    # 处理未计算任务
    warn_times = 1
    while True:
        accomplish = []
        calculating = []
        awating = []
        for root in dataset_roots:
            time_json = root + "/time.json"
            out_log = root + f"/out.log"
            if os.path.isfile(time_json):
                accomplish.append(root)
            elif os.path.isfile(out_log):
                calculating.append(root)
            else:
                awating.append(root)

        if total_time % 5 == 0:
            # Current Task 打印模块
            myprint("\n-------------------------------- abacus -------------------------------\n"
                   f"Total task num: {len(dataset_roots)}\t Total time(s): {round(time.perf_counter() - start_time, 2)}\t  Progress:{len(accomplish)}/{len(dataset_roots)}\n"
                   f"-----------------------------------------------------------------------")
            for task in calculating:
                step, h, m, s = spend_time(task)
                print(f"Current Task: [{task}] Spend Time: [{h}h {m}m {s}s]\n"
                      f"Step: [{step}]\n"
                      f"-----------------------------------------------------------------------")

        if len(accomplish) == len(dataset_roots):
            myprint("计算完成提取 nep 训练集 train.xyz", 'RED')
            myprint(f"Mean time(s):{(time.perf_counter() - start_time)/len(accomplish): .2f} s")
            break

        if len(calculating) == 0 and len(awating) > 0:
            myprint(f"Warning {warn_times}: 以下任务未进行计算!", "RED")
            for task in awating:
                print(f"{task}")
            warn_times += 1
            if warn_times > config["abacus"]["warn_times"]:
                # 警告超过三次 自动退出 进行下一步
                break

        total_time += 1
        time.sleep(60)


def sub_nep(config, version):
    """
    nep 训练
    :param config:
    :return:
    """

    if config["task_type"] == "nep" and not os.path.exists(config["nep"]["init_train_xyz"]):
        myprint(f"{config["nep"]["init_train_xyz"]} 不存在请检查 init_train_xyz 配置", "RED")
        exit()

    # nep.in 写入
    with open("./nep-dataset/nep.in", 'w', encoding='utf-8') as f:
        element_type = config["element_type"]
        cutoff = config["nep"]["cutoff"]

        f.write(f"type {len(element_type)}")
        for ele in element_type:
            f.write(f" {ele}")

        f.write(f"\ncutoff")
        for cutoff in cutoff:
            f.write(f" {cutoff}")

        f.write("\nzbl 2\n lambda_v 0")

        if version != "v0" and config["nep"]["nep_restart"]:
            f.write(f"lambda_1 0\ngeneration {config["nep"]["nep_restart_step"]}")
        elif version == "v0":
            f.write(f"\ngeneration {config["nep"]["generation"]}")

    # no-shifted-vx.xyz 处理 平移
    if config["nep"]["shift_energy"]:
        myprint("train.xyz 能量平移 Atomic energy---->")
        shift_energy(f"./nep-dataset/no-shifted-{version}.xyz", version)
        shutil.copy(f"./nep-dataset/shifted-{version}.xyz", "./nep-dataset/train.xyz")
    else:
        shutil.copy(f"./nep-dataset/no-shifted-{version}.xyz", "./nep-dataset/train.xyz")

    # 任务提交
    myprint(f"nep-{version} 训练中... 详情请查看 nep.log 文件")
    os.chdir("./nep-dataset")
    os.system(f'nohup {config["nep"]["nep_path"]} > nep.log 2>&1')  # 输出 nep.log 文件


def active_gpumd(config):
    """
    主动学习流程搭建 scf -> nep -> gpumd -> select
    :param config:
    :return:
    """
    # 获取数据集
    for iteration in range(config["gpumd"]["iteration"]+1):
        home_path = os.path.abspath(f"./gpumd-dataset/v{iteration}")

        # 1-scf
        if iteration == 0:
            # 跳过 scf
            os.makedirs(home_path+f"/1-scf")
            myprint(f"主动学习: 第 {iteration} 次迭代, 读取 train.xyz 跳过 scf 步骤")
        else:
            # 计算 abacus
            pass

        # 2-nep
        if iteration == 0:
            # 跳过 2-nep
            os.makedirs(home_path+"/2-nep", exist_ok=True)
            myprint(f"主动学习: 第 {iteration} 次迭代, 读取 train.xyz 跳过 nep 步骤")
        else:
            # 计算 nep
            pass

        # 3-gpumd
        os.makedirs(home_path+"/3-gpumd", exist_ok=True)
        myprint(f"主动学习: 第 {iteration} 次迭代 [gpumd: {f"./gpumd-dataset/v{iteration}/gpumd.out"}]", "YELLOW")
        gpumd_dataset_roots = gpumd_dataset(config, iteration)
        # 提交任务
        home_path = os.getcwd()

        os.chdir(gpumd_dataset_roots)
        os.system(f"nohup {config["gpumd"]["gpumd_path"]} > gpumd.log 2>&1 &")
        os.chdir(home_path)
        # 计算完成提取 MD 轨迹文件


