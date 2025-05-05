#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：automation_nep
@File ：cli.py
@Author ：RongYi
@Date ：2025/4/29 14:31
@E-mail ：2071914258@qq.com
"""
import argparse
import os.path
from auto_nep.auto_nep import Auto_nep  # 类
from auto_nep.abacus import Abacus  # 类
from auto_nep.utils.config import load_config
from auto_nep.sysprint import sysprint


def main():
    """
    命令行参数设置
    :return:
    """
    parser = argparse.ArgumentParser(description="Automation NEP CLI")
    subparsers = parser.add_subparsers(dest="command")

    # 添加 train 子命令
    train_parser = subparsers.add_parser("train", help="Run training")
    # 为 train 添加子命令 yaml 配置文件
    train_parser.add_argument("-yaml", default="train.yaml", help="train config file")

    # 添加 abacus2nep 命令
    abacus2nep = subparsers.add_parser("abacus2nep", help="abacus dataset -> train.xyz")
    # 添加子命令 path
    abacus2nep.add_argument("-path", default="./", help="abacus dataset path")

    args = parser.parse_args()
    if args.command == 'train':
        config_path = args.yaml
        if not os.path.exists(args.yaml):
            sysprint(f"{args.yaml} 不存在！", "red")
            exit()
        config = load_config(config_path)
        a = Auto_nep(config)
        a.run()
    elif args.command == "abacus2nep":
        abacus = Abacus()
        abacus.dataset_roots = [f"{args.path}"]
        sysprint(f"从 {args.path} 提取 train.xyz")
        abacus.abacus2nep()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
