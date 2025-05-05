#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：automation_nep
@File ：nep.py
@Author ：RongYi
@Date ：2025/4/30 11:25
@E-mail ：2071914258@qq.com
"""
import os
import re
from tqdm import tqdm
from auto_nep.utils.myprint import myprint


def abacus_nep(dataset_roots, version):
    """
    abacus 训练集 -> nep 训练集
    :param dataset_roots:
    :param version:
    :return:
    """
    xyz_path = f"./nep-dataset/no-shifted-{version}.xyz"
    myprint("正在生成 nep 训练 trian.xyz 文件")
    os.makedirs("./nep-dataset", exist_ok=True)
    # 重置 no-shifted.xyz
    with open(xyz_path, 'w', encoding='utf-8') as f:
        f.close()

    log_files = []
    for root in dataset_roots:
        for root2, _, files in os.walk(root):
            for file in files:
                if file == "running_scf.log":
                    log_files.append(os.path.abspath(os.path.join(root2, file)))

    for log_file in tqdm(log_files):
        with open(log_file, encoding='utf-8') as f:
            content = f.read()
        if "charge density convergence is achieved" not in content:
            myprint(f"任务未收敛: {log_file}", "RED")
            continue

        # config_type 训练集位置 windows 和 linux 不同
        if os.name == "nt":
            # Windows
            config_type = log_file.split("\\")[:-2]
            config_type = "\\".join(config_type)
        elif os.name == "posix":
            # Linux
            config_type = log_file.split("/")[:-2]
            config_type = "/".join(config_type)

        # 提取原子总数
        total_atom_number_match = re.search(r"TOTAL ATOM NUMBER = (\d+)", content)
        if total_atom_number_match:
            total_atom_number = total_atom_number_match.group(1)
        else:
            myprint(f"{log_file} 能量无法提取!", "RED")
            continue

        # 提取晶格常数
        lattice_match = re.search(r" Lattice vectors.*(\n.*\n.*\n.*)", content)
        if lattice_match:
            lattice = lattice_match.group(1).strip().replace('+', '')
            lattice = ' '.join([f"{float(l):.10f}" for l in lattice.split()])
        else:
            myprint(f"{log_file} 晶格常数无法提取!", "RED")
            continue

        # 提取能量
        energy_match = re.search(r"FINAL_ETOT_IS\s+(\S+)", content)
        if energy_match:
            energy = float(energy_match.group(1))
        else:
            myprint(f"{log_file} 能量无法提取!", "RED")
            continue

        # stress 1 ev/A3  =  160.217662 kbar; 1 kbar  =  0.0062415091 ev/A3
        stress_match = re.search(r"TOTAL-STRESS.*\n.*(\n.*\n.*\n.*)", content)
        if stress_match:
            stress = stress_match.group(1).strip()
            stress = ' '.join([f"{float(s) * 0.0062415091:.10f}" for s in stress.split()])
        else:
            myprint(f"{log_file} 压力无法提取!", "RED")
            continue

        # 位置和力 分数坐标 -> 笛卡尔坐标
        # 读取 a b c
        cell_a_match = re.search(r"NORM_A\s+\S+ (.*)", content)
        cell_b_match = re.search(r"NORM_B\s+\S+ (.*)", content)
        cell_c_match = re.search(r"NORM_C\s+\S+ (.*)", content)

        cell_a = float(cell_a_match.group(1))
        cell_b = float(cell_b_match.group(1))
        cell_c = float(cell_c_match.group(1))

        # 元素类型和坐标转换
        type_position_match = re.compile(r"taud_([a-z,A-z]+)\w+\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)")
        type_position = type_position_match.findall(content)
        type_position = [f"{type}\t{float(x) * cell_a:.10f}\t{float(y) * cell_b:.10f}\t{float(z) * cell_c:.10f}" for type, x, y, z in type_position]
        # 力 找到TOTAL-FORCE开头后面,所有这类格式的行
        force_match = re.compile(
    r"TOTAL-FORCE \(eV/Angstrom\)\s*"
    r"------------------------------------------------------------------------------------------\s*"
    r"((?:\s*\S+\s+-?\d+\.\d+\s+-?\d+\.\d+\s+-?\d+\.\d+\s*\n)*)",
    re.DOTALL
)
        force = force_match.search(content).group(1)
        force = list(filter(None, force.split('\n')))
        # 输出文件
        with open(xyz_path, 'a', encoding='utf-8') as f:
            # 表头
            f.write(f"{total_atom_number}\n"
                    f"Energy={energy:.10f} Lattice=\"{lattice}\" Stress=\"{stress}\""
                    f" Config_type=\"{config_type}\" Properties=species:S:1:pos:R:3:forces:R:3"
                    f" Weight=1.0 Pbc=\"T T T\"\n")

            # 元素种类 位置 力
            for part1, part2 in zip(type_position, force):
                part2 = part2.split(' ')
                # 定义正则表达式模式，匹配整数和浮点数
                pattern = re.compile(r'^[+-]?\d+(\.\d+)?$')
                # 使用列表推导式过滤非数字元素
                part2 = [item for item in part2 if pattern.match(item)]
                part2 = '\t'.join(part2)

                part = '\t'.join([part1, part2])
                f.write(part+"\n")
