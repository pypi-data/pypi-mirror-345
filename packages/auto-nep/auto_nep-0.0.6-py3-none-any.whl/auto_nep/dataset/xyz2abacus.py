#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：MyTools
@File ：io.py
@Author ：RongYi
@Date ：2025/4/28 22:56
@E-mail ：2071914258@qq.com
"""

import os
import re
from auto_nep.utils.myprint import myprint
from ase.io import read


def find_pp_basic(config):
    """
    寻找基组赝势文件
    :param config:
    :return:
    """
    pp, basis = {}, {}

    for index, element_type in enumerate(config['element_type']):
        pp_flag, basis_flag = False, False  # 标志位
        # pp_pattern: 以元素类型开头, 以.upf结尾
        pp_pattern = rf"^{element_type}.*upf$"
        # basis_pattern: 以元素类型开头, 以.orb结尾
        basis_pattern = rf"^{element_type}_.*orb$"

        for filename in os.listdir(config["abacus"]["pp_path"]):
            if re.match(pp_pattern, filename):
                pp[f'{element_type}'] = filename
                pp_flag = True
                break

        for filename in os.listdir(config["abacus"]["basis_path"]):
            if re.match(basis_pattern, filename):
                basis[f'{element_type}'] = filename
                basis_flag = True
                break

        if pp_flag is False:
            myprint(f"未找到 {element_type} 赝势文件, 请检查 {config["abacus"]["pp_path"]}", 'RED')
            exit()
        if basis_flag is False:
            myprint(f"未找到 {element_type} 轨道文件, 请检查 {config["abacus"]["basis_path"]}", 'RED')
            exit()
    myprint(f"赝势文件: {pp}", 'YELLOW')
    myprint(f"轨道文件: {basis}", 'YELLOW')
    return pp, basis


def xyz_abacus(config):
    """
    制作 abacus 训练集
    :param config: 训练配置
    :return: 数据集路径
    """
    # 存在 abacus_dataset 读取数据集大小
    if os.path.exists(config["abacus"]["dataset_path"]):
        myprint(f'使用已存在数据集 {config["abacus"]["dataset_path"]}')
        dataset_roots = []
        # 寻找 STRU 统计数据集大小
        for root, _, files in os.walk(config["abacus"]["dataset_path"]):
            for file in files:
                if file == 'STRU':
                    dataset_roots.append(os.path.abspath(root))
                    break

        myprint(f"数据集大小: {len(dataset_roots)}")
        # 绝对路径 不包括 STRU
        return dataset_roots
    else:
        myprint(f"未找到 {config['abacus']['dataset_path']} 请检查配置文件", 'RED')
        exit()

    # 自动生成 abacus dataset
    home_path = os.getcwd()
    dataset_roots = []
    atoms = read(config['init_train_xyz'])
    # 寻找赝势文件和轨道文件
    pp, basis = find_pp_basic(config)
    myprint(f"生成训练集 abacus_dataset 训练集大小: {len(atoms)}")
    for i in range(1, len(atoms) + 1):
        os.makedirs(f'./abacus_dataset/{i}', exist_ok=True)
        atoms.write(f'./abacus_dataset/{i}/STRU', format='abacus', pp=pp,
                    basis=basis)
        dataset_roots.append(os.path.join(home_path, f"./abacus_dataset/{i}/STRU"))
    return dataset_roots

